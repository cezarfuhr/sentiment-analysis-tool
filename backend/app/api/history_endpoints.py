from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from app.core.database import get_db
from app.services.history_service import history_service
from app.services.export_service import export_service
from app.models.schemas import SentimentResult
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class HistoryItem(BaseModel):
    id: int
    text: str
    analysis_type: str
    sentiment_label: Optional[str]
    sentiment_confidence: Optional[float]
    emotion_label: Optional[str]
    emotion_confidence: Optional[float]
    language: Optional[str]
    model_used: Optional[str]
    created_at: datetime
    processing_time: Optional[float]

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total: int
    positive: int
    negative: int
    neutral: int
    avg_confidence: float
    period_days: int


class TrendDataResponse(BaseModel):
    date: datetime
    total_analyses: int
    positive_count: int
    negative_count: int
    neutral_count: int
    avg_positive_score: float
    avg_negative_score: float
    avg_confidence: float

    class Config:
        from_attributes = True


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    analysis_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get analysis history

    - **limit**: Maximum number of results (1-100)
    - **offset**: Number of results to skip
    - **analysis_type**: Filter by type (sentiment, emotion, combined, batch, twitter)
    """
    try:
        # For now, get all recent analyses since we don't have user auth yet
        analyses = history_service.get_recent_analyses(db, limit=limit)

        return analyses
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get sentiment statistics

    - **days**: Number of days to include (1-365)
    """
    try:
        stats = history_service.get_sentiment_stats(db, days=days)
        return stats
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/trends", response_model=List[TrendDataResponse])
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get trend data over time

    - **days**: Number of days to include (1-365)
    - **keyword**: Optional keyword to filter by
    """
    try:
        trends = history_service.get_trend_data(db, days=days, keyword=keyword)
        return trends
    except Exception as e:
        logger.error(f"Error retrieving trends: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving trends: {str(e)}")


@router.post("/trends/update")
async def update_trends(
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Update trend data aggregation for today

    - **keyword**: Optional keyword to aggregate for
    """
    try:
        trend = history_service.update_trend_data(db, keyword=keyword)

        if not trend:
            return {"message": "No data to aggregate"}

        return {
            "message": "Trend data updated successfully",
            "date": trend.date,
            "total_analyses": trend.total_analyses
        }
    except Exception as e:
        logger.error(f"Error updating trends: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating trends: {str(e)}")


@router.get("/export/csv")
async def export_csv(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Export analysis history to CSV"""
    try:
        analyses = history_service.get_recent_analyses(db, limit=1000, hours=days*24)
        export_data = export_service.prepare_export_data(analyses)

        csv_content = export_service.export_to_csv(export_data)

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=sentiment_analysis_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")


@router.get("/export/json")
async def export_json(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Export analysis history to JSON"""
    try:
        analyses = history_service.get_recent_analyses(db, limit=1000, hours=days*24)
        export_data = export_service.prepare_export_data(analyses)

        json_content = export_service.export_to_json(export_data)

        return StreamingResponse(
            iter([json_content]),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=sentiment_analysis_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting JSON: {str(e)}")


@router.get("/export/pdf")
async def export_pdf(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Export analysis history to PDF"""
    try:
        analyses = history_service.get_recent_analyses(db, limit=100, hours=days*24)
        export_data = export_service.prepare_export_data(analyses)

        pdf_content = export_service.export_to_pdf(export_data)

        return StreamingResponse(
            iter([pdf_content]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=sentiment_analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error exporting PDF: {str(e)}")
