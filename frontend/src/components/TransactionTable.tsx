import { Sparkles, AlertCircle, ShoppingBag, Utensils, Zap, Car, Repeat, Hash } from 'lucide-react'
import type { Transaction } from '../types/finance'

interface TransactionTableProps {
  transactions: Transaction[]
}

export function TransactionTable({ transactions }: TransactionTableProps) {
  const getCategoryIcon = (category: string | null) => {
    switch (category?.toLowerCase()) {
      case 'bills':
      case 'rent':
      case 'insurance':
        return <Zap size={20} />
      case 'food':
      case 'groceries':
        return <Utensils size={20} />
      case 'shopping':
        return <ShoppingBag size={20} />
      case 'travel':
        return <Car size={20} />
      case 'subscriptions':
      case 'emi':
        return <Repeat size={20} />
      default:
        return <Hash size={20} />
    }
  }

  const getCategoryTheme = (category: string | null) => {
    switch (category?.toLowerCase()) {
      case 'bills':
      case 'rent':
        return 'text-orange-400 bg-orange-400/10'
      case 'food':
        return 'text-yellow-400 bg-yellow-400/10'
      case 'shopping':
        return 'text-purple-400 bg-purple-400/10'
      case 'travel':
        return 'text-blue-400 bg-blue-400/10'
      case 'subscriptions':
        return 'text-pink-400 bg-pink-400/10'
      case 'emi':
        return 'text-red-400 bg-red-400/10'
      case 'income':
      case 'salary':
        return 'text-primary bg-primary/10'
      default:
        return 'text-on-surface-variant bg-surface-container-highest'
    }
  }

  if (transactions.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-on-surface-variant">
        No transactions to display
      </div>
    )
  }

  return (
    <div className="w-full flex flex-col">
      <div className="px-lg py-md border-b border-outline-variant/10 flex justify-between items-center bg-surface-container-high/30">
        <h3 className="font-serif text-title-md">Institutional Ledger</h3>
        <div className="flex gap-md">
          <span className="text-label-sm font-medium text-on-surface-variant flex items-center gap-xs">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span> Live Updates
          </span>
          <button className="text-label-sm font-bold text-primary hover:underline">View All</button>
        </div>
      </div>
      
      <div className="divide-y divide-outline-variant/10">
        {transactions.map((txn) => {
          const theme = getCategoryTheme(txn.category)
          const isCredit = txn.type === 'credit'
          return (
            <div key={txn.id} className="px-lg py-md flex items-center justify-between hover:bg-surface-container-high/40 transition-colors cursor-default group">
              <div className="flex items-center gap-lg">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center border border-outline-variant/10 transition-all ${theme} group-hover:border-primary/30`}>
                  {getCategoryIcon(txn.category)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-title-md text-body-md font-bold">{txn.description_clean}</p>
                    {txn.metadata?.source === 'llm' && (
                      <span title="Categorized by AI"><Sparkles size={12} className="text-primary" /></span>
                    )}
                    {txn.category_confidence < 0.8 && (
                      <span title="Low confidence categorization"><AlertCircle size={12} className="text-error" /></span>
                    )}
                  </div>
                  <p className="text-label-sm text-on-surface-variant capitalize">
                    {txn.category || 'Other'} • {txn.date}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <p className={`font-mono-data text-body-md ${isCredit ? 'text-primary' : 'text-on-surface'}`}>
                  {isCredit ? '+' : '-'}₹{txn.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </p>
                {txn.is_recurring && (
                  <span className="inline-block px-sm py-0.5 mt-1 rounded-full bg-primary/10 text-[10px] text-primary font-bold uppercase tracking-tighter">
                    Recurring
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
