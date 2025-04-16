import os
import sys
import contextlib
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hypnobot-api")

# Load environment variables
load_dotenv()

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.hypnobot.v2.hypnobot import HypnoBot

# Define request and response models
class HypnoBotRequest(BaseModel):
    user_input: str = Field(..., min_length=1, max_length=10000)
    
    @validator('user_input')
    def validate_user_input(cls, v):
        if not v.strip():
            raise ValueError("Input cannot be empty or only whitespace")
        return v.strip()

class HypnoBotResponse(BaseModel):
    response: str

# Initialize the HypnoBot
bot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app."""
    # Initialize the bot on startup
    global bot
    try:
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        logger.info("Initializing HypnoBot...")
        bot = HypnoBot()
        logger.info("HypnoBot initialization complete.")
        
        yield  # This will run until the app shuts down
    
    except Exception as e:
        logger.error(f"Error initializing HypnoBot: {str(e)}")
        yield
    
    finally:
        # Cleanup on shutdown if needed
        logger.info("Shutting down HypnoBot...")
        bot = None
        logger.info("HypnoBot shutdown complete.")

# Initialize the FastAPI app
app = FastAPI(
    title="HypnoBot API",
    description="API for the HypnoBot hypnotherapy chatbot",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files directory
static_dir = Path(__file__).resolve().parent / "static"
if not static_dir.exists():
    static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Serve index.html at root path
@app.get("/")
async def get_index():
    """Serve the frontend index.html file."""
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.post("/api/chat", response_model=HypnoBotResponse)
async def chat(request: HypnoBotRequest):
    """Process a chat message through the HypnoBot."""
    if not bot:
        raise HTTPException(status_code=503, detail="Bot not initialized. Please try again later.")
    
    try:
        # Log input length and truncate if necessary
        input_length = len(request.user_input)
        truncated = False
        
        if input_length > 1500:
            logger.info(f"Truncating long input from {input_length} to 1500 characters")
            truncated = True
        
        logger.info(f"Processing request: {request.user_input[:30]}...")
        response = bot.process_input(request.user_input)
        
        logger.info("Request processed successfully")
        return HypnoBotResponse(response=response)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    status = "healthy" if bot is not None else "initializing"
    return {"status": status}

# To run this app: uvicorn src.hypnobot.api:app --reload 