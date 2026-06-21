from datetime import date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Category(str, Enum):
    FOOD = "Food"
    GROCERIES = "Groceries"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    BILLS = "Bills"
    EMI = "EMI"
    SUBSCRIPTIONS = "Subscriptions"
    SALARY = "Salary"
    RENT = "Rent"
    INVESTMENTS = "Investments"
    OTHER = "Other"


class RawTransaction(BaseModel):
    date: str | None = None
    description: str
    debit: float | None = None
    credit: float | None = None
    balance: float | None = None
    reference: str | None = None
    source_row: int


class Transaction(BaseModel):
    id: str
    date: date
    description_raw: str
    description_clean: str
    amount: float = Field(ge=0)
    type: Literal["debit", "credit"]
    merchant: str | None = None
    category: Category | None = None
    category_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    is_recurring: bool = False
    is_duplicate: bool = False
    recurring_group_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecurringType(str, Enum):
    SUBSCRIPTION = "subscription"
    EMI = "emi"
    RENT = "rent"
    SIP = "sip"
    INSURANCE = "insurance"
    OTHER = "other"


class RecurringFrequency(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class RecurringGroup(BaseModel):
    id: str
    label: str
    category: Category
    type: RecurringType
    amount: float
    frequency: RecurringFrequency
    monthly_estimate: float
    transaction_ids: list[str]
    next_expected_date: date | None = None
