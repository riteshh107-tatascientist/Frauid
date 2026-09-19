"""
Pydantic schemas for transaction prediction.

Matches the actual Phase 2 model features:
- Time: seconds since first transaction
- V1-V28: anonymized PCA-transformed features
- Amount: transaction amount in EUR
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field, validator
import numpy as np


class TransactionPredictionRequest(BaseModel):
    """
    Transaction data for fraud prediction.
    
    Features match the Kaggle Credit Card Fraud Detection dataset.
    """
    
    # Temporal feature
    Time: float = Field(..., description="Seconds elapsed since first transaction")
    
    # Anonymized PCA features (V1-V28)
    V1: float = Field(..., description="Anonymized feature V1")
    V2: float = Field(..., description="Anonymized feature V2")
    V3: float = Field(..., description="Anonymized feature V3")
    V4: float = Field(..., description="Anonymized feature V4")
    V5: float = Field(..., description="Anonymized feature V5")
    V6: float = Field(..., description="Anonymized feature V6")
    V7: float = Field(..., description="Anonymized feature V7")
    V8: float = Field(..., description="Anonymized feature V8")
    V9: float = Field(..., description="Anonymized feature V9")
    V10: float = Field(..., description="Anonymized feature V10")
    V11: float = Field(..., description="Anonymized feature V11")
    V12: float = Field(..., description="Anonymized feature V12")
    V13: float = Field(..., description="Anonymized feature V13")
    V14: float = Field(..., description="Anonymized feature V14")
    V15: float = Field(..., description="Anonymized feature V15")
    V16: float = Field(..., description="Anonymized feature V16")
    V17: float = Field(..., description="Anonymized feature V17")
    V18: float = Field(..., description="Anonymized feature V18")
    V19: float = Field(..., description="Anonymized feature V19")
    V20: float = Field(..., description="Anonymized feature V20")
    V21: float = Field(..., description="Anonymized feature V21")
    V22: float = Field(..., description="Anonymized feature V22")
    V23: float = Field(..., description="Anonymized feature V23")
    V24: float = Field(..., description="Anonymized feature V24")
    V25: float = Field(..., description="Anonymized feature V25")
    V26: float = Field(..., description="Anonymized feature V26")
    V27: float = Field(..., description="Anonymized feature V27")
    V28: float = Field(..., description="Anonymized feature V28")
    
    # Transaction amount
    Amount: float = Field(..., ge=0, description="Transaction amount in EUR")
    
    @validator('Time')
    def time_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Time must be non-negative')
        return v
    
    @validator('Amount')
    def amount_must_be_reasonable(cls, v):
        # Amount should be between 0 and reasonable max
        if v > 100000:
            raise ValueError('Amount seems unreasonably high')
        return v
    
    @validator('*', pre=True)
    def validate_numeric(cls, v):
        """Validate that all fields are numeric"""
        try:
            float_v = float(v)
            if not np.isfinite(float_v):
                raise ValueError('Value must be finite (not NaN or Inf)')
            return float_v
        except (TypeError, ValueError) as e:
            raise ValueError(f'Must be a valid number: {str(e)}')
    
    class Config:
        schema_extra = {
            "example": {
                "Time": 3600,
                "V1": -1.35,
                "V2": -0.73,
                "V3": -0.47,
                "V4": 1.03,
                "V5": -0.50,
                "V6": 0.27,
                "V7": -0.12,
                "V8": 0.21,
                "V9": -0.04,
                "V10": 0.46,
                "V11": 0.34,
                "V12": -0.57,
                "V13": 0.15,
                "V14": -0.22,
                "V15": 0.11,
                "V16": 0.09,
                "V17": -0.07,
                "V18": -0.03,
                "V19": 0.12,
                "V20": -0.18,
                "V21": 0.08,
                "V22": -0.09,
                "V23": 0.03,
                "V24": -0.04,
                "V25": 0.13,
                "V26": -0.07,
                "V27": 0.06,
                "V28": 0.08,
                "Amount": 149.62
            }
        }


class PredictionResponse(BaseModel):
    """
    Fraud prediction response.
    
    All values are derived from the actual trained model.
    """
    
    prediction: str = Field(
        ...,
        description="Fraud prediction: LEGITIMATE or FRAUD"
    )
    fraud_probability: float = Field(
        ...,
        ge=0,
        le=1,
        description="Probability of fraud (0-1) from ML model"
    )
    risk_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score (0-100)"
    )
    risk_level: str = Field(
        ...,
        description="Risk level: LOW, MEDIUM, or HIGH"
    )
    model_version: str = Field(
        ...,
        description="Version of the ML model used"
    )
    explanation_available: bool = Field(
        default=False,
        description="Whether SHAP explanations are available (Phase 7)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": "LEGITIMATE",
                "fraud_probability": 0.12,
                "risk_score": 12.0,
                "risk_level": "LOW",
                "model_version": "1.0.0",
                "explanation_available": False
            }
        }


class StoredTransactionResponse(BaseModel):
    """Transaction stored in database"""
    
    id: int = Field(..., description="Transaction ID in database")
    amount: float = Field(..., description="Transaction amount")
    prediction: str = Field(..., description="FRAUD or LEGITIMATE")
    fraud_probability: Optional[float] = Field(..., description="Fraud probability")
    risk_score: Optional[float] = Field(..., description="Risk score")
    risk_level: Optional[str] = Field(..., description="Risk level")
    model_version: Optional[str] = Field(..., description="Model version used")
    created_at: str = Field(..., description="ISO timestamp")
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of transactions with pagination"""
    
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    items: list[StoredTransactionResponse] = Field(..., description="Transactions")


class ModelInfoResponse(BaseModel):
    """Model information endpoint response"""
    
    model_name: str = Field(..., description="Name of the ML model")
    model_version: str = Field(..., description="Version of the model")
    threshold: float = Field(..., description="Classification threshold")
    features: list[str] = Field(..., description="List of feature names")
    feature_count: int = Field(..., description="Number of features")
    metrics: Dict = Field(..., description="Model evaluation metrics")
    dataset: Dict = Field(..., description="Dataset information")
    
    class Config:
        schema_extra = {
            "example": {
                "model_name": "XGBoost",
                "model_version": "1.0.0",
                "threshold": 0.5,
                "features": ["Time", "V1", "V2", "...", "V28", "Amount"],
                "feature_count": 30,
                "metrics": {
                    "accuracy": 0.9992,
                    "precision": 0.8678,
                    "recall": 0.8102,
                    "f1": 0.8383,
                    "roc_auc": 0.9754,
                    "pr_auc": 0.8567
                },
                "dataset": {
                    "name": "Kaggle Credit Card Fraud Detection",
                    "total_samples": 227846,
                    "fraud_percentage": 0.172
                }
            }
        }


class DashboardSummaryResponse(BaseModel):
    """Dashboard summary statistics"""
    
    total_transactions: int = Field(..., ge=0)
    fraud_transactions: int = Field(..., ge=0)
    legitimate_transactions: int = Field(..., ge=0)
    high_risk_transactions: int = Field(..., ge=0)
    medium_risk_transactions: int = Field(..., ge=0)
    low_risk_transactions: int = Field(..., ge=0)
    fraud_percentage: float = Field(..., ge=0, le=100)


class DashboardTrendItem(BaseModel):
    """Single item in risk trend"""
    
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    transactions: int = Field(..., ge=0)
    fraud: int = Field(..., ge=0)
    fraud_percentage: float = Field(..., ge=0, le=100)


class ErrorResponse(BaseModel):
    """Error response"""
    
    detail: str = Field(..., description="Error message")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid transaction input."
            }
        }
