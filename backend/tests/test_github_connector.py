from unittest.mock import MagicMock, patch
import httpx
import pytest
from app.core.errors import GitHubAPIError
from app.services.github_connector import GitHubConnector


def test_validate_repository_success():
    connector = GitHubConnector()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": 12345,
        "name": "fastapi",
        "full_name": "fastapi/fastapi",
        "description": "FastAPI framework, high performance",
        "stargazers_count": 80000,
        "open_issues_count": 450,
        "html_url": "https://github.com/fastapi/fastapi",
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        info = connector.validate_repository("fastapi", "fastapi")
        assert info["name"] == "fastapi"
        assert info["stargazers_count"] == 80000


def test_validate_repository_not_found():
    connector = GitHubConnector()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Not Found"

    with patch("httpx.Client.get", return_value=mock_resp):
        with pytest.raises(GitHubAPIError) as exc_info:
            connector.validate_repository("nonexistent", "repo")
        assert "not found" in str(exc_info.value).lower()
        assert exc_info.value.status_code == 404


def test_validate_repository_rate_limit():
    connector = GitHubConnector()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.headers = {"x-ratelimit-reset": "1700000000"}
    mock_resp.text = "API rate limit exceeded"

    with patch("httpx.Client.get", return_value=mock_resp):
        with pytest.raises(GitHubAPIError) as exc_info:
            connector.validate_repository("owner", "repo")
        assert "rate limit" in str(exc_info.value).lower()
        assert exc_info.value.status_code == 403


def test_fetch_issues_excludes_pull_requests():
    connector = GitHubConnector()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {
            "id": 101,
            "number": 1,
            "title": "Real Bug Report",
            "body": "App crashes when clicking submit button repeatedly.",
            "html_url": "https://github.com/owner/repo/issues/1",
            "state": "open",
            "user": {"login": "dev1"},
            "labels": [{"name": "bug"}],
            "comments": 5,
        },
        {
            "id": 102,
            "number": 2,
            "title": "Fix crash bug in submit button",
            "body": "This PR fixes issue #1",
            "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/2"},
            "html_url": "https://github.com/owner/repo/pull/2",
            "state": "open",
            "user": {"login": "contributor"},
            "labels": [],
            "comments": 1,
        },
    ]

    with patch("httpx.Client.get", return_value=mock_resp):
        issues = connector.fetch_issues("owner", "repo", limit=10)
        assert len(issues) == 1
        assert issues[0]["issue_number"] == 1
        assert issues[0]["title"] == "Real Bug Report"
        assert issues[0]["author"] == "dev1"
        assert issues[0]["labels"] == ["bug"]

