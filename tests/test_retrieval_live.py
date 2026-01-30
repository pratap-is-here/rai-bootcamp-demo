"""
Live integration test for fetching actual SharePoint sources defined in
`config/sources.json`.

Notes:
- This test performs real HTTP requests and requires network access and
  appropriate authentication to the SharePoint tenants.
- By default, the test is skipped. To run it, set environment variable
  `RUN_LIVE_TESTS=1`.
- The test succeeds if at least one configured SharePoint URL is reachable
  and yields non-empty chunks after cleaning and chunking.
"""
from __future__ import annotations

import os
import pytest
from pathlib import Path

from app.config_loader import load_config
from dotenv import load_dotenv
from app.retrieval import DocumentRetriever


RUN_LIVE = os.getenv("RUN_LIVE_TESTS") == "1"


@pytest.mark.skipif(not RUN_LIVE, reason="Live tests disabled. Set RUN_LIVE_TESTS=1 to enable.")
def test_fetch_sharepoint_live_sources(tmp_path: Path):
  # Ensure environment variables are loaded from .env if present
  load_dotenv()
  # Load configured sources from the project's config
  cfg = load_config()
  cache_path = tmp_path / "data_cache.json"

  retriever = DocumentRetriever(cfg.sources, str(cache_path))
  chunks = retriever.fetch_and_cache()

  if not chunks:
    pytest.skip(
      "No chunks fetched from live sources. This can happen if network/auth to SharePoint is unavailable."
    )

# Ensure we fetched at least one chunk from expected domains
    expected_domains = (
        "https://microsoft.sharepoint.com",
        "https://microsoftapc.sharepoint.com",
        "https://www.microsoft.com",
    )
    assert any(any(c.url.startswith(d) for d in expected_domains) for c in chunks), "No chunks from expected domains detected."
  assert cache_path.exists(), "Cache file should be created after fetching."


@pytest.mark.skipif(not RUN_LIVE, reason="Live tests disabled. Set RUN_LIVE_TESTS=1 to enable.")
def test_fetch_specific_techweb_page(tmp_path: Path):
    """
    Targeted live test for a publicly accessible Microsoft Research blog page.

    Uses the URL:
    https://www.microsoft.com/en-us/research/blog/learning-from-other-domains-to-advance-ai-evaluation-and-testing/

    Skips gracefully if unreachable due to network constraints.
    """
    load_dotenv()

    sources = [
        {
            "name": "Microsoft Research Blog",
            "url": "https://www.microsoft.com/en-us/research/blog/learning-from-other-domains-to-advance-ai-evaluation-and-testing/",
            "description": "Microsoft Research Blog on AI Evaluation",
        }
    ]
    cache_path = tmp_path / "data_cache.json"

    retriever = DocumentRetriever(sources, str(cache_path))
    chunks = retriever.fetch_and_cache()

    if not chunks:
        pytest.skip(
            "Microsoft Research blog fetch yielded no chunks. Likely due to network issues."
        )

    # Print summary and preview of retrieved chunks
    print(f"\n{'='*80}")
    print(f"Retrieved {len(chunks)} chunks from Microsoft Research blog")
    print(f"{'='*80}\n")
    
    for i, chunk in enumerate(chunks[:5], 1):  # Show first 5 chunks
        preview = chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text
        print(f"Chunk #{i} (ID: {chunk.chunk_id}):")
        print(f"  URL: {chunk.url}")
        print(f"  Length: {len(chunk.text)} characters")
        print(f"  Preview: {preview}")
        print(f"{'-'*80}\n")

    # Verify chunks were created from the expected URL
    assert any(
        c.url.startswith("https://www.microsoft.com") for c in chunks
    ), "Expected chunks from microsoft.com domain."
    assert cache_path.exists(), "Cache file should be created after fetching."
    
    # Validate chunk content has reasonable text
    assert all(len(c.text) > 50 for c in chunks[:3]), "Chunks should contain meaningful text content."
