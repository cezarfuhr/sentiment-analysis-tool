from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class EmotionLabel(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    LOVE = "love"
    NEUTRAL = "neutral"


class ModelType(str, Enum):
    NLTK = "nltk"
    SPACY = "spacy"
    TRANSFORMERS = "transformers"


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to analyze")
    language: Optional[str] = Field(None, description="Language code (en, pt, es). Auto-detected if not provided")
    model: Optional[ModelType] = Field(None, description="Model to use for analysis")


class BatchTextInput(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to analyze")
    language: Optional[str] = Field(None, description="Language code (en, pt, es). Auto-detected if not provided")
    model: Optional[ModelType] = Field(None, description="Model to use for analysis")


class SentimentScore(BaseModel):
    positive: float = Field(..., ge=0, le=1)
    negative: float = Field(..., ge=0, le=1)
    neutral: float = Field(..., ge=0, le=1)


class SentimentResult(BaseModel):
    text: str
    label: SentimentLabel
    scores: SentimentScore
    confidence: float = Field(..., ge=0, le=1)
    language: str
    model_used: str


class EmotionScore(BaseModel):
    joy: float = Field(..., ge=0, le=1)
    sadness: float = Field(..., ge=0, le=1)
    anger: float = Field(..., ge=0, le=1)
    fear: float = Field(..., ge=0, le=1)
    surprise: float = Field(..., ge=0, le=1)
    love: float = Field(..., ge=0, le=1)


class EmotionResult(BaseModel):
    text: str
    primary_emotion: EmotionLabel
    scores: EmotionScore
    confidence: float = Field(..., ge=0, le=1)
    language: str
    model_used: str


class CombinedAnalysisResult(BaseModel):
    sentiment: SentimentResult
    emotion: EmotionResult


class BatchSentimentResult(BaseModel):
    results: List[SentimentResult]
    summary: Dict[str, int]
    average_confidence: float


class TwitterSearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of tweets to analyze")
    language: Optional[str] = Field(None, description="Language filter")


class TwitterAnalysisResult(BaseModel):
    query: str
    total_tweets: int
    sentiment_distribution: Dict[str, int]
    emotion_distribution: Dict[str, int]
    average_sentiment_scores: SentimentScore
    tweets: List[Dict]


class HealthCheck(BaseModel):
    status: str
    version: str
    models_loaded: Dict[str, bool]
