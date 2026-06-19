from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.transaction import Category, RecurringGroup, Transaction


class CategorySummary(BaseModel):
    category: Category
    amount: float
    percentage: float
    transaction_count: int


class MonthlySpend(BaseModel):
    month: str
    amount: float
    transaction_count: int


class TransactionSummary(BaseModel):
    id: str
    date: date
    description: str
    amount: float
    category: Category | None = None


class FinancialMetrics(BaseModel):
    period_start: date
    period_end: date
    total_income: float
    total_spend: float
    savings: float
    savings_rate: float | None = None
    transaction_count: int
    by_category: dict[str, float]
    top_categories: list[CategorySummary]
    biggest_debit: TransactionSummary | None = None
    biggest_credit: TransactionSummary | None = None
    monthly_spend: list[MonthlySpend]
    recurring_monthly_total: float = 0.0


class InsightSeverity(str):
    INFO = "info"
    WARNING = "warning"
    POSITIVE = "positive"


class Insight(BaseModel):
    id: str
    title: str
    body: str
    category: str | None = None
    amount: float | None = None
    severity: Literal["info", "warning", "positive"] = "info"
    source: Literal["template", "llm"] = "template"


class AnalysisSummary(BaseModel):
    total_income: float
    total_spend: float
    savings: float
    transaction_count: int
    insight_count: int


class AnalysisJobStatus(str):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisResult(BaseModel):
    job_id: str
    status: Literal["pending", "processing", "completed", "failed"] = "completed"
    filename: str
    created_at: datetime
    expires_at: datetime
    transactions: list[Transaction] = Field(default_factory=list)
    recurring: list[RecurringGroup] = Field(default_factory=list)
    metrics: FinancialMetrics | None = None
    insights: list[Insight] = Field(default_factory=list)
    summary: AnalysisSummary | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
    llm_provider: str
    llm_enabled: bool
