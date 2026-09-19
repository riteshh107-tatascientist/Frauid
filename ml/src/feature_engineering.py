"""
Feature Engineering for Fraud Detection

IMPORTANT LIMITATION:
The Kaggle Credit Card Fraud Detection dataset contains anonymized PCA-transformed features (V1-V28).
This means we cannot engineer interpretable features like:
- Unusual transaction amount
- Unusual transaction time
- Device changes
- Location changes
- Account age
- Transaction frequency

These behavioral features would require the original raw transaction data.

For the initial ML model, we use the provided features as-is.
In Phase 4, we can extend the model with behavioral features if additional data is available.
"""

import pandas as pd
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for fraud detection"""
    
    @staticmethod
    def analyze_feature_importance_potential(df: pd.DataFrame) -> dict:
        """
        Analyze which features might be most predictive.
        
        Args:
            df: Dataset with features and target
            
        Returns:
            Dictionary of analysis results
        """
        # Separate legitimate and fraud transactions
        legitimate = df[df['Class'] == 0].drop(columns=['Class'])
        fraud = df[df['Class'] == 1].drop(columns=['Class'])
        
        feature_variance = {}
        for col in legitimate.columns:
            # Measure difference in distributions
            variance_diff = abs(legitimate[col].mean() - fraud[col].mean()) / (legitimate[col].std() + 1e-8)
            feature_variance[col] = variance_diff
        
        # Sort by variance
        sorted_features = sorted(feature_variance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'top_discriminative_features': [f[0] for f in sorted_features[:10]],
            'all_feature_variance': dict(sorted_features)
        }
    
    @staticmethod
    def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create time-based features from Time column.
        
        The Time column contains seconds elapsed since the first transaction in the dataset.
        
        Args:
            df: Dataset with Time column
            
        Returns:
            DataFrame with additional time features
        """
        df = df.copy()
        
        # Convert time to hours for interpretability
        df['Time_Hours'] = df['Time'] / 3600
        
        # Extract hour of day (assuming data spans multiple days)
        seconds_per_day = 86400
        df['Hour_of_Day'] = (df['Time'] % seconds_per_day) / 3600
        
        # Extract day number
        df['Day_Number'] = df['Time'] // seconds_per_day
        
        logger.info("Created time-based features: Time_Hours, Hour_of_Day, Day_Number")
        
        return df
    
    @staticmethod
    def create_amount_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create amount-based features.
        
        Args:
            df: Dataset with Amount column
            
        Returns:
            DataFrame with additional amount features
        """
        df = df.copy()
        
        # Log-transform amount (for skewed distribution)
        df['Amount_Log'] = np.log1p(df['Amount'])
        
        # Amount category
        df['Amount_Category'] = pd.cut(
            df['Amount'], 
            bins=[0, 50, 200, 1000, 5000, np.inf],
            labels=['very_small', 'small', 'medium', 'large', 'very_large']
        )
        
        logger.info("Created amount-based features: Amount_Log, Amount_Category")
        
        return df
    
    @staticmethod
    def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Apply all feature engineering transformations.
        
        Args:
            df: Dataset
            
        Returns:
            Tuple of (engineered dataframe, feature info dict)
        """
        logger.info("Starting feature engineering...")
        
        df_engineered = df.copy()
        
        # Create time features
        df_engineered = FeatureEngineer.create_time_features(df_engineered)
        
        # Create amount features
        df_engineered = FeatureEngineer.create_amount_features(df_engineered)
        
        # Analyze feature importance
        analysis = FeatureEngineer.analyze_feature_importance_potential(df_engineered)
        
        feature_info = {
            'original_features': [col for col in df.columns if col != 'Class'],
            'engineered_features': [col for col in df_engineered.columns if col not in df.columns and col != 'Class'],
            'total_features': len(df_engineered.columns) - 1,  # Excluding Class
            'feature_analysis': analysis
        }
        
        logger.info(f"Feature engineering complete. Total features: {feature_info['total_features']}")
        
        return df_engineered, feature_info


def main():
    """Test feature engineering"""
    from data_loader import DataLoader
    
    loader = DataLoader()
    df = loader.load_dataset()
    
    print("\n" + "="*60)
    print("FEATURE ENGINEERING ANALYSIS")
    print("="*60)
    
    print("\nDataset Limitations:")
    print("  - Features are anonymized (PCA-transformed)")
    print("  - Cannot derive: device type, location, account age, etc.")
    print("  - Features available: V1-V28, Time, Amount")
    
    # Create features
    df_engineered, feature_info = FeatureEngineer.engineer_features(df)
    
    print(f"\nOriginal features: {len(feature_info['original_features'])}")
    print(f"Engineered features: {len(feature_info['engineered_features'])}")
    print(f"Total features: {feature_info['total_features']}")
    
    print(f"\nTop discriminative features:")
    for i, feature in enumerate(feature_info['feature_analysis']['top_discriminative_features'][:10], 1):
        print(f"  {i}. {feature}")


if __name__ == "__main__":
    main()
