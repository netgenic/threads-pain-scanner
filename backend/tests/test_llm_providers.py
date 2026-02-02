"""Tests for LLM providers."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from llm.base import LLMProvider
from llm.ollama import OllamaProvider
from llm.openai import OpenAIProvider
from llm.anthropic import AnthropicProvider
from llm.xai import XAIProvider
from llm.factory import get_llm_provider
from models import AnalysisResult


class TestLLMProviderBase:
    """Test base LLMProvider functionality."""
    
    def test_analysis_prompt_contains_required_sections(self):
        """Test that analysis prompt has all required sections."""
        provider = OllamaProvider()
        prompt = provider.get_analysis_prompt("Test content")
        
        assert "ПОСТЫ ДЛЯ АНАЛИЗА" in prompt
        assert "БОЛИ и ПРОБЛЕМЫ" in prompt
        assert "НЕУДОВЛЕТВОРЁННЫЕ ПОТРЕБНОСТИ" in prompt
        assert "ИДЕИ" in prompt
        assert "JSON" in prompt
    
    def test_parse_llm_response_clean_json(self):
        """Test parsing clean JSON response."""
        provider = OllamaProvider()
        content = '{"pains": ["test pain"], "needs": [], "app_ideas": [], "sentiment": "neutral", "keywords_found": []}'
        
        result = provider.parse_llm_response(content)
        
        assert result["pains"] == ["test pain"]
        assert result["sentiment"] == "neutral"
    
    def test_parse_llm_response_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        provider = OllamaProvider()
        content = '```json\n{"pains": ["pain1"], "needs": [], "app_ideas": [], "sentiment": "negative", "keywords_found": []}\n```'
        
        result = provider.parse_llm_response(content)
        
        assert result["pains"] == ["pain1"]
    
    def test_fallback_analysis_detects_pain_keywords(self):
        """Test that fallback analysis detects pain keywords."""
        provider = OllamaProvider()
        posts = ["Это бесит, проблема не решается", "Устал от этого"]
        
        result = provider.fallback_analysis(posts)
        
        assert isinstance(result, AnalysisResult)
        assert len(result.pains) > 0


class TestOllamaProvider:
    """Test Ollama provider."""
    
    def test_name_includes_model(self):
        """Test that provider name includes model name."""
        provider = OllamaProvider(model="test-model:7b")
        assert "Ollama" in provider.name
        assert "test-model:7b" in provider.name
    
    @pytest.mark.asyncio
    async def test_is_available_returns_false_when_ollama_not_running(self):
        """Test availability check when Ollama is not running."""
        provider = OllamaProvider()
        provider._available = None  # Reset cache
        
        with patch('llm.ollama.ollama.list', side_effect=Exception("Connection refused")):
            result = await provider.is_available()
        
        assert result is False


class TestOpenAIProvider:
    """Test OpenAI provider."""
    
    def test_name_includes_model(self):
        """Test that provider name includes model name."""
        provider = OpenAIProvider(api_key="test", model="gpt-4o")
        assert "OpenAI" in provider.name
        assert "gpt-4o" in provider.name
    
    @pytest.mark.asyncio
    async def test_is_available_returns_false_without_api_key(self):
        """Test availability check without API key."""
        provider = OpenAIProvider(api_key=None)
        result = await provider.is_available()
        assert result is False


class TestAnthropicProvider:
    """Test Anthropic provider."""
    
    def test_name_includes_model(self):
        """Test that provider name includes model name."""
        provider = AnthropicProvider(api_key="test", model="claude-3-sonnet")
        assert "Anthropic" in provider.name
        assert "claude-3-sonnet" in provider.name


class TestXAIProvider:
    """Test xAI provider."""
    
    def test_name_includes_model(self):
        """Test that provider name includes model name."""
        provider = XAIProvider(api_key="test", model="grok-2")
        assert "xAI" in provider.name
        assert "grok-2" in provider.name


class TestLLMFactory:
    """Test LLM provider factory."""
    
    def test_factory_returns_ollama_by_default(self):
        """Test that factory returns Ollama provider by default."""
        with patch.dict('os.environ', {'LLM_PROVIDER': 'ollama'}, clear=False):
            provider = get_llm_provider()
        assert isinstance(provider, OllamaProvider)
    
    def test_factory_returns_openai_provider(self):
        """Test that factory returns OpenAI provider."""
        provider = get_llm_provider("openai")
        assert isinstance(provider, OpenAIProvider)
    
    def test_factory_returns_anthropic_provider(self):
        """Test that factory returns Anthropic provider."""
        provider = get_llm_provider("anthropic")
        assert isinstance(provider, AnthropicProvider)
    
    def test_factory_returns_xai_provider(self):
        """Test that factory returns xAI provider."""
        provider = get_llm_provider("xai")
        assert isinstance(provider, XAIProvider)
    
    def test_factory_handles_aliases(self):
        """Test that factory handles provider aliases."""
        assert isinstance(get_llm_provider("gpt"), OpenAIProvider)
        assert isinstance(get_llm_provider("chatgpt"), OpenAIProvider)
        assert isinstance(get_llm_provider("claude"), AnthropicProvider)
        assert isinstance(get_llm_provider("grok"), XAIProvider)
    
    def test_factory_falls_back_to_ollama_for_unknown(self):
        """Test that factory falls back to Ollama for unknown provider."""
        provider = get_llm_provider("unknown_provider")
        assert isinstance(provider, OllamaProvider)
