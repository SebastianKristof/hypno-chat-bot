import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.hypnobot.v2.hypnobot import HypnoBot

# Define request and response models
class HypnoBotRequest(BaseModel):
    user_input: str

class HypnoBotResponse(BaseModel):
    response: str

# Initialize the FastAPI app
app = FastAPI(
    title="HypnoBot API",
    description="API for the HypnoBot hypnotherapy chatbot",
    version="2.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the HypnoBot
bot = None

@app.on_event("startup")
async def startup_event():
    """Initialize the bot at startup."""
    global bot
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    bot = HypnoBot()

@app.post("/api/chat", response_model=HypnoBotResponse)
async def chat(request: HypnoBotRequest):
    """Process a chat message through the HypnoBot."""
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        response = bot.process_input(request.user_input)
        return HypnoBotResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# To run this app: uvicorn src.hypnobot.api:app --reload 