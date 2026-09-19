"""
Model Evaluation and Threshold Analysis

Analyzes different classification thresholds to find optimal operating point
for fraud detection based on business requirements.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_curve, roc_curve, auc
import logging
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)


class ThresholdAnalyzer:
    """Analyze classification thresholds for fraud detection"""
    
    @staticmethod
    def analyze_thresholds(
        y_true,
        y_pred_proba,
        thresholds: List[float] = None
    ) -> pd.DataFrame:
        """
        Analyze model performance at different thresholds.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            thresholds: List of thresholds to test
            
        Returns:
            DataFrame with metrics at each threshold
        """
        if thresholds is None:
            thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        
        results = []
        
        for threshold in thresholds:
            y_pred = (y_pred_proba >= threshold).astype(int)
            
            # Calculate metrics
            tp = ((y_pred == 1) & (y_true == 1)).sum()
            fp = ((y_pred == 1) & (y_true == 0)).sum()
            tn = ((y_pred == 0) & (y_true == 0)).sum()
            fn = ((y_pred == 0) & (y_true == 1)).sum()
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            
            results.append({
                'Threshold': f"{threshold:.2f}",
                'TP': int(tp),
                'FP': int(fp),
                'FN': int(fn),
                'TN': int(tn),
                'Precision': f"{precision:.4f}",
                'Recall': f"{recall:.4f}",
                'Specificity': f"{specificity:.4f}",
                'F1': f"{f1:.4f}",
            })
        
        return pd.DataFrame(results)
    
    @staticmethod
    def recommend_threshold(
        y_true,
        y_pred_proba,
        objective: str = 'balanced'
    ) -> Tuple[float, Dict]:
        """
        Recommend optimal threshold based on objective.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            objective: 'balanced', 'precision', 'recall'
                - 'balanced': Maximize F1-score
                - 'precision': Minimize false positives
                - 'recall': Minimize false negatives (catch all fraud)
            
        Returns:
            Tuple of (optimal_threshold, metrics_at_threshold)
        """
        from sklearn.metrics import precision_recall_curve, f1_score
        
        precisions, recalls, thresholds_pr = precision_recall_curve(y_true, y_pred_proba)
        
        best_threshold = 0.5
        best_score = 0
        
        if objective == 'balanced':
            # Maximize F1
            for threshold in thresholds_pr:
                y_pred = (y_pred_proba >= threshold).astype(int)
                f1 = f1_score(y_true, y_pred, zero_division=0)
                if f1 > best_score:
                    best_score = f1
                    best_threshold = threshold
        
        elif objective == 'recall':
            # Maximize recall (catch more fraud, accept more false positives)
            min_precision = 0.5  # Require at least 50% precision
            for threshold in thresholds_pr:
                y_pred = (y_pred_proba >= threshold).astype(int)
                precision = precision_recall_curve(y_true, y_pred_proba)[0]
                recall = recall_score(y_true, y_pred, zero_division=0)
                if precision >= min_precision and recall > best_score:
                    best_score = recall
                    best_threshold = threshold
        
        elif objective == 'precision':
            # Maximize precision (minimize false positives)
            min_recall = 0.5  # Require at least 50% recall
            for threshold in thresholds_pr:
                y_pred = (y_pred_proba >= threshold).astype(int)
                precision = precision_score(y_true, y_pred, zero_division=0)
                recall = recall_score(y_true, y_pred, zero_division=0)
                if recall >= min_recall and precision > best_score:
                    best_score = precision
                    best_threshold = threshold
        
        # Get metrics at best threshold
        y_pred_best = (y_pred_proba >= best_threshold).astype(int)
        
        metrics = {
            'threshold': best_threshold,
            'precision': precision_score(y_true, y_pred_best, zero_division=0),
            'recall': recall_score(y_true, y_pred_best, zero_division=0),
            'f1': f1_score(y_true, y_pred_best, zero_division=0),
        }
        
        return best_threshold, metrics


class ModelEvaluator:
    """Comprehensive model evaluation"""
    
    @staticmethod
    def evaluate_and_select_model(
        models: Dict,
        results: Dict,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Tuple[str, object, float]:
        """
        Select best model based on comprehensive evaluation.
        
        For fraud detection, prioritize:
        1. PR-AUC (best for imbalanced data)
        2. Recall (catch fraud)
        3. Precision (minimize false positives)
        
        Args:
            models: Dictionary of trained models
            results: Dictionary of evaluation results
            X_test: Test features
            y_test: Test target
            
        Returns:
            Tuple of (best_model_name, best_model, optimal_threshold)
        """
        print("\n" + "="*60)
        print("MODEL SELECTION ANALYSIS")
        print("="*60)
        
        print("\nFor fraud detection, we prioritize:")
        print("  1. PR-AUC (Precision-Recall Area Under Curve)")
        print("     - Best metric for imbalanced classification")
        print("     - Considers both precision and recall")
        print("  2. Recall (Coverage of actual fraud)")
        print("     - Miss fraud = lost money / customer liability")
        print("  3. Precision (False positive rate)")
        print("     - Too many false positives = poor customer experience")
        
        print("\nWhy not accuracy?")
        print("  - With 0.17% fraud, predicting all legitimate = 99.83% accuracy")
        print("  - But catches 0% of actual fraud (useless)")
        
        print("\n" + "-"*60)
        print("MODEL SCORES")
        print("-"*60)
        
        # Rank models by PR-AUC (primary metric)
        for model_name in sorted(results.keys(), 
                                key=lambda x: results[x]['pr_auc'], 
                                reverse=True):
            r = results[model_name]
            print(f"\n{model_name}:")
            print(f"  PR-AUC: {r['pr_auc']:.4f} ← PRIMARY METRIC")
            print(f"  ROC-AUC: {r['roc_auc']:.4f}")
            print(f"  Recall: {r['recall']:.4f}")
            print(f"  Precision: {r['precision']:.4f}")
            print(f"  F1: {r['f1']:.4f}")
        
        # Select model with highest PR-AUC
        best_model_name = max(results.keys(), key=lambda x: results[x]['pr_auc'])
        best_model = models[best_model_name]
        
        print(f"\n" + "="*60)
        print(f"SELECTED MODEL: {best_model_name}")
        print(f"="*60)
        print(f"\nReason: Highest PR-AUC ({results[best_model_name]['pr_auc']:.4f})")
        print(f"        This is the best metric for imbalanced fraud detection.")
        
        # Analyze optimal threshold
        y_pred_proba = best_model.predict_proba(X_test)[:, 1]
        
        print(f"\n" + "-"*60)
        print("THRESHOLD ANALYSIS")
        print("-"*60)
        
        analyzer = ThresholdAnalyzer()
        threshold_analysis = analyzer.analyze_thresholds(y_test, y_pred_proba)
        print("\n" + str(threshold_analysis.to_string(index=False)))
        
        # Recommend threshold
        optimal_threshold, threshold_metrics = analyzer.recommend_threshold(
            y_test, y_pred_proba, objective='balanced'
        )
        
        print(f"\n" + "-"*60)
        print("RECOMMENDED THRESHOLD")
        print("-"*60)
        print(f"\nObjective: Balanced (maximize F1)")
        print(f"Optimal Threshold: {optimal_threshold:.2f}")
        print(f"  Precision: {threshold_metrics['precision']:.4f}")
        print(f"  Recall: {threshold_metrics['recall']:.4f}")
        print(f"  F1: {threshold_metrics['f1']:.4f}")
        
        print(f"\nInterpretation:")
        print(f"  - Flag transaction as fraud if probability >= {optimal_threshold:.2f}")
        print(f"  - Catches {threshold_metrics['recall']*100:.1f}% of actual fraud")
        print(f"  - {threshold_metrics['precision']*100:.1f}% of flagged transactions are real fraud")
        
        print(f"\nNote: Thresholds should be tuned using business cost analysis:")
        print(f"  - Cost of false positive (blocking legitimate transaction)")
        print(f"  - Cost of false negative (missing fraudulent transaction)")
        print(f"  - In production, use cost-benefit analysis to select threshold")
        
        return best_model_name, best_model, optimal_threshold


def main():
    """Test evaluation pipeline"""
    from data_loader import DataLoader
    from preprocessing import DataPreprocessor
    from train import ModelTrainer
    
    # Load and preprocess
    loader = DataLoader()
    df = loader.load_dataset()
    
    preprocessor = DataPreprocessor(random_state=42, test_size=0.2)
    X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(df)
    
    # Train models
    trainer = ModelTrainer(random_state=42)
    models, results = trainer.train_all_models(X_train, y_train, X_test, y_test)
    
    # Evaluate and select
    best_model_name, best_model, optimal_threshold = ModelEvaluator.evaluate_and_select_model(
        models, results, X_test, y_test
    )


if __name__ == "__main__":
    main()
