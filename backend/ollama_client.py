"""Ollama client for local LLM inference."""

import ollama
import json
import os
from typing import Optional
from dotenv import load_dotenv

from models import AnalysisResult

load_dotenv()

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


class OllamaClient:
    """Client for Ollama local LLM."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self._available: Optional[bool] = None
    
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
            return self._available
        except Exception as e:
            print(f"Ollama check failed: {e}")
            self._available = False
            return False
    
    async def analyze_posts(self, posts_text: list[str], focus: str = "pains") -> AnalysisResult:
        """
        Analyze posts using local LLM.
        
        Args:
            posts_text: List of post texts to analyze
            focus: Focus area - "pains", "needs", or "ideas"
            
        Returns:
            AnalysisResult with extracted insights
        """
        if not await self.is_available():
            return self._fallback_analysis(posts_text)
        
        combined_text = "\n---\n".join(posts_text[:20])  # Limit to 20 posts per batch
        
        prompt = f"""Ты — эксперт по маркетинговым исследованиям. Проанализируй следующие посты из социальной сети и извлеки полезную информацию.

ПОСТЫ ДЛЯ АНАЛИЗА:
{combined_text}

ЗАДАЧА:
1. Найди все БОЛИ и ПРОБЛЕМЫ пользователей (frustrations, complaints, issues)
2. Определи НЕУДОВЛЕТВОРЁННЫЕ ПОТРЕБНОСТИ (что людям не хватает)
3. Предложи ИДЕИ для приложений/сервисов которые могли бы решить эти проблемы
4. Определи общий SENTIMENT (positive, negative, neutral, mixed)
5. Выдели ключевые ТЕМЫ и слова

ВАЖНО: Отвечай ТОЛЬКО валидным JSON без markdown форматирования, без ```json блоков.

Формат ответа:
{{"pains": ["боль 1", "боль 2"], "needs": ["потребность 1"], "app_ideas": ["идея 1"], "sentiment": "negative", "keywords_found": ["тема 1", "тема 2"]}}"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.3,
                    "num_predict": 1024,
                }
            )
            
            content = response.message.content.strip()
            
            # Clean up response - remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            # Parse JSON response
            data = json.loads(content)
            
            return AnalysisResult(
                pains=data.get("pains", []),
                needs=data.get("needs", []),
                app_ideas=data.get("app_ideas", []),
                sentiment=data.get("sentiment", "neutral"),
                keywords_found=data.get("keywords_found", []),
            )
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {content[:500]}")
            return self._fallback_analysis(posts_text)
        except Exception as e:
            print(f"Ollama analysis error: {e}")
            return self._fallback_analysis(posts_text)
    
    def _fallback_analysis(self, posts_text: list[str]) -> AnalysisResult:
        """Simple keyword-based analysis when LLM is unavailable."""
        pain_keywords = ["проблема", "сложно", "не работает", "бесит", "устал", "надоело", "плохо", "ужас", "кошмар", "😤", "😭", "💸"]
        need_keywords = ["хочу", "нужно", "не хватает", "было бы круто", "мечтаю", "ищу", "ищем"]
        
        pains = []
        needs = []
        
        combined = " ".join(posts_text).lower()
        
        for kw in pain_keywords:
            if kw.lower() in combined:
                pains.append(f"Обнаружен индикатор проблемы: '{kw}'")
        
        for kw in need_keywords:
            if kw.lower() in combined:
                needs.append(f"Обнаружена потребность: '{kw}'")
        
        return AnalysisResult(
            pains=pains[:5] if pains else ["Запустите Ollama для полного анализа"],
            needs=needs[:5] if needs else ["Установите модель qwen2.5:7b"],
            app_ideas=["Для генерации идей нужен AI-анализ"],
            sentiment="unknown",
            keywords_found=["ollama", "не", "доступен"],
        )
    
    async def get_model_info(self) -> dict:
        """Get info about the current model."""
        try:
            info = ollama.show(self.model)
            return {
                "model": self.model,
                "size": info.get("size", "unknown"),
                "family": info.get("details", {}).get("family", "unknown"),
            }
        except Exception:
            return {"model": self.model, "status": "not loaded"}
