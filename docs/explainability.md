# SHAP Explainability in FraudGuard AI

## What is SHAP?

SHAP (SHapley Additive exPlanations) is a game-theoretic approach to explain the output of any machine learning model.

It connects game theory and local explanations, ensuring that each prediction is explained by its attributive values from a coalition game.

### Key Concepts

**Shapley Value**: A concept from game theory where each player (feature) receives a fair share of the payoff based on their contribution to the total outcome.

**SHAP Value for ML**: The amount that a feature contributes to changing the model's output from the base value to the actual prediction.

## How SHAP Works in FraudGuard

### 1. Base Value (Expected Model Output)

The base value is the model's average prediction when no features are considered.

```
base_value = average(all_predictions)  # ~0.17% fraud rate
```

### 2. SHAP Values (Feature Contributions)

For each feature in each prediction, SHAP calculates:

```
shap_value = contribution of feature to changing from base_value to actual_prediction
```

### 3. SHAP Additive Property

The fundamental property of SHAP:

```
base_value + Σ(all_shap_values) ≈ model_output
```

**Example**:
```
base_value (0.002) 
+ V14 contribution (0.42)
+ V10 contribution (-0.15)
+ V7 contribution (0.28)
+ ... (26 more features)
_________________________________
= fraud_probability (0.934)
```

## SHAP Explainer Types

### TreeExplainer (Used in FraudGuard)

Optimized for tree-based models (XGBoost, Random Forest, LightGBM).

**Why TreeExplainer for XGBoost?**
- Native understanding of tree structure
- Efficient computation
- Exact SHAP values for tree models
- ~10x faster than generic explainer

### LinearExplainer

For linear models (Logistic Regression, Linear SVM).

### Generic Explainer

Falls back for unsupported models.

## Feature Contribution Interpretation

### SHAP Value Sign

```
SHAP > 0  → Feature contributes toward FRAUD class
SHAP < 0  → Feature contributes toward LEGITIMATE class
SHAP ≈ 0  → Feature has minimal contribution
```

### Example Interpretation

**Transaction 1: High-Risk Prediction**
```
Feature V14: +0.42 shap_value (toward fraud)
    → This feature's value pushed the prediction toward fraud
    
Feature V10: -0.15 shap_value (toward legitimate)
    → This feature's value pushed the prediction toward legitimate
    
Net effect: V14 contribution > V10 contribution → Fraud prediction
```

## Dataset Feature Limitations

### Anonymized Features (V1-V28)

The Kaggle Credit Card Fraud Detection dataset features are anonymized using PCA.

**What this means**:
- Original features transformed via Principal Component Analysis
- Cannot interpret as: location, device, merchant category, etc.
- Can only interpret as: "this component contributes X amount"

**Example**:
```
❌ WRONG: "V14 is a suspicious country indicator"
❌ WRONG: "V10 is a risky device"

✅ RIGHT: "V14 (PCA component 14) contributed 0.42 toward the fraud prediction"
✅ RIGHT: "V10 (PCA component 10) contributed -0.15 toward the legitimate prediction"
```

## Using Explanations in Practice

### Step 1: Make a Prediction

```
POST /api/transactions/predict
{
  "Time": 0.0,
  "V1": 1.234,
  ...,
  "Amount": 123.45
}

Response:
{
  "prediction": "FRAUD",
  "fraud_probability": 0.934
}
```

### Step 2: Request Explanation

```
GET /api/transactions/{id}/explanation?top_n=10

Response:
{
  "top_features": [
    {
      "feature": "V14",
      "shap_value": 0.42,
      "direction": "toward_fraud",
      "impact": "high"
    },
    ...
  ]
}
```

### Step 3: Interpret Results

1. **Look at top features** - which features contributed most?
2. **Check directions** - which pushed toward fraud vs legitimate?
3. **Assess confidence** - high-impact features indicate stronger signal
4. **Consider context** - automated fraud detection is not proof

## Important Disclaimers

### What SHAP Explains

✅ Which features the model used  
✅ How much each feature contributed  
✅ Direction of contribution (fraud vs legitimate)  
✅ Relative importance ranking  

### What SHAP Does NOT Explain

❌ Why this is actually fraud (no ground truth)  
❌ Real-world interpretation (features are anonymized)  
❌ Causation (only correlation in model)  
❌ Proof of fraud (only model signal)  

### Using Predictions Responsibly

1. **Model signal only** - use as one input in fraud detection workflow
2. **Not proof** - explanations show model logic, not proof of fraud
3. **Dataset bias** - model trained on this specific dataset
4. **Anonymized features** - cannot be interpreted as real business factors
5. **Historical data** - patterns may change over time

## SHAP Calculations Details

### Computational Process

1. **Load trained model** - XGBoost from Phase 2
2. **Preprocess features** - RobustScaler transformation (same as training)
3. **Calculate SHAP values** - TreeExplainer.shap_values()
4. **Extract base value** - explainer.expected_value
5. **Build explanations** - rank features, calculate impacts
6. **Return results** - structured response

