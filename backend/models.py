"""Pydantic models for the Threads Research Tool."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SearchType(str, Enum):
    TOP = "TOP"
    RECENT = "RECENT"


class MediaType(str, Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class SearchRequest(BaseModel):
    """Request model for Threads search."""
    keywords: str = Field(..., description="Keywords to search for")
    search_type: SearchType = Field(default=SearchType.TOP, description="TOP or RECENT")
    media_type: Optional[MediaType] = Field(default=MediaType.TEXT, description="Type of media")
    limit: int = Field(default=25, ge=1, le=100, description="Number of results")
    since: Optional[datetime] = Field(default=None, description="Start date")
    until: Optional[datetime] = Field(default=None, description="End date")


class ThreadsPost(BaseModel):
    """A single post from Threads."""
    id: str
    text: str
    username: str
    timestamp: datetime
    permalink: str
    media_type: str
    has_replies: bool = False
    is_reply: bool = False
    replies: list['ThreadsPost'] = []


class AnalysisResult(BaseModel):
    """Result of AI analysis."""
    pains: list[str] = Field(default_factory=list, description="User pains/problems")
    needs: list[str] = Field(default_factory=list, description="Unmet needs")
    app_ideas: list[str] = Field(default_factory=list, description="App ideas")
    sentiment: str = Field(default="neutral", description="Overall sentiment")
    keywords_found: list[str] = Field(default_factory=list, description="Key topics")


class SearchResponse(BaseModel):
    """Response from search and analysis."""
    posts: list[ThreadsPost]
    analysis: Optional[AnalysisResult] = None
    total_posts: int
    query: str


class AnalyzeRequest(BaseModel):
    """Request to analyze posts."""
    posts: list[ThreadsPost]
    focus: str = Field(default="pains", description="Focus area: pains, needs, ideas")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    ollama_available: bool
    threads_api_configured: bool
