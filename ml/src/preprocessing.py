"""
Data Preprocessing Pipeline

Handles:
- Missing value imputation
- Duplicate detection
- Feature scaling
- Train/test split
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import logging
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocessing pipeline for fraud detection"""
    
    def __init__(self, random_state: int = 42, test_size: float = 0.2):
        """
        Initialize preprocessor.
        
        Args:
            random_state: Random seed for reproducibility
            test_size: Proportion of data for testing
        """
        self.random_state = random_state
        self.test_size = test_size
        self.scaler = None
        self.preprocessor = None
        self.feature_names = None
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data by handling missing values and duplicates.
        
        Args:
            df: Raw dataset
            
        Returns:
            Cleaned dataset
        """
        df = df.copy()
        initial_rows = len(df)
        
        # Check for missing values
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            logger.warning(f"Found {missing_count} missing values, dropping rows")
            df = df.dropna()
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            logger.warning(f"Found {duplicate_count} duplicate rows, dropping them")
            df = df.drop_duplicates()
        
        rows_removed = initial_rows - len(df)
        if rows_removed > 0:
            logger.info(f"Removed {rows_removed} rows during cleaning")
        else:
            logger.info("No rows removed during cleaning")
        
        return df
    
    def split_data(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        stratify: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into train and test sets with stratification.
        
        Args:
            X: Features
            y: Target
            stratify: Whether to stratify by target (for imbalanced data)
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        stratify_arg = y if stratify else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=stratify_arg
        )
        
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Log class distribution
        train_fraud_pct = (y_train == 1).sum() / len(y_train) * 100
        test_fraud_pct = (y_test == 1).sum() / len(y_test) * 100
        
        logger.info(f"Train fraud percentage: {train_fraud_pct:.2f}%")
        logger.info(f"Test fraud percentage: {test_fraud_pct:.2f}%")
        
        return X_train, X_test, y_train, y_test
    
    def create_preprocessor(
        self, 
        X_train: pd.DataFrame,
        exclude_columns: List[str] = None
    ) -> ColumnTransformer:
        """
        Create preprocessing pipeline.
        
        Uses RobustScaler for features to handle outliers well (important for fraud data).
        
        Args:
            X_train: Training features for fitting
            exclude_columns: Columns to exclude from scaling
            
        Returns:
            ColumnTransformer pipeline
        """
        if exclude_columns is None:
            exclude_columns = []
        
        # Get all numeric columns except excluded ones
        numeric_features = [col for col in X_train.columns 
                           if col not in exclude_columns]
        
        # Create preprocessing pipeline
        self.preprocessor = ColumnTransformer(
            transformers=[
                ('scaler', RobustScaler(), numeric_features)
            ],
            remainder='passthrough'
        )
        
        # Fit on training data only (prevent data leakage)
        self.preprocessor.fit(X_train)
        self.feature_names = numeric_features
        
        logger.info(f"Preprocessor fitted on {len(numeric_features)} features")
        
        return self.preprocessor
    
    def prepare_data(
        self, 
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, ColumnTransformer]:
        """
        Complete preprocessing pipeline.
        
        Args:
            df: Raw dataset with 'Class' column as target
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test, preprocessor)
        """
        # Clean data
        logger.info("Starting data preprocessing...")
        df = self.clean_data(df)
        
        # Separate features and target
        X = df.drop(columns=['Class'])
        y = df['Class']
        
        # Split data (stratified by target)
        X_train, X_test, y_train, y_test = self.split_data(X, y, stratify=True)
        
        # Create and fit preprocessor on training data only
        self.create_preprocessor(X_train)
        
        # Transform data
        X_train_transformed = pd.DataFrame(
            self.preprocessor.transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )
        X_test_transformed = pd.DataFrame(
            self.preprocessor.transform(X_test),
            columns=X_test.columns,
            index=X_test.index
        )
        
        logger.info("Data preprocessing complete")
        
        return X_train_transformed, X_test_transformed, y_train, y_test, self.preprocessor


def analyze_features(df: pd.DataFrame) -> Dict:
    """
    Analyze feature statistics.
    
    Args:
        df: Dataset
        
    Returns:
        Dictionary of feature statistics
    """
    stats = {
        'feature_count': len(df.columns) - 1,  # Excluding target
        'numerical_features': list(df.select_dtypes(include=[np.number]).columns),
        'feature_ranges': {},
    }
    
    for col in df.columns:
        if col != 'Class':
            stats['feature_ranges'][col] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std(),
            }
    
    return stats


def main():
    """Test preprocessing pipeline"""
    from data_loader import DataLoader
    
    # Load data
    loader = DataLoader()
    df = loader.load_dataset()
    
    # Preprocess
    preprocessor = DataPreprocessor(random_state=42, test_size=0.2)
    X_train, X_test, y_train, y_test, pipe = preprocessor.prepare_data(df)
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE")
    print("="*60)
    print(f"\nTrain set shape: {X_train.shape}")
    print(f"Test set shape: {X_test.shape}")
    print(f"\nTrain target distribution:")
    print(f"  Legitimate: {(y_train == 0).sum()}")
    print(f"  Fraud: {(y_train == 1).sum()}")
    print(f"\nTest target distribution:")
    print(f"  Legitimate: {(y_test == 0).sum()}")
    print(f"  Fraud: {(y_test == 1).sum()}")


if __name__ == "__main__":
    main()
