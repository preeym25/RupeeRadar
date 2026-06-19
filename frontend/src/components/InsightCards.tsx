import type { Insight } from '../types/finance'

interface InsightCardsProps {
  insights: Insight[]
}

export function InsightCards({ insights }: InsightCardsProps) {
  if (insights.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
        Personalized insights will appear after analysis
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {insights.map((insight) => (
        <article key={insight.id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">{insight.title}</h3>
          <p className="mt-2 text-sm text-slate-600">{insight.body}</p>
          {insight.amount != null && (
            <p className="mt-3 text-sm font-medium text-emerald-700">
              ₹{insight.amount.toLocaleString('en-IN')}
            </p>
          )}
        </article>
      ))}
    </div>
  )
}
