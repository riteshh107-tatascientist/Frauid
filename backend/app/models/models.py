"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    """User model for authentication"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    fraud_alerts = relationship("FraudAlert", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Prediction(str, enum.Enum):
    """Prediction enumeration"""
    LEGITIMATE = "legitimate"
    FRAUD = "fraud"


class Transaction(Base):
    """Transaction model for storing transaction data and predictions"""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=True)
    transaction_hour = Column(Integer, nullable=True)
    device_type = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Risk features
    new_device = Column(Boolean, default=False, nullable=True)
    location_change = Column(Boolean, default=False, nullable=True)
    failed_attempts = Column(Integer, default=0, nullable=True)
    account_age = Column(Integer, nullable=True)  # Days
    previous_transaction_count = Column(Integer, default=0, nullable=True)
    
    # ML Predictions
    fraud_probability = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    prediction = Column(Enum(Prediction), nullable=True)
    
    # Risk factors and explanations
    risk_factors = Column(Text, nullable=True)  # JSON stored as text
    shap_values = Column(Text, nullable=True)  # JSON stored as text
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    fraud_alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, risk_level={self.risk_level})>"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration"""
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    RESOLVED = "RESOLVED"


class FraudAlert(Base):
    """Fraud alert model for high-risk transactions"""
    
    __tablename__ = "fraud_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True, unique=True)
    
    # Alert details
    status = Column(Enum(AlertStatus), default=AlertStatus.OPEN, nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="fraud_alerts")
    transaction = relationship("Transaction", back_populates="fraud_alerts")
    
    def __repr__(self):
        return f"<FraudAlert(id={self.id}, transaction_id={self.transaction_id}, status={self.status})>"


class ModelVersion(Base):
    """Model version and metadata tracking"""
    
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False, index=True)
    model_type = Column(String(100), nullable=False)
    training_date = Column(DateTime, nullable=False)
    
    # Dataset info
    dataset_name = Column(String(255), nullable=True)
    dataset_size = Column(Integer, nullable=True)
    fraud_percentage = Column(Float, nullable=True)
    
    # Performance metrics
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    roc_auc = Column(Float, nullable=True)
    pr_auc = Column(Float, nullable=True)
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON stored as text
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ModelVersion(id={self.id}, version={self.version}, model_type={self.model_type})>"
