"""SQLAlchemy database models for RupeeRadar."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.transaction import Category


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    statements = relationship("Statement", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    recurring_patterns = relationship("RecurringPattern", back_populates="user", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="user", cascade="all, delete-orphan")
    category_preferences = relationship("CategoryPreference", back_populates="user", cascade="all, delete-orphan")


class Statement(Base):
    """Bank statement upload record."""
    __tablename__ = "statements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)  # SHA256 hash
    total_transactions = Column(Integer, default=0)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="statements")
    transactions = relationship("Transaction", back_populates="statement", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="statement", cascade="all, delete-orphan")


class Transaction(Base):
    """Cleaned and categorized transaction."""
    __tablename__ = "transactions"
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'transaction_date'),
        Index('idx_user_category', 'user_id', 'category'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id"), nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    raw_description = Column(String(500), nullable=False)
    cleaned_description = Column(String(500), nullable=False)
    category = Column(SQLEnum(Category), nullable=True, index=True)
    merchant_name = Column(String(255), nullable=True, index=True)
    transaction_type = Column(String(10), nullable=False)  # CREDIT or DEBIT
    is_recurring = Column(Boolean, default=False, index=True)
    recurring_id = Column(Integer, ForeignKey("recurring_patterns.id"), nullable=True)
    is_duplicate = Column(Boolean, default=False)
    category_confidence = Column(Float, default=0.0)
    metadata = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    statement = relationship("Statement", back_populates="transactions")


class RecurringPattern(Base):
    """Detected recurring payment patterns."""
    __tablename__ = "recurring_patterns"
    __table_args__ = (
        Index('idx_user_merchant', 'user_id', 'merchant_name'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    merchant_name = Column(String(255), nullable=False)
    category = Column(SQLEnum(Category), nullable=True)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly, yearly, irregular
    avg_amount = Column(Float, nullable=False)
    last_occurrence = Column(DateTime, nullable=True)
    next_expected = Column(DateTime, nullable=True)
    occurrences_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    amount_variance = Column(Float, default=0.0)  # Percentage variance
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="recurring_patterns")
    transactions = relationship("Transaction", foreign_keys=[Transaction.recurring_id])


class Insight(Base):
    """Generated financial insights."""
    __tablename__ = "insights"
    __table_args__ = (
        Index('idx_user_type', 'user_id', 'insight_type'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id"), nullable=False, index=True)
    insight_text = Column(Text, nullable=False)
    insight_type = Column(String(50), nullable=False)  # spending_pattern, recurring_cost, savings_rate, etc.
    metric_value = Column(String(100), nullable=True)
    metric_unit = Column(String(50), nullable=True)  # percentage, currency, count, etc.
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    is_actionable = Column(Boolean, default=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="insights")
    statement = relationship("Statement", back_populates="insights")


class CategoryPreference(Base):
    """User's custom category preferences and overrides."""
    __tablename__ = "category_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    merchant_pattern = Column(String(255), nullable=False)  # Regex or exact match
    assigned_category = Column(SQLEnum(Category), nullable=False)
    confidence = Column(Float, default=1.0)
    is_manual_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="category_preferences")
