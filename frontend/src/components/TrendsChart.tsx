import { useState, useMemo } from 'react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
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

  const { data } = useMemo(() => {
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

    return { data: chartData }
  }, [transactions, interval])

  if (transactions.length === 0) {
    return (
      <div className="flex h-[450px] items-center justify-center glass-panel rounded-2xl hairline-border text-sm text-on-surface-variant">
        Trends will appear after analysis
      </div>
    )
  }

  return (
    <div className="flex h-[450px] flex-col glass-panel rounded-2xl hairline-border p-lg relative">
      <div className="mb-lg flex flex-wrap items-center justify-between gap-4 relative z-10">
        <div>
          <h3 className="font-serif text-title-md text-foreground">Wealth Trajectory</h3>
          <p className="text-label-sm text-on-surface-variant mt-1">Income vs Expenditure ({interval})</p>
        </div>
        
        <div className="flex gap-sm">
          {INTERVALS.filter(int => int !== 'Yearly').map(int => (
            <button
              key={int}
              onClick={() => setInterval(int)}
              className={`px-md py-xs rounded-full text-label-sm font-bold transition-all ${
                interval === int
                  ? 'bg-primary text-primary-foreground shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                  : 'bg-surface-container-high text-on-surface hover:bg-surface-container-highest'
              }`}
            >
              {int === 'Daily' ? '1D' : int === 'Weekly' ? '1W' : '1M'}
            </button>
          ))}
        </div>
      </div>

      <div className="min-h-0 flex-1 w-full relative z-10 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={300}>
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="glowLine" x1="0%" x2="100%" y1="0%" y2="0%">
                <stop offset="0%" style={{stopColor:'var(--color-primary)', stopOpacity:0.1}} />
                <stop offset="50%" style={{stopColor:'var(--color-primary)', stopOpacity:1}} />
                <stop offset="100%" style={{stopColor:'var(--color-primary)', stopOpacity:0.3}} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur result="coloredBlur" stdDeviation="4" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {/* Removed cartesian grid entirely to match the clean design */}
            <XAxis 
              dataKey="display" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 10, fill: 'var(--color-surface-foreground-variant)', fontFamily: 'monospace' }} 
              dy={15}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fontSize: 12, fill: 'var(--color-surface-foreground-variant)', opacity: 0.5 }}
              tickFormatter={(value) => `₹${value >= 1000 ? (value / 1000).toFixed(0) + 'k' : value}`}
            />
            <Tooltip 
              formatter={(value: any) => [`₹${Number(value).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`, 'Amount']}
              labelStyle={{ color: 'var(--color-surface-foreground-variant)', fontSize: '12px' }}
              contentStyle={{ 
                backgroundColor: 'rgba(16, 20, 21, 0.9)', 
                borderColor: 'rgba(144, 144, 151, 0.2)', 
                color: 'var(--color-foreground)', 
                borderRadius: '8px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
              }}
              itemStyle={{ color: 'var(--color-primary)', fontWeight: 'bold' }}
            />
            <Area 
              type="monotone" 
              dataKey="amount" 
              stroke="var(--color-primary)" 
              strokeWidth={4}
              fillOpacity={0}
              style={{ filter: 'url(#glow)' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
