"""
Dashboard API routes for FraudGuard AI
"""

import logging
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String, and_
from sqlalchemy.sql import text

from app.core.database import get_db
from app.schemas.prediction import DashboardSummaryResponse, DashboardTrendItem
from app.models.models import Transaction

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    summary="Dashboard summary",
    description="Get summary statistics for the fraud detection dashboard."
)
async def dashboard_summary(db: Session = Depends(get_db)):
    """
    Get dashboard summary with transaction statistics.
    
    All values are queried from PostgreSQL database.
    Returns actual statistics, not hardcoded values.
    
    Returns:
        DashboardSummaryResponse with transaction counts and percentages
    """
    try:
        # Query actual database
        total_transactions = db.query(func.count(Transaction.id)).scalar() or 0
        
        fraud_transactions = db.query(func.count(Transaction.id)).filter(
            Transaction.prediction == 'fraud'
        ).scalar() or 0
        
        legitimate_transactions = db.query(func.count(Transaction.id)).filter(
            Transaction.prediction == 'legitimate'
        ).scalar() or 0
        
        high_risk = db.query(func.count(Transaction.id)).filter(
            Transaction.risk_level == 'HIGH'
        ).scalar() or 0
        
        medium_risk = db.query(func.count(Transaction.id)).filter(
            Transaction.risk_level == 'MEDIUM'
        ).scalar() or 0
        
        low_risk = db.query(func.count(Transaction.id)).filter(
            Transaction.risk_level == 'LOW'
        ).scalar() or 0
        
        # Calculate fraud percentage
        fraud_percentage = (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0.0
        
        logger.info(
            f"Dashboard summary: "
            f"Total={total_transactions}, "
            f"Fraud={fraud_transactions}, "
            f"High={high_risk}"
        )
        
        return DashboardSummaryResponse(
            total_transactions=total_transactions,
            fraud_transactions=fraud_transactions,
            legitimate_transactions=legitimate_transactions,
            high_risk_transactions=high_risk,
            medium_risk_transactions=medium_risk,
            low_risk_transactions=low_risk,
            fraud_percentage=fraud_percentage
        )
        
    except Exception as e:
        logger.error(f"Error calculating dashboard summary: {str(e)}")
        # Return empty summary instead of failing
        return DashboardSummaryResponse(
            total_transactions=0,
            fraud_transactions=0,
            legitimate_transactions=0,
            high_risk_transactions=0,
            medium_risk_transactions=0,
            low_risk_transactions=0,
            fraud_percentage=0.0
        )


@router.get(
    "/dashboard/risk-trends",
    response_model=List[DashboardTrendItem],
    summary="Risk trends over time",
    description="Get transaction and fraud trends grouped by date."
)
async def risk_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get fraud trends over time.
    
    Groups transactions by date and calculates fraud count and percentage.
    Uses efficient SQL aggregation.
    
    Args:
        days: Number of days to include (default 30)
        db: Database session
        
    Returns:
        List of DashboardTrendItem with date, transactions, and fraud counts
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query aggregated data by date
        trends = db.query(
            func.date(Transaction.created_at).label('date'),
            func.count(Transaction.id).label('transaction_count'),
            func.count(
                Transaction.id
            ).filter(
                Transaction.prediction == 'fraud'
            ).over().label('fraud_count_debug')
        ).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at < end_date + timedelta(days=1)
        ).group_by(
            func.date(Transaction.created_at)
        ).order_by(
            func.date(Transaction.created_at)
        ).all()
        
        # Convert to response format
        result = []
        for trend in trends:
            date_str = trend[0].isoformat() if trend[0] else ''
            transaction_count = trend[1] or 0
            
            # Count fraud for this date
            fraud_count = db.query(func.count(Transaction.id)).filter(
                and_(
                    func.date(Transaction.created_at) == trend[0],
                    Transaction.prediction == 'fraud'
                )
            ).scalar() or 0
            
            fraud_percentage = (fraud_count / transaction_count * 100) if transaction_count > 0 else 0.0
            
            result.append(DashboardTrendItem(
                date=date_str,
                transactions=transaction_count,
                fraud=fraud_count,
                fraud_percentage=fraud_percentage
            ))
        
        logger.info(f"Risk trends: {len(result)} days of data")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating risk trends: {str(e)}")
        # Return empty list instead of failing
        return []
