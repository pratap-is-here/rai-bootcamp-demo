"""
Evaluation configuration and utilities.

Load evaluation resource credentials and project scope for Azure AI Safety Evaluations SDK.
"""
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass
class EvalProjectScope:
    """Azure AI project scope for evaluations."""
    subscription_id: str
    resource_group: str
    project_name: str


def load_eval_config() -> EvalProjectScope:
    """Load evaluation project configuration from environment."""
    return EvalProjectScope(
        subscription_id=os.getenv("EVAL_AZURE_SUBSCRIPTION_ID", ""),
        resource_group=os.getenv("EVAL_AZURE_RESOURCE_GROUP", ""),
        project_name=os.getenv("EVAL_AZURE_AI_PROJECT_NAME", ""),
    )


def get_azure_ai_project_dict(scope: EvalProjectScope) -> dict:
    """Convert scope to Azure AI project dict for SDK."""
    return {
        "subscription_id": scope.subscription_id,
        "resource_group_name": scope.resource_group,
        "project_name": scope.project_name,
    }
