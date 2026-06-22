import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { TrendsChart } from '../components/TrendsChart'
import { RecurringList } from '../components/RecurringList'
import { ReportView } from '../components/ReportView'
import { SummaryCards } from '../components/SummaryCards'
import { TransactionTable } from '../components/TransactionTable'
import { WealthGoals } from '../components/WealthGoals'
import { PortfolioAudit } from '../components/PortfolioAudit'
import type { AnalysisResult } from '../types/finance'

type Tab = 'overview' | 'transactions' | 'recurring' | 'portfolio_audit' | 'report'

export function DashboardPage() {
  const location = useLocation()
  const result = (location.state as { result?: AnalysisResult } | null)?.result ?? null
  const [tab, setTab] = useState<Tab>('overview')

  if (!result) {
    return (
      <div className="glass-panel rounded-xl border border-outline-variant/10 p-10 text-center mx-auto max-w-2xl mt-10">
        <p className="text-on-surface-variant mb-4">No analysis yet. Upload a bank statement to get started.</p>
        <Link
          to="/"
          className="inline-block rounded-md bg-primary px-6 py-3 text-sm font-bold text-primary-foreground hover:bg-primary/90 transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] hover:shadow-[0_0_25px_rgba(16,185,129,0.5)]"
        >
          Upload statement
        </Link>
      </div>
    )
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: 'overview', label: 'Overview' },
    { id: 'transactions', label: 'Ledger' },
    { id: 'recurring', label: 'Recurring' },
    { id: 'portfolio_audit', label: 'Portfolio Audit' },
    { id: 'report', label: 'Report' },
  ]

  return (
    <div className="space-y-xl">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-[32px] font-bold text-foreground">Dashboard</h1>
          <p className="text-sm font-medium text-on-surface-variant uppercase tracking-widest break-all">Source: {result.filename}</p>
        </div>
        <Link
          to="/"
          className="rounded-xl bg-primary px-6 py-2.5 text-sm font-bold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 active:scale-95"
        >
          New upload
        </Link>
      </div>

      {/* Hero Stats Row */}
      <SummaryCards metrics={result.metrics} />

      {/* Tabs */}
      <nav className="flex flex-wrap space-x-6 border-b border-outline-variant/10">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`pb-3 text-sm font-bold uppercase tracking-widest transition-all relative ${
              tab === t.id
                ? 'text-primary'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {t.label}
            {tab === t.id && (
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-t-full shadow-[0_-2px_10px_rgba(16,185,129,0.5)]"></div>
            )}
          </button>
        ))}
      </nav>

      {/* Tab Content */}
      <div className="pt-2">
        {tab === 'overview' && (
          <div className="asymmetric-grid">
            <div className="col-span-1 md:col-span-2">
              <TrendsChart transactions={result.transactions} />
            </div>
            <div className="col-span-1 flex flex-col gap-lg">
              <WealthGoals />
              <div className="glass-panel p-lg rounded-2xl hairline-border flex-1 flex flex-col">
                <h4 className="text-label-sm font-bold text-on-surface-variant uppercase tracking-widest mb-4">Top Insights</h4>
                <div className="space-y-4 overflow-y-auto custom-scrollbar flex-1 pr-2">
                   {result.insights.slice(0, 3).map((insight, idx) => (
                     <div key={idx} className="border-l-2 border-primary/50 pl-3 py-1">
                       <p className="text-sm font-bold text-foreground">{insight.title}</p>
                       <p className="text-xs text-foreground/90">{insight.body}</p>
                     </div>
                   ))}
                </div>
              </div>
            </div>
          </div>
        )}
        
        {tab === 'transactions' && (
          <div className="glass-panel rounded-2xl hairline-border overflow-hidden">
            <TransactionTable transactions={result.transactions} />
          </div>
        )}
        
        {tab === 'recurring' && (
          <div className="glass-panel rounded-2xl hairline-border overflow-hidden p-6">
            <RecurringList recurring={result.recurring} />
          </div>
        )}
        
        {tab === 'portfolio_audit' && <PortfolioAudit result={result} />}
        
        {tab === 'report' && (
          <div className="glass-panel rounded-2xl hairline-border overflow-hidden p-6">
            <ReportView jobId={result.job_id} />
          </div>
        )}
      </div>
    </div>
  )
}
