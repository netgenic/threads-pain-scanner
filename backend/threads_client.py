"""Threads API Client for keyword search."""

import httpx
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

from models import ThreadsPost, SearchType, MediaType

load_dotenv()

THREADS_API_BASE = "https://graph.threads.net/v1.0"


class ThreadsClient:
    """Client for interacting with Threads API."""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv("THREADS_ACCESS_TOKEN")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @property
    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        return bool(self.access_token and self.access_token != "your_threads_access_token_here")
    
    async def search(
        self,
        query: str,
        search_type: SearchType = SearchType.RECENT,
        media_type: Optional[MediaType] = MediaType.TEXT,
        limit: int = 25,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> list[ThreadsPost]:
        """
        Search Threads by keyword.
        
        Args:
            query: Keywords to search for
            search_type: TOP or RECENT
            media_type: TEXT, IMAGE, or VIDEO
            limit: Max number of results (1-100)
            since: Start date filter
            until: End date filter
            
        Returns:
            List of ThreadsPost objects
        """
        if not self.is_configured:
            # Return demo data when not configured
            return self._get_demo_posts(query)
        
        params = {
            "q": query,
            "search_type": search_type.value,
            "fields": "id,text,media_type,permalink,timestamp,username,has_replies,is_reply",
            "access_token": self.access_token,
            "limit": str(limit),
        }
        
        if media_type:
            params["media_type"] = media_type.value
        
        if since:
            params["since"] = str(int(since.timestamp()))
        
        if until:
            params["until"] = str(int(until.timestamp()))
        
        try:
            response = await self.client.get(
                f"{THREADS_API_BASE}/keyword_search",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data.get("data", []):
                posts.append(ThreadsPost(
                    id=item["id"],
                    text=item.get("text", ""),
                    username=item.get("username", "unknown"),
                    timestamp=datetime.fromisoformat(item["timestamp"].replace("+0000", "+00:00")),
                    permalink=item.get("permalink", ""),
                    media_type=item.get("media_type", "TEXT"),
                    has_replies=item.get("has_replies", False),
                    is_reply=item.get("is_reply", False),
                ))
            
            # Fetch replies for top posts to improve analysis context
            # We limit to top 5 to avoid rate limits
            for i, post in enumerate(posts[:5]):
                if post.has_replies:
                    try:
                        replies = await self.get_post_conversation(post.id)
                        post.replies = replies
                    except Exception as e:
                        print(f"Failed to fetch replies for {post.id}: {e}")

            return posts
            
        except httpx.HTTPError as e:
            print(f"Threads API error: {e}")
            return []
    
    async def get_post_conversation(self, post_id: str) -> list[ThreadsPost]:
        """
        Fetch conversation (replies) for a post.
        Note: The 'conversation' endpoint retrieves the entire thread.
        We will filter for direct replies or return relevant parts.
        Actually, API provides /conversation endpoint which returns a list of data.
        """
        if not self.is_configured:
            return []

        params = {
            "fields": "id,text,username,timestamp,media_type,permalink,is_reply",
            "access_token": self.access_token,
            "reverse": "true" 
        }

        try:
            response = await self.client.get(
                f"{THREADS_API_BASE}/{post_id}/conversation",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            replies = []
            for item in data.get("data", []):
                # Skip the post itself if returned
                if item["id"] == post_id:
                    continue
                    
                replies.append(ThreadsPost(
                    id=item["id"],
                    text=item.get("text", ""),
                    username=item.get("username", "unknown"),
                    timestamp=datetime.fromisoformat(item["timestamp"].replace("+0000", "+00:00")),
                    permalink=item.get("permalink", ""),
                    media_type=item.get("media_type", "TEXT"),
                    is_reply=True
                ))
            
            return replies
            
        except httpx.HTTPError as e:
            print(f"Error fetching conversation for {post_id}: {e}")
            return []

    def _get_demo_posts(self, query: str) -> list[ThreadsPost]:
        """Return demo posts for testing without API access."""
        demo_data = [
            {
                "id": "demo_1",
                "text": f"Искал приложение для {query}, но все существующие слишком сложные. Хочется чего-то простого и понятного 😤",
                "username": "demo_user1",
                "sentiment": "negative"
            },
            {
                "id": "demo_2", 
                "text": f"Почему нет нормального решения для {query}? Пробовал 5 разных приложений — все либо платные, либо с кучей рекламы",
                "username": "demo_user2",
                "sentiment": "negative"
            },
            {
                "id": "demo_3",
                "text": f"Кто-нибудь знает хороший инструмент для {query}? Устал от того что приходится всё делать вручную",
                "username": "demo_user3",
                "sentiment": "neutral"
            },
            {
                "id": "demo_4",
                "text": f"Мечтаю о приложении которое бы автоматизировало {query}. Трачу на это по 2 часа в день 😭",
                "username": "demo_user4",
                "sentiment": "negative"
            },
            {
                "id": "demo_5",
                "text": f"Главная проблема с {query} — нет интеграции между инструментами. Приходится копировать данные туда-сюда",
                "username": "demo_user5",
                "sentiment": "negative"
            },
            {
                "id": "demo_6",
                "text": f"Было бы круто если бы появилось AI-решение для {query}. Готов платить за это!",
                "username": "demo_user6",
                "sentiment": "positive"
            },
            {
                "id": "demo_7",
                "text": f"Работаю с {query} каждый день. Самое бесящее — нет мобильной версии у большинства сервисов",
                "username": "demo_user7",
                "sentiment": "negative"
            },
            {
                "id": "demo_8",
                "text": f"Нашёл решение для {query} но оно стоит $50/месяц. Это слишком дорого для фрилансера 💸",
                "username": "demo_user8",
                "sentiment": "negative"
            },
        ]
        
        now = datetime.now()
        posts = []
        for i, item in enumerate(demo_data):
            posts.append(ThreadsPost(
                id=item["id"],
                text=item["text"],
                username=item["username"],
                timestamp=now,
                permalink=f"https://threads.net/@{item['username']}/post/{item['id']}",
                media_type="TEXT",
                has_replies=True,
                is_reply=False,
            ))
        
        return posts
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
