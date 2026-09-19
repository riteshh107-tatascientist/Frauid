"""
Risk Engine for FraudGuard AI

Classifies fraud risk based on model probability and configured thresholds.
Centralizes risk logic.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class RiskEngine:
    """Risk classification engine"""
    
    def __init__(
        self,
        low_threshold: float = 0.3,
        high_threshold: float = 0.7,
        prediction_threshold: float = 0.5
    ):
        """
        Initialize risk engine.
        
        Args:
            low_threshold: Probability below this is LOW risk
            high_threshold: Probability above this is HIGH risk
            prediction_threshold: Probability above this predicts FRAUD
        """
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.prediction_threshold = prediction_threshold
        
        # Validate thresholds
        if not (0 <= low_threshold <= 1):
            raise ValueError("low_threshold must be between 0 and 1")
        if not (0 <= high_threshold <= 1):
            raise ValueError("high_threshold must be between 0 and 1")
        if not (0 <= prediction_threshold <= 1):
            raise ValueError("prediction_threshold must be between 0 and 1")
        if low_threshold >= high_threshold:
            raise ValueError("low_threshold must be less than high_threshold")
    
    def get_risk_level(self, fraud_probability: float) -> str:
        """
        Classify risk level based on fraud probability.
        
        Args:
            fraud_probability: Probability from ML model (0-1)
            
        Returns:
            Risk level: 'LOW', 'MEDIUM', or 'HIGH'
        """
        if fraud_probability < self.low_threshold:
            return "LOW"
        elif fraud_probability < self.high_threshold:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def get_prediction(self, fraud_probability: float) -> str:
        """
        Get fraud prediction.
        
        Args:
            fraud_probability: Probability from ML model (0-1)
            
        Returns:
            Prediction: 'FRAUD' or 'LEGITIMATE'
        """
        return "FRAUD" if fraud_probability >= self.prediction_threshold else "LEGITIMATE"
    
    def classify(self, fraud_probability: float) -> Dict[str, object]:
        """
        Complete risk classification.
        
        Args:
            fraud_probability: Probability from ML model (0-1)
            
        Returns:
            Dictionary with risk_score, risk_level, prediction
        """
        if not (0 <= fraud_probability <= 1):
            raise ValueError("Fraud probability must be between 0 and 1")
        
        risk_score = fraud_probability * 100  # Scale to 0-100
        risk_level = self.get_risk_level(fraud_probability)
        prediction = self.get_prediction(fraud_probability)
        
        return {
            'risk_score': float(risk_score),
            'risk_level': risk_level,
            'prediction': prediction,
        }
    
    def get_config(self) -> Dict:
        """Get risk engine configuration"""
        return {
            'low_threshold': self.low_threshold,
            'high_threshold': self.high_threshold,
            'prediction_threshold': self.prediction_threshold,
        }


# Global risk engine instance
_risk_engine: RiskEngine = None


def get_risk_engine() -> RiskEngine:
    """Get global risk engine instance"""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine


def initialize_risk_engine(
    low_threshold: float = 0.3,
    high_threshold: float = 0.7,
    prediction_threshold: float = 0.5
) -> RiskEngine:
    """Initialize global risk engine"""
    global _risk_engine
    _risk_engine = RiskEngine(
        low_threshold=low_threshold,
        high_threshold=high_threshold,
        prediction_threshold=prediction_threshold
    )
    return _risk_engine
