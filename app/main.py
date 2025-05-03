<<<<<<< HEAD
# source .venv/bin/activate 
=======
# source venvAnkitaTiwari/bin/activate 
>>>>>>> 10ea94d63b78da66bb861a7ac7de7cf034028959
# python3 -m app.main

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers import auth, ai, strategies
import uvicorn
from loguru import logger
import sys
import traceback

# Configure logger to output to console
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="DEBUG")

app = FastAPI(
    title="Aspire - Your AI Strategy Partner",
    description="Welcome to Aspire - Your AI-powered business strategy assistant that helps turn your business dreams into actionable plans.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(strategies.router)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and catch exceptions."""
    path = request.url.path
    logger.info(f"Request: {request.method} {path}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request {path}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal error occurred. Please check the server logs for more information.",
                "error_type": str(type(e).__name__),
            }
        )

@app.get("/", tags=["Welcome"])
async def root():
    """Welcome to Aspire!"""
    return {
        "message": "👋 Welcome to Aspire - Your AI Strategy Partner!",
        "status": "online",
        "getting_started": "Visit /docs to explore our API endpoints",
        "support": "Need help? Contact our team at support@aspire.ai"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    logger.debug("Health check endpoint called")
    
    # Check database connection
    from app.database.database import engine
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        db_status = f"error: {str(e)}"
    
    # Check OpenAI API key
    import os
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_status = "configured" if openai_key and len(openai_key) > 10 else "missing"
    
    return {
        "status": "healthy",
        "message": "All systems operational! 🚀",
        "version": "1.0.0",
        "database": db_status,
        "openai_api": openai_status
    }

if __name__ == "__main__":
    logger.info("🌟 Starting Aspire API server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)



# while True:
#     try:
#         conn =  psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='anki2030', cursor_factory=RealDictCursor)
#         cursor = conn.cursor
#         print('Database connected!')
#         break
#     except Exception as error:
#         print("Connection failed")
#         print("Error: ", error)
#         time.sleep(2)

