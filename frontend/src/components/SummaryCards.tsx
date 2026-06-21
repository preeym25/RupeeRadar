import type { FinancialMetrics } from '../types/finance'

interface SummaryCardsProps {
  metrics: FinancialMetrics | null
}

function formatInr(value: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value)
}

export function SummaryCards({ metrics }: SummaryCardsProps) {
  const items = [
    { label: 'Total Income', value: metrics ? formatInr(metrics.total_income) : '—', colorClass: 'text-positive' },
    { label: 'Total Spend', value: metrics ? formatInr(metrics.total_spend) : '—', colorClass: 'text-foreground' },
    { label: 'Savings', value: metrics ? formatInr(metrics.savings) : '—', colorClass: 'text-positive' },
    {
      label: 'Transactions',
      value: metrics ? String(metrics.transaction_count) : '—',
      colorClass: 'text-foreground'
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <div key={item.label} className="rounded-xl border border-border bg-surface p-5 shadow-sm">
          <p className="text-sm text-foreground/60">{item.label}</p>
          <p className={`mt-2 text-2xl font-bold ${item.colorClass}`}>{item.value}</p>
        </div>
      ))}
    </div>
  )
}
