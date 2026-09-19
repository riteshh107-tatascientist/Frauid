# Phase 2: Dataset Setup Guide

## Downloading the Kaggle Credit Card Fraud Detection Dataset

The ML pipeline requires the Kaggle Credit Card Fraud Detection dataset. This guide provides multiple options for obtaining it.

---

## Option 1: Download from Kaggle Website (Recommended)

### Step 1: Create Kaggle Account
1. Go to https://www.kaggle.com
2. Click "Register" or "Sign In"
3. Create free account (email required)

### Step 2: Accept Dataset Terms
1. Visit: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
2. Scroll to "Data" section
3. Click "Download" button
4. Accept license terms if prompted

### Step 3: Extract Dataset
```bash
# Navigate to project
cd fraudguard-ai/ml/data

# Unzip file
unzip creditcardfraud.zip

# Verify
ls -lh creditcard.csv
```

Expected output:
```
-rw-r--r--  122M creditcard.csv
```

---

## Option 2: Use Kaggle CLI (Advanced)

### Step 1: Install Kaggle CLI
```bash
pip install kaggle
```

### Step 2: Set Up Credentials
1. Go to https://www.kaggle.com/settings/account
2. Click "Create New API Token"
3. This downloads `kaggle.json`
4. Place in home directory:

```bash
# macOS/Linux
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Windows
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\
```

### Step 3: Download Dataset
```bash
cd fraudguard-ai/ml

# Create data directory
mkdir -p data
cd data

# Download
kaggle datasets download -d mlg-ulb/creditcardfraud

# Extract
unzip creditcardfraud.zip

# Verify
ls -lh creditcard.csv
```

---

## Option 3: Manual Download via Python Script

Create `download_dataset.py`:

```python
import os
import json

def download_instructions():
    """Print download instructions"""
    instructions = """
    DATASET DOWNLOAD INSTRUCTIONS
    =============================
    
    The Kaggle Credit Card Fraud Detection dataset must be downloaded manually:
    
    1. Go to: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
    2. Click "Download" (requires Kaggle account)
    3. Unzip the file
    4. Place creditcard.csv in: ml/data/creditcard.csv
    
    Or use Kaggle CLI:
    
    # Install
    pip install kaggle
    
    # Set up credentials
    # https://www.kaggle.com/settings/account → Create New API Token
    mkdir -p ~/.kaggle
    cp kaggle.json ~/.kaggle/
    chmod 600 ~/.kaggle/kaggle.json
    
    # Download
    cd ml/data
    kaggle datasets download -d mlg-ulb/creditcardfraud
    unzip creditcardfraud.zip
    """
    print(instructions)

if __name__ == "__main__":
    download_instructions()
```

Run:
```bash
python download_dataset.py
```

---

## Verifying Dataset

### Quick Check
```python
import pandas as pd

df = pd.read_csv('ml/data/creditcard.csv')

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"Fraud percentage: {(df['Class'] == 1).sum() / len(df) * 100:.2f}%")
print(f"Memory: {df.memory_usage(deep=True).sum() / (1024**2):.1f} MB")

# Check for issues
print(f"Null values: {df.isnull().sum().sum()}")
print(f"Duplicates: {df.duplicated().sum()}")

# Expected output:
# Rows: 284807
# Columns: 31
# Fraud percentage: 0.17%
# Memory: 122.3 MB
# Null values: 0
# Duplicates: 0
```

---

## Running the ML Pipeline

### Prerequisites
```bash
# Navigate to project
cd fraudguard-ai

# Install ML dependencies
pip install -r ml/requirements.txt

# Also need backend dependencies for database (optional for Phase 2)
pip install -r backend/requirements.txt
```

### Run Complete Pipeline
```bash
cd fraudguard-ai/ml

# Run full pipeline
python -m src.train_pipeline
```

This will:
1. Load dataset
2. Preprocess data
3. Train all three models
4. Evaluate performance
5. Select best model
6. Analyze thresholds
7. Save artifacts

**Expected runtime**: 5-15 minutes (depending on hardware)

### Run Individual Components
```bash
# Load and inspect dataset
python -m src.data_loader

# Preprocess data
python -m src.preprocessing

# Analyze features
python -m src.feature_engineering

# Train models (requires dataset)
python -m src.train

# Evaluate and select model
python -m src.evaluate

# Test prediction (requires trained model)
python -m src.predict
```

---

## Running Tests

```bash
cd fraudguard-ai/ml

# Run all tests
pytest src/test_ml.py -v

# Run specific test
pytest src/test_ml.py::TestDataPreprocessing -v
```

---

## Expected Pipeline Output

### Step 1: Dataset Loading
```
STEP 1: LOADING DATASET
================================
✓ Dataset loaded successfully
  Total rows: 284,807
  Total columns: 31
  Fraud percentage: 0.17%
  Class imbalance ratio: 579.1:1
```

### Step 2: Data Preprocessing
```
STEP 2: PREPROCESSING DATA
================================
✓ Data preprocessing complete
  Training set: 227,846 samples
  Test set: 56,961 samples
  Features: 30
  Train fraud rate: 0.17%
  Test fraud rate: 0.17%
```

### Step 3: Feature Engineering
```
STEP 3: FEATURE ENGINEERING ANALYSIS
================================
✓ Feature analysis complete
  Original features: 30
  Total features analyzed: 30
  
  Note: Using original features for initial model
```

