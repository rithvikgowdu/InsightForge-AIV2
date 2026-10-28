from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.core.errors import GitHubAPIError
from app.core.logging import logger


class GitHubConnector:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.base_url = settings.GITHUB_API_BASE_URL.rstrip("/")
        self.timeout = 25.0

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "InsightForge-AI/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def validate_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Verify repository exists and is accessible."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=self._get_headers())
                
                if response.status_code == 404:
                    raise GitHubAPIError(
                        f"Repository '{owner}/{repo}' was not found on GitHub. Please check the spelling or ensure it is public.",
                        status_code=404,
                    )
                if response.status_code == 403:
                    rate_limit_reset = response.headers.get("x-ratelimit-reset")
                    msg = "GitHub API rate limit exceeded."
                    if not self.token:
                        msg += " Configure a GITHUB_TOKEN in your environment for a 5,000 requests/hour limit."
                    raise GitHubAPIError(msg, status_code=403, details={"reset": rate_limit_reset})
                
                if response.status_code != 200:
                    raise GitHubAPIError(
                        f"GitHub API returned unexpected status code {response.status_code}: {response.text[:200]}",
                        status_code=response.status_code,
                    )

                data = response.json()
                return {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "full_name": data.get("full_name"),
                    "description": data.get("description"),
                    "stargazers_count": data.get("stargazers_count", 0),
                    "open_issues_count": data.get("open_issues_count", 0),
                    "html_url": data.get("html_url"),
                }
        except httpx.TimeoutException:
            raise GitHubAPIError("Timed out while contacting GitHub API. Please try again.", status_code=504)
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Network error connecting to GitHub: {str(e)}", status_code=502)

    def fetch_issues(
        self,
        owner: str,
        repo: str,
        limit: int = 50,
        include_closed: bool = True,
    ) -> List[Dict[str, Any]]:
        """Fetch issues (excluding pull requests) from GitHub repository."""
        collected: List[Dict[str, Any]] = []
        seen_ids = set()
        page = 1
        per_page = min(limit, 100)
        state = "all" if include_closed else "open"

        logger.info(f"Fetching up to {limit} issues for {owner}/{repo} (state={state})...")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                while len(collected) < limit:
                    url = f"{self.base_url}/repos/{owner}/{repo}/issues"
                    params = {
                        "state": state,
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "direction": "desc",
                    }
                    response = client.get(url, headers=self._get_headers(), params=params)

                    if response.status_code == 404:
                        raise GitHubAPIError(f"Repository '{owner}/{repo}' not found.", status_code=404)
                    if response.status_code == 403:
                        raise GitHubAPIError("GitHub API rate limit exceeded while collecting issues.", status_code=403)
                    if response.status_code != 200:
                        raise GitHubAPIError(
                            f"Failed to fetch issues: GitHub returned {response.status_code}",
                            status_code=response.status_code,
                        )

                    batch = response.json()
                    if not isinstance(batch, list) or len(batch) == 0:
                        break  # No more issues

                    added_in_page = 0
                    for item in batch:
                        # Exclude pull requests (GitHub issues API includes PRs with a "pull_request" key)
                        if "pull_request" in item:
                            continue

                        issue_num = item.get("number")
                        if not issue_num or issue_num in seen_ids:
                            continue

                        seen_ids.add(issue_num)
                        added_in_page += 1

                        # Extract labels
                        raw_labels = item.get("labels", [])
                        labels = [
                            l.get("name") if isinstance(l, dict) else str(l)
                            for l in raw_labels
                        ]

                        # Parse created_at
                        source_created_at = None
                        raw_date = item.get("created_at")
                        if raw_date:
                            try:
                                source_created_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                            except Exception:
                                pass

                        author = None
                        user_obj = item.get("user")
                        if isinstance(user_obj, dict):
                            author = user_obj.get("login")

                        collected.append({
                            "source_id": str(item.get("id", issue_num)),
                            "issue_number": issue_num,
                            "title": item.get("title", "").strip(),
                            "body": item.get("body") or "",
                            "url": item.get("html_url", f"https://github.com/{owner}/{repo}/issues/{issue_num}"),
                            "state": item.get("state", "open"),
                            "author": author,
                            "labels": labels,
                            "comments_count": item.get("comments", 0),
                            "source_created_at": source_created_at,
                        })

                        if len(collected) >= limit:
                            break

                    # If this page returned fewer than per_page items, or no new issues were added, we have reached the end
                    if len(batch) < per_page or added_in_page == 0:
                        break

                    page += 1

        except httpx.TimeoutException:
            raise GitHubAPIError("Timed out while retrieving issues from GitHub.", status_code=504)
        except httpx.RequestError as e:
            raise GitHubAPIError(f"Network error while retrieving issues: {str(e)}", status_code=502)

        logger.info(f"Successfully collected {len(collected)} issues from {owner}/{repo}.")
        return collected


github_connector = GitHubConnector()

