"""FastAPI server for Threads Research Tool."""

import os
import json
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
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


@app.post("/api/export-pdf")
async def export_pdf(data: SearchResponse):
    """Generate and return a PDF report."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Register Cyrillic Font (Arial)
    font_name = 'Helvetica' # Fallback
    try:
        # Try standard Windows path
        pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
        font_name = 'Arial'
    except Exception:
        pass

    styles = getSampleStyleSheet()
    
    # Update styles to use the font
    styles['Normal'].fontName = font_name
    styles['Heading1'].fontName = font_name
    styles['Heading2'].fontName = font_name
    styles['Title'].fontName = font_name
    
    story = []

    # Title
    story.append(Paragraph("Threads Pain Scanner Report", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Query Info
    story.append(Paragraph(f"Query: {data.query}", styles['Normal']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Paragraph(f"Total Posts: {data.total_posts}", styles['Normal']))
    story.append(Spacer(1, 24))

    if data.analysis:
        # Pains
        story.append(Paragraph("Pains & Problems", styles['Heading2']))
        for pain in data.analysis.pains:
            story.append(Paragraph(f"• {pain}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Needs
        story.append(Paragraph("User Needs", styles['Heading2']))
        for need in data.analysis.needs:
            story.append(Paragraph(f"• {need}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Ideas
        story.append(Paragraph("App Ideas", styles['Heading2']))
        for idea in data.analysis.app_ideas:
            story.append(Paragraph(f"• {idea}", styles['Normal']))
        story.append(Spacer(1, 24))

    # Top Posts
    story.append(Paragraph("Top Posts", styles['Heading2']))
    for i, post in enumerate(data.posts[:10], 1):
        story.append(Paragraph(f"<b>@{post.username}</b> ({post.timestamp.strftime('%Y-%m-%d')})", styles['Normal']))
        story.append(Paragraph(post.text, styles['Normal']))
        if post.replies:
             story.append(Paragraph(f"<i>Replies: {len(post.replies)}</i>", styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    }
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers=headers)


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
