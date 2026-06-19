import type { Transaction } from '../types/finance'

interface TransactionTableProps {
  transactions: Transaction[]
}

export function TransactionTable({ transactions }: TransactionTableProps) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
        No transactions to display
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
          <tr>
            <th className="px-4 py-3 font-medium">Date</th>
            <th className="px-4 py-3 font-medium">Description</th>
            <th className="px-4 py-3 font-medium">Category</th>
            <th className="px-4 py-3 font-medium">Amount</th>
            <th className="px-4 py-3 font-medium">Recurring</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn) => (
            <tr key={txn.id} className="border-b border-slate-100">
              <td className="px-4 py-3 whitespace-nowrap">{txn.date}</td>
              <td className="px-4 py-3 max-w-xs truncate" title={txn.description_raw}>
                {txn.description_clean}
              </td>
              <td className="px-4 py-3">{txn.category ?? 'Other'}</td>
              <td className="px-4 py-3 whitespace-nowrap">
                {txn.type === 'debit' ? '-' : '+'}₹{txn.amount.toLocaleString('en-IN')}
              </td>
              <td className="px-4 py-3">{txn.is_recurring ? 'Yes' : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
