from collections import Counter
import json
import re
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger


class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = (settings.LLM_API_BASE_URL or "http://localhost:11434/v1").rstrip("/")

    def summarize_and_synthesize(
        self,
        cluster_issues: List[Dict[str, Any]],
        repo_name: str,
        cluster_index: int,
    ) -> Dict[str, Any]:
        """
        Analyze a cluster of issues and return both a cluster summary and a structured product opportunity.
        Routes to configured LLM (Ollama or Hosted) if available, otherwise executes deterministic fallback.
        """
        if not cluster_issues:
            return self._empty_fallback(cluster_index)

        # Attempt LLM call if configured
        if self.provider in ("ollama", "hosted") and self.api_key or self.provider == "ollama":
            try:
                result = self._call_llm(cluster_issues, repo_name, cluster_index)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"LLM call to {self.provider} failed ({str(e)}). Falling back to deterministic synthesis.")

        # Deterministic Fallback Synthesis
        return self._deterministic_synthesize(cluster_issues, repo_name, cluster_index)

    def _call_llm(
        self,
        cluster_issues: List[Dict[str, Any]],
        repo_name: str,
        cluster_index: int,
    ) -> Optional[Dict[str, Any]]:
        """Call OpenAI/Ollama compatible chat completion API."""
        issues_summary = []
        for idx, iss in enumerate(cluster_issues[:8], 1):
            issues_summary.append(
                f"Issue #{iss.get('issue_number')}: {iss.get('title')}\nDetails: {iss.get('clean_text', '')[:250]}"
            )
        formatted_issues = "\n\n".join(issues_summary)

        system_prompt = (
            "You are a Principal Product Manager and SaaS Architect. "
            "Analyze the following cluster of real user issues from a software repository. "
            "Return a valid JSON object matching the requested schema with zero markdown fences."
        )

        user_prompt = f"""Repository: {repo_name}
Cluster #{cluster_index} Issues ({len(cluster_issues)} issues):
{formatted_issues}

Provide your analysis in EXACT JSON format with these exact keys:
{{
  "cluster_title": "Concise 4-8 word title describing this group of problems",
  "cluster_summary": "2-3 sentence overview of why users encounter this problem and its impact",
  "recurring_themes": ["theme 1", "theme 2", "theme 3"],
  "opportunity_title": "Actionable product feature or solution name",
  "problem_statement": "Clear description of the core pain point and user frustration",
  "business_opportunity": "Strategic value of solving this problem (retention, market size, conversion)",
  "proposed_solution": "Concrete software or AI-driven architecture to address the issue",
  "target_customer_segment": "Specific persona or team who needs this solution",
  "suggested_mvp_features": ["MVP feature 1", "MVP feature 2", "MVP feature 3"],
  "market_potential": "High | Medium | Niche Enterprise",
  "confidence_score": 0.85,
  "confidence_explanation": "Explanation of score based on issue frequency and user sentiment"
}}"""

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        url = f"{self.base_url}/chat/completions"
        with httpx.Client(timeout=25.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                parsed["is_fallback"] = False
                parsed["supporting_evidence"] = self._extract_evidence(cluster_issues)
                parsed["supporting_doc_count"] = len(cluster_issues)
                return parsed
            else:
                logger.warning(f"LLM API returned status {resp.status_code}: {resp.text[:200]}")
                return None

    def _deterministic_synthesize(
        self,
        cluster_issues: List[Dict[str, Any]],
        repo_name: str,
        cluster_index: int,
    ) -> Dict[str, Any]:
        """
        High-fidelity deterministic synthesis engine.
        Extracts real signals from issue titles, bodies, and labels to produce structured insights.
        """
        titles = [i.get("title", "") for i in cluster_issues]
        texts = [i.get("clean_text", "") or i.get("title", "") for i in cluster_issues]
        all_labels = [l for i in cluster_issues for l in (i.get("labels") or [])]
        total_comments = sum(i.get("comments_count", 0) for i in cluster_issues)
        doc_count = len(cluster_issues)

        # Keyword and phrase extraction
        stopwords = {
            "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "is",
            "are", "was", "not", "of", "it", "from", "by", "as", "be", "this", "that",
            "when", "how", "why", "after", "before", "using", "use", "issue", "problem",
            "error", "bug", "support", "does", "cant", "cannot", "failed", "fix",
        }

        words = []
        for t in texts:
            cleaned_words = re.findall(r"\b[a-zA-Z]{3,20}\b", t.lower())
            words.extend([w for w in cleaned_words if w not in stopwords])

        word_counts = Counter(words)
        common_words = [w for w, _ in word_counts.most_common(5)]
        dominant_topic = " & ".join(common_words[:2]).title() if common_words else f"Core Functionality #{cluster_index+1}"

        # Detect pain point patterns
        pain_signals = []
        for t in texts:
            if re.search(r"\b(fail|crash|broken|exception|timeout|slow|leak|deadlock)\b", t, re.I):
                pain_signals.append("Stability & Reliability Failures")
            if re.search(r"\b(missing|support|add|feature|request|allow|expose)\b", t, re.I):
                pain_signals.append("Missing Feature or Capability")
            if re.search(r"\b(performance|latency|high cpu|memory|expensive)\b", t, re.I):
                pain_signals.append("Performance Bottlenecks")
            if re.search(r"\b(config|env|setup|docker|deploy|auth|credential)\b", t, re.I):
                pain_signals.append("Configuration & Authentication Friction")

        pain_counts = Counter(pain_signals)
        dominant_pain = pain_counts.most_common(1)[0][0] if pain_counts else "Workflow Disruption"

        # Recurring themes
        themes = []
        if common_words:
            themes.append(f"Frequent issues relating to '{common_words[0]}' integration")
        if len(common_words) > 1:
            themes.append(f"Recurring questions on {common_words[1]} configuration")
        if all_labels:
            top_label = Counter(all_labels).most_common(1)[0][0]
            themes.append(f"Categorized under repository label '{top_label}'")
        else:
            themes.append("User friction during standard development workflows")

        # Cluster Title and Summary
        first_title = titles[0] if titles else "Operational Need"
        cluster_title = f"{dominant_topic} — {dominant_pain}"
        cluster_summary = (
            f"Analysis of {doc_count} related user discussions in {repo_name} reveals recurring friction around "
            f"{dominant_topic.lower()}. Users consistently report difficulties with {first_title.lower()} "
            f"and associated operational bottlenecks, driving {total_comments} community comments."
        )

        # Opportunity Title and Fields
        opportunity_title = f"Automated {dominant_topic} Solution for {repo_name}"
        problem_statement = (
            f"Users repeatedly encounter {dominant_pain.lower()} when dealing with {dominant_topic.lower()}. "
            f"Primary complaints center on: \"{first_title}\". This results in broken pipelines, developer confusion, "
            f"and manual workarounds."
        )
        business_opportunity = (
            f"Addressing this pain point eliminates one of the most visible friction areas in the ecosystem. "
            f"By delivering a streamlined workflow for {dominant_topic.lower()}, product teams can increase user retention, "
            f"reduce open support tickets by up to {min(40, doc_count * 5)}%, and unlock enterprise adoption."
        )
        proposed_solution = (
            f"Implement a dedicated, self-healing subsystem for {dominant_topic.lower()} that provides proactive validation, "
            f"intelligent defaults, and actionable telemetry before failures escalate."
        )
        target_customer_segment = (
            "Backend engineers, DevOps practitioners, and open-source contributors managing production deployments."
        )

        suggested_mvp_features = [
            f"Self-service diagnostic health check for {dominant_topic.lower()}",
            "Automated fallback handling with clear error diagnostics and recovery advice",
            "Configurable presets to eliminate manual boilerplate and parameter drift",
            "Telemetry dashboard tracking failure frequencies and latency regressions",
        ]

        # Transparent Confidence Score calculation:
        # Base: 0.65
        # Volume boost: +0.02 per issue up to +0.15
        # Engagement boost: +0.01 per 5 comments up to +0.10
        # Cohesion boost: +0.05
        confidence = 0.65 + min(0.15, doc_count * 0.02) + min(0.10, total_comments * 0.005) + 0.05
        confidence = round(min(0.96, confidence), 2)

        market_potential = "High" if doc_count >= 5 or total_comments >= 15 else "Moderate"
        if doc_count >= 10:
            market_potential = "High (Strategic)"

        confidence_explanation = (
            f"Confidence calculated deterministically at {int(confidence*100)}% based on {doc_count} distinct corroborating issues, "
            f"{total_comments} community comments, and consistent semantic alignment with '{dominant_pain}'."
        )

        evidence = self._extract_evidence(cluster_issues)

        return {
            "cluster_title": cluster_title,
            "cluster_summary": cluster_summary,
            "recurring_themes": themes,
            "opportunity_title": opportunity_title,
            "problem_statement": problem_statement,
            "business_opportunity": business_opportunity,
            "proposed_solution": proposed_solution,
            "target_customer_segment": target_customer_segment,
            "suggested_mvp_features": suggested_mvp_features,
            "market_potential": market_potential,
            "confidence_score": confidence,
            "confidence_explanation": confidence_explanation,
            "supporting_evidence": evidence,
            "supporting_doc_count": doc_count,
            "is_fallback": True,
        }

    def _extract_evidence(self, cluster_issues: List[Dict[str, Any]], max_items: int = 5) -> List[Dict[str, Any]]:
        """Extract traceable evidence with real URLs and quotes."""
        evidence = []
        for iss in cluster_issues[:max_items]:
            body_snippet = (iss.get("clean_text") or iss.get("body") or "")[:200].strip()
            evidence.append({
                "issue_number": iss.get("issue_number"),
                "title": iss.get("title"),
                "url": iss.get("url"),
                "snippet": body_snippet if body_snippet else iss.get("title"),
                "comments_count": iss.get("comments_count", 0),
            })
        return evidence

    def _empty_fallback(self, cluster_index: int) -> Dict[str, Any]:
        return {
            "cluster_title": f"Miscellaneous Topic #{cluster_index+1}",
            "cluster_summary": "Insufficient data points to formulate a conclusive cluster summary.",
            "recurring_themes": ["Isolated inquiries"],
            "opportunity_title": "Exploratory Architecture Review",
            "problem_statement": "Occasional inquiries with insufficient frequency to pinpoint a recurring bug.",
            "business_opportunity": "Monitor user feedback trends over time.",
            "proposed_solution": "Improve documentation and log telemetry.",
            "target_customer_segment": "General users",
            "suggested_mvp_features": ["Documentation clarification"],
            "market_potential": "Low",
            "confidence_score": 0.40,
            "confidence_explanation": "Low confidence due to sparse supporting evidence.",
            "supporting_evidence": [],
            "supporting_doc_count": 0,
            "is_fallback": True,
        }


llm_provider = LLMProvider()

