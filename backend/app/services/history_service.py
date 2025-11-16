from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.models.database import Analysis, TrendData, User
import hashlib
import json


class HistoryService:
    """Service for managing analysis history and trends"""

    @staticmethod
    def create_analysis_record(
        db: Session,
        text: str,
        analysis_type: str,
        sentiment_result: dict = None,
        emotion_result: dict = None,
        user_id: Optional[int] = None,
        processing_time: float = 0.0,
        twitter_query: str = None,
        twitter_data: dict = None
    ) -> Analysis:
        """Create a new analysis record"""

        # Create text hash for caching
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        # Create analysis record
        analysis = Analysis(
            user_id=user_id,
            text=text[:1000],  # Store first 1000 chars
            text_hash=text_hash,
            analysis_type=analysis_type,
            processing_time=processing_time,
            twitter_query=twitter_query,
            twitter_data=twitter_data
        )

        # Add sentiment data
        if sentiment_result:
            analysis.sentiment_label = sentiment_result.get('label')
            analysis.sentiment_confidence = sentiment_result.get('confidence')
            analysis.language = sentiment_result.get('language')
            analysis.model_used = sentiment_result.get('model_used')

            scores = sentiment_result.get('scores', {})
            analysis.sentiment_positive = scores.get('positive', 0.0)
            analysis.sentiment_negative = scores.get('negative', 0.0)
            analysis.sentiment_neutral = scores.get('neutral', 0.0)

        # Add emotion data
        if emotion_result:
            analysis.emotion_label = emotion_result.get('primary_emotion')
            analysis.emotion_confidence = emotion_result.get('confidence')
            analysis.emotion_scores = emotion_result.get('scores')

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis

    @staticmethod
    def get_user_history(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        analysis_type: Optional[str] = None
    ) -> List[Analysis]:
        """Get user's analysis history"""

        query = db.query(Analysis).filter(Analysis.user_id == user_id)

        if analysis_type:
            query = query.filter(Analysis.analysis_type == analysis_type)

        return query.order_by(desc(Analysis.created_at)).offset(offset).limit(limit).all()

    @staticmethod
    def get_recent_analyses(
        db: Session,
        limit: int = 100,
        hours: int = 24
    ) -> List[Analysis]:
        """Get recent analyses"""

        since = datetime.utcnow() - timedelta(hours=hours)

        return db.query(Analysis).filter(
            Analysis.created_at >= since
        ).order_by(desc(Analysis.created_at)).limit(limit).all()

    @staticmethod
    def get_sentiment_stats(
        db: Session,
        user_id: Optional[int] = None,
        days: int = 7
    ) -> dict:
        """Get sentiment statistics"""

        since = datetime.utcnow() - timedelta(days=days)

        query = db.query(Analysis).filter(
            Analysis.created_at >= since,
            Analysis.sentiment_label.isnot(None)
        )

        if user_id:
            query = query.filter(Analysis.user_id == user_id)

        analyses = query.all()

        if not analyses:
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "avg_confidence": 0.0
            }

        positive = sum(1 for a in analyses if a.sentiment_label == "positive")
        negative = sum(1 for a in analyses if a.sentiment_label == "negative")
        neutral = sum(1 for a in analyses if a.sentiment_label == "neutral")
        avg_confidence = sum(a.sentiment_confidence or 0 for a in analyses) / len(analyses)

        return {
            "total": len(analyses),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "avg_confidence": avg_confidence,
            "period_days": days
        }

    @staticmethod
    def update_trend_data(
        db: Session,
        keyword: Optional[str] = None,
        date: Optional[datetime] = None
    ):
        """Update trend data aggregation"""

        if not date:
            date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Get analyses for the date
        next_date = date + timedelta(days=1)

        query = db.query(Analysis).filter(
            and_(
                Analysis.created_at >= date,
                Analysis.created_at < next_date
            )
        )

        if keyword:
            # Filter by keyword in text (simple approach)
            query = query.filter(Analysis.text.contains(keyword))

        analyses = query.all()

        if not analyses:
            return None

        # Calculate aggregations
        total = len(analyses)
        positive = sum(1 for a in analyses if a.sentiment_label == "positive")
        negative = sum(1 for a in analyses if a.sentiment_label == "negative")
        neutral = sum(1 for a in analyses if a.sentiment_label == "neutral")

        avg_positive = sum(a.sentiment_positive or 0 for a in analyses) / total
        avg_negative = sum(a.sentiment_negative or 0 for a in analyses) / total
        avg_confidence = sum(a.sentiment_confidence or 0 for a in analyses) / total

        # Emotion distribution
        emotions = {}
        for a in analyses:
            if a.emotion_label:
                emotions[a.emotion_label] = emotions.get(a.emotion_label, 0) + 1

        # Create or update trend record
        trend = db.query(TrendData).filter(
            and_(
                TrendData.date == date,
                TrendData.keyword == keyword
            )
        ).first()

        if trend:
            trend.total_analyses = total
            trend.positive_count = positive
            trend.negative_count = negative
            trend.neutral_count = neutral
            trend.avg_positive_score = avg_positive
            trend.avg_negative_score = avg_negative
            trend.avg_confidence = avg_confidence
            trend.emotion_distribution = emotions
        else:
            trend = TrendData(
                date=date,
                keyword=keyword,
                total_analyses=total,
                positive_count=positive,
                negative_count=negative,
                neutral_count=neutral,
                avg_positive_score=avg_positive,
                avg_negative_score=avg_negative,
                avg_confidence=avg_confidence,
                emotion_distribution=emotions
            )
            db.add(trend)

        db.commit()
        db.refresh(trend)

        return trend

    @staticmethod
    def get_trend_data(
        db: Session,
        days: int = 30,
        keyword: Optional[str] = None
    ) -> List[TrendData]:
        """Get trend data over time"""

        since = datetime.utcnow() - timedelta(days=days)

        query = db.query(TrendData).filter(TrendData.date >= since)

        if keyword:
            query = query.filter(TrendData.keyword == keyword)

        return query.order_by(TrendData.date).all()


# Global instance
history_service = HistoryService()
