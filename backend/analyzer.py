"""Post analyzer - combines Threads data with LLM analysis."""

from typing import Optional
from models import ThreadsPost, AnalysisResult, SearchResponse
from ollama_client import OllamaClient


class PostAnalyzer:
    """Analyzes Threads posts using LLM."""
    
    def __init__(self):
        self.ollama = OllamaClient()
    
    async def analyze(
        self, 
        posts: list[ThreadsPost], 
        query: str,
        focus: str = "pains"
    ) -> SearchResponse:
        """
        Analyze a list of posts and return insights.
        
        Args:
            posts: List of ThreadsPost objects
            query: Original search query
            focus: What to focus on - pains, needs, or ideas
            
        Returns:
            SearchResponse with posts and analysis
        """
        if not posts:
            return SearchResponse(
                posts=[],
                analysis=None,
                total_posts=0,
                query=query
            )
        
        # Filter out empty posts and replies (we want original posts)
        valid_posts = [
            p for p in posts 
            if p.text and len(p.text.strip()) > 10 and not p.is_reply
        ]
        
        # Remove duplicates by text similarity
        unique_posts = self._deduplicate(valid_posts)
        
        # Extract text for analysis
        texts = [p.text for p in unique_posts]
        
        # Run LLM analysis
        analysis = await self.ollama.analyze_posts(texts, focus)
        
        return SearchResponse(
            posts=unique_posts,
            analysis=analysis,
            total_posts=len(unique_posts),
            query=query
        )
    
    def _deduplicate(self, posts: list[ThreadsPost]) -> list[ThreadsPost]:
        """Remove near-duplicate posts."""
        seen_texts = set()
        unique = []
        
        for post in posts:
            # Normalize text for comparison
            normalized = post.text.lower().strip()[:100]
            
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                unique.append(post)
        
        return unique
    
    async def batch_analyze(
        self, 
        posts: list[ThreadsPost],
        batch_size: int = 10
    ) -> list[AnalysisResult]:
        """
        Analyze posts in batches for better performance.
        
        Args:
            posts: All posts to analyze
            batch_size: Number of posts per batch
            
        Returns:
            List of AnalysisResult for each batch
        """
        results = []
        
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i + batch_size]
            texts = [p.text for p in batch]
            result = await self.ollama.analyze_posts(texts)
            results.append(result)
        
        return results
    
    def merge_analyses(self, analyses: list[AnalysisResult]) -> AnalysisResult:
        """Merge multiple analysis results into one."""
        all_pains = []
        all_needs = []
        all_ideas = []
        all_keywords = []
        sentiments = []
        
        for analysis in analyses:
            all_pains.extend(analysis.pains)
            all_needs.extend(analysis.needs)
            all_ideas.extend(analysis.app_ideas)
            all_keywords.extend(analysis.keywords_found)
            sentiments.append(analysis.sentiment)
        
        # Deduplicate
        unique_pains = list(dict.fromkeys(all_pains))[:10]
        unique_needs = list(dict.fromkeys(all_needs))[:10]
        unique_ideas = list(dict.fromkeys(all_ideas))[:10]
        unique_keywords = list(dict.fromkeys(all_keywords))[:15]
        
        # Determine overall sentiment
        if sentiments:
            neg_count = sentiments.count("negative")
            pos_count = sentiments.count("positive")
            if neg_count > pos_count:
                overall = "negative"
            elif pos_count > neg_count:
                overall = "positive"
            else:
                overall = "mixed"
        else:
            overall = "neutral"
        
        return AnalysisResult(
            pains=unique_pains,
            needs=unique_needs,
            app_ideas=unique_ideas,
            sentiment=overall,
            keywords_found=unique_keywords,
        )
