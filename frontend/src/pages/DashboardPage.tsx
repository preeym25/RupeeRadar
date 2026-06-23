import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { TrendsChart } from '../components/TrendsChart'
import { RecurringList } from '../components/RecurringList'
import { ReportView } from '../components/ReportView'
import { SummaryCards } from '../components/SummaryCards'
import { TransactionTable } from '../components/TransactionTable'
import { WealthGoals } from '../components/WealthGoals'
import { PortfolioAudit } from '../components/PortfolioAudit'
import { useAnalysis } from '../hooks/useAnalysis'

type Tab = 'overview' | 'transactions' | 'recurring' | 'portfolio_audit' | 'report'

export function DashboardPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { result, clearAnalysis } = useAnalysis()
  const tab = (searchParams.get('tab') as Tab) || 'overview'

  const handleNewUpload = async () => {
    await clearAnalysis()
    navigate('/')
  }

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

  const tabTitles = {
    overview: 'Overview',
    transactions: 'Institutional Ledger',
    recurring: 'Recurring Payments',
    portfolio_audit: 'Portfolio Audit',
    report: 'Financial Report Summary',
  }

  return (
    <div className="space-y-xl">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-[32px] font-bold text-foreground">{tabTitles[tab] || 'Dashboard'}</h1>
          <p className="text-sm font-medium text-on-surface-variant uppercase tracking-widest break-all">Source: {result.filename}</p>
        </div>
        <button
          onClick={handleNewUpload}
          className="rounded-xl bg-primary px-6 py-2.5 text-sm font-bold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 active:scale-95 cursor-pointer"
        >
          New upload
        </button>
      </div>

      {/* Hero Stats Row */}
      <SummaryCards metrics={result.metrics} />

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
