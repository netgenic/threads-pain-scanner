"""Tests for PostAnalyzer."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from analyzer import PostAnalyzer
from models import ThreadsPost, AnalysisResult


class TestPostAnalyzer:
    """Test PostAnalyzer class."""
    
    @pytest.fixture
    def mock_llm_provider(self, mock_analysis_result):
        """Create a mock LLM provider."""
        mock = MagicMock()
        mock.name = "MockProvider"
        mock.analyze_posts = AsyncMock(return_value=mock_analysis_result)
        return mock
    
    @pytest.fixture
    def sample_threads_posts(self):
        """Create sample ThreadsPost objects."""
        return [
            ThreadsPost(
                id="1",
                text="Искал приложение для продуктивности, но все слишком сложные",
                username="user1",
                timestamp=datetime.now(),
                permalink="https://threads.net/post/1",
                media_type="TEXT",
                is_reply=False
            ),
            ThreadsPost(
                id="2",
                text="Устал от сложных интерфейсов в приложениях",
                username="user2",
                timestamp=datetime.now(),
                permalink="https://threads.net/post/2",
                media_type="TEXT",
                is_reply=False
            ),
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_returns_search_response(
        self, 
        mock_llm_provider, 
        sample_threads_posts
    ):
        """Test that analyze returns SearchResponse."""
        analyzer = PostAnalyzer(llm_provider=mock_llm_provider)
        
        result = await analyzer.analyze(sample_threads_posts, "продуктивность")
        
        assert result.query == "продуктивность"
        assert result.total_posts > 0
        assert result.analysis is not None
    
    @pytest.mark.asyncio
    async def test_analyze_empty_posts(self, mock_llm_provider):
        """Test analyze with empty posts list."""
        analyzer = PostAnalyzer(llm_provider=mock_llm_provider)
        
        result = await analyzer.analyze([], "test")
        
        assert result.total_posts == 0
        assert result.posts == []
        assert result.analysis is None
    
    @pytest.mark.asyncio
    async def test_analyze_filters_replies(self, mock_llm_provider):
        """Test that analyze filters out replies."""
        posts = [
            ThreadsPost(
                id="1",
                text="Original post with enough text to pass filter",
                username="user1",
                timestamp=datetime.now(),
                permalink="https://threads.net/post/1",
                media_type="TEXT",
                is_reply=False
            ),
            ThreadsPost(
                id="2",
                text="This is a reply that should be filtered out",
                username="user2",
                timestamp=datetime.now(),
                permalink="https://threads.net/post/2",
                media_type="TEXT",
                is_reply=True
            ),
        ]
        
        analyzer = PostAnalyzer(llm_provider=mock_llm_provider)
        result = await analyzer.analyze(posts, "test")
        
        # Only non-reply posts should be included
        assert result.total_posts == 1
    
    def test_deduplicate_removes_similar_posts(self, mock_llm_provider):
        """Test that deduplication removes similar posts."""
        posts = [
            ThreadsPost(
                id="1",
                text="This is a duplicate post about the same topic",
                username="user1",
                timestamp=datetime.now(),
                permalink="",
                media_type="TEXT"
            ),
            ThreadsPost(
                id="2",
                text="This is a duplicate post about the same topic",  # Same text
                username="user2",
                timestamp=datetime.now(),
                permalink="",
                media_type="TEXT"
            ),
        ]
        
        analyzer = PostAnalyzer(llm_provider=mock_llm_provider)
        unique = analyzer._deduplicate(posts)
        
        assert len(unique) == 1
    
    def test_merge_analyses(self, mock_llm_provider):
        """Test merging multiple analysis results."""
        analyzer = PostAnalyzer(llm_provider=mock_llm_provider)
        
        analyses = [
            AnalysisResult(
                pains=["Pain 1", "Pain 2"],
                needs=["Need 1"],
                app_ideas=["Idea 1"],
                sentiment="negative",
                keywords_found=["keyword1"]
            ),
            AnalysisResult(
                pains=["Pain 2", "Pain 3"],  # Pain 2 is duplicate
                needs=["Need 2"],
                app_ideas=["Idea 2"],
                sentiment="positive",
                keywords_found=["keyword2"]
            ),
        ]
        
        merged = analyzer.merge_analyses(analyses)
        
        # Should have 3 unique pains (Pain 2 deduplicated)
        assert len(merged.pains) == 3
        assert "Pain 1" in merged.pains
        assert "Pain 3" in merged.pains
        
        # Sentiment should be mixed (one negative, one positive)
        assert merged.sentiment == "mixed"
