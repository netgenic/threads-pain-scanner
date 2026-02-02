"""Ollama LLM provider for local inference."""

import logging
from typing import Optional

import ollama

from models import AnalysisResult
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Provider for local Ollama LLM."""
    
    def __init__(self, model: str = "qwen2.5:7b"):
        self.model = model
        self._available: Optional[bool] = None
    
    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"
    
    async def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        if self._available is not None:
            return self._available
        
        try:
            models = ollama.list()
            available_models = [m.model for m in models.models]
            # Check if our model or a variant is available
            self._available = any(
                self.model.split(":")[0] in m 
                for m in available_models
            )
            if self._available:
                logger.info(f"Ollama model '{self.model}' is available")
            else:
                logger.warning(f"Ollama model '{self.model}' not found. Available: {available_models}")
            return self._available
        except Exception as e:
            logger.error(f"Ollama check failed: {e}")
            self._available = False
            return False
    
    async def analyze_posts(
        self, 
        posts_text: list[str], 
        focus: str = "pains"
    ) -> AnalysisResult:
        """Analyze posts using local Ollama LLM."""
        if not await self.is_available():
            logger.warning("Ollama not available, using fallback analysis")
            return self.fallback_analysis(posts_text)
        
        combined_text = "\n---\n".join(posts_text[:20])  # Limit to 20 posts
        prompt = self.get_analysis_prompt(combined_text)
        
        try:
            logger.info(f"Analyzing {len(posts_text)} posts with Ollama")
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.3,
                    "num_predict": 1024,
                }
            )
            
            content = response.message.content.strip()
            data = self.parse_llm_response(content)
            
            logger.info("Ollama analysis completed successfully")
            return AnalysisResult(
                pains=data.get("pains", []),
                needs=data.get("needs", []),
                app_ideas=data.get("app_ideas", []),
                sentiment=data.get("sentiment", "neutral"),
                keywords_found=data.get("keywords_found", []),
            )
            
        except Exception as e:
            logger.error(f"Ollama analysis error: {e}")
            return self.fallback_analysis(posts_text)
