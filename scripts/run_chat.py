"""
Interactive CLI chat application.

Usage:
    python scripts/run_chat.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from app.config_loader import load_config
from app.retrieval import DocumentRetriever
from app.llm import InferenceLLM
from app.chat import ChatApp


def main():
    """Run interactive chat CLI."""
    print("=" * 80)
    print("RAI Bootcamp Demo - Interactive Chat")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    print("\n✓ Loaded environment variables")
    
    # Load configuration
    cfg = load_config()
    print(f"✓ Loaded configuration")
    
    # Initialize retriever
    retriever = DocumentRetriever(cfg.sources, cfg.data_cache_path)
    chunks = retriever.get_chunks()
    
    if not chunks:
        print("\n⚠ No cached data found. Please run: python scripts/prep_data.py")
        return 1
    
    print(f"✓ Loaded {len(chunks)} cached chunks")
    
    # Initialize LLM
    print(f"\n✓ Connecting to inference endpoint: {cfg.inference.endpoint}")
    print(f"  Deployment: {cfg.inference.deployment_name}")
    
    try:
        llm = InferenceLLM(
            endpoint=cfg.inference.endpoint,
            deployment_name=cfg.inference.deployment_name,
            api_version=cfg.inference.api_version,
        )
        print("✓ LLM client initialized with Entra ID auth")
    except Exception as e:
        print(f"\n✗ Failed to initialize LLM: {e}")
        print("  Ensure you're authenticated via 'az login'")
        return 1
    
    # Initialize chat app
    chat = ChatApp(llm=llm, retriever=retriever)
    print("\n✓ Chat application ready!")
    
    # Interactive loop
    print("\n" + "=" * 80)
    print("Ask questions about the cached sources.")
    print("Type 'quit' or 'exit' to end the session.")
    print("=" * 80 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break
            
            # Get answer
            print("\nThinking...")
            response = chat.answer_question(user_input, top_k=3)
            
            # Display answer
            print(f"\nAssistant: {response.answer}")
            
            # Display citations
            if response.cited_sources:
                print("\n📚 Sources:")
                for i, source in enumerate(response.cited_sources, 1):
                    print(f"\n  [{i}] {source['url']}")
                    print(f"      {source['snippet']}")
            
            print("\n" + "-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
