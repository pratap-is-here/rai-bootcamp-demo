"""
Quick validation of default scenarios JSONL.
"""
import json

with open('evaluation/scenarios/default_scenarios.jsonl', 'r') as f:
    lines = f.readlines()
    data = [json.loads(l) for l in lines if l.strip()]

print(f"✓ Valid JSONL: {len(data)} scenarios\n")

for i, scenario in enumerate(data, 1):
    query = scenario.get("query", "")[:70]
    print(f"  [{i}] {query}")

print(f"\n✓ Scenarios ready for evaluation")
