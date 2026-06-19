import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { CategoryChart } from '../components/CategoryChart'
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
      <div className="rounded-xl border border-slate-200 bg-white p-10 text-center">
        <p className="text-slate-600">No analysis yet. Upload a bank statement to get started.</p>
        <Link
          to="/"
          className="mt-4 inline-block rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
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
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500">{result.filename}</p>
        </div>
        <Link
          to="/"
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          New upload
        </Link>
      </div>

      <SummaryCards metrics={result.metrics} />

      <nav className="flex flex-wrap gap-2">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-lg px-4 py-2 text-sm font-medium ${
              tab === t.id
                ? 'bg-emerald-600 text-white'
                : 'bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      {tab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-2">
          <CategoryChart metrics={result.metrics} />
          <InsightCards insights={result.insights.slice(0, 3)} />
        </div>
      )}
      {tab === 'transactions' && <TransactionTable transactions={result.transactions} />}
      {tab === 'recurring' && <RecurringList recurring={result.recurring} />}
      {tab === 'insights' && <InsightCards insights={result.insights} />}
      {tab === 'report' && <ReportView jobId={result.job_id} />}
    </div>
  )
}
