-- FraudGuard AI Database Schema
-- PostgreSQL

-- Create ENUM types
CREATE TYPE risk_level_enum AS ENUM ('LOW', 'MEDIUM', 'HIGH');
CREATE TYPE prediction_enum AS ENUM ('legitimate', 'fraud');
CREATE TYPE alert_status_enum AS ENUM ('OPEN', 'REVIEWED', 'RESOLVED');

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Transaction details
    amount FLOAT NOT NULL,
    transaction_type VARCHAR(50),
    transaction_hour INTEGER,
    device_type VARCHAR(50),
    location VARCHAR(255),
    
    -- Risk features
    new_device BOOLEAN DEFAULT FALSE,
    location_change BOOLEAN DEFAULT FALSE,
    failed_attempts INTEGER DEFAULT 0,
    account_age INTEGER,  -- Days
    previous_transaction_count INTEGER DEFAULT 0,
    
    -- ML Predictions
    fraud_probability FLOAT,
    risk_score FLOAT,
    risk_level risk_level_enum,
    prediction prediction_enum,
    
    -- Risk factors and explanations
    risk_factors TEXT,  -- JSON
    shap_values TEXT,   -- JSON
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_risk_level ON transactions(risk_level);
CREATE INDEX idx_transactions_prediction ON transactions(prediction);

-- Fraud alerts table
CREATE TABLE fraud_alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_id INTEGER NOT NULL UNIQUE REFERENCES transactions(id) ON DELETE CASCADE,
    
    -- Alert details
    status alert_status_enum DEFAULT 'OPEN' NOT NULL,
    risk_score FLOAT NOT NULL,
    reason TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_fraud_alerts_user_id ON fraud_alerts(user_id);
CREATE INDEX idx_fraud_alerts_transaction_id ON fraud_alerts(transaction_id);
CREATE INDEX idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_fraud_alerts_created_at ON fraud_alerts(created_at);

-- Model versions table
CREATE TABLE model_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    training_date TIMESTAMP NOT NULL,
    
    -- Dataset info
    dataset_name VARCHAR(255),
    dataset_size INTEGER,
    fraud_percentage FLOAT,
    
    -- Performance metrics
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    roc_auc FLOAT,
    pr_auc FLOAT,
    
    -- Metadata
    metadata TEXT,  -- JSON
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_model_versions_version ON model_versions(version);
CREATE INDEX idx_model_versions_is_active ON model_versions(is_active);

-- Create a materialized view for dashboard summary
CREATE VIEW dashboard_summary AS
SELECT
    (SELECT COUNT(*) FROM transactions) as total_transactions,
    (SELECT COUNT(*) FROM transactions WHERE prediction = 'fraud') as fraud_detected,
    (SELECT COUNT(*) FROM transactions WHERE risk_level = 'HIGH') as high_risk_transactions,
    (SELECT AVG(risk_score) FROM transactions WHERE risk_score IS NOT NULL) as avg_risk_score;

-- Create a view for recent fraud
CREATE VIEW recent_fraud AS
SELECT
    t.id,
    t.user_id,
    t.amount,
    t.prediction,
    t.risk_score,
    t.risk_level,
    t.created_at,
    u.username
FROM transactions t
JOIN users u ON t.user_id = u.id
WHERE t.prediction = 'fraud'
ORDER BY t.created_at DESC
LIMIT 50;
