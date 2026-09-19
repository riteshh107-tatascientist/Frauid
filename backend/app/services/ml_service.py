"""
ML Service for FraudGuard AI

Loads and manages the trained fraud detection model.
Handles preprocessing and predictions.
"""

import json
import joblib
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class MLService:
    """ML Model Service - loads and manages fraud detection model"""
    
    def __init__(self, model_path: str, preprocessor_path: str, metadata_path: str):
        """
        Initialize ML Service.
        
        Args:
            model_path: Path to trained model artifact
            preprocessor_path: Path to fitted preprocessor
            metadata_path: Path to model metadata JSON
        """
        self.model_path = model_path
        self.preprocessor_path = preprocessor_path
        self.metadata_path = metadata_path
        
        self.model = None
        self.preprocessor = None
        self.metadata = None
        self.is_loaded = False
        
        self.load_artifacts()
    
    def load_artifacts(self) -> bool:
        """
        Load model, preprocessor, and metadata from disk.
        
        Returns:
            True if successfully loaded, False otherwise
        """
        try:
            # Load model
            if not os.path.exists(self.model_path):
                logger.error(f"Model not found at {self.model_path}")
                return False
            
            self.model = joblib.load(self.model_path)
            logger.info(f"✓ Model loaded: {self.model_path}")
            
            # Load preprocessor
            if not os.path.exists(self.preprocessor_path):
                logger.error(f"Preprocessor not found at {self.preprocessor_path}")
                return False
            
            self.preprocessor = joblib.load(self.preprocessor_path)
            logger.info(f"✓ Preprocessor loaded: {self.preprocessor_path}")
            
            # Load metadata
            if not os.path.exists(self.metadata_path):
                logger.error(f"Metadata not found at {self.metadata_path}")
                return False
            
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            logger.info(f"✓ Metadata loaded: {self.metadata_path}")
            
            # Validate metadata
            if not self._validate_metadata():
                return False
            
            self.is_loaded = True
            logger.info("✓ ML Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ML artifacts: {str(e)}")
            return False
    
    def _validate_metadata(self) -> bool:
        """Validate metadata structure"""
        required_keys = ['model_name', 'threshold', 'features', 'metrics']
        missing_keys = [k for k in required_keys if k not in self.metadata]
        
        if missing_keys:
            logger.error(f"Metadata missing required keys: {missing_keys}")
            return False
        
        return True
    
    def predict(self, features: Dict[str, float]) -> Tuple[float, str]:
        """
        Make fraud prediction on transaction.
        
        Args:
            features: Dictionary of transaction features
            
        Returns:
            Tuple of (fraud_probability, prediction)
        """
        if not self.is_loaded:
            raise RuntimeError("ML Service not loaded")
        
        try:
            # Convert to DataFrame with correct column order
            df = pd.DataFrame([features])
            
            # Ensure correct feature order matches training
            feature_columns = self.metadata.get('features', list(features.keys()))
            df = df[feature_columns]
            
            # Preprocess
            df_processed = self.preprocessor.transform(df)
            
            # Predict
            fraud_probability = self.model.predict_proba(df_processed)[0][1]
            
            # Validate probability
            if not (0 <= fraud_probability <= 1):
                logger.error(f"Invalid probability: {fraud_probability}")
                raise ValueError("Invalid fraud probability from model")
            
            # Get prediction
            threshold = self.metadata.get('threshold', 0.5)
            prediction = "FRAUD" if fraud_probability >= threshold else "LEGITIMATE"
            
            return float(fraud_probability), prediction
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict:
        """
        Get model information from metadata.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_loaded:
            raise RuntimeError("ML Service not loaded")
        
        return {
            'model_name': self.metadata.get('model_name', 'Unknown'),
            'model_version': self.metadata.get('model_version', '1.0.0'),
            'threshold': self.metadata.get('threshold', 0.5),
            'features': self.metadata.get('features', []),
            'feature_count': len(self.metadata.get('features', [])),
            'metrics': self.metadata.get('metrics', {}),
            'dataset': self.metadata.get('dataset', {}),
        }
    
    def get_feature_names(self) -> list:
        """Get list of expected feature names"""
        if not self.is_loaded:
            raise RuntimeError("ML Service not loaded")
        
        return self.metadata.get('features', [])
    
    def validate_features(self, features: Dict[str, float]) -> Tuple[bool, Optional[str]]:
        """
        Validate input features.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.is_loaded:
            return False, "ML Service not loaded"
        
        expected_features = set(self.get_feature_names())
        provided_features = set(features.keys())
        
        # Check for missing features
        missing = expected_features - provided_features
        if missing:
            return False, f"Missing required features: {missing}"
        
        # Check for extra features
        extra = provided_features - expected_features
        if extra:
            return False, f"Unexpected features: {extra}"
        
        # Validate feature values
        for feature, value in features.items():
            if not isinstance(value, (int, float)):
                return False, f"Feature '{feature}' must be numeric, got {type(value).__name__}"
            
            if not np.isfinite(value):
                return False, f"Feature '{feature}' must be finite (not NaN or Inf)"
        
        return True, None
    
    def get_status(self) -> Dict:
        """Get service status"""
        return {
            'status': 'healthy' if self.is_loaded else 'unavailable',
            'model_loaded': self.is_loaded,
            'model_name': self.metadata.get('model_name', 'Unknown') if self.is_loaded else None,
            'model_version': self.metadata.get('model_version', '1.0.0') if self.is_loaded else None,
        }


# Global ML Service instance
_ml_service: Optional[MLService] = None


def get_ml_service() -> MLService:
    """Get global ML Service instance"""
    if _ml_service is None:
        raise RuntimeError("ML Service not initialized")
    return _ml_service


def initialize_ml_service(model_path: str, preprocessor_path: str, metadata_path: str) -> bool:
    """
    Initialize global ML Service.
    
    Args:
        model_path: Path to trained model
        preprocessor_path: Path to preprocessor
        metadata_path: Path to metadata
        
    Returns:
        True if successfully initialized
    """
    global _ml_service
    _ml_service = MLService(model_path, preprocessor_path, metadata_path)
    return _ml_service.is_loaded
