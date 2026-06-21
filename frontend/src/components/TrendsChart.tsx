import { useState, useMemo } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Transaction } from '../types/finance'

interface TrendsChartProps {
  transactions: Transaction[]
}

type Interval = 'Daily' | 'Weekly' | 'Monthly' | 'Yearly'
const INTERVALS: Interval[] = ['Daily', 'Weekly', 'Monthly', 'Yearly']

function getWeekString(dateString: string) {
  const d = new Date(dateString)
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7))
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  const weekNo = Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7)
  return `${d.getUTCFullYear()}-W${weekNo.toString().padStart(2, '0')}`
}

export function TrendsChart({ transactions }: TrendsChartProps) {
  const [interval, setInterval] = useState<Interval>('Monthly')

  const { data, total, percentChange } = useMemo(() => {
    const debits = transactions.filter(t => t.type === 'debit')
    debits.sort((a, b) => a.date.localeCompare(b.date))
    
    const grouped: Record<string, number> = {}
    
    debits.forEach(t => {
      let key = ''
      switch(interval) {
        case 'Daily':
          key = t.date
          break
        case 'Weekly':
          key = getWeekString(t.date)
          break
        case 'Monthly':
          key = t.date.substring(0, 7)
          break
        case 'Yearly':
          key = t.date.substring(0, 4)
          break
      }
      grouped[key] = (grouped[key] || 0) + t.amount
    })
    
    const sortedKeys = Object.keys(grouped).sort()
    const chartData = sortedKeys.map(key => {
      let display = key
      if (interval === 'Monthly') {
        const [y, m] = key.split('-')
        const d = new Date(parseInt(y), parseInt(m) - 1)
        display = d.toLocaleString('default', { month: 'short' }) + ` '${y.slice(2)}`
      } else if (interval === 'Yearly') {
        display = key
      } else if (interval === 'Weekly') {
        display = key.replace('-W', ' Wk')
      } else if (interval === 'Daily') {
        const [y, m, d] = key.split('-')
        display = `${parseInt(d)} ${new Date(parseInt(y), parseInt(m)-1).toLocaleString('default', { month: 'short' })}`
      }
      return { key, display, amount: grouped[key] }
    })

    const totalSpend = chartData.reduce((sum, item) => sum + item.amount, 0)
    let change = 0
    if (chartData.length >= 2) {
      const last = chartData[chartData.length - 1].amount
      const prev = chartData[chartData.length - 2].amount
      if (prev > 0) {
        change = ((last - prev) / prev) * 100
      }
    }

    return { data: chartData, total: totalSpend, percentChange: change }
  }, [transactions, interval])

  if (transactions.length === 0) {
    return (
      <div className="flex h-[400px] items-center justify-center rounded-xl border border-border bg-surface text-sm text-foreground/60">
        Trends will appear after analysis
      </div>
    )
  }

  return (
    <div className="flex h-[450px] flex-col rounded-xl border border-border bg-surface p-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-foreground">Spend Trends</h3>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-foreground">
              ₹{total.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
            {data.length >= 2 && (
              <span className={`text-sm font-medium ${percentChange > 0 ? 'text-error' : 'text-secondary'}`}>
                {percentChange > 0 ? '+' : ''}{percentChange.toFixed(1)}% vs last {interval.toLowerCase().replace('ly', '')}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex rounded-lg bg-surface-bright p-1">
          {INTERVALS.map(int => (
            <button
              key={int}
              onClick={() => setInterval(int)}
              className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                interval === int
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'text-foreground/70 hover:text-foreground'
              }`}
            >
              {int}
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-0 flex-1 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" opacity={0.5} />
            <XAxis 
              dataKey="display" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: 'var(--color-foreground)', opacity: 0.7 }} 
              dy={10}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: 'var(--color-foreground)', opacity: 0.7 }}
              tickFormatter={(value) => `₹${value >= 1000 ? (value / 1000).toFixed(0) + 'k' : value}`}
            />
            <Tooltip 
              formatter={(value: any) => [`₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, 'Spend']}
              labelStyle={{ color: 'var(--color-foreground)' }}
              contentStyle={{ 
                backgroundColor: 'var(--color-surface-bright)', 
                borderColor: 'var(--color-border)', 
                color: 'var(--color-foreground)', 
                borderRadius: '0.5rem' 
              }}
            />
            <Area 
              type="monotone" 
              dataKey="amount" 
              stroke="var(--color-primary)" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorSpend)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
