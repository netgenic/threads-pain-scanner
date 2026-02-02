"""xAI (Grok) LLM provider."""

import logging
import os
from typing import Optional

from models import AnalysisResult
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class XAIProvider(LLMProvider):
    """Provider for xAI Grok models (OpenAI-compatible API)."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "grok-2-latest"
    ):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.model = model
        self.base_url = "https://api.x.ai/v1"
        self._client = None
    
    @property
    def name(self) -> str:
        return f"xAI ({self.model})"
    
    def _get_client(self):
        """Lazy initialization of OpenAI-compatible client for xAI."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                return None
        return self._client
    
    async def is_available(self) -> bool:
        """Check if xAI API is configured."""
        if not self.api_key:
            logger.warning("xAI API key not configured")
            return False
        
        client = self._get_client()
        if client is None:
            return False
        
        try:
            await client.models.list()
            logger.info(f"xAI connected, using model: {self.model}")
            return True
        except Exception as e:
            logger.error(f"xAI API check failed: {e}")
            return False
    
    async def analyze_posts(
        self, 
        posts_text: list[str], 
        focus: str = "pains"
    ) -> AnalysisResult:
        """Analyze posts using xAI Grok."""
        client = self._get_client()
        if client is None or not self.api_key:
            logger.warning("xAI not available, using fallback analysis")
            return self.fallback_analysis(posts_text)
        
        combined_text = "\n---\n".join(posts_text[:20])
        prompt = self.get_analysis_prompt(combined_text)
        
        try:
            logger.info(f"Analyzing {len(posts_text)} posts with Grok {self.model}")
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )
            
            content = response.choices[0].message.content.strip()
            data = self.parse_llm_response(content)
            
            logger.info("Grok analysis completed successfully")
            return AnalysisResult(
                pains=data.get("pains", []),
                needs=data.get("needs", []),
                app_ideas=data.get("app_ideas", []),
                sentiment=data.get("sentiment", "neutral"),
                keywords_found=data.get("keywords_found", []),
            )
            
        except Exception as e:
            logger.error(f"Grok analysis error: {e}")
            return self.fallback_analysis(posts_text)
