"""
Evaluation entrypoint: runs RAI evaluations and generates reports.

Usage:
    python scripts/run_eval.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from app.config_loader import load_config
from evaluation.runner import EvaluationRunner
from evaluation.evaluators_config import EvalProjectScope


def build_storage_role_command(scope: EvalProjectScope) -> str:
    """Return a ready-to-run role assignment command for blob access."""
    subscription = scope.subscription_id or "<subscription-id>"
    resource_group = scope.resource_group or "<resource-group>"
    return (
        "az role assignment create --role \"Storage Blob Data Contributor\" "
        f"--scope /subscriptions/{subscription}/resourceGroups/{resource_group} "
        "--assignee-principal-type User --assignee-object-id \"<user-object-id>\""
    )


def main():
    """Run safety evaluations."""
    print("=" * 80)
    print("RAI Bootcamp Demo - Safety Evaluation")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    print("\n✓ Loaded environment variables")
    
    # Load configuration
    cfg = load_config()
    print(f"✓ Loaded configuration")
    
    # Initialize runner
    scenarios_path = "evaluation/scenarios/default_scenarios.jsonl"
    runner = EvaluationRunner(scenarios_path)
    print(f"✓ Initialized evaluation runner")
    print(f"  Scenarios: {scenarios_path}")
    print(f"  Project: {runner.eval_config.project_name}")
    print(f"  Region: {runner.eval_config.resource_group}")
    role_cmd = build_storage_role_command(runner.eval_config)
    print("\nReminder: ensure your identity has Storage Blob Data Contributor on the eval resource group.")
    print(f"  Example: {role_cmd}")
    
    # Prepare model config for evaluators (inference endpoint)
    model_config = {
        "azure_endpoint": cfg.inference.endpoint,
        "azure_deployment": cfg.inference.deployment_name,
        "api_version": cfg.inference.api_version,
    }
    
    print(f"\n✓ Model config prepared")
    print(f"  Endpoint: {cfg.inference.endpoint}")
    print(f"  Deployment: {cfg.inference.deployment_name}")
    
    # Run evaluations
    print("\n" + "=" * 80)
    print("Running Evaluations...")
    print("=" * 80)
    
    try:
        # Groundedness evaluation
        groundedness_results = runner.run_groundedness_eval(model_config)
        
        # Harmful content evaluation
        harmful_content_results = runner.run_harmful_content_eval()
        
        # Generate summary report
        runner.generate_summary_report(groundedness_results, harmful_content_results)
        
        print("\n" + "=" * 80)
        print("✓ Evaluation Complete!")
        print("=" * 80)
        print(f"\nReports saved to: evaluation/reports/")
        print("\nNext steps:")
        print("  1. Review JSON results for detailed scores")
        print("  2. Export results to Excel for OneRAI submission")
        print("  3. Share summary report with stakeholders")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Evaluation failed: {e}")
        print("\nTroubleshooting:")
        print("  - Verify .env is configured with eval resource details")
        print("  - Ensure you're authenticated: az login")
        print("  - Check that evaluation scenarios JSONL is valid")
        return 1


if __name__ == "__main__":
    sys.exit(main())
