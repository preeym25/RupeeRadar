import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { checkHealth } from '../api/client'
import { UploadZone } from '../components/UploadZone'
import { useAnalysis } from '../hooks/useAnalysis'

export function UploadPage() {
  const navigate = useNavigate()
  const { loading, error, analyze, loadDemoData } = useAnalysis()
  const [apiStatus, setApiStatus] = useState<string>('checking')

  useEffect(() => {
    checkHealth()
      .then((h) => setApiStatus(`${h.service} · LLM: ${h.llm_provider} (${h.llm_enabled ? 'on' : 'off'})`))
      .catch(() => setApiStatus('API unreachable'))
  }, [])

  const handleFile = async (file: File) => {
    try {
      await analyze(file)
      navigate('/dashboard')
    } catch {
      // error surfaced via hook
    }
  }

  const handleDemoLoad = () => {
    loadDemoData()
    navigate('/dashboard')
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Upload statement</h1>
        <p className="mt-1 text-sm text-foreground/60">
          Analyze your bank CSV to see where your money goes.
        </p>
        <p className="mt-2 text-xs text-secondary">Backend: {apiStatus}</p>
      </div>

      <div className="flex flex-col gap-4">
        <UploadZone onFileSelect={handleFile} loading={loading} />
        
        <div className="flex items-center justify-between gap-4 p-4 rounded-xl border border-outline-variant/10 bg-surface-container-low/50">
          <div>
            <p className="text-sm font-bold text-foreground">No bank statement on hand?</p>
            <p className="text-xs text-on-surface-variant">Try RupeeRadar with a simulated bank statement instantly.</p>
          </div>
          <button
            onClick={handleDemoLoad}
            className="rounded-lg bg-primary/10 border border-primary/20 text-primary px-4 py-2 text-sm font-bold hover:bg-primary/20 transition-all active:scale-95 whitespace-nowrap shadow-sm shadow-primary/5 cursor-pointer"
          >
            Load Demo Data
          </button>
        </div>
      </div>

      {error && (
        <p className="rounded-lg border border-error bg-error/10 px-4 py-3 text-sm text-error">
          {error}
        </p>
      )}
      <p className="text-xs text-foreground/40">
        Try the sample file at <code className="text-foreground/60 bg-surface-bright px-1 py-0.5 rounded">sample_data/sample_statement.csv</code>
      </p>
    </div>
  )
}
