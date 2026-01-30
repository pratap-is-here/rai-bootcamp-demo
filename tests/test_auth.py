"""
Unit tests for Entra ID authentication module.

Tests cover:
- Token acquisition with mocked credentials
- Error handling for authentication failures
- Bearer token provider factory
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError
from app.auth import (
    get_inference_token,
    get_eval_token,
    get_bearer_token_provider,
    AZURE_OPENAI_SCOPE,
)


class TestGetInferenceToken:
    """Tests for get_inference_token() function."""

    @patch("app.auth.DefaultAzureCredential")
    def test_get_inference_token_success(self, mock_credential_class):
        """Test successful token acquisition for inference resource."""
        # Arrange
        mock_token = AccessToken(token="mock_inference_token_12345", expires_on=9999999999)
        mock_credential = Mock()
        mock_credential.get_token.return_value = mock_token
        mock_credential_class.return_value = mock_credential

        # Act
        token = get_inference_token()

        # Assert
        assert token == "mock_inference_token_12345"
        mock_credential.get_token.assert_called_once_with(AZURE_OPENAI_SCOPE)

    @patch("app.auth.DefaultAzureCredential")
    def test_get_inference_token_client_auth_error(self, mock_credential_class):
        """Test handling of ClientAuthenticationError during token acquisition."""
        # Arrange
        mock_credential = Mock()
        mock_credential.get_token.side_effect = ClientAuthenticationError("Invalid credentials")
        mock_credential_class.return_value = mock_credential

        # Act & Assert
        with pytest.raises(ClientAuthenticationError) as exc_info:
            get_inference_token()

        assert "Failed to acquire inference token" in str(exc_info.value)
        assert "az login" in str(exc_info.value)

    @patch("app.auth.DefaultAzureCredential")
    def test_get_inference_token_unexpected_error(self, mock_credential_class):
        """Test handling of unexpected errors during token acquisition."""
        # Arrange
        mock_credential = Mock()
        mock_credential.get_token.side_effect = RuntimeError("Network error")
        mock_credential_class.return_value = mock_credential

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            get_inference_token()

        assert "Unexpected error acquiring inference token" in str(exc_info.value)


class TestGetEvalToken:
    """Tests for get_eval_token() function."""

    @patch("app.auth.DefaultAzureCredential")
    def test_get_eval_token_success(self, mock_credential_class):
        """Test successful token acquisition for evaluation resource."""
        # Arrange
        mock_token = AccessToken(token="mock_eval_token_67890", expires_on=9999999999)
        mock_credential = Mock()
        mock_credential.get_token.return_value = mock_token
        mock_credential_class.return_value = mock_credential

        # Act
        token = get_eval_token()

        # Assert
        assert token == "mock_eval_token_67890"
        mock_credential.get_token.assert_called_once_with(AZURE_OPENAI_SCOPE)

    @patch("app.auth.DefaultAzureCredential")
    def test_get_eval_token_client_auth_error(self, mock_credential_class):
        """Test handling of ClientAuthenticationError for evaluation resource."""
        # Arrange
        mock_credential = Mock()
        mock_credential.get_token.side_effect = ClientAuthenticationError("Unauthorized")
        mock_credential_class.return_value = mock_credential

        # Act & Assert
        with pytest.raises(ClientAuthenticationError) as exc_info:
            get_eval_token()

        assert "Failed to acquire evaluation token" in str(exc_info.value)


class TestGetBearerTokenProvider:
    """Tests for get_bearer_token_provider() function."""

    @patch("app.auth.get_bearer_token_provider")
    @patch("app.auth.DefaultAzureCredential")
    def test_get_bearer_token_provider_returns_callable(self, mock_credential_class, mock_provider_func):
        """Test that get_bearer_token_provider returns a callable token provider."""
        # Arrange
        mock_credential = Mock()
        mock_credential_class.return_value = mock_credential
        mock_callable_provider = Mock()
        mock_provider_func.return_value = mock_callable_provider

        # Act
        provider = get_bearer_token_provider()

        # Assert
        # Verify that the function was called and returned the mock provider
        assert provider is not None
        # Verify DefaultAzureCredential was instantiated
        mock_credential_class.assert_called_once()
        # Verify get_bearer_token_provider was called with correct args
        mock_provider_func.assert_called_once_with(mock_credential, AZURE_OPENAI_SCOPE)


class TestAuthenticationIntegration:
    """Integration-style tests for authentication module."""

    @patch("app.auth.DefaultAzureCredential")
    def test_inference_and_eval_tokens_are_different_calls(self, mock_credential_class):
        """
        Test that inference and eval token acquisition are independent.
        (In practice they may return the same token, but they should be separate calls.)
        """
        # Arrange
        mock_token_1 = AccessToken(token="token_1", expires_on=9999999999)
        mock_token_2 = AccessToken(token="token_2", expires_on=9999999999)
        mock_credential = Mock()
        mock_credential.get_token.side_effect = [mock_token_1, mock_token_2]
        mock_credential_class.return_value = mock_credential

        # Act
        token_1 = get_inference_token()
        token_2 = get_eval_token()

        # Assert
        assert token_1 == "token_1"
        assert token_2 == "token_2"
        # Verify two separate get_token calls were made
        assert mock_credential.get_token.call_count == 2
