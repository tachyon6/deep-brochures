from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
import logging
from dotenv import load_dotenv

from media_kit_agent import MediaKitSearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Media Kit Search API",
    description="API for searching media kits and advertising materials from Korean media outlets",
    version="1.0.0"
)

# Request model
class MediaSearchRequest(BaseModel):
    media_name: str
    openai_api_key: str
    firecrawl_api_key: str

# Response model
class MediaSearchResponse(BaseModel):
    result: Dict[str, str]


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Media Kit Search API",
        "description": "Search for media kits and advertising materials from Korean media outlets",
        "endpoints": {
            "POST /search": "Search for media kit URL by media name"
        }
    }

@app.post("/search", response_model=MediaSearchResponse)
async def search_media_kit(request: MediaSearchRequest):
    """
    Search for media kit URL for the given Korean media outlet
    
    Args:
        request: MediaSearchRequest with media_name field
        
    Returns:
        MediaSearchResponse with the search result
    """
    try:
        # Validate input
        if not request.media_name or not request.media_name.strip():
            raise HTTPException(status_code=400, detail="Media name cannot be empty")
        
        logger.info(f"[API] Received search request for: {request.media_name}")
        
        # Create a new agent instance for each request (independent context)
        agent = MediaKitSearchAgent(
            openai_api_key=request.openai_api_key,
            firecrawl_api_key=request.firecrawl_api_key
        )
        
        # Search for media kit
        result = agent.search_media_kit(request.media_name.strip())
        
        logger.info(f"[API] Returning result: {result}")
        return MediaSearchResponse(result=result)
        
    except Exception as e:
        logger.error(f"[API ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Production에서는 gunicorn 사용 권장
    # 개발 환경에서만 직접 실행
    uvicorn.run(
        app, 
        host="127.0.0.1",  # production에서는 127.0.0.1 (nginx 뒤에서 실행)
        port=8000, 
        log_config=None,
        workers=1  # EC2 t3.micro의 경우 1개 워커 권장
    )