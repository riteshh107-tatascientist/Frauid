"""
FraudGuard AI - Complete ML Training Pipeline

This script orchestrates the entire ML pipeline:
1. Load dataset
2. Preprocess data
3. Engineer features
4. Train models
5. Evaluate and select best model
6. Analyze thresholds
7. Save artifacts

Run with:
    python -m ml.src.train_pipeline
"""

import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_loader import DataLoader
from preprocessing import DataPreprocessor
from feature_engineering import FeatureEngineer
from train import ModelTrainer
from evaluate import ModelEvaluator, ThresholdAnalyzer
from predict import ModelArtifactManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run complete ML pipeline"""
    
    print("\n" + "="*70)
    print("FRAUDGUARD AI - MACHINE LEARNING PIPELINE")
    print("="*70)
    
    try:
        # =====================================================================
        # STEP 1: LOAD DATASET
        # =====================================================================
        print("\n" + "="*70)
        print("STEP 1: LOADING DATASET")
        print("="*70)
        
        loader = DataLoader()
        df = loader.load_dataset()
        
        # Inspect dataset
        stats = loader.inspect_dataset(df)
        print(f"\n✓ Dataset loaded successfully")
        print(f"  Total rows: {stats['total_rows']:,}")
        print(f"  Total columns: {stats['total_columns']}")
        print(f"  Fraud percentage: {stats.get('fraud_percentage', 0):.2f}%")
        print(f"  Class imbalance ratio: {stats.get('class_imbalance_ratio', 0):.1f}:1")
        
        # Validate dataset
        is_valid, issues = loader.validate_dataset(df)
        if is_valid:
            print(f"✓ Dataset validation passed")
        else:
            print(f"✗ Dataset has validation issues:")
            for issue in issues:
                print(f"  - {issue}")
            return
        
        # =====================================================================
        # STEP 2: PREPROCESS DATA
        # =====================================================================
        print("\n" + "="*70)
        print("STEP 2: PREPROCESSING DATA")
        print("="*70)
        
        preprocessor = DataPreprocessor(random_state=42, test_size=0.2)
        X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(df)
        
        print(f"\n✓ Data preprocessing complete")
        print(f"  Training set: {len(X_train):,} samples")
        print(f"  Test set: {len(X_test):,} samples")
        print(f"  Features: {X_train.shape[1]}")
        print(f"  Train fraud rate: {(y_train == 1).sum() / len(y_train) * 100:.2f}%")
        print(f"  Test fraud rate: {(y_test == 1).sum() / len(y_test) * 100:.2f}%")
        
        # =====================================================================
        # STEP 3: FEATURE ENGINEERING
        # =====================================================================
        print("\n" + "="*70)
        print("STEP 3: FEATURE ENGINEERING ANALYSIS")
        print("="*70)
        
        # Analyze features
        df_analysis = df.copy()
        feature_analysis, feature_info = FeatureEngineer.engineer_features(df_analysis)
        
        print(f"\n✓ Feature analysis complete")
        print(f"  Original features: {len(feature_info['original_features'])}")
        print(f"  Total features analyzed: {feature_info['total_features']}")
        print(f"\n  Note: Using original features for initial model")
        print(f"        Kaggle dataset features are PCA-transformed (anonymized)")
        print(f"        Cannot derive: device type, location, behavioral features")
        
        # =====================================================================
        # STEP 4: TRAIN MODELS
        # =====================================================================
        print("\n" + "="*70)
        print("STEP 4: TRAINING MODELS")
        print("="*70)
        
        trainer = ModelTrainer(random_state=42)
        models, results = trainer.train_all_models(X_train, y_train, X_test, y_test)
        
        print(f"\n✓ All models trained successfully")
        print("\n" + str(trainer.compare_models()))
        
        # =====================================================================
        # STEP 5: EVALUATE AND SELECT MODEL
        # =====================================================================
        print("\n" + "="*70)
        print("STEP 5: MODEL EVALUATION AND SELECTION")
        print("="*70)
        
        best_model_name, best_model, optimal_threshold = ModelEvaluator.evaluate_and_select_model(
            models, results, X_test, y_test
        )
        
        # =====================================================================
        # STEP 6: SAVE ARTIFACTS
        # =====================================================================
        print("\n" + "="*70)
        print("STEP 6: SAVING MODEL ARTIFACTS")
        print("="*70)
        
        # Get best model metrics for metadata
        best_metrics = results[best_model_name]
        best_metrics['threshold'] = optimal_threshold
        
        model_path, preprocessor_path, metadata_path = ModelArtifactManager.save_model_artifacts(
            best_model,
            pipe,
            model_name=best_model_name,
            model_version='1.0.0',
            threshold=optimal_threshold,
            metrics=best_metrics,
            X_train=X_train,
            y_train=y_train
        )
        
        print(f"\n✓ Artifacts saved successfully")
        print(f"  Model: {model_path}")
        print(f"  Preprocessor: {preprocessor_path}")
        print(f"  Metadata: {metadata_path}")
        
        # =====================================================================
        # FINAL SUMMARY
        # =====================================================================
        print("\n" + "="*70)
        print("PIPELINE COMPLETE - SUMMARY")
        print("="*70)
        
        print(f"\n📊 DATASET STATISTICS")
        print(f"  Total transactions: {len(df):,}")
        print(f"  Legitimate: {(df['Class'] == 0).sum():,} ({(df['Class'] == 0).sum() / len(df) * 100:.2f}%)")
        print(f"  Fraudulent: {(df['Class'] == 1).sum():,} ({(df['Class'] == 1).sum() / len(df) * 100:.2f}%)")
        print(f"  Class imbalance: {(df['Class'] == 0).sum() / (df['Class'] == 1).sum():.1f}:1")
        
        print(f"\n🤖 MODELS TRAINED")
        print(f"  1. Logistic Regression")
        print(f"  2. Random Forest")
        print(f"  3. XGBoost")
        
        print(f"\n🏆 SELECTED MODEL: {best_model_name}")
        print(f"  Reason: Highest PR-AUC (best for imbalanced data)")
        
        print(f"\n📈 METRICS (Test Set)")
        print(f"  Accuracy: {best_metrics['accuracy']:.4f}")
        print(f"  Precision: {best_metrics['precision']:.4f}")
        print(f"  Recall: {best_metrics['recall']:.4f}")
        print(f"  F1-Score: {best_metrics['f1']:.4f}")
        print(f"  ROC-AUC: {best_metrics['roc_auc']:.4f}")
        print(f"  PR-AUC: {best_metrics['pr_auc']:.4f}")
        
        print(f"\n⚙️  CLASSIFICATION THRESHOLD")
        print(f"  Selected: {optimal_threshold:.2f}")
        print(f"  Rationale: Balanced F1-score")
        print(f"  Note: Thresholds should be tuned with business cost analysis")
        
        print(f"\n💾 ARTIFACTS SAVED")
        print(f"  Model type: {best_model_name}")
        print(f"  Version: 1.0.0")
        print(f"  Training date: Now")
        print(f"  Features: {X_train.shape[1]}")
        
        print(f"\n⚠️  DATASET LIMITATIONS")
        print(f"  - Features are anonymized (PCA-transformed)")
        print(f"  - No device, location, or user behavior features")
        print(f"  - Model represents transactional fraud only")
        print(f"  - Does NOT detect:")
        print(f"    • Account takeover")
        print(f"    • Location-based fraud")
        print(f"    • Device fraud")
        print(f"    • Behavioral anomalies (beyond transaction amount/timing)")
        
        print(f"\n✅ NEXT STEPS")
        print(f"  1. Phase 3: Integrate model with FastAPI")
        print(f"  2. Phase 4: Implement authentication")
        print(f"  3. Phase 5: Build dashboard")
        print(f"  4. Phase 6: Add transaction history and alerts")
        print(f"  5. Phase 7: Integrate SHAP for explainability")
        
        print(f"\n" + "="*70)
        print("✅ PHASE 2 COMPLETE")
        print("="*70 + "\n")
        
        return True
        
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease download the dataset first:")
        DataLoader.download_instructions()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
