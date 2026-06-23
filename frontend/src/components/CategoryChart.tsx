import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { FinancialMetrics } from '../types/finance'

const COLORS = ['#4edea3', '#adc6ff', '#f59e0b', '#ffb4ab', '#8b5cf6', '#64748b']

interface CategoryChartProps {
  metrics: FinancialMetrics | null
}

export function CategoryChart({ metrics }: CategoryChartProps) {
  const data = metrics
    ? Object.entries(metrics.by_category)
        .filter(([_, value]) => value > 0)
        .map(([name, value]) => ({ name, value }))
    : []

  if (data.length === 0) {
    return (
      <div className="flex h-80 items-center justify-center rounded-xl border border-border bg-surface text-sm text-foreground/60">
        Category breakdown will appear after analysis
      </div>
    )
  }

  return (
    <div className="flex h-80 flex-col rounded-xl border border-border bg-surface p-4">
      <h3 className="mb-2 text-sm font-semibold text-foreground/80">Spending by category</h3>
      <div className="min-h-0 flex-1 w-full min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={250}>
          <PieChart>
            <Pie 
              data={data} 
              dataKey="value" 
              nameKey="name" 
              cx="45%" 
              cy="50%" 
              innerRadius={50}
              outerRadius={80} 
              paddingAngle={2}
              stroke="none"
            >
              {data.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`} 
              contentStyle={{ 
                backgroundColor: 'var(--color-surface-bright)', 
                borderColor: 'var(--color-border)', 
                color: 'var(--color-foreground)', 
                borderRadius: '0.5rem' 
              }}
              itemStyle={{ color: 'var(--color-foreground)' }}
            />
            <Legend 
              layout="vertical" 
              verticalAlign="middle" 
              align="right"
              wrapperStyle={{ fontSize: '13px' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
