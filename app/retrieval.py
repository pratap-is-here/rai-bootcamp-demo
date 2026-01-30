"""
Retrieval module: fetches SharePoint pages, cleans HTML, chunks text,
provides a simple TF‑IDF scorer to select top‑k passages for a query.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    url: str
    chunk_id: int
    text: str


class DocumentRetriever:
    def __init__(self, sources: List[Dict[str, Any]], cache_path: str):
        self.sources = sources
        self.cache_path = Path(cache_path)
        self._chunks: List[Chunk] = []

    def fetch_and_cache(self) -> List[Chunk]:
        """Fetch sources, clean, chunk, and cache to JSON."""
        all_chunks: List[Chunk] = []
        for src in self.sources:
            url = src.get("url")
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                cleaned = self._clean_html(resp.text)
                chunks = self._chunk_text(cleaned)
                for i, ch in enumerate(chunks, start=1):
                    all_chunks.append(Chunk(url=url, chunk_id=i, text=ch))
            except Exception:
                # Skip unreachable sources to keep demo resilient
                continue

        self._chunks = all_chunks
        self._write_cache(all_chunks)
        return all_chunks

    def load_cache(self) -> List[Chunk]:
        """Load chunks from cache if present."""
        if not self.cache_path.exists():
            return []
        try:
            raw = json.loads(self.cache_path.read_text(encoding="utf-8"))
            chunks = [Chunk(**item) for item in raw]
            self._chunks = chunks
            return chunks
        except Exception:
            return []

    def get_chunks(self) -> List[Chunk]:
        """Return cached chunks or fetch and cache if none available."""
        cached = self.load_cache()
        if cached:
            return cached
        return self.fetch_and_cache()

    def _write_cache(self, chunks: List[Chunk]) -> None:
        payload = [
            {"url": c.url, "chunk_id": c.chunk_id, "text": c.text}
            for c in chunks
        ]
        self.cache_path.write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def _clean_html(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _chunk_text(text: str, max_words: int = 300, overlap: int = 50) -> List[str]:
        words = text.split()
        if not words:
            return []
        chunks: List[str] = []
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start = end - overlap
            if start < 0:
                start = 0
        return chunks


class SimpleScorer:
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._texts = [c.text for c in chunks]

    def build_index(self) -> None:
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform(self._texts)

    def score(self, query: str, top_k: int = 3) -> List[Tuple[float, Chunk]]:
        if not self._vectorizer or self._matrix is None:
            self.build_index()
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix).flatten()
        # Get top_k indices
        indices = sims.argsort()[::-1][:top_k]
        results: List[Tuple[float, Chunk]] = []
        for idx in indices:
            results.append((float(sims[idx]), self.chunks[idx]))
        return results


def retrieve_for_query(query: str, retriever: DocumentRetriever, top_k: int = 3) -> List[Chunk]:
    """Convenience function: load chunks and return top‑k by TF‑IDF scoring."""
    chunks = retriever.get_chunks()
    scorer = SimpleScorer(chunks)
    scored = scorer.score(query, top_k=top_k)
    return [c for _, c in scored]
