"""
Admin-only endpoints for FraudGuard AI
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User, UserRole, FraudAlert, AlertStatus
from app.schemas.user import UserResponse
from app.api.dependencies import get_current_admin

logger = logging.getLogger(__name__)

router = APIRouter()


# User Management Endpoints

@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all users",
    description="Admin-only: Get list of all users"
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List all users in the system.
    
    Only accessible by ADMIN users.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        List of UserResponse objects
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(u) for u in users]


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Get user details",
    description="Admin-only: Get details of a specific user"
)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific user.
    
    Only accessible by ADMIN users.
    
    Args:
        user_id: ID of user to retrieve
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        UserResponse object
        
    Raises:
        404: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    return UserResponse.from_orm(user)


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    summary="Update user status",
    description="Admin-only: Activate or deactivate a user"
)
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update user active status.
    
    Only accessible by ADMIN users.
    Cannot deactivate the currently logged-in admin.
    
    Args:
        user_id: ID of user to update
        is_active: New active status
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated UserResponse object
        
    Raises:
        404: If user not found
        403: If trying to deactivate current admin
    """
    # Prevent admin from deactivating themselves
    if user_id == current_admin.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate your own admin account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    logger.info(f"Admin {current_admin.id} updated user {user_id} status to {is_active}")
    
    return UserResponse.from_orm(user)


# Fraud Alert Management Endpoints

@router.get(
    "/alerts",
    summary="List fraud alerts",
    description="Admin-only: Get list of all fraud alerts"
)
async def list_alerts(
    status_filter: str = Query(None, description="Filter by status: OPEN, REVIEWED, RESOLVED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    List fraud alerts with optional status filtering.
    
    Only accessible by ADMIN users.
    
    Args:
        status_filter: Optional status filter
        skip: Number of alerts to skip
        limit: Maximum number of alerts
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        List of fraud alerts
    """
    query = db.query(FraudAlert)
    
    if status_filter:
        try:
            alert_status = AlertStatus[status_filter.upper()]
            query = query.filter(FraudAlert.status == alert_status)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be OPEN, REVIEWED, or RESOLVED"
            )
    
    alerts = query.order_by(FraudAlert.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "alerts": alerts
    }


@router.get(
    "/alerts/{alert_id}",
    summary="Get alert details",
    description="Admin-only: Get details of a specific fraud alert"
)
async def get_alert(
    alert_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific fraud alert.
    
    Only accessible by ADMIN users.
    
    Args:
        alert_id: ID of alert to retrieve
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Fraud alert object
        
    Raises:
        404: If alert not found
    """
    alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    return alert


@router.patch(
    "/alerts/{alert_id}/status",
    summary="Update alert status",
    description="Admin-only: Update status of a fraud alert"
)
async def update_alert_status(
    alert_id: int,
    new_status: str,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Update fraud alert status.
    
    Only accessible by ADMIN users.
    
    Args:
        alert_id: ID of alert to update
        new_status: New status (OPEN, REVIEWED, RESOLVED)
        current_admin: Current authenticated admin user
        db: Database session
        
    Returns:
        Updated alert object
        
    Raises:
        404: If alert not found
        400: If invalid status
    """
    try:
        status_enum = AlertStatus[new_status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be OPEN, REVIEWED, or RESOLVED"
        )
    
    alert = db.query(FraudAlert).filter(FraudAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert {alert_id} not found"
        )
    
    alert.status = status_enum
    db.commit()
    db.refresh(alert)
    
    logger.info(f"Admin {current_admin.id} updated alert {alert_id} status to {new_status}")
    
    return alert
