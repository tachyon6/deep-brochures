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

# Response model
class MediaSearchResponse(BaseModel):
    result: Dict[str, str]

# Get Firecrawl API key
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "fc-6c6fb40857a14880b0145507e929b14a")

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
        agent = MediaKitSearchAgent(firecrawl_api_key=FIRECRAWL_API_KEY)
        
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
    # Run with console logging only (no file logging)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)