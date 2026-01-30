"""
LLM wrapper for inference using Azure OpenAI with Entra ID authentication.
"""
from __future__ import annotations

from typing import List, Dict, Any
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class InferenceLLM:
    """Wrapper for Azure OpenAI inference endpoint with Entra ID auth."""
    
    def __init__(self, endpoint: str, deployment_name: str, api_version: str):
        """
        Initialize the inference LLM client.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            deployment_name: Deployment name for the model
            api_version: API version string
        """
        self.endpoint = endpoint
        self.deployment = deployment_name
        self.api_version = api_version
        
        # Create token provider for Entra ID
        credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
        token_provider = get_bearer_token_provider(
            credential,
            "https://cognitiveservices.azure.com/.default"
        )
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_version=api_version,
            azure_ad_token_provider=token_provider,
        )
    
    def complete(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system instruction
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        messages: List[Dict[str, Any]] = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content or ""
