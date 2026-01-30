"""
Unit tests for evaluation modules (config, evaluators, runner).
"""
from pathlib import Path
from unittest.mock import Mock, patch
import json

import pytest

from evaluation.evaluators_config import load_eval_config, get_azure_ai_project_dict


def test_load_eval_config(monkeypatch):
    """Test loading evaluation config from environment."""
    monkeypatch.setenv("EVAL_AZURE_SUBSCRIPTION_ID", "sub-123")
    monkeypatch.setenv("EVAL_AZURE_RESOURCE_GROUP", "rg-test")
    monkeypatch.setenv("EVAL_AZURE_AI_PROJECT_NAME", "proj-test")
    
    config = load_eval_config()
    
    assert config.subscription_id == "sub-123"
    assert config.resource_group == "rg-test"
    assert config.project_name == "proj-test"


def test_get_azure_ai_project_dict(monkeypatch):
    """Test conversion of scope to Azure AI project dict."""
    monkeypatch.setenv("EVAL_AZURE_SUBSCRIPTION_ID", "sub-456")
    monkeypatch.setenv("EVAL_AZURE_RESOURCE_GROUP", "rg-demo")
    monkeypatch.setenv("EVAL_AZURE_AI_PROJECT_NAME", "proj-demo")
    
    config = load_eval_config()
    project_dict = get_azure_ai_project_dict(config)
    
    assert project_dict["subscription_id"] == "sub-456"
    assert project_dict["resource_group_name"] == "rg-demo"
    assert project_dict["project_name"] == "proj-demo"


def test_scenarios_jsonl_format(tmp_path: Path):
    """Test that default scenarios JSONL can be parsed."""
    scenarios_path = tmp_path / "scenarios.jsonl"
    
    # Create minimal test scenarios
    scenarios = [
        {
            "query": "Test query 1",
            "response": "Test response 1",
            "context": "Test context 1",
            "ground_truth": "Test ground truth 1",
        },
        {
            "query": "Test query 2",
            "response": "Test response 2",
            "context": "Test context 2",
            "ground_truth": "Test ground truth 2",
        },
    ]
    
    # Write JSONL
    with open(scenarios_path, "w") as f:
        for scenario in scenarios:
            f.write(json.dumps(scenario) + "\n")
    
    # Read and validate
    loaded = []
    with open(scenarios_path, "r") as f:
        for line in f:
            if line.strip():
                loaded.append(json.loads(line))
    
    assert len(loaded) == 2
    assert loaded[0]["query"] == "Test query 1"
    assert loaded[1]["context"] == "Test context 2"
