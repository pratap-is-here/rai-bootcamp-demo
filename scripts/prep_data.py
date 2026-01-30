"""
Data preparation script: fetches and caches configured sources.

Usage:
    python scripts/prep_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from app.config_loader import load_config
from app.retrieval import DocumentRetriever


def main():
    """Fetch sources and cache for use in chat and evaluation."""
    print("=" * 80)
    print("RAI Bootcamp Demo - Data Preparation")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    print("\n✓ Loaded environment variables")
    
    # Load configuration
    cfg = load_config()
    print(f"✓ Loaded configuration with {len(cfg.sources)} sources")
    
    # Display sources
    print("\nConfigured sources:")
    for i, src in enumerate(cfg.sources, 1):
        print(f"  {i}. {src.get('name', 'Unknown')}")
        print(f"     {src.get('url', 'No URL')}")
    
    # Create retriever
    retriever = DocumentRetriever(cfg.sources, cfg.data_cache_path)
    print(f"\n✓ Created retriever with cache path: {cfg.data_cache_path}")
    
    # Fetch and cache
    print("\nFetching sources (this may take a moment)...")
    chunks = retriever.fetch_and_cache()
    
    if not chunks:
        print("\n⚠ No chunks retrieved. Check network connectivity and source URLs.")
        return 1
    
    # Summary
    print(f"\n{'=' * 80}")
    print(f"✓ Successfully cached {len(chunks)} chunks")
    print(f"{'=' * 80}\n")
    
    # Show sample chunks
    print("Sample chunks (first 3):")
    for i, chunk in enumerate(chunks[:3], 1):
        preview = chunk.text[:150] + "..." if len(chunk.text) > 150 else chunk.text
        print(f"\nChunk {i}:")
        print(f"  URL: {chunk.url}")
        print(f"  Length: {len(chunk.text)} chars")
        print(f"  Preview: {preview}")
    
    print(f"\n✓ Data preparation complete!")
    print(f"  Cache file: {cfg.data_cache_path}")
    print(f"  Ready for chat and evaluation.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
