"""LLM Provider factory."""

import logging
import os
from typing import Optional

from llm.base import LLMProvider
from llm.ollama import OllamaProvider
from llm.openai import OpenAIProvider
from llm.anthropic import AnthropicProvider
from llm.xai import XAIProvider

logger = logging.getLogger(__name__)


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Factory function to create LLM provider based on configuration.
    
    Args:
        provider_name: Provider name (ollama, openai, anthropic, xai).
                      If None, reads from LLM_PROVIDER env var.
    
    Returns:
        Configured LLMProvider instance
    """
    provider = provider_name or os.getenv("LLM_PROVIDER", "ollama").lower()
    
    match provider:
        case "ollama":
            model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
            logger.info(f"Using Ollama provider with model: {model}")
            return OllamaProvider(model=model)
        
        case "openai" | "gpt" | "chatgpt":
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            logger.info(f"Using OpenAI provider with model: {model}")
            return OpenAIProvider(model=model)
        
        case "anthropic" | "claude":
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            logger.info(f"Using Anthropic provider with model: {model}")
            return AnthropicProvider(model=model)
        
        case "xai" | "grok":
            model = os.getenv("XAI_MODEL", "grok-2-latest")
            logger.info(f"Using xAI provider with model: {model}")
            return XAIProvider(model=model)
        
        case _:
            logger.warning(f"Unknown provider '{provider}', falling back to Ollama")
            return OllamaProvider()
