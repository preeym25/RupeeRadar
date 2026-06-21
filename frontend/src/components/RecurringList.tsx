import type { RecurringGroup } from '../types/finance'

interface RecurringListProps {
  recurring: RecurringGroup[]
}

export function RecurringList({ recurring }: RecurringListProps) {
  if (recurring.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface p-8 text-center text-sm text-foreground/60">
        Recurring payments will appear after analysis
      </div>
    )
  }

  return (
    <ul className="divide-y divide-border/50 rounded-xl border border-border bg-surface">
      {recurring.map((item) => (
        <li key={item.id} className="flex items-center justify-between px-4 py-3 text-sm">
          <div>
            <p className="font-medium text-foreground">{item.label}</p>
            <p className="text-foreground/60 capitalize">
              {item.type} · {item.frequency}
            </p>
          </div>
          <p className="font-semibold text-foreground">
            ₹{item.monthly_estimate.toLocaleString('en-IN')}/mo
          </p>
        </li>
      ))}
    </ul>
  )
}
