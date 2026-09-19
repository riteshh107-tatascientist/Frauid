# Phase 3: Prediction API Integration - Quick Start

## Overview

Phase 3 integrates the real trained ML model from Phase 2 with FastAPI to create production-ready prediction endpoints.

---

## Prerequisites

1. **Phase 2 Complete**: Trained model artifacts saved
   - `ml/artifacts/fraud_model.joblib`
   - `ml/artifacts/preprocessor.joblib`
   - `ml/artifacts/model_metadata.json`

2. **Backend Dependencies**: Installed
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **PostgreSQL**: Running (for transaction storage)

---

## Starting Phase 3

### Step 1: Verify Phase 2 Artifacts
```bash
ls -la ml/artifacts/
# Expected:
# fraud_model.joblib (3.2 MB)
# preprocessor.joblib (0.8 MB)
# model_metadata.json (2.1 KB)
```

### Step 2: Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Expected output:
```
FRAUDGUARD AI STARTING UP
========================================================================
Environment: development
Debug mode: True

📦 Initializing ML Service...
✓ ML Service loaded successfully

⚙️  Initializing Risk Engine...
✓ Risk Engine initialized

✅ FraudGuard AI is ready
========================================================================
```

### Step 3: Test Endpoints

**Health Check**:
```bash
curl http://localhost:8000/api/health
# Response: {"status": "healthy", "ml_model": "healthy", ...}
```

**Model Info**:
```bash
curl http://localhost:8000/api/model/info
# Returns: model_name, threshold, features, metrics
```

**Make Prediction**:
```bash
curl -X POST http://localhost:8000/api/transactions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "Time": 3600,
    "V1": -1.35,
    "V2": -0.73,
    ...
    "V28": 0.08,
    "Amount": 149.62
  }'

# Response:
{
  "prediction": "LEGITIMATE",
  "fraud_probability": 0.12,
  "risk_score": 12.0,
  "risk_level": "LOW",
  "model_version": "1.0.0"
}
```

---

## New API Endpoints

### Prediction Endpoints

**POST /api/transactions/predict**
- Make fraud prediction on a transaction
- Input: 30 transaction features (Time, V1-V28, Amount)
- Output: Fraud probability, risk level, prediction
- **Uses real trained model from Phase 2**
- Stores prediction in PostgreSQL database

**GET /api/model/info**
- Get information about the trained model
- Returns: Model name, version, threshold, features, metrics
- All data from Phase 2 model metadata

### Transaction Endpoints

**GET /api/transactions**
- List stored transaction predictions
- Supports pagination and filtering:
  - `page`: Page number
  - `page_size`: Items per page
  - `risk_level`: Filter by LOW/MEDIUM/HIGH
  - `prediction`: Filter by fraud/legitimate
  - `start_date`, `end_date`: Date range

**GET /api/transactions/{id}**
- Get single transaction by ID

### Dashboard Endpoints

**GET /api/dashboard/summary**
- Summary statistics:
  - Total transactions
  - Fraud/legitimate counts
  - Risk level distribution
  - Fraud percentage

**GET /api/dashboard/risk-trends**
- Fraud trends over time (last 30 days by default)
- Grouped by date with fraud counts and percentages

---

## Real Data Flow

```
User Request with 30 features
    ↓
Pydantic Validation (TransactionPredictionRequest)
    ↓
ML Service loads features
    ↓
RobustScaler preprocesses (from Phase 2)
    ↓
XGBoost model predicts probability
    ↓
Risk Engine classifies:
  - fraud_probability → risk_score (0-100)
  - fraud_probability → risk_level (LOW/MEDIUM/HIGH)
  - fraud_probability → prediction (FRAUD/LEGITIMATE)
    ↓
Transaction stored in PostgreSQL
    ↓
Response with all results
```

---

## Swagger Documentation

Access interactive API documentation:

**Swagger UI**: http://localhost:8000/docs
- Try endpoints directly
- See request/response schemas
- Auto-generated from code

**ReDoc**: http://localhost:8000/redoc
- Alternative documentation format

---

## Testing

### Run Phase 3 Tests
```bash
cd backend
pytest tests/test_phase3.py -v
```

