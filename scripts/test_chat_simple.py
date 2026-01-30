"""
Simple non-interactive test of the chat application.
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from app.config_loader import load_config
from app.retrieval import DocumentRetriever
from app.llm import InferenceLLM
from app.chat import ChatApp

# Load environment
load_dotenv()
cfg = load_config()

# Initialize components
retriever = DocumentRetriever(cfg.sources, cfg.data_cache_path)
chunks = retriever.get_chunks()
print(f"✓ Loaded {len(chunks)} cached chunks\n")

llm = InferenceLLM(
    endpoint=cfg.inference.endpoint,
    deployment_name=cfg.inference.deployment_name,
    api_version=cfg.inference.api_version,
)
print(f"✓ Connected to LLM: {cfg.inference.deployment_name}\n")

chat = ChatApp(llm=llm, retriever=retriever)

# Test question
question = "What are Microsoft's principles for responsible AI?"
print(f"Question: {question}\n")

response = chat.answer_question(question, top_k=3)

print(f"Answer: {response.answer}\n")
print(f"\n📚 Sources ({len(response.cited_sources)}):")
for i, source in enumerate(response.cited_sources, 1):
    print(f"\n  [{i}] {source['url']}")
    print(f"      {source['snippet']}")
