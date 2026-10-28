from app.services.preprocessing import TextPreprocessor


def test_clean_text_strips_markdown_and_boilerplate():
    preprocessor = TextPreprocessor()
    raw = """
    <!-- Comment -->
    ### Checklist
    - [x] I checked existing issues
    
    ```python
    def crash():
        pass
    ```
    Thank you for submitting an issue!
    Here is the actual bug: The application fails to reconnect after network drop.
    Check documentation at https://example.com/docs
    """
    cleaned = preprocessor.clean_text(raw)
    assert "Checklist" not in cleaned
    assert "def crash" not in cleaned
    assert "https://example.com" not in cleaned
    assert "application fails to reconnect after network drop" in cleaned


def test_preprocess_issues_deduplication():
    preprocessor = TextPreprocessor()
    issues = [
        {
            "title": "Database connection pool timeout",
            "body": "Postgres connection pooling fails under high concurrency.",
            "source_id": "1",
        },
        {
            "title": "Database connection pool timeout",
            "body": "Postgres connection pooling fails under high concurrency.",
            "source_id": "2",
        },
        {
            "title": "Very short",
            "body": "x",  # Trivial length
            "source_id": "3",
        },
    ]

    valid, docs = preprocessor.preprocess_issues(issues)
    assert len(valid) == 1
    assert valid[0]["source_id"] == "1"
    assert len(docs) == 1

