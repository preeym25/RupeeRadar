import { useCallback, useState } from 'react'
import { analyzeStatement } from '../api/client'
import type { AnalysisResult } from '../types/finance'

export function useAnalysis() {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyze = useCallback(async (file: File) => {
    setLoading(true)
    setError(null)
    try {
      const data = await analyzeStatement(file)
      setResult(data)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const reset = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])

  return { result, loading, error, analyze, reset }
}
