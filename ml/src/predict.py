"""
Prediction Module

Load saved model and make predictions on new transactions.
"""

import joblib
import json
import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class FraudPredictor:
    """Make fraud predictions using trained model"""
    
    def __init__(self, model_path: str, metadata_path: str, preprocessor_path: str):
        """
        Initialize predictor with model artifacts.
        
        Args:
            model_path: Path to saved model
            metadata_path: Path to model metadata JSON
            preprocessor_path: Path to saved preprocessor
        """
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.preprocessor_path = preprocessor_path
        
        self.model = None
        self.metadata = None
        self.preprocessor = None
        self.threshold = None
        
        self.load_artifacts()
    
    def load_artifacts(self):
        """Load model, metadata, and preprocessor"""
        # Load model
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        logger.info(f"Model loaded from {self.model_path}")
        
        # Load metadata
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Metadata not found at {self.metadata_path}")
        
        with open(self.metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        self.threshold = self.metadata.get('threshold', 0.5)
        logger.info(f"Metadata loaded. Threshold: {self.threshold}")
        
        # Load preprocessor
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(f"Preprocessor not found at {self.preprocessor_path}")
        
        self.preprocessor = joblib.load(self.preprocessor_path)
        logger.info(f"Preprocessor loaded from {self.preprocessor_path}")
    
    def get_risk_level(self, fraud_probability: float) -> str:
        """
        Classify risk level based on fraud probability.
        
        Args:
            fraud_probability: Probability of fraud (0-1)
            
        Returns:
            Risk level: 'LOW', 'MEDIUM', or 'HIGH'
        """
        low_threshold = self.metadata.get('risk_thresholds', {}).get('low', 0.3)
        high_threshold = self.metadata.get('risk_thresholds', {}).get('high', 0.7)
        
        if fraud_probability < low_threshold:
            return 'LOW'
        elif fraud_probability < high_threshold:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def predict_single(self, features_dict: Dict) -> Dict:
        """
        Predict fraud probability for a single transaction.
        
        Args:
            features_dict: Dictionary of transaction features
            
        Returns:
            Dictionary with prediction results
        """
        # Convert to DataFrame
        df = pd.DataFrame([features_dict])
        
        # Preprocess
        df_processed = self.preprocessor.transform(df)
        
        # Predict
        fraud_probability = self.model.predict_proba(df_processed)[0][1]
        risk_score = fraud_probability * 100
        risk_level = self.get_risk_level(fraud_probability)
        prediction = 'fraud' if fraud_probability >= self.threshold else 'legitimate'
        
        return {
            'prediction': prediction,
            'fraud_probability': float(fraud_probability),
            'risk_score': float(risk_score),
            'risk_level': risk_level,
            'threshold': self.threshold,
        }
    
    def predict_batch(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict fraud probability for multiple transactions.
        
        Args:
            features_df: DataFrame with transaction features
            
        Returns:
            DataFrame with predictions for each transaction
        """
        # Preprocess
        df_processed = self.preprocessor.transform(features_df)
        
        # Predict
        fraud_probabilities = self.model.predict_proba(df_processed)[:, 1]
        predictions = (fraud_probabilities >= self.threshold).astype(int)
        
        results = pd.DataFrame({
            'fraud_probability': fraud_probabilities,
            'risk_score': fraud_probabilities * 100,
            'prediction': ['fraud' if p >= self.threshold else 'legitimate' for p in fraud_probabilities],
            'risk_level': [self.get_risk_level(p) for p in fraud_probabilities],
        })
        
        return results


class ModelArtifactManager:
    """Save and load model artifacts"""
    
    ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'artifacts')
    
    @staticmethod
    def save_model_artifacts(
        model,
        preprocessor,
        model_name: str,
        model_version: str,
        threshold: float,
        metrics: Dict,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ):
        """
        Save model, preprocessor, and metadata.
        
        Args:
            model: Trained model
            preprocessor: Fitted preprocessor
            model_name: Name of model
            model_version: Version string
            threshold: Classification threshold
            metrics: Evaluation metrics dictionary
            X_train: Training features (for info)
            y_train: Training target (for info)
        """
        # Ensure artifacts directory exists
        os.makedirs(ModelArtifactManager.ARTIFACTS_DIR, exist_ok=True)
        
        # Save model
        model_path = os.path.join(ModelArtifactManager.ARTIFACTS_DIR, 'fraud_model.joblib')
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Save preprocessor
        preprocessor_path = os.path.join(ModelArtifactManager.ARTIFACTS_DIR, 'preprocessor.joblib')
        joblib.dump(preprocessor, preprocessor_path)
        logger.info(f"Preprocessor saved to {preprocessor_path}")
        
        # Create and save metadata
        metadata = {
            'model_name': model_name,
            'model_version': model_version,
            'model_type': type(model).__name__,
            'training_date': datetime.utcnow().isoformat(),
            'threshold': threshold,
            'risk_thresholds': {
                'low': 0.3,
                'high': 0.7,
            },
            'dataset': {
                'name': 'Kaggle Credit Card Fraud Detection',
                'total_samples': len(X_train),
                'fraud_percentage': (y_train == 1).sum() / len(y_train) * 100,
            },
            'metrics': {
                'accuracy': float(metrics.get('accuracy', 0)),
                'precision': float(metrics.get('precision', 0)),
                'recall': float(metrics.get('recall', 0)),
                'f1': float(metrics.get('f1', 0)),
                'roc_auc': float(metrics.get('roc_auc', 0)),
                'pr_auc': float(metrics.get('pr_auc', 0)),
            },
            'confusion_matrix': metrics.get('confusion_matrix', {}),
            'features': list(X_train.columns),
        }
        
        metadata_path = os.path.join(ModelArtifactManager.ARTIFACTS_DIR, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {metadata_path}")
        
        return model_path, preprocessor_path, metadata_path


def main():
    """Test prediction pipeline"""
    from data_loader import DataLoader
    from preprocessing import DataPreprocessor
    
    # Load data
    loader = DataLoader()
    df = loader.load_dataset()
    
    # Preprocess
    preprocessor = DataPreprocessor(random_state=42, test_size=0.2)
    X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(df)
    
    print("\n" + "="*60)
    print("SAMPLE PREDICTION")
    print("="*60)
    
    # Get a sample transaction
    sample_legitimate = X_test[y_test == 0].iloc[0].to_dict()
    sample_fraud = X_test[y_test == 1].iloc[0].to_dict()
    
    print("\nExample Legitimate Transaction:")
    print(f"  Features: {list(sample_legitimate.keys())[:5]}...")
    print(f"  Expected: Legitimate")
    
    print("\nExample Fraudulent Transaction:")
    print(f"  Features: {list(sample_fraud.keys())[:5]}...")
    print(f"  Expected: Fraud")
    
    print("\nNote: Model artifacts must be saved in Phase 2 training step")
    print("      Then predictions can be made in Phase 3 API integration")


if __name__ == "__main__":
    main()
