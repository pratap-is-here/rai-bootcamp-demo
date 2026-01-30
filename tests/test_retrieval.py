"""
Unit tests for retrieval module (fetch, clean, chunk, score).
"""
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import patch, Mock

import json
import pytest

from app.retrieval import DocumentRetriever, SimpleScorer, Chunk, retrieve_for_query


SAMPLE_HTML = """
<html>
<head><title>Test Page</title><style>.x{}</style></head>
<body>
<h1>Authentication Troubleshooting</h1>
<p>If you cannot sign in, check your MFA and SSO settings.</p>
<script>var x=1;</script>
<p>Virtual Agent is available 24x7 for support.</p>
</body>
</html>
"""


def make_sources(tmp_path: Path) -> List[Dict[str, Any]]:
    # Provide a single test URL
    return [{"name": "Test", "url": "https://sharepoint.example/test", "description": "Test source"}]


@patch("app.retrieval.requests.get")
def test_fetch_and_cache(mock_get, tmp_path):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_HTML
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    cache_path = tmp_path / "data_cache.json"
    retriever = DocumentRetriever(make_sources(tmp_path), str(cache_path))
    chunks = retriever.fetch_and_cache()

    assert len(chunks) >= 1
    assert cache_path.exists()
    # Validate cache content
    data = json.loads(cache_path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["url"] == "https://sharepoint.example/test"


def test_simple_scorer_ranks_relevant_chunks(tmp_path):
    # Build a few chunks manually
    chunks = [
        Chunk(url="u1", chunk_id=1, text="authentication sign in sso mfa"),
        Chunk(url="u2", chunk_id=1, text="virtual agent support helpdesk"),
        Chunk(url="u3", chunk_id=1, text="unrelated content about cafeteria menu"),
    ]
    scorer = SimpleScorer(chunks)
    results = scorer.score("How do I troubleshoot authentication errors?", top_k=2)
    # First result should be the authentication chunk
    assert results[0][1].url == "u1"


def test_retrieve_for_query(tmp_path):
    # Use cache to avoid HTTP in this test
    cache_path = tmp_path / "data_cache.json"
    payload = [
        {"url": "u1", "chunk_id": 1, "text": "authentication mfa sso"},
        {"url": "u2", "chunk_id": 1, "text": "virtual agent support"},
    ]
    cache_path.write_text(json.dumps(payload), encoding="utf-8")

    retriever = DocumentRetriever([], str(cache_path))
    top = retrieve_for_query("Where is the virtual agent?", retriever, top_k=1)
    assert len(top) == 1
    assert top[0].url == "u2"