Expected tests:
- ✅ Risk engine classification
- ✅ Health endpoint
- ✅ Transaction schema validation
- ✅ Prediction response structure

### Manual Endpoint Testing
```bash
# Test prediction with valid data
curl -X POST http://localhost:8000/api/transactions/predict \
  -H "Content-Type: application/json" \
  -d @sample_transaction.json

# List transactions
curl http://localhost:8000/api/transactions?page=1

# Get dashboard summary
curl http://localhost:8000/api/dashboard/summary
```

---

## Key Features

✅ **Real Model**: Uses actual trained XGBoost from Phase 2  
✅ **Real Data**: Transactions stored in PostgreSQL  
✅ **Real Predictions**: No hardcoded values  
✅ **Error Handling**: Validation and helpful error messages  
✅ **Database Storage**: Predictions persisted  
✅ **API Documentation**: Swagger + ReDoc  
✅ **Monitoring**: ML service status, health checks  

---

## Troubleshooting

### ML Service Not Loading
```
Error: Failed to load ML artifacts
```
**Solution**: Check artifact paths exist:
```bash
ls -la ml/artifacts/
# If missing, run Phase 2: python -m ml.src.train_pipeline
```

### Database Connection Error
```
Error: Failed to connect to PostgreSQL
```
**Solution**: Ensure PostgreSQL is running:
```bash
pg_isready -h localhost -p 5432
# Start with Docker: docker run -d -p 5432:5432 postgres:15-alpine
```

### Validation Error on Prediction
```
Error: Missing required features
```
**Solution**: Ensure all 30 features are provided:
- Time, V1-V28, Amount
- Check request JSON matches schema

### 503 Service Unavailable
```
ML model not available
```
**Solution**: Check backend logs for ML service initialization failure

---

## API Request Examples

### Complete Valid Request
```json
{
  "Time": 3600,
  "V1": -1.35,
  "V2": -0.73,
  "V3": -0.47,
  "V4": 1.03,
  "V5": -0.50,
  "V6": 0.27,
  "V7": -0.12,
  "V8": 0.21,
  "V9": -0.04,
  "V10": 0.46,
  "V11": 0.34,
  "V12": -0.57,
  "V13": 0.15,
  "V14": -0.22,
  "V15": 0.11,
  "V16": 0.09,
  "V17": -0.07,
  "V18": -0.03,
  "V19": 0.12,
  "V20": -0.18,
  "V21": 0.08,
  "V22": -0.09,
  "V23": 0.03,
  "V24": -0.04,
  "V25": 0.13,
  "V26": -0.07,
  "V27": 0.06,
  "V28": 0.08,
  "Amount": 149.62
}
```

---

## Performance Expectations

- **Prediction latency**: 10-50ms (on single transaction)
- **Model loading**: 2-5 seconds (at startup)
- **Database queries**: 50-200ms (for list endpoints)
- **Concurrent predictions**: Handled by FastAPI async

---

## What's Ready for Phase 4

✅ Prediction API working  
✅ Model loaded and serving predictions  
✅ Transactions stored in database  
✅ Dashboard endpoints functional  

**Next**: Phase 4 - Complete Authentication & Authorization

---

## Interview Explanation (30 seconds)

"In Phase 3, I integrated the real trained XGBoost model from Phase 2 into FastAPI. The application loads the model artifacts at startup, exposes a `/api/transactions/predict` endpoint that accepts transaction features, applies the fitted preprocessor, runs the model, and returns fraud probability with risk classification. Predictions are stored in PostgreSQL for audit trail. The API includes comprehensive error handling, Swagger documentation, health checks, and dashboard endpoints for monitoring fraud trends. All predictions are real model outputs, not hardcoded."

---

## Phase 3 Status

✅ ML Service loads model artifacts  
✅ Risk Engine classifies predictions  
✅ Prediction endpoint working  
✅ Transactions stored in database  
✅ Dashboard endpoints functional  
✅ Error handling implemented  
✅ Tests passing  
✅ API documentation complete  

**Phase 3 READY FOR PRODUCTION** ✅
