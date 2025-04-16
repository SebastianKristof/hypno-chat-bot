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
import threading
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hypnobot-api")

# Load environment variables
load_dotenv()

# Add the project root to the system path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Apply memory patch first, before any other imports
from src.hypnobot.memory_patch import patch_memory
if not patch_memory():
    logger.error("Failed to apply memory patch - API may not function correctly")

# Now import HypnoBot
try:
    # First try to import directly
    logger.info("Attempting to import HypnoBot...")
    from src.hypnobot.v2 import HypnoBot
    logger.info("Successfully imported HypnoBot via package import")
except ImportError as e:
    logger.warning(f"Package import failed: {e}")
    try:
        # Try alternative direct import
        from src.hypnobot.v2.hypnobot import HypnoBot
        logger.info("Successfully imported HypnoBot via direct module import")
    except ImportError as e:
        logger.error(f"Failed to import HypnoBot: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Set HypnoBot to None so we can continue loading the API
        HypnoBot = None
        logger.error("API will start but bot functionality will be unavailable")

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
initialization_error = None
initialization_lock = threading.Lock()
is_initializing = False

def init_bot():
    """Initialize the HypnoBot outside of the lifespan context."""
    global bot, initialization_error, is_initializing, HypnoBot
    
    # Check if already initialized or initializing
    with initialization_lock:
        if bot is not None or is_initializing:
            return
        is_initializing = True
    
    try:
        # Check if API key is set
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Check if HypnoBot class was imported successfully
        if HypnoBot is None:
            raise ImportError("HypnoBot class not found. Please check import paths and dependencies.")
        
        logger.info("Initializing HypnoBot...")
        bot = HypnoBot()
        logger.info("HypnoBot initialization complete.")
    except Exception as e:
        initialization_error = str(e)
        logger.error(f"Error initializing HypnoBot: {initialization_error}")
        logger.error(traceback.format_exc())
    finally:
        with initialization_lock:
            is_initializing = False

# Start initialization in the background if HypnoBot is available
if HypnoBot is not None:
    threading.Thread(target=init_bot, daemon=True).start()
else:
    initialization_error = "HypnoBot class could not be imported"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for the FastAPI app."""
    # Yield control back to FastAPI
    yield
    
    # Cleanup on shutdown
    global bot
    if bot is not None:
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
    # Check for initialization error
    if initialization_error:
        raise HTTPException(
            status_code=500, 
            detail=f"HypnoBot initialization failed: {initialization_error}"
        )
    
    # Check if bot is ready
    if bot is None:
        # If not initializing yet, start initialization
        if not is_initializing and HypnoBot is not None:
            threading.Thread(target=init_bot, daemon=True).start()
        
        raise HTTPException(
            status_code=503, 
            detail="HypnoBot is still initializing. Please try again in a moment."
        )
    
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
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    import_status = "imported" if HypnoBot is not None else "import_failed"
    
    if initialization_error:
        return {
            "status": "error",
            "error": initialization_error,
            "import_status": import_status,
            "api_running": True
        }
    elif bot is None:
        return {
            "status": "initializing" if HypnoBot is not None else "failed",
            "message": "HypnoBot is starting up. Please wait." if HypnoBot is not None else "HypnoBot could not be loaded",
            "import_status": import_status,
            "api_running": True
        }
    else:
        return {
            "status": "healthy",
            "ready": True,
            "import_status": import_status,
            "api_running": True
        }

# To run this app: uvicorn src.hypnobot.api:app --reload 