"""
Chat application: retrieval-augmented generation with citations.
"""
from __future__ import annotations

from typing import List, Dict, Any
from dataclasses import dataclass

from app.retrieval import DocumentRetriever, retrieve_for_query, Chunk
from app.llm import InferenceLLM


@dataclass
class ChatResponse:
    """Response from the chat application."""
    answer: str
    cited_sources: List[Dict[str, str]]
    context_chunks: List[Chunk]


class ChatApp:
    """RAG chat application with retrieval and LLM-based answering."""
    
    def __init__(self, llm: InferenceLLM, retriever: DocumentRetriever):
        """
        Initialize chat application.
        
        Args:
            llm: Inference LLM wrapper
            retriever: Document retriever with cached sources
        """
        self.llm = llm
        self.retriever = retriever
    
    def answer_question(self, user_query: str, top_k: int = 3) -> ChatResponse:
        """
        Answer a user question using retrieval and LLM generation.
        
        Args:
            user_query: User's question
            top_k: Number of top chunks to retrieve
            
        Returns:
            ChatResponse with answer and citations
        """
        # Retrieve relevant chunks
        chunks = retrieve_for_query(user_query, self.retriever, top_k=top_k)
        
        if not chunks:
            return ChatResponse(
                answer="I don't have enough information to answer that question.",
                cited_sources=[],
                context_chunks=[],
            )
        
        # Build grounded prompt
        context_text = "\n\n".join([
            f"Source {i+1} ({chunk.url}):\n{chunk.text}"
            for i, chunk in enumerate(chunks)
        ])
        
        prompt = f"""Based on the following sources, answer the question.
If the answer is not in the sources, say so.

Sources:
{context_text}

Question: {user_query}

Answer:"""
        
        system_prompt = "You are a helpful assistant that answers questions based on provided sources. Always cite which source you're using."
        
        # Generate answer
        answer = self.llm.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500,
        )
        
        # Format citations
        cited_sources = [
            {
                "url": chunk.url,
                "snippet": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
            }
            for chunk in chunks
        ]
        
        return ChatResponse(
            answer=answer,
            cited_sources=cited_sources,
            context_chunks=chunks,
        )
