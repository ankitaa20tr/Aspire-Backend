# source venvAnkitaTiwari/bin/activate
# python3 -m app.main
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, ai, strategies
import uvicorn
from loguru import logger

app = FastAPI(
    title="Aspire - Your AI Strategy Partner",
    description="Welcome to Aspire - Your AI-powered business strategy assistant that helps turn your business dreams into actionable plans.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)



# Include routers
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(strategies.router)

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
    return {
        "status": "healthy",
        "message": "All systems operational! 🚀",
        "version": "1.0.0"
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