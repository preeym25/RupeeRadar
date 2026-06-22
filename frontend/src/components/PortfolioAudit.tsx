import type { AnalysisResult } from '../types/finance'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

export function PortfolioAudit({ result }: { result: AnalysisResult }) {
  // Use Emerald green and subtle cool tones for the pie chart
  const COLORS = ['#10b981', '#0ea5e9', '#6366f1', '#8b5cf6', '#d946ef', '#f43f5e', '#334155']

  const expenseData = Object.entries(result.metrics?.by_category || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="font-serif text-title-md text-foreground">Portfolio Audit</h3>
          <p className="text-label-sm text-on-surface-variant">Deep-dive structural analysis of expenditure</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel p-lg rounded-2xl hairline-border flex flex-col items-center">
          <h4 className="text-label-sm font-bold uppercase tracking-widest w-full text-on-surface-variant mb-4">Capital Allocation</h4>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={expenseData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="none"
                >
                  {expenseData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => `₹${value.toLocaleString()}`}
                  contentStyle={{ backgroundColor: 'rgba(16, 20, 21, 0.9)', border: '1px solid rgba(144, 144, 151, 0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#e0e3e5' }}
                />
                <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '12px', color: '#e0e3e5' }}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-lg rounded-2xl hairline-border flex flex-col gap-4">
           <h4 className="text-label-sm font-bold uppercase tracking-widest text-on-surface-variant">Key Findings</h4>
           <div className="space-y-4 flex-1 overflow-y-auto custom-scrollbar pr-2">
             {result.insights.map((insight, idx) => (
               <div key={idx} className="p-4 bg-surface-container-high/50 rounded-xl border border-outline-variant/10">
                 <p className="text-sm font-bold text-foreground">{insight.title}</p>
                 <p className="text-xs text-foreground/80 mt-1">{insight.body}</p>
               </div>
             ))}
           </div>
        </div>
      </div>
    </div>
  )
}
