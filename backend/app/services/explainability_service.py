"""
SHAP Explainability Service

Provides model interpretability using SHAP (SHapley Additive exPlanations).
Explains which features contributed to fraud predictions.

Key Components:
- SHAP explainer initialization
- SHAP value calculation
- Feature contribution ranking
- Direction analysis (toward fraud vs legitimate)
"""

import shap
import numpy as np
import pandas as pd
import logging
import os
import pickle
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FeatureContribution:
    """Represents a feature's contribution to the prediction"""
    feature: str
    feature_value: float
    shap_value: float
    base_value: float
    direction: str  # "toward_fraud" or "toward_legitimate"
    impact: str  # "high", "medium", "low"
    abs_contribution: float  # Absolute SHAP value for ranking


class SHAPExplainer:
    """
    SHAP-based model explainer for fraud predictions.
    
    Uses TreeExplainer for tree-based models (XGBoost, Random Forest).
    Provides per-transaction explanations.
    """
    
    def __init__(self, model, preprocessor, metadata: Dict, max_samples: int = 100):
        """
        Initialize SHAP explainer.
        
        Args:
            model: Trained model (XGBoost, Random Forest, etc.)
            preprocessor: Fitted preprocessing pipeline
            metadata: Model metadata dict with features list
            max_samples: Number of samples to use for SHAP background (for performance)
        """
        self.model = model
        self.preprocessor = preprocessor
        self.metadata = metadata
        self.max_samples = max_samples
        
        self.explainer = None
        self.background_data = None
        self.feature_names = metadata.get('features', [])
        
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """
        Initialize the appropriate SHAP explainer based on model type.
        
        Supports:
        - XGBoost models → TreeExplainer
        - Random Forest models → TreeExplainer
        - Linear models → LinearExplainer (future)
        """
        try:
            model_type = type(self.model).__name__
            logger.info(f"Initializing SHAP explainer for model type: {model_type}")
            
            # Use TreeExplainer for tree-based models
            if model_type in ['XGBClassifier', 'RandomForestClassifier', 'DecisionTreeClassifier']:
                logger.info("Using TreeExplainer for tree-based model")
                self.explainer = shap.TreeExplainer(self.model)
            elif model_type == 'LogisticRegression':
                logger.info("Using LinearExplainer for Logistic Regression")
                # For Linear models, use a simpler approach
                self.explainer = shap.LinearExplainer(self.model)
            else:
                logger.warning(f"Unsupported model type {model_type}, using generic Explainer")
                self.explainer = shap.Explainer(self.model)
            
            logger.info("✓ SHAP explainer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SHAP explainer: {str(e)}")
            raise
    
    def explain_prediction(
        self, 
        features_dict: Dict[str, float],
        top_n: int = 10
    ) -> Dict:
        """
        Generate SHAP explanation for a single prediction.
        
        Args:
            features_dict: Dictionary of transaction features
            top_n: Number of top contributing features to return (1-20)
            
        Returns:
            Dictionary with explanation data
        """
        if self.explainer is None:
            raise RuntimeError("SHAP explainer not initialized")
        
        # Validate top_n
        top_n = max(1, min(20, top_n))  # Bounded 1-20
        
        try:
            # Convert to DataFrame with correct column order
            df = pd.DataFrame([features_dict])
            feature_columns = self.metadata.get('features', list(features_dict.keys()))
            df = df[feature_columns]
            
            # Preprocess
            df_processed = self.preprocessor.transform(df)
            
            # Get model prediction
            fraud_probability = self.model.predict_proba(df_processed)[0][1]
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(df_processed)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # For binary classification, take positive class (fraud)
                shap_array = shap_values[1]
            else:
                shap_array = shap_values
            
            # Ensure correct shape
            if shap_array.ndim == 2:
                shap_row = shap_array[0]
            else:
                shap_row = shap_array
            
            # Get base value
            if isinstance(self.explainer.expected_value, list):
                base_value = self.explainer.expected_value[1]
            else:
                base_value = self.explainer.expected_value
            
            # Build feature contributions
            contributions = self._build_contributions(
                features_dict, 
                shap_row, 
                base_value,
                feature_columns
            )
            
            # Sort by absolute contribution
            contributions.sort(key=lambda x: x.abs_contribution, reverse=True)
            
            # Return top N
            top_features = contributions[:top_n]
            
            return {
                'prediction': self._classify_prediction(fraud_probability),
                'fraud_probability': float(fraud_probability),
                'risk_level': self._get_risk_level(fraud_probability),
                'model_version': self.metadata.get('model_version', '1.0.0'),
                'base_value': float(base_value),
                'feature_count': len(contributions),
                'top_features': [
                    {
                        'feature': fc.feature,
                        'feature_value': float(fc.feature_value),
                        'shap_value': float(fc.shap_value),
                        'direction': fc.direction,
                        'impact': fc.impact,
                        'abs_contribution': float(fc.abs_contribution),
                    }
                    for fc in top_features
                ],
                'explainer_type': type(self.explainer).__name__,
                'shap_note': 'Features are anonymized (PCA-transformed). V1-V28 do not have direct business interpretation.',
                'mathematical_note': f'base_value ({float(base_value):.4f}) + sum(SHAP contributions) ≈ model_output',
            }
            
        except Exception as e:
            logger.error(f"SHAP explanation failed: {str(e)}")
            raise
    
    def _build_contributions(
        self,
        features_dict: Dict[str, float],
        shap_values: np.ndarray,
        base_value: float,
        feature_names: List[str]
    ) -> List[FeatureContribution]:
        """
        Build feature contribution objects from SHAP values.
        
        Args:
            features_dict: Original feature values
            shap_values: SHAP values array
            base_value: Base value / expected model output
            feature_names: List of feature names
            
        Returns:
            List of FeatureContribution objects
        """
        contributions = []
        
        # Get max absolute contribution for impact calculation
        max_abs_shap = np.max(np.abs(shap_values))
        
        for i, feature_name in enumerate(feature_names):
            if i >= len(shap_values):
                continue
            
            shap_value = float(shap_values[i])
            feature_value = float(features_dict.get(feature_name, 0))
            abs_contribution = float(np.abs(shap_value))
            
            # Determine direction
            # Positive SHAP = contributes to fraud prediction (class 1)
            # Negative SHAP = contributes to legitimate prediction (class 0)
            direction = "toward_fraud" if shap_value > 0 else "toward_legitimate"
            
            # Determine impact level based on contribution
            if max_abs_shap > 0:
                impact_ratio = abs_contribution / max_abs_shap
                if impact_ratio >= 0.7:
                    impact = "high"
                elif impact_ratio >= 0.3:
                    impact = "medium"
                else:
                    impact = "low"
            else:
                impact = "low"
            
            contribution = FeatureContribution(
                feature=feature_name,
                feature_value=feature_value,
                shap_value=shap_value,
                base_value=base_value,
                direction=direction,
                impact=impact,
                abs_contribution=abs_contribution,
            )
            
            contributions.append(contribution)
        
        return contributions
    
    def _classify_prediction(self, fraud_probability: float) -> str:
        """Classify prediction as FRAUD or LEGITIMATE"""
        threshold = self.metadata.get('threshold', 0.5)
        return "FRAUD" if fraud_probability >= threshold else "LEGITIMATE"
    
    def _get_risk_level(self, fraud_probability: float) -> str:
        """Get risk level (LOW, MEDIUM, HIGH)"""
        if fraud_probability < 0.3:
            return "LOW"
        elif fraud_probability < 0.7:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def generate_summary(self, explanation: Dict) -> str:
        """
        Generate a natural-language summary of the explanation.
        
        Args:
            explanation: Explanation dict from explain_prediction
            
        Returns:
            Natural-language summary string
        """
        top_features = explanation.get('top_features', [])
        if not top_features:
            return "No features available for explanation."
        
        fraud_features = [f for f in top_features if f['direction'] == 'toward_fraud']
        legit_features = [f for f in top_features if f['direction'] == 'toward_legitimate']
        
        summary = f"The model's prediction was influenced by {len(top_features)} key features. "
        
        if fraud_features:
            fraud_names = [f['feature'] for f in fraud_features[:3]]
            summary += f"Features contributing toward fraud: {', '.join(fraud_names)}. "
        
        if legit_features:
            legit_names = [f['feature'] for f in legit_features[:3]]
            summary += f"Features contributing toward legitimate classification: {', '.join(legit_names)}. "
        
        summary += "Note: Features are anonymized PCA components (V1-V28) without direct business interpretation."
        
        return summary


