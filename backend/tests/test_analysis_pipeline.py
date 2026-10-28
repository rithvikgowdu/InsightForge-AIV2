from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.orchestrator import orchestrator


def test_submit_analysis_endpoint(client: TestClient, auth_headers: dict):
    payload = {
        "repo_url": "https://github.com/astral-sh/uv",
        "issue_limit": 25,
    }
    with patch("app.services.background_worker.background_worker.dispatch_analysis") as mock_dispatch:
        response = client.post("/api/v1/analysis", json=payload, headers=auth_headers)
        assert response.status_code == 202
        data = response.json()
        assert data["repo_owner"] == "astral-sh"
        assert data["repo_name"] == "uv"
        assert data["status"] == "QUEUED"
        assert "id" in data
        mock_dispatch.assert_called_once()


def test_user_data_isolation(
    client: TestClient,
    auth_headers: dict,
    user2_auth_headers: dict,
):
    # User 1 submits analysis
    with patch("app.services.background_worker.background_worker.dispatch_analysis"):
        create_resp = client.post(
            "/api/v1/analysis",
            json={"repo_url": "facebook/react", "issue_limit": 10},
            headers=auth_headers,
        )
        assert create_resp.status_code == 202
        analysis_id = create_resp.json()["id"]

    # User 1 can access
    resp1 = client.get(f"/api/v1/analysis/{analysis_id}", headers=auth_headers)
    assert resp1.status_code == 200

    # User 2 CANNOT access User 1's analysis (Forbidden / Permission Denied)
    resp2 = client.get(f"/api/v1/analysis/{analysis_id}", headers=user2_auth_headers)
    assert resp2.status_code in (403, 404)

    # User 2 cannot access status of User 1's analysis
    resp3 = client.get(f"/api/v1/analysis/{analysis_id}/status", headers=user2_auth_headers)
    assert resp3.status_code in (403, 404)


def test_orchestrator_pipeline_execution(client: TestClient, auth_headers: dict, db_session: Session):
    # Submit analysis
    with patch("app.services.background_worker.background_worker.dispatch_analysis"):
        create_resp = client.post(
            "/api/v1/analysis",
            json={"repo_url": "encode/uvicorn", "issue_limit": 10},
            headers=auth_headers,
        )
        analysis_id = create_resp.json()["id"]

    # Mock GitHub Connector responses
    mock_issues = [
        {
            "source_id": "1",
            "issue_number": 1,
            "title": "WebSocket connection disconnects unexpectedly under high load",
            "body": "Clients experience disconnection during concurrent broadcasts.",
            "url": "https://github.com/encode/uvicorn/issues/1",
            "state": "open",
            "author": "alice",
            "labels": ["bug", "websocket"],
            "comments_count": 6,
            "source_created_at": None,
        },
        {
            "source_id": "2",
            "issue_number": 2,
            "title": "WebSocket handshake timeout error when behind nginx reverse proxy",
            "body": "When running behind proxy, websocket upgrade handshake times out.",
            "url": "https://github.com/encode/uvicorn/issues/2",
            "state": "open",
            "author": "bob",
            "labels": ["bug", "network"],
            "comments_count": 3,
            "source_created_at": None,
        },
        {
            "source_id": "3",
            "issue_number": 3,
            "title": "Add support for custom TLS cipher suites in SSLConfig",
            "body": "Security requirements mandate disabling legacy TLS 1.1 ciphers.",
            "url": "https://github.com/encode/uvicorn/issues/3",
            "state": "open",
            "author": "carol",
            "labels": ["feature", "security"],
            "comments_count": 9,
            "source_created_at": None,
        },
    ]

    with patch("app.services.github_connector.github_connector.validate_repository", return_value={"name": "uvicorn"}), \
         patch("app.services.github_connector.github_connector.fetch_issues", return_value=mock_issues):
        # Execute pipeline synchronously
        orchestrator.run_analysis_pipeline(db_session, analysis_id)

    # Fetch detail via API
    detail_resp = client.get(f"/api/v1/analysis/{analysis_id}", headers=auth_headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()

    assert detail["status"] == "COMPLETED"
    assert detail["progress_pct"] == 100
    assert detail["total_issues_collected"] == 3
    assert len(detail["clusters"]) >= 1
    assert len(detail["opportunities"]) >= 1
    assert len(detail["sample_issues"]) == 3

    # Check opportunity structure
    opp = detail["opportunities"][0]
    assert opp["confidence_score"] >= 0.50
    assert len(opp["suggested_mvp_features"]) > 0
    assert opp["is_fallback"] is True

