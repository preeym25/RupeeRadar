import { Sparkles, AlertCircle } from 'lucide-react'
import type { Transaction } from '../types/finance'

interface TransactionTableProps {
  transactions: Transaction[]
}

export function TransactionTable({ transactions }: TransactionTableProps) {
  const getCategoryClasses = (category: string | null) => {
    switch (category?.toLowerCase()) {
      case 'bills':
      case 'rent':
      case 'emi':
      case 'insurance':
        return 'bg-[var(--color-cat-bills-bg)] text-[var(--color-cat-bills-text)]'
      case 'food':
      case 'groceries':
        return 'bg-[var(--color-cat-food-bg)] text-[var(--color-cat-food-text)]'
      case 'shopping':
        return 'bg-[var(--color-cat-shopping-bg)] text-[var(--color-cat-shopping-text)]'
      case 'travel':
        return 'bg-[var(--color-cat-travel-bg)] text-[var(--color-cat-travel-text)]'
      case 'subscriptions':
        return 'bg-[var(--color-cat-subs-bg)] text-[var(--color-cat-subs-text)]'
      default:
        return 'bg-[var(--color-cat-other-bg)] text-[var(--color-cat-other-text)]'
    }
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface p-8 text-center text-sm text-foreground/60">
        No transactions to display
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border bg-surface">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-border bg-surface-bright text-foreground/70">
          <tr>
            <th className="px-4 py-3 font-medium">Date</th>
            <th className="px-4 py-3 font-medium">Description</th>
            <th className="px-4 py-3 font-medium">Category</th>
            <th className="px-4 py-3 font-medium">Amount</th>
            <th className="px-4 py-3 font-medium">Recurring</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border/50 text-foreground">
          {transactions.map((txn) => (
            <tr key={txn.id} className="hover:bg-primary/5 transition-colors">
              <td className="px-4 py-3 whitespace-nowrap">{txn.date}</td>
              <td className="px-4 py-3 max-w-xs truncate" title={txn.description_raw}>
                {txn.description_clean}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${getCategoryClasses(txn.category)}`}>
                    {txn.category ?? 'Other'}
                  </span>
                  {txn.metadata?.source === 'llm' ? (
                    <span title="Categorized by AI"><Sparkles size={14} className="text-secondary" /></span>
                  ) : txn.category_confidence < 0.8 ? (
                    <span title="Low confidence categorization"><AlertCircle size={14} className="text-amber-500" /></span>
                  ) : null}
                </div>
              </td>
              <td className={`px-4 py-3 font-medium whitespace-nowrap ${txn.type === 'credit' ? 'text-positive' : 'text-negative'}`}>
                {txn.type === 'debit' ? '-' : '+'}₹{txn.amount.toLocaleString('en-IN')}
              </td>
              <td className="px-4 py-3">
                {txn.is_recurring ? (
                  <span className="inline-flex rounded-full bg-secondary/10 px-2.5 py-0.5 text-xs font-medium text-secondary">
                    Yes
                  </span>
                ) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
