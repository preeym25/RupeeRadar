export type Category =
  | 'Food'
  | 'Travel'
  | 'Shopping'
  | 'Bills'
  | 'EMI'
  | 'Subscriptions'
  | 'Salary'
  | 'Rent'
  | 'Investments'
  | 'Other'

export type TransactionType = 'debit' | 'credit'

export type RecurringType =
  | 'subscription'
  | 'emi'
  | 'rent'
  | 'sip'
  | 'insurance'
  | 'other'

export type RecurringFrequency = 'weekly' | 'monthly' | 'quarterly' | 'yearly'

export type InsightSeverity = 'info' | 'warning' | 'positive'

export type InsightSource = 'template' | 'llm'

export interface Transaction {
  id: string
  date: string
  description_raw: string
  description_clean: string
  amount: number
  type: TransactionType
  merchant: string | null
  category: Category | null
  category_confidence: number
  is_recurring: boolean
  is_duplicate: boolean
  recurring_group_id: string | null
  metadata: Record<string, unknown>
}

export interface RecurringGroup {
  id: string
  label: string
  category: Category
  type: RecurringType
  amount: number
  frequency: RecurringFrequency
  monthly_estimate: number
  transaction_ids: string[]
  next_expected_date: string | null
}

export interface CategorySummary {
  category: Category
  amount: number
  percentage: number
  transaction_count: number
}

export interface MonthlySpend {
  month: string
  amount: number
  transaction_count: number
}

export interface TransactionSummary {
  id: string
  date: string
  description: string
  amount: number
  category: Category | null
}

export interface FinancialMetrics {
  period_start: string
  period_end: string
  total_income: number
  total_spend: number
  savings: number
  savings_rate: number | null
  transaction_count: number
  by_category: Record<string, number>
  top_categories: CategorySummary[]
  biggest_debit: TransactionSummary | null
  biggest_credit: TransactionSummary | null
  monthly_spend: MonthlySpend[]
  recurring_monthly_total: number
}

export interface Insight {
  id: string
  title: string
  body: string
  category: string | null
  amount: number | null
  severity: InsightSeverity
  source: InsightSource
}

export interface AnalysisSummary {
  total_income: number
  total_spend: number
  savings: number
  transaction_count: number
  insight_count: number
}

export interface AnalysisResult {
  job_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  filename: string
  created_at: string
  expires_at: string
  transactions: Transaction[]
  recurring: RecurringGroup[]
  metrics: FinancialMetrics | null
  insights: Insight[]
  summary: AnalysisSummary | null
  error: string | null
}

export interface HealthResponse {
  status: string
  service: string
  llm_provider: string
  llm_enabled: boolean
}
