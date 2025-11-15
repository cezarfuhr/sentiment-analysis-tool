from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.core.config import settings
from app.api.endpoints import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Sentiment Analysis API

    Powerful sentiment and emotion analysis API supporting multiple languages and models.

    ### Features
    * 📊 **Sentiment Analysis** - Detect positive, negative, or neutral sentiment
    * 🎭 **Emotion Detection** - Identify emotions like joy, sadness, anger, fear, surprise, and love
    * 🌐 **Multi-language Support** - Analyze texts in English, Portuguese, Spanish, and more
    * 🤖 **Multiple Models** - Choose between NLTK, spaCy, and Transformers models
    * 📦 **Batch Processing** - Analyze multiple texts at once
    * 🐦 **Twitter Integration** - Analyze sentiment from Twitter searches

    ### Models
    * **NLTK (VADER)** - Fast, rule-based sentiment analysis
    * **spaCy** - Advanced NLP with entity recognition
    * **Transformers (BERT)** - State-of-the-art deep learning models

    ### Languages
    * English (en)
    * Portuguese (pt)
    * Spanish (es)
    * Auto-detection for other languages
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"CORS origins: {settings.cors_origins_list}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutting down application")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sentiment Analysis API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
