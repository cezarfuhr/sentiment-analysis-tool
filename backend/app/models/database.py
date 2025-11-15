from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    analyses = relationship("Analysis", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100))
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=100)  # requests per hour

    # Relationships
    user = relationship("User", back_populates="api_keys")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    text = Column(Text, nullable=False)
    text_hash = Column(String(64), index=True)  # For caching

    # Analysis type
    analysis_type = Column(String(20), nullable=False)  # sentiment, emotion, combined, batch, twitter

    # Results
    sentiment_label = Column(String(20))
    sentiment_positive = Column(Float)
    sentiment_negative = Column(Float)
    sentiment_neutral = Column(Float)
    sentiment_confidence = Column(Float)

    emotion_label = Column(String(20))
    emotion_scores = Column(JSON)
    emotion_confidence = Column(Float)

    # Metadata
    language = Column(String(10))
    model_used = Column(String(50))

    # Twitter specific
    twitter_query = Column(String(500), nullable=True)
    twitter_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    processing_time = Column(Float)  # seconds

    # Indexes for performance
    __table_args__ = (
        Index('ix_user_created', 'user_id', 'created_at'),
        Index('ix_type_created', 'analysis_type', 'created_at'),
    )

    # Relationships
    user = relationship("User", back_populates="analyses")


class TrendData(Base):
    __tablename__ = "trend_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, index=True, nullable=False)
    keyword = Column(String(200), index=True)

    # Aggregated sentiment data
    total_analyses = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)

    avg_positive_score = Column(Float)
    avg_negative_score = Column(Float)
    avg_confidence = Column(Float)

    # Emotion aggregation
    emotion_distribution = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_date_keyword', 'date', 'keyword'),
    )
