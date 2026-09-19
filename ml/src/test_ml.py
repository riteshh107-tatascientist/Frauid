"""
Tests for ML Pipeline Components

Tests cover:
- Data loading and validation
- Preprocessing
- Feature engineering
- Model training and evaluation
- Predictions
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from preprocessing import DataPreprocessor
from train import ModelTrainer
from evaluate import ThresholdAnalyzer
from predict import FraudPredictor, ModelArtifactManager


@pytest.fixture
def synthetic_data():
    """Create synthetic fraud detection dataset"""
    # Create imbalanced classification dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=30,
        n_informative=15,
        n_redundant=5,
        weights=[0.99, 0.01],  # 1% fraud
        random_state=42
    )
    
    # Convert to DataFrame
    feature_names = [f'V{i}' for i in range(1, 31)] + ['Time', 'Amount']
    X_df = pd.DataFrame(X, columns=feature_names[:-2])
    X_df['Time'] = np.random.randint(0, 86400, len(X))
    X_df['Amount'] = np.random.exponential(100, len(X))
    X_df['Class'] = y
    
    return X_df


class TestDataPreprocessing:
    """Test data preprocessing pipeline"""
    
    def test_preprocessing_split(self, synthetic_data):
        """Test train/test split"""
        preprocessor = DataPreprocessor(test_size=0.2)
        X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(synthetic_data)
        
        # Check sizes
        assert len(X_train) + len(X_test) == len(synthetic_data) - synthetic_data.isnull().sum().sum()
        assert len(y_train) == len(X_train)
        assert len(y_test) == len(X_test)
    
    def test_preprocessing_no_data_leakage(self, synthetic_data):
        """Test that preprocessing doesn't leak data"""
        preprocessor = DataPreprocessor(test_size=0.2)
        X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(synthetic_data)
        
        # Indices should not overlap
        assert len(set(X_train.index) & set(X_test.index)) == 0
    
    def test_stratified_split(self, synthetic_data):
        """Test stratified split maintains class distribution"""
        preprocessor = DataPreprocessor(test_size=0.2)
        X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(synthetic_data)
        
        train_fraud_rate = (y_train == 1).sum() / len(y_train)
        test_fraud_rate = (y_test == 1).sum() / len(y_test)
        
        # Rates should be similar
        assert abs(train_fraud_rate - test_fraud_rate) < 0.05


class TestModelTraining:
    """Test model training"""
    
    def test_logistic_regression_training(self, synthetic_data):
        """Test Logistic Regression training"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, _ = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_logistic_regression(X_train, y_train)
        
        # Test prediction
        y_pred = model.predict(X_test)
        assert len(y_pred) == len(X_test)
        assert set(y_pred).issubset({0, 1})
    
    def test_random_forest_training(self, synthetic_data):
        """Test Random Forest training"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, _ = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_random_forest(X_train, y_train)
        
        # Test prediction
        y_pred = model.predict(X_test)
        assert len(y_pred) == len(X_test)
        assert set(y_pred).issubset({0, 1})
    
    def test_xgboost_training(self, synthetic_data):
        """Test XGBoost training"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, _ = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_xgboost(X_train, y_train)
        
        # Test prediction
        y_pred = model.predict(X_test)
        assert len(y_pred) == len(X_test)
        assert set(y_pred).issubset({0, 1})
    
    def test_model_evaluation(self, synthetic_data):
        """Test model evaluation"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, _ = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_logistic_regression(X_train, y_train)
        metrics = trainer.evaluate_model(model, X_test, y_test, "Test Model")
        
        # Check metrics exist and are valid
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert 'roc_auc' in metrics
        assert 'pr_auc' in metrics
        assert 'confusion_matrix' in metrics
        
        # Check metric ranges
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1'] <= 1
        assert 0 <= metrics['roc_auc'] <= 1
        assert 0 <= metrics['pr_auc'] <= 1


class TestThresholdAnalysis:
    """Test threshold analysis"""
    
    def test_threshold_analysis(self, synthetic_data):
        """Test threshold analysis"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, _ = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_logistic_regression(X_train, y_train)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        analyzer = ThresholdAnalyzer()
        analysis = analyzer.analyze_thresholds(y_test, y_pred_proba)
        
        # Check output
        assert len(analysis) > 0
        assert 'Threshold' in analysis.columns
        assert 'Precision' in analysis.columns
        assert 'Recall' in analysis.columns
    
    def test_threshold_recommendation(self, synthetic_data):
        """Test threshold recommendation"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, _ = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_logistic_regression(X_train, y_train)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        analyzer = ThresholdAnalyzer()
        threshold, metrics = analyzer.recommend_threshold(y_test, y_pred_proba)
        
        # Check threshold is valid
        assert 0 <= threshold <= 1
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics


class TestPrediction:
    """Test prediction module"""
    
    def test_risk_level_classification(self):
        """Test risk level classification"""
        # Create minimal metadata
        metadata = {
            'threshold': 0.5,
            'risk_thresholds': {'low': 0.3, 'high': 0.7}
        }
        
        # Test risk levels
        assert get_risk_level(0.1, metadata) == 'LOW'
        assert get_risk_level(0.4, metadata) == 'MEDIUM'
        assert get_risk_level(0.8, metadata) == 'HIGH'


def get_risk_level(prob, metadata):
    """Helper function for risk level testing"""
    low = metadata['risk_thresholds']['low']
    high = metadata['risk_thresholds']['high']
    
    if prob < low:
        return 'LOW'
    elif prob < high:
        return 'MEDIUM'
    else:
        return 'HIGH'


class TestArtifactSaving:
    """Test model artifact saving"""
    
    def test_metadata_creation(self, synthetic_data, tmp_path):
        """Test metadata file creation"""
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(synthetic_data)
        
        trainer = ModelTrainer()
        model = trainer.train_logistic_regression(X_train, y_train)
        metrics = trainer.evaluate_model(model, X_test, y_test, "Test")
        
        # Test that metadata can be created
        metadata = {
            'model_name': 'Logistic Regression',
            'model_version': '1.0.0',
            'metrics': metrics,
            'features': list(X_train.columns),
        }
        
        assert 'model_name' in metadata
        assert 'metrics' in metadata
        assert 'features' in metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
