import tweepy
from typing import List, Dict, Optional
import logging
from app.core.config import settings
from app.services.sentiment_analyzer import sentiment_analyzer
from app.models.schemas import TwitterAnalysisResult, SentimentScore

logger = logging.getLogger(__name__)


class TwitterService:
    def __init__(self):
        self.client = None
        self.api = None
        self._init_client()

    def _init_client(self):
        """Initialize Twitter API client"""
        try:
            if settings.TWITTER_BEARER_TOKEN:
                self.client = tweepy.Client(
                    bearer_token=settings.TWITTER_BEARER_TOKEN,
                    consumer_key=settings.TWITTER_API_KEY,
                    consumer_secret=settings.TWITTER_API_SECRET,
                    access_token=settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=settings.TWITTER_ACCESS_SECRET,
                    wait_on_rate_limit=True
                )
                logger.info("Twitter client initialized successfully")
            else:
                logger.warning("Twitter credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")

    def search_tweets(
        self,
        query: str,
        max_results: int = 10,
        language: Optional[str] = None
    ) -> List[Dict]:
        """Search tweets by query"""
        if not self.client:
            raise ValueError("Twitter client not initialized. Please configure API credentials.")

        try:
            # Search recent tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )

            if not tweets.data:
                return []

            # Format tweets
            users = {user.id: user for user in tweets.includes.get('users', [])}
            results = []

            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': str(tweet.created_at),
                    'lang': tweet.lang,
                    'author': {
                        'username': author.username if author else 'unknown',
                        'name': author.name if author else 'unknown'
                    },
                    'metrics': {
                        'likes': tweet.public_metrics.get('like_count', 0),
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0)
                    }
                })

            return results

        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            raise

    def analyze_tweets(
        self,
        query: str,
        max_results: int = 10,
        language: Optional[str] = None
    ) -> TwitterAnalysisResult:
        """Search and analyze sentiment of tweets"""
        # Search tweets
        tweets = self.search_tweets(query, max_results, language)

        if not tweets:
            return TwitterAnalysisResult(
                query=query,
                total_tweets=0,
                sentiment_distribution={
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0
                },
                emotion_distribution={
                    "joy": 0,
                    "sadness": 0,
                    "anger": 0,
                    "fear": 0,
                    "surprise": 0,
                    "love": 0
                },
                average_sentiment_scores=SentimentScore(
                    positive=0.0,
                    negative=0.0,
                    neutral=0.0
                ),
                tweets=[]
            )

        # Analyze sentiments
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        emotion_counts = {
            "joy": 0, "sadness": 0, "anger": 0,
            "fear": 0, "surprise": 0, "love": 0
        }
        total_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

        analyzed_tweets = []
        for tweet in tweets:
            # Sentiment analysis
            sentiment_result = sentiment_analyzer.analyze_sentiment(
                tweet['text'],
                language=language
            )

            # Emotion analysis
            emotion_result = sentiment_analyzer.analyze_emotions(
                tweet['text'],
                language=language
            )

            # Update counts
            sentiment_counts[sentiment_result.label] += 1
            emotion_counts[emotion_result.primary_emotion] += 1

            # Update scores
            total_scores["positive"] += sentiment_result.scores.positive
            total_scores["negative"] += sentiment_result.scores.negative
            total_scores["neutral"] += sentiment_result.scores.neutral

            # Add analysis to tweet
            analyzed_tweets.append({
                **tweet,
                'sentiment': {
                    'label': sentiment_result.label,
                    'confidence': sentiment_result.confidence,
                    'scores': {
                        'positive': sentiment_result.scores.positive,
                        'negative': sentiment_result.scores.negative,
                        'neutral': sentiment_result.scores.neutral
                    }
                },
                'emotion': {
                    'label': emotion_result.primary_emotion,
                    'confidence': emotion_result.confidence
                }
            })

        # Calculate averages
        num_tweets = len(tweets)
        avg_scores = SentimentScore(
            positive=total_scores["positive"] / num_tweets,
            negative=total_scores["negative"] / num_tweets,
            neutral=total_scores["neutral"] / num_tweets
        )

        return TwitterAnalysisResult(
            query=query,
            total_tweets=num_tweets,
            sentiment_distribution=sentiment_counts,
            emotion_distribution=emotion_counts,
            average_sentiment_scores=avg_scores,
            tweets=analyzed_tweets
        )


# Global instance
twitter_service = TwitterService()
