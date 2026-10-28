from app.services.llm_provider import LLMProvider


def test_deterministic_fallback_synthesis():
    provider = LLMProvider()
    cluster_issues = [
        {
            "issue_number": 101,
            "title": "OAuth2 authentication token refresh fails intermittently",
            "body": "When refreshing expired tokens, endpoint throws HTTP 500 internal server error.",
            "clean_text": "OAuth2 authentication token refresh fails intermittently. When refreshing expired tokens, endpoint throws HTTP 500.",
            "url": "https://github.com/acme/project/issues/101",
            "comments_count": 8,
            "labels": ["bug", "security"],
        },
        {
            "issue_number": 105,
            "title": "JWT refresh token expires too early in background jobs",
            "body": "Background worker jobs terminate when token refresh is rejected.",
            "clean_text": "JWT refresh token expires too early in background jobs. Background worker jobs terminate.",
            "url": "https://github.com/acme/project/issues/105",
            "comments_count": 4,
            "labels": ["bug", "auth"],
        },
    ]

    result = provider.summarize_and_synthesize(cluster_issues, "acme/project", cluster_index=0)

    assert result["is_fallback"] is True
    assert "problem_statement" in result
    assert "business_opportunity" in result
    assert "proposed_solution" in result
    assert "suggested_mvp_features" in result
    assert len(result["suggested_mvp_features"]) > 0
    assert result["confidence_score"] > 0.60
    assert "supporting_evidence" in result
    assert len(result["supporting_evidence"]) == 2
    assert result["supporting_evidence"][0]["issue_number"] == 101

