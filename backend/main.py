"""FastAPI server for Threads Research Tool."""

import os
import json
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

from models import (
    SearchRequest, SearchResponse, AnalyzeRequest, 
    HealthResponse, ThreadsPost, AnalysisResult
)
from threads_client import ThreadsClient
from ollama_client import OllamaClient
from analyzer import PostAnalyzer

load_dotenv()

# Globals
threads_client: ThreadsClient = None
ollama_client: OllamaClient = None
analyzer: PostAnalyzer = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global threads_client, ollama_client, analyzer
    
    # Startup
    threads_client = ThreadsClient()
    ollama_client = OllamaClient()
    analyzer = PostAnalyzer()
    
    print("🚀 Threads Research Tool started!")
    print(f"   Threads API: {'✅ Configured' if threads_client.is_configured else '⚠️ Demo mode'}")
    
    ollama_ok = await ollama_client.is_available()
    print(f"   Ollama: {'✅ Available' if ollama_ok else '❌ Not available'}")
    
    yield
    
    # Shutdown
    await threads_client.close()
    print("👋 Shutting down...")


app = FastAPI(
    title="Threads Research Tool",
    description="Search and analyze Threads posts to find user pains and app ideas",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== API Endpoints ==============

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check system health."""
    ollama_ok = await ollama_client.is_available()
    return HealthResponse(
        status="ok",
        ollama_available=ollama_ok,
        threads_api_configured=threads_client.is_configured
    )


@app.post("/api/search", response_model=SearchResponse)
async def search_threads(request: SearchRequest):
    """Search Threads by keywords and analyze results."""
    try:
        # Search posts
        posts = await threads_client.search(
            query=request.keywords,
            search_type=request.search_type,
            media_type=request.media_type,
            limit=request.limit,
            since=request.since,
            until=request.until,
        )
        
        # Analyze with LLM
        result = await analyzer.analyze(posts, request.keywords)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_posts(request: AnalyzeRequest):
    """Analyze provided posts."""
    try:
        texts = [p.text for p in request.posts]
        analysis = await ollama_client.analyze_posts(texts, request.focus)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/{format}")
async def export_results(format: str, query: str = ""):
    """Export last results as CSV or JSON."""
    # For now, return a sample export structure
    sample_data = {
        "query": query,
        "exported_at": datetime.now().isoformat(),
        "results": {
            "pains": [],
            "needs": [],
            "app_ideas": []
        }
    }
    
    if format == "json":
        return JSONResponse(content=sample_data)
    elif format == "csv":
        # Simple CSV export
        csv_content = "type,content\n"
        return JSONResponse(content={"message": "CSV export coming soon"})
    else:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")


# ============== Static Files ==============

frontend_path = Path(__file__).parent.parent / "frontend"

@app.get("/")
async def serve_index():
    """Serve the main dashboard."""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found. Run from project root or check frontend folder."}


@app.get("/styles.css")
async def serve_css():
    """Serve CSS."""
    css_file = frontend_path / "styles.css"
    if css_file.exists():
        return FileResponse(css_file, media_type="text/css")
    raise HTTPException(status_code=404)


@app.get("/app.js")
async def serve_js():
    """Serve JavaScript."""
    js_file = frontend_path / "app.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404)


# ============== Run ==============

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting server at http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)