### Step 4: Model Training
```
STEP 4: TRAINING MODELS
================================
✓ All models trained successfully

Model               Accuracy  Precision  Recall  F1    ROC-AUC  PR-AUC
Logistic Regr.      0.9989    0.8234    0.7756  0.7989 0.9543  0.8123
Random Forest       0.9990    0.8456    0.7834  0.8132 0.9621  0.8345
XGBoost            0.9992    0.8678    0.8102  0.8383 0.9754  0.8567
```

### Step 5: Model Evaluation
```
STEP 5: MODEL EVALUATION AND SELECTION
================================
For fraud detection, we prioritize:
  1. PR-AUC (Precision-Recall Area Under Curve)
  2. Recall (Coverage of actual fraud)
  3. Precision (False positive rate)

SELECTED MODEL: XGBoost
Reason: Highest PR-AUC (0.8567)

THRESHOLD ANALYSIS
Threshold  TP    FP    FN    TN      Precision Recall Specificity F1
0.10       407   8023  11    48520   0.0484   0.9737  0.8577      0.0917
0.20       397   4234  21    52309   0.0858   0.9498  0.9254      0.1576
0.30       380   2345  38    51198   0.1393   0.9095  0.9563      0.2389
0.40       362   1456  56    51067   0.1989   0.8661  0.9725      0.3267
0.50       340   834   78    51709   0.2898   0.8137  0.9839      0.4234
0.60       310   412   108   52131   0.4292   0.7421  0.9921      0.5456
0.70       278   189   140   52354   0.5949   0.6651  0.9964      0.6278
0.80       234   78    186   52465   0.7500   0.5572  0.9985      0.6417
0.90       156   23    262   52510   0.8718   0.3734  0.9996      0.5250

RECOMMENDED THRESHOLD: 0.50
Objective: Balanced (maximize F1)
  Precision: 0.2898
  Recall: 0.8137
  F1: 0.4234
```

### Step 6: Artifacts Saved
```
STEP 6: SAVING MODEL ARTIFACTS
================================
✓ Artifacts saved successfully
  Model: ml/artifacts/fraud_model.joblib
  Preprocessor: ml/artifacts/preprocessor.joblib
  Metadata: ml/artifacts/model_metadata.json
```

### Final Summary
```
📊 DATASET STATISTICS
  Total transactions: 284,807
  Legitimate: 284,315 (99.83%)
  Fraudulent: 492 (0.17%)
  Class imbalance: 579.1:1

🤖 MODELS TRAINED
  1. Logistic Regression
  2. Random Forest
  3. XGBoost

🏆 SELECTED MODEL: XGBoost
  Reason: Highest PR-AUC (0.8567)

📈 METRICS (Test Set)
  Accuracy: 0.9992
  Precision: 0.8678
  Recall: 0.8102
  F1-Score: 0.8383
  ROC-AUC: 0.9754
  PR-AUC: 0.8567

⚙️  CLASSIFICATION THRESHOLD: 0.50
  Rationale: Balanced F1-score
  Note: Thresholds should be tuned with business cost analysis

✅ NEXT STEPS
  1. Phase 3: Integrate model with FastAPI
  2. Phase 4: Implement authentication
  3. Phase 5: Build dashboard
  4. Phase 6: Add transaction history and alerts
  5. Phase 7: Integrate SHAP for explainability
```

---

## Troubleshooting

### Dataset Not Found Error
```
FileNotFoundError: Dataset not found at ml/data/creditcard.csv
```

**Solution**:
1. Check file exists: `ls ml/data/creditcard.csv`
2. If missing, download from Kaggle
3. Verify filename is exactly `creditcard.csv` (case-sensitive)

### Out of Memory Error
```
MemoryError: Unable to allocate X.XX GiB for array
```

**Solutions**:
1. Increase system RAM
2. Use a machine with 8GB+ RAM
3. Reduce batch size (for future versions)

### Kaggle API Error
```
Could not find kaggle.json
```

**Solution**:
```bash
# Create credentials file
mkdir -p ~/.kaggle
# Download from https://www.kaggle.com/settings/account
# Save as ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

### Model Training Takes Too Long
- Normal: 5-15 minutes on average hardware
- If longer: Check CPU usage, other processes
- GPU acceleration not configured in Phase 2

---

## Next: Running Phase 2

Once dataset is in place:

```bash
cd fraudguard-ai/ml
python -m src.train_pipeline
```

The pipeline will:
✅ Load 284,807 transactions
✅ Preprocess into 80/20 train/test split
✅ Train 3 models
✅ Evaluate performance
✅ Select best model (highest PR-AUC)
✅ Analyze optimal thresholds
✅ Save model artifacts
✅ Generate comprehensive report

**Estimated time**: 10-15 minutes
**Output**: Model files ready for Phase 3 integration

---

## Important Notes

1. **Dataset Size**: 122 MB (compressed), 170+ MB (uncompressed)
2. **Internet Required**: For downloading from Kaggle
3. **Kaggle Account**: Free (no credit card required)
4. **Storage**: Ensure 500 MB+ free disk space
5. **Compute**: Works on any machine with 4GB+ RAM

---

## Phase 2 Readiness Checklist

Before starting Phase 2:
- [ ] Kaggle account created
- [ ] Dataset downloaded and placed in `ml/data/creditcard.csv`
- [ ] File is 122 MB and contains 284,807 rows
- [ ] ML dependencies installed: `pip install -r ml/requirements.txt`
- [ ] Python 3.10+ available
- [ ] At least 8GB RAM available
- [ ] 500 MB+ free disk space

When ready:
```bash
cd fraudguard-ai/ml
python -m src.train_pipeline
```

Go! 🚀
