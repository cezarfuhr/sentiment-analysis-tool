from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
from app.models.schemas import (
    TextInput, SentimentResult, EmotionResult,
    CombinedAnalysisResult, BatchTextInput, BatchSentimentResult,
    TwitterSearchInput, TwitterAnalysisResult, HealthCheck,
    SentimentLabel
)
from app.services.sentiment_analyzer import sentiment_analyzer
from app.services.twitter_service import twitter_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        models_loaded=sentiment_analyzer.models_loaded
    )


@router.post("/sentiment", response_model=SentimentResult)
async def analyze_sentiment(input_data: TextInput):
    """
    Analyze sentiment of a single text.

    Returns:
    - label: positive, negative, or neutral
    - scores: probability scores for each sentiment
    - confidence: confidence level of the prediction
    - language: detected language
    - model_used: model used for analysis
    """
    try:
        result = sentiment_analyzer.analyze_sentiment(
            text=input_data.text,
            language=input_data.language,
            model=input_data.model
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing sentiment: {str(e)}"
        )


@router.post("/emotion", response_model=EmotionResult)
async def analyze_emotion(input_data: TextInput):
    """
    Analyze emotions in a single text.

    Returns:
    - primary_emotion: dominant emotion detected
    - scores: probability scores for each emotion
    - confidence: confidence level of the prediction
    - language: detected language
    - model_used: model used for analysis
    """
    try:
        result = sentiment_analyzer.analyze_emotions(
            text=input_data.text,
            language=input_data.language
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing emotion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing emotion: {str(e)}"
        )


@router.post("/analyze", response_model=CombinedAnalysisResult)
async def analyze_combined(input_data: TextInput):
    """
    Perform combined sentiment and emotion analysis.

    Returns both sentiment and emotion analysis results.
    """
    try:
        sentiment_result = sentiment_analyzer.analyze_sentiment(
            text=input_data.text,
            language=input_data.language,
            model=input_data.model
        )

        emotion_result = sentiment_analyzer.analyze_emotions(
            text=input_data.text,
            language=input_data.language
        )

        return CombinedAnalysisResult(
            sentiment=sentiment_result,
            emotion=emotion_result
        )
    except Exception as e:
        logger.error(f"Error in combined analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in combined analysis: {str(e)}"
        )


@router.post("/sentiment/batch", response_model=BatchSentimentResult)
async def analyze_sentiment_batch(input_data: BatchTextInput):
    """
    Analyze sentiment for multiple texts.

    Returns:
    - results: list of sentiment analysis results
    - summary: count of positive/negative/neutral sentiments
    - average_confidence: average confidence across all predictions
    """
    try:
        results = sentiment_analyzer.analyze_batch(
            texts=input_data.texts,
            language=input_data.language,
            model=input_data.model
        )

        # Calculate summary
        summary = {
            SentimentLabel.POSITIVE: 0,
            SentimentLabel.NEGATIVE: 0,
            SentimentLabel.NEUTRAL: 0
        }
        total_confidence = 0.0

        for result in results:
            summary[result.label] += 1
            total_confidence += result.confidence

        avg_confidence = total_confidence / len(results) if results else 0.0

        return BatchSentimentResult(
            results=results,
            summary=summary,
            average_confidence=avg_confidence
        )
    except Exception as e:
        logger.error(f"Error in batch analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch analysis: {str(e)}"
        )


@router.post("/twitter/analyze", response_model=TwitterAnalysisResult)
async def analyze_twitter(input_data: TwitterSearchInput):
    """
    Search and analyze sentiment of tweets.

    Returns:
    - query: search query used
    - total_tweets: number of tweets analyzed
    - sentiment_distribution: count of positive/negative/neutral tweets
    - emotion_distribution: count of different emotions
    - average_sentiment_scores: average sentiment scores
    - tweets: list of tweets with sentiment analysis
    """
    try:
        result = twitter_service.analyze_tweets(
            query=input_data.query,
            max_results=input_data.max_results,
            language=input_data.language
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error analyzing Twitter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing Twitter: {str(e)}"
        )


@router.get("/models")
async def list_models():
    """List available models and their status"""
    return {
        "models": [
            {
                "name": "NLTK (VADER)",
                "type": "nltk",
                "loaded": sentiment_analyzer.models_loaded.get("nltk", False),
                "description": "Rule-based sentiment analysis, good for social media"
            },
            {
                "name": "spaCy",
                "type": "spacy",
                "loaded": sentiment_analyzer.models_loaded.get("spacy", False),
                "description": "NLP processing with entity recognition",
                "languages": ["en", "pt", "es"]
            },
            {
                "name": "Transformers (BERT)",
                "type": "transformers",
                "loaded": sentiment_analyzer.models_loaded.get("transformers", False),
                "description": "State-of-the-art deep learning models",
                "capabilities": ["sentiment", "emotion", "multilingual"]
            }
        ]
    }


@router.get("/languages")
async def list_languages():
    """List supported languages"""
    return {
        "languages": [
            {"code": "en", "name": "English", "models": ["nltk", "spacy", "transformers"]},
            {"code": "pt", "name": "Portuguese", "models": ["spacy", "transformers"]},
            {"code": "es", "name": "Spanish", "models": ["spacy", "transformers"]},
            {"code": "auto", "name": "Auto-detect", "models": ["transformers"]}
        ]
    }