### Performance

- **Time per transaction**: 50-200ms (TreeExplainer optimized)
- **Memory usage**: Minimal (no large arrays stored)
- **Scaling**: Can handle 100+ predictions/second
- **Caching**: Currently not cached (fresh calculation per request)

## API Reference

### Endpoints

#### Get Transaction Explanation
```
GET /api/transactions/{transaction_id}/explanation?top_n=10

Parameters:
- transaction_id (required): ID of transaction
- top_n (optional): 1-20, default 10

Authorization: Bearer token required
Response: TransactionExplanationResponse
```

#### On-Demand Explanation
```
POST /api/transactions/explain?top_n=10

Body: PredictionRequest with features
Authorization: Bearer token required
Response: ExplanationResponse
```

#### Explainer Health
```
GET /api/health/explainer

Response:
{
  "status": "healthy|unavailable",
  "explainability_available": true|false
}
```

## Troubleshooting

### "Explanation service temporarily unavailable"

**Cause**: SHAP explainer not initialized or model not loaded

**Solution**:
1. Check ML Service is healthy: `GET /api/health`
2. Check SHAP service: `GET /api/health/explainer`
3. Review application startup logs

### "Feature not found in transaction"

**Cause**: Transaction missing required feature values

**Solution**:
1. Verify all 30 features provided
2. Check feature order matches metadata
3. Ensure all values are numeric

### "Missing required features: {features}"

**Cause**: Prediction request missing features

**Solution**:
1. Include all 30 required features
2. V1-V28, Time, Amount required
3. No extra features allowed

### "Transaction not found"

**Cause**: 
- Transaction doesn't exist
- Or you don't have permission to view it

**Solution**:
1. Users can only view their own transactions
2. Admins can view any transaction
3. Verify transaction ID is correct

## Advanced Topics

### SHAP Base Value

The base value represents the model's expected output when no features are observed.

For fraud detection, this is:
```
base_value ≈ fraud_percentage_in_training_data ≈ 0.17%
```

This is why even a legitimate transaction might show small positive contributions - we're starting from a low base.

### SHAP Value Interaction

Current implementation shows individual SHAP values. Future enhancement could show feature interactions (e.g., V1 and V2 together).

### Shapley Fairness

SHAP values ensure fairness: each feature gets credit for its actual contribution, as determined by Shapley values from cooperative game theory.

### Limitations

1. **Computational cost** - SHAP can be expensive for complex models
2. **Background data** - Uses 100 samples for TreeExplainer (affects accuracy slightly)
3. **Local explanations only** - Explains individual predictions, not global model
4. **No causation** - Shows correlation in model, not real causation
5. **Dataset dependent** - Explanations reflect training data patterns

## Example Transaction Breakdown

### Scenario: Flagged as HIGH RISK (94.2% fraud probability)

```
Base Value: 0.002346 (average transaction)

Top Contributing Factors:
1. V14: +0.424 (toward fraud)  [40% of total contribution]
2. V10: -0.152 (toward legitimate) [-14% offset]
3. V17: +0.318 (toward fraud)  [30% of total contribution]
4. V27: +0.204 (toward fraud)  [19% of total contribution]
5. V4:  -0.095 (toward legitimate) [-9% offset]

Sum of all 30 features: +0.932
Final probability: 0.002346 + 0.932 = 0.934342 (94.3%)

Interpretation:
- V14, V17, V27 pushed toward fraud
- V10, V4 pushed toward legitimate (but weaker)
- Net: Strong fraud signal from features 14, 17, 27
- Model confidence: HIGH (multiple strong signals)
```

## Best Practices

1. **Always check top features** - understand what drove the prediction
2. **Look for patterns** - do same features appear for similar transactions?
3. **Consider business context** - model signal + business rules + manual review
4. **Track over time** - monitor if SHAP patterns change
5. **Test edge cases** - verify explanations make sense for boundary transactions

## Future Enhancements

### Planned
- Feature interaction analysis
- Global model explanations (not just per-transaction)
- SHAP value caching for performance
- Custom background data selection

### Optional
- Async SHAP calculation for high-load scenarios
- SHAP dependency plots
- Force plots for visualization
- Waterfall plots for narrative explanations

## References

- SHAP Paper: https://arxiv.org/abs/1705.07874
- SHAP GitHub: https://github.com/slundberg/shap
- SHAP Documentation: https://shap.readthedocs.io/
- XGBoost + SHAP: https://shap.readthedocs.io/en/latest/example_notebooks/trees.html

## Questions?

For implementation questions, refer to:
- `PHASE7-COMPLETE.md` - Implementation details
- `backend/app/services/explainability_service.py` - Code implementation
- `frontend/src/components/SHAPExplanation.tsx` - Frontend visualization
