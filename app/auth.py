"""
Authentication module for Entra ID token acquisition.

Provides token retrieval for both inference and evaluation resources using
Azure Identity SDK's DefaultAzureCredential, which supports:
- Azure CLI (az login)
- Managed Identity (when running in Azure)
- Interactive browser login (fallback)
"""

import os
from typing import Optional
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.exceptions import ClientAuthenticationError


# Azure service scope for token acquisition
AZURE_OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


def get_inference_token() -> str:
    """
    Acquire an Entra ID bearer token for the inference resource.

    Returns:
        str: Bearer token string for Azure OpenAI inference endpoint.

    Raises:
        ClientAuthenticationError: If token acquisition fails.
    """
    try:
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        token = credential.get_token(AZURE_OPENAI_SCOPE)
        return token.token
    except ClientAuthenticationError as e:
        raise ClientAuthenticationError(
            f"Failed to acquire inference token. Ensure you're authenticated via 'az login' or have valid Entra ID credentials. Error: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error acquiring inference token: {e}"
        ) from e


def get_eval_token() -> str:
    """
    Acquire an Entra ID bearer token for the evaluation resource.

    Returns:
        str: Bearer token string for Azure AI Foundry evaluation endpoint.

    Raises:
        ClientAuthenticationError: If token acquisition fails.
    """
    try:
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        token = credential.get_token(AZURE_OPENAI_SCOPE)
        return token.token
    except ClientAuthenticationError as e:
        raise ClientAuthenticationError(
            f"Failed to acquire evaluation token. Ensure you're authenticated via 'az login' or have valid Entra ID credentials. Error: {e}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error acquiring evaluation token: {e}"
        ) from e


def get_bearer_token_provider():
    """
    Get a callable token provider for Azure SDK clients.

    Returns:
        callable: A function that returns a fresh token on each call.
                  Compatible with AzureOpenAI and other Azure SDK clients.

    Example:
        from openai import AzureOpenAI
        token_provider = get_bearer_token_provider()
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version=api_version,
            azure_ad_token_provider=token_provider
        )
    """
    credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    return get_bearer_token_provider(credential, AZURE_OPENAI_SCOPE)
