import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import spacy
from transformers import pipeline
from langdetect import detect, LangDetectException
from typing import Dict, Optional, List
import logging
from app.models.schemas import (
    SentimentLabel, SentimentScore, SentimentResult,
    EmotionLabel, EmotionScore, EmotionResult,
    ModelType
)

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    def __init__(self):
        self.models_loaded = {
            "nltk": False,
            "spacy": False,
            "transformers": False
        }
        self._init_models()

    def _init_models(self):
        """Initialize all NLP models"""
        try:
            # NLTK
            self.sia = SentimentIntensityAnalyzer()
            self.models_loaded["nltk"] = True
            logger.info("NLTK model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load NLTK model: {e}")

        try:
            # spaCy models for different languages
            self.spacy_models = {
                "en": spacy.load("en_core_web_sm"),
                "pt": spacy.load("pt_core_news_sm"),
                "es": spacy.load("es_core_news_sm")
            }
            self.models_loaded["spacy"] = True
            logger.info("spaCy models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy models: {e}")
            self.spacy_models = {}

        try:
            # Transformers pipelines
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )

            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )

            # Multilingual sentiment
            self.multilingual_pipeline = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment"
            )

            self.models_loaded["transformers"] = True
            logger.info("Transformers models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Transformers models: {e}")

    def detect_language(self, text: str) -> str:
        """Detect language of the text"""
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return "en"  # Default to English

    def analyze_sentiment_nltk(self, text: str, language: str) -> Dict:
        """Analyze sentiment using NLTK (VADER)"""
        scores = self.sia.polarity_scores(text)

        # Determine label
        if scores['compound'] >= 0.05:
            label = SentimentLabel.POSITIVE
        elif scores['compound'] <= -0.05:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL

        return {
            "label": label,
            "scores": SentimentScore(
                positive=scores['pos'],
                negative=scores['neg'],
                neutral=scores['neu']
            ),
            "confidence": abs(scores['compound'])
        }

    def analyze_sentiment_transformers(self, text: str, language: str) -> Dict:
        """Analyze sentiment using Transformers"""
        # Use multilingual model for non-English texts
        if language != "en":
            result = self.multilingual_pipeline(text)[0]
            # Convert 5-star rating to sentiment
            stars = int(result['label'].split()[0])
            if stars >= 4:
                label = SentimentLabel.POSITIVE
                pos_score = result['score']
                neg_score = 0.0
            elif stars <= 2:
                label = SentimentLabel.NEGATIVE
                pos_score = 0.0
                neg_score = result['score']
            else:
                label = SentimentLabel.NEUTRAL
                pos_score = 0.0
                neg_score = 0.0

            neutral_score = 1.0 - pos_score - neg_score
        else:
            result = self.sentiment_pipeline(text)[0]
            label_map = {
                "POSITIVE": SentimentLabel.POSITIVE,
                "NEGATIVE": SentimentLabel.NEGATIVE
            }
            label = label_map.get(result['label'], SentimentLabel.NEUTRAL)

            if label == SentimentLabel.POSITIVE:
                pos_score = result['score']
                neg_score = 1.0 - result['score']
                neutral_score = 0.0
            else:
                pos_score = 1.0 - result['score']
                neg_score = result['score']
                neutral_score = 0.0

        return {
            "label": label,
            "scores": SentimentScore(
                positive=pos_score,
                negative=neg_score,
                neutral=neutral_score
            ),
            "confidence": max(pos_score, neg_score, neutral_score)
        }

    def analyze_sentiment(
        self,
        text: str,
        language: Optional[str] = None,
        model: Optional[ModelType] = None
    ) -> SentimentResult:
        """Main sentiment analysis method"""
        # Detect language if not provided
        if language is None:
            language = self.detect_language(text)

        # Select model
        model_type = model or ModelType.TRANSFORMERS

        # Analyze based on selected model
        if model_type == ModelType.NLTK:
            result = self.analyze_sentiment_nltk(text, language)
            model_used = "NLTK (VADER)"
        elif model_type == ModelType.TRANSFORMERS:
            result = self.analyze_sentiment_transformers(text, language)
            model_used = "Transformers (BERT)"
        else:
            # Default to transformers
            result = self.analyze_sentiment_transformers(text, language)
            model_used = "Transformers (BERT)"

        return SentimentResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            label=result["label"],
            scores=result["scores"],
            confidence=result["confidence"],
            language=language,
            model_used=model_used
        )

    def analyze_emotions(
        self,
        text: str,
        language: Optional[str] = None
    ) -> EmotionResult:
        """Analyze emotions in text"""
        if language is None:
            language = self.detect_language(text)

        # Use emotion pipeline
        results = self.emotion_pipeline(text)[0]

        # Map emotions
        emotion_map = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "love": 0.0
        }

        for item in results:
            label = item['label'].lower()
            score = item['score']
            if label in emotion_map:
                emotion_map[label] = score
            elif label == "disgust":
                emotion_map["anger"] += score * 0.5
            elif label == "neutral":
                # Distribute neutral to all emotions equally
                for key in emotion_map:
                    emotion_map[key] += score / 6

        # Find primary emotion
        primary = max(emotion_map.items(), key=lambda x: x[1])
        primary_emotion = EmotionLabel[primary[0].upper()]

        return EmotionResult(
            text=text[:100] + "..." if len(text) > 100 else text,
            primary_emotion=primary_emotion,
            scores=EmotionScore(**emotion_map),
            confidence=primary[1],
            language=language,
            model_used="Transformers (RoBERTa)"
        )

    def analyze_batch(
        self,
        texts: List[str],
        language: Optional[str] = None,
        model: Optional[ModelType] = None
    ) -> List[SentimentResult]:
        """Analyze multiple texts"""
        results = []
        for text in texts:
            result = self.analyze_sentiment(text, language, model)
            results.append(result)
        return results


# Global instance
sentiment_analyzer = SentimentAnalyzer()
