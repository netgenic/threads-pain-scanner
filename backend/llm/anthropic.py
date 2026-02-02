"""Anthropic (Claude) LLM provider."""

import logging
import os
from typing import Optional

from models import AnalysisResult
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None
    
    @property
    def name(self) -> str:
        return f"Anthropic ({self.model})"
    
    def _get_client(self):
        """Lazy initialization of Anthropic client."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.error("anthropic package not installed. Run: pip install anthropic")
                return None
        return self._client
    
    async def is_available(self) -> bool:
        """Check if Anthropic API is configured."""
        if not self.api_key:
            logger.warning("Anthropic API key not configured")
            return False
        
        client = self._get_client()
        if client is None:
            return False
        
        # For Anthropic, we just check if client is initialized
        # No simple health check endpoint available
        logger.info(f"Anthropic configured, using model: {self.model}")
        return True
    
    async def analyze_posts(
        self, 
        posts_text: list[str], 
        focus: str = "pains"
    ) -> AnalysisResult:
        """Analyze posts using Anthropic Claude."""
        client = self._get_client()
        if client is None or not self.api_key:
            logger.warning("Anthropic not available, using fallback analysis")
            return self.fallback_analysis(posts_text)
        
        combined_text = "\n---\n".join(posts_text[:20])
        prompt = self.get_analysis_prompt(combined_text)
        
        try:
            logger.info(f"Analyzing {len(posts_text)} posts with Claude {self.model}")
            response = await client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            data = self.parse_llm_response(content)
            
            logger.info("Claude analysis completed successfully")
            return AnalysisResult(
                pains=data.get("pains", []),
                needs=data.get("needs", []),
                app_ideas=data.get("app_ideas", []),
                sentiment=data.get("sentiment", "neutral"),
                keywords_found=data.get("keywords_found", []),
            )
            
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return self.fallback_analysis(posts_text)
