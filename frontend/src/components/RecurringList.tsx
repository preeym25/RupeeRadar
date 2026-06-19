import type { RecurringGroup } from '../types/finance'

interface RecurringListProps {
  recurring: RecurringGroup[]
}

export function RecurringList({ recurring }: RecurringListProps) {
  if (recurring.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
        Recurring payments will appear after analysis
      </div>
    )
  }

  return (
    <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white">
      {recurring.map((item) => (
        <li key={item.id} className="flex items-center justify-between px-4 py-3 text-sm">
          <div>
            <p className="font-medium text-slate-800">{item.label}</p>
            <p className="text-slate-500">
              {item.type} · {item.frequency}
            </p>
          </div>
          <p className="font-semibold text-slate-900">
            ₹{item.monthly_estimate.toLocaleString('en-IN')}/mo
          </p>
        </li>
      ))}
    </ul>
  )
}
