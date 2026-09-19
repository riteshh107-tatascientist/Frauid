"""
SHAP Explanation Schemas

Pydantic models for explanation API responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class FeatureContributionResponse(BaseModel):
    """Single feature contribution in SHAP explanation"""
    
    feature: str = Field(..., description="Feature name")
    feature_value: float = Field(..., description="Actual feature value in the transaction")
    shap_value: float = Field(..., description="SHAP contribution value")
    direction: str = Field(
        ..., 
        description="Direction of contribution: toward_fraud or toward_legitimate"
    )
    impact: str = Field(
        ..., 
        description="Impact level: high, medium, or low"
    )
    abs_contribution: float = Field(
        ..., 
        description="Absolute SHAP value (for magnitude ranking)"
    )


class ExplanationResponse(BaseModel):
    """
    SHAP-based explanation for a fraud prediction.
    
    Explains which features contributed to the model's decision.
    """
    
    prediction: str = Field(
        ..., 
        description="Model prediction: FRAUD or LEGITIMATE"
    )
    fraud_probability: float = Field(
        ..., 
        description="Fraud probability (0-1)"
    )
    risk_level: str = Field(
        ..., 
        description="Risk level: LOW, MEDIUM, or HIGH"
    )
    model_version: str = Field(
        ..., 
        description="Model version string"
    )
    base_value: float = Field(
        ..., 
        description="Base value (expected model output)"
    )
    feature_count: int = Field(
        ..., 
        description="Total number of features analyzed"
    )
    top_features: List[FeatureContributionResponse] = Field(
        ..., 
        description="Top contributing features"
    )
    explainer_type: str = Field(
        ..., 
        description="Type of SHAP explainer used (e.g., TreeExplainer)"
    )
    shap_note: str = Field(
        ..., 
        description="Important note about feature interpretation"
    )
    mathematical_note: str = Field(
        ..., 
        description="Note about SHAP mathematical properties"
    )


class TransactionExplanationResponse(BaseModel):
    """
    Complete explanation for a transaction with prediction and explanation.
    """
    
    transaction_id: int = Field(..., description="Transaction ID")
    prediction: str = Field(..., description="Fraud prediction")
    fraud_probability: float = Field(..., description="Fraud probability")
    risk_level: str = Field(..., description="Risk level")
    model_version: str = Field(..., description="Model version")
    
    # SHAP explanation
    base_value: float = Field(..., description="SHAP base value")
    feature_count: int = Field(..., description="Number of features")
    top_features: List[FeatureContributionResponse] = Field(
        ..., 
        description="Top contributing features"
    )
    
    # Metadata
    explainer_type: str = Field(..., description="SHAP explainer type")
    shap_note: str = Field(..., description="Feature interpretation note")


class ExplanationErrorResponse(BaseModel):
    """Error response for explanation requests"""
    
    detail: str = Field(..., description="Error message")
    error_type: str = Field(
        default="explanation_error", 
        description="Error type identifier"
    )
