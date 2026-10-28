import hashlib
import re
from typing import Any, Dict, List, Tuple


class TextPreprocessor:
    def __init__(self, min_text_len: int = 15, max_text_len: int = 2000):
        self.min_text_len = min_text_len
        self.max_text_len = max_text_len

        # Common bot / boilerplate templates to strip
        self.boilerplate_patterns = [
            r"<!--[\s\S]*?-->",  # HTML comments
            r"```[\s\S]*?```",   # Fenced code blocks
            r"`[^`]+`",          # Inline code
            r"!\[.*?\]\(.*?\)",  # Images
            r"\[.*?\]\(.*?\)",   # Markdown links
            r"https?://\S+",     # Raw URLs
            r"###\s*(Checklist|Environment|Version|System Information)[^\n]*",
            r"- \[[ xX]\].*",    # Checkbox line
            r"Thank you for (submitting|opening|filing) (an?|this) (issue|report)[^\n\.]*[\.\n]?",
            r"This issue (has been automatically marked as stale|was closed because)[^\n\.]*[\.\n]?",
        ]

    def clean_text(self, text: str) -> str:
        """Strip markdown noise, template boilerplate, and excess whitespace."""
        if not text:
            return ""

        cleaned = text

        for pattern in self.boilerplate_patterns:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

        # Collapse excess whitespace and newlines
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def prepare_document(self, issue: Dict[str, Any]) -> str:
        """Combine title and cleaned body into a unified semantic document representation."""
        title = issue.get("title", "").strip()
        body = issue.get("body", "") or ""
        cleaned_body = self.clean_text(body)

        # Prioritize the title heavily by prepending and repeating key subject
        if cleaned_body:
            combined = f"{title}. {cleaned_body}"
        else:
            combined = title

        # Limit max length
        if len(combined) > self.max_text_len:
            combined = combined[: self.max_text_len].rsplit(" ", 1)[0] + "..."

        return combined

    def preprocess_issues(
        self, issues: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Clean, deduplicate, and filter a list of raw issues.
        Returns (valid_issues, clean_documents).
        """
        valid_issues: List[Dict[str, Any]] = []
        clean_docs: List[str] = []
        seen_hashes = set()

        for item in issues:
            title = (item.get("title") or "").strip()
            if not title:
                continue

            doc_text = self.prepare_document(item)

            if len(doc_text) < self.min_text_len:
                continue

            # Normalized hash for deduplication
            norm_key = re.sub(r"[^a-zA-Z0-9]", "", doc_text.lower())
            doc_hash = hashlib.md5(norm_key.encode("utf-8")).hexdigest()

            if doc_hash in seen_hashes:
                continue
            seen_hashes.add(doc_hash)

            # Store clean text back in the issue dictionary
            item_copy = dict(item)
            item_copy["clean_text"] = doc_text
            valid_issues.append(item_copy)
            clean_docs.append(doc_text)

        return valid_issues, clean_docs


preprocessor = TextPreprocessor()

