"""
Evaluation runner orchestrates groundedness and harmful content assessments.

Executes evaluations against scenarios and generates reports.
"""
from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from azure.ai.evaluation import evaluate
from azure.identity import DefaultAzureCredential

from evaluation.evaluators_config import load_eval_config, get_azure_ai_project_dict
from evaluation.evaluators_wrapper import get_qa_evaluator, get_content_safety_evaluator


class EvaluationRunner:
    """Runs safety evaluations on scenario data."""
    
    def __init__(self, scenarios_path: str, reports_dir: str = "evaluation/reports"):
        """
        Initialize evaluation runner.
        
        Args:
            scenarios_path: Path to JSONL file with scenarios
            reports_dir: Directory to save evaluation reports
        """
        self.scenarios_path = Path(scenarios_path)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load eval config
        self.eval_config = load_eval_config()
        self.project_dict = get_azure_ai_project_dict(self.eval_config)
        
        # Credentials
        self.credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    
    def run_groundedness_eval(
        self,
        model_config: Dict[str, Any],
        output_path: str | None = None,
    ) -> Dict[str, Any]:
        """
        Run groundedness evaluation on scenarios.
        
        Args:
            model_config: Azure OpenAI model config (endpoint, deployment, api_version)
            output_path: Optional output file path; defaults to reports/groundedness_results.json
        
        Returns:
            Evaluation results dict
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.reports_dir / f"groundedness_{timestamp}.json")
        
        print(f"\nRunning groundedness evaluation...")
        print(f"  Scenarios: {self.scenarios_path}")
        print(f"  Project: {self.eval_config.project_name}")
        
        qa_evaluator = get_qa_evaluator(model_config)
        
        results = evaluate(
            data=str(self.scenarios_path),
            evaluators={"qa": qa_evaluator},
            azure_ai_project=self.project_dict,
            output_path=output_path,
        )
        
        print(f"  ✓ Results saved to: {output_path}")
        return results
    
    def run_harmful_content_eval(
        self,
        output_path: str | None = None,
    ) -> Dict[str, Any]:
        """
        Run harmful content evaluation on scenarios.
        
        Args:
            output_path: Optional output file path; defaults to reports/harmful_content_results.json
        
        Returns:
            Evaluation results dict
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.reports_dir / f"harmful_content_{timestamp}.json")
        
        print(f"\nRunning harmful content evaluation...")
        print(f"  Scenarios: {self.scenarios_path}")
        print(f"  Project: {self.eval_config.project_name}")
        
        content_safety_eval = get_content_safety_evaluator(self.credential)
        
        results = evaluate(
            data=str(self.scenarios_path),
            evaluators={"content_safety": content_safety_eval},
            azure_ai_project=self.project_dict,
            output_path=output_path,
        )
        
        print(f"  ✓ Results saved to: {output_path}")
        return results
    
    def generate_summary_report(
        self,
        groundedness_results: Dict[str, Any],
        harmful_content_results: Dict[str, Any],
        output_path: str | None = None,
    ) -> None:
        """
        Generate a summary report combining both evaluations.
        
        Args:
            groundedness_results: Results from groundedness eval
            harmful_content_results: Results from harmful content eval
            output_path: Optional output file path; defaults to reports/summary_report.csv
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.reports_dir / f"summary_report_{timestamp}.csv")
        
        print(f"\nGenerating summary report...")
        
        # Extract pass/fail counts from results
        def count_results(results: Dict[str, Any]) -> tuple[int, int]:
            """Count passed and failed rows from evaluation results."""
            passed = 0
            failed = 0
            if "rows" in results:
                for row in results["rows"]:
                    # Check if any *_result field has "pass" or "fail"
                    has_pass = any("_result" in k and row.get(k) == "pass" for k in row.keys())
                    has_fail = any("_result" in k and row.get(k) == "fail" for k in row.keys())
                    
                    if has_fail:
                        failed += 1
                    elif has_pass:
                        passed += 1
            return passed, failed
        
        grd_passed, grd_failed = count_results(groundedness_results)
        hc_passed, hc_failed = count_results(harmful_content_results)
        
        summary = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "project": self.eval_config.project_name,
            "scenarios_file": str(self.scenarios_path),
            "groundedness_passed": grd_passed,
            "groundedness_failed": grd_failed,
            "harmful_content_passed": hc_passed,
            "harmful_content_failed": hc_failed,
        }
        
        # Write summary CSV
        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=summary.keys())
            writer.writeheader()
            writer.writerow(summary)
        
        print(f"  ✓ Summary saved to: {output_path}")
        print(f"\nSummary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