class ExplainabilityService:
    """
    High-level service for model explainability.
    Manages SHAP explainer and provides explanation API.
    """
    
    _instance: Optional['ExplainabilityService'] = None
    
    def __init__(self, model, preprocessor, metadata: Dict):
        """
        Initialize explainability service.
        
        Args:
            model: Trained model
            preprocessor: Fitted preprocessor
            metadata: Model metadata
        """
        self.model = model
        self.preprocessor = preprocessor
        self.metadata = metadata
        self.explainer: Optional[SHAPExplainer] = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize SHAP explainer"""
        try:
            self.explainer = SHAPExplainer(
                self.model,
                self.preprocessor,
                self.metadata,
                max_samples=100
            )
            logger.info("✓ Explainability service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize explainability service: {str(e)}")
            self.explainer = None
    
    def is_available(self) -> bool:
        """Check if explainability is available"""
        return self.explainer is not None
    
    def explain(
        self,
        features_dict: Dict[str, float],
        top_n: int = 10
    ) -> Dict:
        """
        Get explanation for a prediction.
        
        Args:
            features_dict: Transaction features
            top_n: Number of top features to return
            
        Returns:
            Explanation dictionary
        """
        if not self.is_available():
            raise RuntimeError("Explainability service not available")
        
        return self.explainer.explain_prediction(features_dict, top_n)
    
    def get_summary(self, explanation: Dict) -> str:
        """Get natural-language summary"""
        if not self.is_available():
            return "Explanation not available"
        
        return self.explainer.generate_summary(explanation)
    
    @classmethod
    def get_instance(cls) -> Optional['ExplainabilityService']:
        """Get singleton instance"""
        return cls._instance
    
    @classmethod
    def initialize(cls, model, preprocessor, metadata: Dict) -> 'ExplainabilityService':
        """
        Initialize global explainability service.
        
        Args:
            model: Trained model
            preprocessor: Preprocessor
            metadata: Model metadata
            
        Returns:
            ExplainabilityService instance
        """
        cls._instance = cls(model, preprocessor, metadata)
        return cls._instance


def get_explainability_service() -> Optional[ExplainabilityService]:
    """Get global explainability service instance"""
    return ExplainabilityService.get_instance()
