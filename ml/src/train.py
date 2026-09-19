"""
Model Training: Logistic Regression, Random Forest, XGBoost

This script trains three models and compares their performance.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, 
    average_precision_score, confusion_matrix, accuracy_score
)
import json
import joblib
import logging
from datetime import datetime
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ModelTrainer:
    """Train and evaluate fraud detection models"""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize trainer.
        
        Args:
            random_state: Seed for reproducibility
        """
        self.random_state = random_state
        self.models = {}
        self.results = {}
    
    def train_logistic_regression(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series
    ) -> LogisticRegression:
        """
        Train Logistic Regression model.
        
        Uses class_weight='balanced' to handle class imbalance.
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            Trained model
        """
        logger.info("Training Logistic Regression...")
        
        model = LogisticRegression(
            random_state=self.random_state,
            class_weight='balanced',  # Handle class imbalance
            max_iter=1000,
            solver='lbfgs'
        )
        
        model.fit(X_train, y_train)
        logger.info("Logistic Regression training complete")
        
        return model
    
    def train_random_forest(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series
    ) -> RandomForestClassifier:
        """
        Train Random Forest model.
        
        Uses class_weight='balanced' for imbalanced data.
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            Trained model
        """
        logger.info("Training Random Forest...")
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=self.random_state,
            class_weight='balanced',  # Handle class imbalance
            n_jobs=-1,
            verbose=1
        )
        
        model.fit(X_train, y_train)
        logger.info("Random Forest training complete")
        
        return model
    
    def train_xgboost(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series
    ) -> XGBClassifier:
        """
        Train XGBoost model.
        
        XGBoost handles class imbalance through scale_pos_weight.
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            Trained model
        """
        logger.info("Training XGBoost...")
        
        # Calculate scale_pos_weight to handle imbalance
        scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
        
        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=self.random_state,
            verbosity=1,
            use_label_encoder=False,
            eval_metric='aucpr'  # Use PR-AUC for imbalanced data
        )
        
        model.fit(X_train, y_train)
        logger.info("XGBoost training complete")
        
        return model
    
    def evaluate_model(
        self, 
        model,
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        model_name: str
    ) -> Dict:
        """
        Evaluate model on test set.
        
        Calculates comprehensive metrics for fraud detection.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
            model_name: Name of model
            
        Returns:
            Dictionary of metrics
        """
        logger.info(f"Evaluating {model_name}...")
        
        # Get predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'model': model_name,
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'pr_auc': average_precision_score(y_test, y_pred_proba),
        }
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        metrics['confusion_matrix'] = {
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
        }
        
        # Log metrics
        logger.info(f"\n{model_name} Metrics:")
        logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall: {metrics['recall']:.4f}")
        logger.info(f"  F1: {metrics['f1']:.4f}")
        logger.info(f"  ROC-AUC: {metrics['roc_auc']:.4f}")
        logger.info(f"  PR-AUC: {metrics['pr_auc']:.4f}")
        logger.info(f"  TP: {tp}, FP: {fp}, FN: {fn}, TN: {tn}")
        
        return metrics
    
    def train_all_models(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Tuple[Dict, Dict]:
        """
        Train and evaluate all models.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_test: Test features
            y_test: Test target
            
        Returns:
            Tuple of (trained_models dict, results dict)
        """
        logger.info("Starting model training and evaluation...")
        logger.info(f"Training set size: {len(X_train)}")
        logger.info(f"Test set size: {len(X_test)}")
        logger.info(f"Features: {X_train.shape[1]}")
        
        # Train Logistic Regression
        lr_model = self.train_logistic_regression(X_train, y_train)
        self.models['Logistic Regression'] = lr_model
        self.results['Logistic Regression'] = self.evaluate_model(
            lr_model, X_test, y_test, 'Logistic Regression'
        )
        
        # Train Random Forest
        rf_model = self.train_random_forest(X_train, y_train)
        self.models['Random Forest'] = rf_model
        self.results['Random Forest'] = self.evaluate_model(
            rf_model, X_test, y_test, 'Random Forest'
        )
        
        # Train XGBoost
        xgb_model = self.train_xgboost(X_train, y_train)
        self.models['XGBoost'] = xgb_model
        self.results['XGBoost'] = self.evaluate_model(
            xgb_model, X_test, y_test, 'XGBoost'
        )
        
        return self.models, self.results
    
    def compare_models(self) -> pd.DataFrame:
        """
        Create comparison table of all models.
        
        Returns:
            DataFrame with model comparison
        """
        comparison_data = []
        
        for model_name, metrics in self.results.items():
            comparison_data.append({
                'Model': model_name,
                'Accuracy': f"{metrics['accuracy']:.4f}",
                'Precision': f"{metrics['precision']:.4f}",
                'Recall': f"{metrics['recall']:.4f}",
                'F1': f"{metrics['f1']:.4f}",
                'ROC-AUC': f"{metrics['roc_auc']:.4f}",
                'PR-AUC': f"{metrics['pr_auc']:.4f}",
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        return comparison_df


def main():
    """Train all models"""
    from data_loader import DataLoader
    from preprocessing import DataPreprocessor
    
    # Load and preprocess data
    print("\n" + "="*60)
    print("LOADING DATA")
    print("="*60)
    
    loader = DataLoader()
    df = loader.load_dataset()
    
    print("\n" + "="*60)
    print("PREPROCESSING DATA")
    print("="*60)
    
    preprocessor = DataPreprocessor(random_state=42, test_size=0.2)
    X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(df)
    
    # Train models
    print("\n" + "="*60)
    print("TRAINING MODELS")
    print("="*60)
    
    trainer = ModelTrainer(random_state=42)
    models, results = trainer.train_all_models(X_train, y_train, X_test, y_test)
    
    # Compare models
    print("\n" + "="*60)
    print("MODEL COMPARISON")
    print("="*60)
    print("\n" + str(trainer.compare_models().to_string(index=False)))
    
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    
    print("\nWhy accuracy is misleading in fraud detection:")
    print("  - With 0.17% fraud rate, a model predicting all legitimate gets 99.83% accuracy")
    print("  - But it misses 100% of actual fraud (recall = 0%)")
    print("  - Focus on Precision, Recall, F1, ROC-AUC, and PR-AUC instead")
    
    print("\nKey metrics for fraud detection:")
    print("  - Recall: What % of fraud do we catch? (minimize false negatives)")
    print("  - Precision: Of flagged transactions, how many are really fraud? (minimize false positives)")
    print("  - F1: Balance between precision and recall")
    print("  - PR-AUC: Best for imbalanced data (fraud detection)")


if __name__ == "__main__":
    main()
