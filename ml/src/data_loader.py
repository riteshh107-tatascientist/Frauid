"""
Data Loader for Kaggle Credit Card Fraud Detection Dataset

Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
License: Database Contents License (DbCL) v1.0

The dataset contains transactions made by credit cards in September 2013 by European cardholders.

Dataset Statistics:
- Total transactions: ~284,807
- Fraud transactions: ~492 (0.17%)
- Features: Time, V1-V28 (anonymized), Amount
- All numerical features are the result of PCA transformation
- Target: Class (0 = legitimate, 1 = fraud)
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and validate Kaggle Credit Card Fraud Detection dataset"""
    
    DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'creditcard.csv')
    TARGET_COLUMN = 'Class'
    
    @staticmethod
    def download_instructions():
        """Print instructions for downloading the dataset"""
        instructions = """
        DATASET DOWNLOAD INSTRUCTIONS
        ==============================
        
        The Kaggle Credit Card Fraud Detection dataset must be downloaded manually:
        
        1. Go to: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
        2. Click "Download" (requires Kaggle account)
        3. Unzip the file
        4. Place creditcard.csv in: ml/data/creditcard.csv
        
        Alternatively, using Kaggle CLI:
        
        # Install kaggle CLI
        pip install kaggle
        
        # Set up credentials (copy from https://www.kaggle.com/settings/account)
        mkdir -p ~/.kaggle
        cp kaggle.json ~/.kaggle/
        chmod 600 ~/.kaggle/kaggle.json
        
        # Download dataset
        cd fraudguard-ai/ml
        kaggle datasets download -d mlg-ulb/creditcardfraud
        unzip creditcardfraud.zip
        
        The dataset file should be at: ml/data/creditcard.csv
        """
        print(instructions)
    
    @classmethod
    def load_dataset(cls) -> pd.DataFrame:
        """
        Load the credit card fraud dataset.
        
        Returns:
            DataFrame with all transactions
            
        Raises:
            FileNotFoundError: If dataset not found
        """
        if not os.path.exists(cls.DATASET_PATH):
            logger.error(f"Dataset not found at {cls.DATASET_PATH}")
            cls.download_instructions()
            raise FileNotFoundError(
                f"Dataset not found at {cls.DATASET_PATH}\n"
                f"Please download from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
            )
        
        logger.info(f"Loading dataset from {cls.DATASET_PATH}")
        df = pd.read_csv(cls.DATASET_PATH)
        logger.info(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        return df
    
    @staticmethod
    def inspect_dataset(df: pd.DataFrame) -> Dict:
        """
        Inspect dataset structure and quality.
        
        Args:
            df: Dataset DataFrame
            
        Returns:
            Dictionary with dataset statistics
        """
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 ** 2),
        }
        
        # Target distribution
        if 'Class' in df.columns:
            value_counts = df['Class'].value_counts()
            stats['class_distribution'] = value_counts.to_dict()
            stats['fraud_percentage'] = (value_counts.get(1, 0) / len(df)) * 100
            stats['class_imbalance_ratio'] = value_counts.get(0, 1) / max(value_counts.get(1, 1), 1)
        
        return stats
    
    @staticmethod
    def validate_dataset(df: pd.DataFrame) -> Tuple[bool, list]:
        """
        Validate dataset integrity.
        
        Args:
            df: Dataset DataFrame
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check required columns
        required_columns = ['Class', 'Time', 'Amount']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")
        
        # Check target column
        if 'Class' in df.columns:
            valid_classes = set(df['Class'].unique())
            if not valid_classes.issubset({0, 1}):
                issues.append(f"Invalid class values: {valid_classes}")
        
        # Check for null values in critical columns
        null_cols = df.columns[df.isnull().any()].tolist()
        if null_cols:
            issues.append(f"Columns with null values: {null_cols}")
        
        # Check data types
        for col in df.columns:
            if col not in ['Class', 'Time']:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f"Column {col} is not numeric")
        
        is_valid = len(issues) == 0
        return is_valid, issues


def main():
    """Test data loading"""
    try:
        loader = DataLoader()
        df = loader.load_dataset()
        
        print("\n" + "="*60)
        print("DATASET INSPECTION")
        print("="*60)
        
        stats = loader.inspect_dataset(df)
        
        print(f"\nRows: {stats['total_rows']}")
        print(f"Columns: {stats['total_columns']}")
        print(f"Columns: {', '.join(stats['columns'][:5])}... (showing first 5)")
        print(f"Memory Usage: {stats['memory_usage_mb']:.2f} MB")
        print(f"Duplicate rows: {stats['duplicate_rows']}")
        
        if 'class_distribution' in stats:
            print(f"\nClass Distribution:")
            print(f"  Legitimate (0): {stats['class_distribution'].get(0, 0):,}")
            print(f"  Fraud (1): {stats['class_distribution'].get(1, 0):,}")
            print(f"  Fraud Percentage: {stats['fraud_percentage']:.2f}%")
            print(f"  Imbalance Ratio: {stats['class_imbalance_ratio']:.1f}:1")
        
        print(f"\nMissing values:")
        missing = {k: v for k, v in stats['missing_values'].items() if v > 0}
        if missing:
            for col, count in missing.items():
                print(f"  {col}: {count}")
        else:
            print("  None")
        
        # Validate dataset
        print(f"\nValidation:")
        is_valid, issues = loader.validate_dataset(df)
        if is_valid:
            print("  ✓ Dataset is valid")
        else:
            print("  ✗ Dataset has issues:")
            for issue in issues:
                print(f"    - {issue}")
        
        print("\n" + "="*60)
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        print("\nPlease download the dataset first.")


if __name__ == "__main__":
    main()
