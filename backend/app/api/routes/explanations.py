"""
Explanation API Routes

Endpoints for generating SHAP-based explanations of fraud predictions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from app.api.dependencies import get_current_user
from app.models.models import User, Transaction
from app.core.database import get_db
from app.services.ml_service import get_ml_service
from app.services.explainability_service import get_explainability_service
from app.schemas.explanation import (
    ExplanationResponse, 
    TransactionExplanationResponse,
    ExplanationErrorResponse
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["explanations"])


@router.get(
    "/transactions/{transaction_id}/explanation",
    response_model=TransactionExplanationResponse,
    summary="Get SHAP explanation for a transaction",
    description="Returns SHAP-based explanation showing which features contributed to the fraud prediction"
)
async def get_transaction_explanation(
    transaction_id: int,
    top_n: int = Query(10, ge=1, le=20, description="Number of top features to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get SHAP explanation for a transaction's fraud prediction.
    
    Users can only view their own transactions.
    Admins can view any transaction.
    
    Args:
        transaction_id: ID of transaction
        top_n: Number of top contributing features (1-20)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        TransactionExplanationResponse with SHAP explanation
        
    Raises:
        404: Transaction not found or unauthorized
        503: Explainability service unavailable
    """
    try:
        # Get transaction
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Check authorization (user owns transaction or is admin)
        if transaction.user_id != current_user.id and current_user.role.value != "ADMIN":
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Get explainability service
        explainability_service = get_explainability_service()
        if not explainability_service or not explainability_service.is_available():
            raise HTTPException(
                status_code=503, 
                detail="Model explanation service is temporarily unavailable"
            )
        
        # Reconstruct features from transaction
        ml_service = get_ml_service()
        feature_names = ml_service.get_feature_names()
        
        features_dict = {}
        for feature in feature_names:
            # Get feature value from transaction stored features
            # Assuming transaction has these fields or we need to reconstruct
            feature_value = getattr(transaction, feature, None)
            if feature_value is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Feature '{feature}' not found in transaction"
                )
            features_dict[feature] = float(feature_value)
        
        # Generate explanation
        explanation = explainability_service.explain(features_dict, top_n=top_n)
        
        return TransactionExplanationResponse(
            transaction_id=transaction_id,
            prediction=explanation['prediction'],
            fraud_probability=explanation['fraud_probability'],
            risk_level=explanation['risk_level'],
            model_version=explanation['model_version'],
            base_value=explanation['base_value'],
            feature_count=explanation['feature_count'],
            top_features=explanation['top_features'],
            explainer_type=explanation['explainer_type'],
            shap_note=explanation['shap_note'],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate explanation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate model explanation"
        )


@router.post(
    "/transactions/explain",
    response_model=ExplanationResponse,
    summary="Explain a fraud prediction",
    description="Generate SHAP explanation for provided transaction features"
)
async def explain_prediction(
    prediction_request,  # Use PredictionRequest from prediction schema
    top_n: int = Query(10, ge=1, le=20, description="Number of top features to return"),
    current_user: User = Depends(get_current_user),
):
    """
    Generate SHAP explanation for a fraud prediction.
    
    This endpoint accepts transaction features and generates an explanation
    for the fraud prediction without storing the transaction.
    
    Args:
        prediction_request: PredictionRequest with transaction features
        top_n: Number of top features (1-20)
        current_user: Authenticated user
        
    Returns:
        ExplanationResponse with SHAP analysis
        
    Raises:
        503: Explainability service unavailable
    """
    try:
        # Get services
        ml_service = get_ml_service()
        explainability_service = get_explainability_service()
        
        if not explainability_service or not explainability_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Model explanation service is temporarily unavailable"
            )
        
        # Validate features
        is_valid, error_msg = ml_service.validate_features(prediction_request.dict())
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate explanation
        explanation = explainability_service.explain(
            prediction_request.dict(),
            top_n=top_n
        )
        
        return ExplanationResponse(**explanation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate explanation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate model explanation"
        )


@router.get(
    "/health/explainer",
    summary="Check explainability service health",
    description="Returns status of SHAP explainability service"
)
async def check_explainer_health():
    """
    Check if explainability service is available.
    
    Returns:
        Dictionary with health status
    """
    try:
        explainability_service = get_explainability_service()
        is_available = explainability_service is not None and explainability_service.is_available()
        
        return {
            "status": "healthy" if is_available else "unavailable",
            "explainability_available": is_available,
            "service": "SHAP Explainer"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "error",
            "explainability_available": False,
            "service": "SHAP Explainer"
        }
