import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { CategoryChart } from '../components/CategoryChart'
import { TrendsChart } from '../components/TrendsChart'
import { InsightCards } from '../components/InsightCards'
import { RecurringList } from '../components/RecurringList'
import { ReportView } from '../components/ReportView'
import { SummaryCards } from '../components/SummaryCards'
import { TransactionTable } from '../components/TransactionTable'
import type { AnalysisResult } from '../types/finance'

type Tab = 'overview' | 'transactions' | 'recurring' | 'insights' | 'report'

export function DashboardPage() {
  const location = useLocation()
  const result = (location.state as { result?: AnalysisResult } | null)?.result ?? null
  const [tab, setTab] = useState<Tab>('overview')

  if (!result) {
    return (
      <div className="rounded-xl border border-border bg-surface p-10 text-center">
        <p className="text-foreground/70">No analysis yet. Upload a bank statement to get started.</p>
        <Link
          to="/"
          className="mt-4 inline-block rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Upload statement
        </Link>
      </div>
    )
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'transactions', label: 'Transactions' },
    { id: 'recurring', label: 'Recurring' },
    { id: 'insights', label: 'Insights' },
    { id: 'report', label: 'Report' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-base font-medium text-foreground break-all">{result.filename}</p>
        </div>
        <Link
          to="/"
          className="rounded-md bg-brand-active px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity"
        >
          New upload
        </Link>
      </div>

      <SummaryCards metrics={result.metrics} />

      <nav className="flex flex-wrap space-x-4 border-b border-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`px-3 py-2 text-sm font-medium border-b-2 -mb-[1px] transition-colors ${
              tab === t.id
                ? 'border-brand-active text-brand-active'
                : 'border-transparent text-foreground-variant hover:text-foreground hover:border-border'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'overview' && (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <CategoryChart metrics={result.metrics} />
            <InsightCards insights={result.insights.slice(0, 3)} />
          </div>
          <TrendsChart transactions={result.transactions} />
        </div>
      )}
      {tab === 'transactions' && <TransactionTable transactions={result.transactions} />}
      {tab === 'recurring' && <RecurringList recurring={result.recurring} />}
      {tab === 'insights' && <InsightCards insights={result.insights} />}
      {tab === 'report' && <ReportView jobId={result.job_id} />}
    </div>
  )
}
