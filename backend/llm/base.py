"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from models import AnalysisResult


class LLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass
    
    @abstractmethod
    async def analyze_posts(
        self, 
        posts_text: list[str], 
        focus: str = "pains"
    ) -> AnalysisResult:
        """
        Analyze posts and extract insights.
        
        Args:
            posts_text: List of post texts to analyze
            focus: Focus area - "pains", "needs", or "ideas"
            
        Returns:
            AnalysisResult with extracted insights
        """
        pass
    
    def get_analysis_prompt(self, combined_text: str) -> str:
        """Generate the analysis prompt. Shared by all providers."""
        return f"""Ты — эксперт по маркетинговым исследованиям. Проанализируй следующие посты из социальной сети и извлеки полезную информацию.

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

    def parse_llm_response(self, content: str) -> dict:
        """Parse LLM response, handling markdown code blocks."""
        import json
        
        content = content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        
        return json.loads(content)

    def fallback_analysis(self, posts_text: list[str]) -> AnalysisResult:
        """Simple keyword-based analysis when LLM is unavailable."""
        pain_keywords = [
            "проблема", "сложно", "не работает", "бесит", "устал", 
            "надоело", "плохо", "ужас", "кошмар", "😤", "😭", "💸"
        ]
        need_keywords = [
            "хочу", "нужно", "не хватает", "было бы круто", 
            "мечтаю", "ищу", "ищем"
        ]
        
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
            pains=pains[:5] if pains else ["LLM недоступен для полного анализа"],
            needs=needs[:5] if needs else ["Настройте LLM провайдер"],
            app_ideas=["Для генерации идей нужен AI-анализ"],
            sentiment="unknown",
            keywords_found=["llm", "не", "настроен"],
        )
