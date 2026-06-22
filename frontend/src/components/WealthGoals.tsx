import { Target, ArrowRight } from 'lucide-react'

export function WealthGoals() {
  return (
    <div className="glass-panel p-lg rounded-2xl hairline-border flex flex-col justify-between group cursor-pointer overflow-hidden relative">
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 rounded-full blur-3xl opacity-50 group-hover:opacity-100 transition-opacity"></div>
      <div className="flex justify-between items-start relative z-10">
        <span className="text-primary p-2 bg-primary/10 rounded-full">
          <Target size={24} />
        </span>
        <span className="text-on-surface-variant group-hover:translate-x-1 transition-transform">
          <ArrowRight size={20} />
        </span>
      </div>
      <div className="mt-8 relative z-10">
        <h4 className="text-label-sm font-bold text-on-surface-variant uppercase tracking-widest">Active Goals</h4>
        <p className="font-serif text-title-md mt-1 text-foreground">Emergency Fund</p>
        <div className="flex justify-between text-xs text-on-surface-variant mt-3 mb-1 font-mono-data">
          <span>₹1.5L / ₹3.0L</span>
          <span className="text-primary">50%</span>
        </div>
        <div className="h-1.5 w-full bg-surface-container-high rounded-full overflow-hidden">
          <div className="h-full bg-primary w-[50%] rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
        </div>
      </div>
    </div>
  )
}
