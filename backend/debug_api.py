import asyncio
import os
import httpx
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

THREADS_API_BASE = "https://graph.threads.net/v1.0"
TOKEN = os.getenv("THREADS_ACCESS_TOKEN")

async def test_api():
    print("--- Threads API Debugger ---")
    
    # 1. Check Token Existence
    if not TOKEN:
        print("❌ ERROR: THREADS_ACCESS_TOKEN not found in .env")
        return
    
    masked_token = TOKEN[:5] + "..." + TOKEN[-5:] if len(TOKEN) > 10 else "***"
    print(f"✅ Token found: {masked_token}")
    
    if TOKEN == "your_threads_access_token_here":
        print("❌ ERROR: Token is still the default placeholder!")
        return

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 2. Check Token Validity (Me Endpoint)
        print("\nTesting Token Validity (Get User Profile)...")
        try:
            response = await client.get(
                f"{THREADS_API_BASE}/me",
                params={"access_token": TOKEN, "fields": "id,username"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ SUCCESS: Authenticated as @{user_data.get('username')} (ID: {user_data.get('id')})")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response: {response.text}")
                return

        except Exception as e:
            print(f"❌ Network/Client Error: {e}")
            return

        # 3. Check Search Functionality (TOP) - EXACT FIELDS AS APP
        print("\nTesting Search (Query: 'гравитация', Type: 'TOP', Full Fields)...")
        try:
            params = {
                "q": "гравитация",
                "search_type": "TOP",
                "fields": "id,text,media_type,permalink,timestamp,username,has_replies,is_reply",
                "access_token": TOKEN,
                "limit": "5"
            }
            response = await client.get(
                f"{THREADS_API_BASE}/keyword_search",
                params=params
            )
            
            print(f"Response Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', [])
                print(f"✅ SUCCESS: Found {len(posts)} posts.")
                # Print full raw data to debug
                print(f"Raw Data: {data}")
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Search Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_api())
