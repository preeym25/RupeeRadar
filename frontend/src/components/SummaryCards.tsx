import { TrendingUp, Wallet, CreditCard } from 'lucide-react'
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
  if (!metrics) return null;

  const savingsRate = metrics.total_income > 0 
    ? Math.round((metrics.savings / metrics.total_income) * 100) 
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
      <div className="glass-panel p-lg rounded-2xl hairline-border flex flex-col justify-between h-48 relative overflow-hidden group hover:scale-[1.01] transition-transform">
        <div className="absolute -right-8 -top-8 w-32 h-32 bg-primary/10 rounded-full blur-3xl transition-all group-hover:bg-primary/20"></div>
        <div>
          <p className="text-label-sm font-bold uppercase tracking-widest text-on-surface-variant">Net Savings</p>
          <h2 className="font-serif text-[42px] mt-sm leading-none">{formatInr(metrics.savings)}</h2>
        </div>
        <div className="flex items-center gap-sm text-primary">
          <TrendingUp size={18} />
          <span className="font-mono-data text-mono-data">Savings Rate: {savingsRate}%</span>
        </div>
      </div>

      <div className="glass-panel p-lg rounded-2xl hairline-border flex flex-col justify-between h-48 relative overflow-hidden group hover:scale-[1.01] transition-transform">
        <div className="absolute -right-8 -top-8 w-32 h-32 bg-tertiary/10 rounded-full blur-3xl transition-all group-hover:bg-tertiary/20"></div>
        <div>
          <p className="text-label-sm font-bold uppercase tracking-widest text-on-surface-variant">Total Income (YTD)</p>
          <h2 className="font-serif text-[42px] mt-sm leading-none">{formatInr(metrics.total_income)}</h2>
        </div>
        <div className="flex items-center gap-sm text-on-surface-variant">
          <Wallet size={18} />
          <span className="font-mono-data text-mono-data">{metrics.transaction_count} total transactions</span>
        </div>
      </div>

      <div className="glass-panel p-lg rounded-2xl hairline-border flex flex-col justify-between h-48 relative overflow-hidden group hover:scale-[1.01] transition-transform">
        <div className="absolute -right-8 -top-8 w-32 h-32 bg-error/10 rounded-full blur-3xl transition-all group-hover:bg-error/20"></div>
        <div>
          <p className="text-label-sm font-bold uppercase tracking-widest text-on-surface-variant">Total Spend</p>
          <h2 className="font-serif text-[42px] mt-sm leading-none text-foreground">{formatInr(metrics.total_spend)}</h2>
        </div>
        <div className="flex items-center gap-sm text-error">
          <CreditCard size={18} />
          <span className="font-mono-data text-mono-data">Across all categories</span>
        </div>
      </div>
    </div>
  )
}
