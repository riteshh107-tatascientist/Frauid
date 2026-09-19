"""
Transaction API routes for FraudGuard AI
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.core.database import get_db
from app.schemas.prediction import StoredTransactionResponse, TransactionListResponse
from app.models.models import Transaction, RiskLevel, Prediction, User
from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/transactions",
    response_model=TransactionListResponse,
    summary="List transactions",
    description="Get paginated list of stored transaction predictions for the current user."
)
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: LOW, MEDIUM, HIGH"),
    prediction: Optional[str] = Query(None, description="Filter by prediction: fraud, legitimate"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List stored transaction predictions with pagination and filtering.
    
    Query parameters allow filtering by:
    - risk_level: LOW, MEDIUM, HIGH
    - prediction: fraud, legitimate
    - start_date, end_date: Date range
    
    Args:
        page: Page number (1-indexed)
        page_size: Items per page (1-100)
        risk_level: Optional risk level filter
        prediction: Optional prediction filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        db: Database session
        
    Returns:
        TransactionListResponse with paginated transactions
    """
    try:
        # Start with user's own transactions
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
        
        # Apply filters
        if risk_level:
            risk_level_upper = risk_level.upper()
            if risk_level_upper not in ['LOW', 'MEDIUM', 'HIGH']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid risk_level. Must be LOW, MEDIUM, or HIGH"
                )
            query = query.filter(Transaction.risk_level == risk_level_upper)
        
        if prediction:
            pred_lower = prediction.lower()
            if pred_lower not in ['fraud', 'legitimate']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid prediction. Must be 'fraud' or 'legitimate'"
                )
            query = query.filter(Transaction.prediction == pred_lower)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Transaction.created_at >= start_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date. Use YYYY-MM-DD format"
                )
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                # Add 1 day to include all of end_date
                end_dt = end_dt + timedelta(days=1)
                query = query.filter(Transaction.created_at < end_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date. Use YYYY-MM-DD format"
                )
        
        # Get total count
        total = query.count()
        
        # Apply sorting (newest first) and pagination
        skip = (page - 1) * page_size
        transactions = query.order_by(desc(Transaction.created_at)).offset(skip).limit(page_size).all()
        
        return TransactionListResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[StoredTransactionResponse.from_orm(t) for t in transactions]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list transactions"
        )


@router.get(
    "/transactions/{transaction_id}",
    response_model=StoredTransactionResponse,
    summary="Get transaction",
    description="Get details of a specific transaction prediction (user can only access their own)."
)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single transaction by ID.
    
    Args:
        transaction_id: Transaction ID
        db: Database session
        
    Returns:
        StoredTransactionResponse with transaction details
        
    Raises:
        404: If transaction not found
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            # Return 404 whether transaction doesn't exist or user doesn't own it
            # This prevents information disclosure
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction {transaction_id} not found"
            )
        
        return StoredTransactionResponse.from_orm(transaction)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction"
        )
