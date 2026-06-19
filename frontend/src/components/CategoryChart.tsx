import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { FinancialMetrics } from '../types/finance'

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']

interface CategoryChartProps {
  metrics: FinancialMetrics | null
}

export function CategoryChart({ metrics }: CategoryChartProps) {
  const data = metrics
    ? Object.entries(metrics.by_category).map(([name, value]) => ({ name, value }))
    : []

  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl border border-slate-200 bg-white text-sm text-slate-500">
        Category breakdown will appear after analysis
      </div>
    )
  }

  return (
    <div className="h-64 rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="mb-2 text-sm font-semibold text-slate-700">Spending by category</h3>
      <ResponsiveContainer width="100%" height="90%">
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
