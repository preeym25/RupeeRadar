import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { checkHealth } from '../api/client'
import { UploadZone } from '../components/UploadZone'
import { useAnalysis } from '../hooks/useAnalysis'

export function UploadPage() {
  const navigate = useNavigate()
  const { loading, error, analyze } = useAnalysis()
  const [apiStatus, setApiStatus] = useState<string>('checking')

  useEffect(() => {
    checkHealth()
      .then((h) => setApiStatus(`${h.service} · LLM: ${h.llm_provider} (${h.llm_enabled ? 'on' : 'off'})`))
      .catch(() => setApiStatus('API unreachable'))
  }, [])

  const handleFile = async (file: File) => {
    try {
      const result = await analyze(file)
      navigate('/dashboard', { state: { result } })
    } catch {
      // error surfaced via hook
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Upload statement</h1>
        <p className="mt-1 text-sm text-slate-500">
          Analyze your bank CSV to see where your money goes.
        </p>
        <p className="mt-2 text-xs text-emerald-700">Backend: {apiStatus}</p>
      </div>
      <UploadZone onFileSelect={handleFile} loading={loading} />
      {error && (
        <p className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}
      <p className="text-xs text-slate-400">
        Try the sample file at <code className="text-slate-600">sample_data/sample_statement.csv</code>
      </p>
    </div>
  )
}
