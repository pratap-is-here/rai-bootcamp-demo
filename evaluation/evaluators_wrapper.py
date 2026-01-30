"""
Evaluation wrappers for groundedness and harmful content assessments.

Wraps Azure AI Evaluation SDK evaluators for convenience.
"""
from __future__ import annotations

from typing import Any, Dict

from azure.ai.evaluation import QAEvaluator, ContentSafetyEvaluator
from azure.identity import DefaultAzureCredential

from evaluation.evaluators_config import load_eval_config, get_azure_ai_project_dict


def get_qa_evaluator(model_config: Dict[str, Any]) -> QAEvaluator:
    """
    Instantiate QAEvaluator for groundedness assessment.
    
    Args:
        model_config: Dict with keys:
            - azure_endpoint: Azure OpenAI endpoint
            - azure_deployment: Deployment name
            - api_version: API version
    
    Returns:
        Configured QAEvaluator instance.
    """
    return QAEvaluator(model_config=model_config)


def get_content_safety_evaluator(
    credential: DefaultAzureCredential | None = None,
) -> ContentSafetyEvaluator:
    """
    Instantiate ContentSafetyEvaluator for harmful content detection.
    
    Args:
        credential: Optional Entra ID credential. Uses DefaultAzureCredential if None.
    
    Returns:
        Configured ContentSafetyEvaluator instance.
    """
    if credential is None:
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    
    # Load eval project scope
    eval_config = load_eval_config()
    azure_ai_project = get_azure_ai_project_dict(eval_config)
    
    return ContentSafetyEvaluator(credential=credential, azure_ai_project=azure_ai_project)
