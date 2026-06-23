import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { analyzeStatement, getAnalysis, deleteAnalysis } from '../api/client'
import type { AnalysisResult } from '../types/finance'
import demoData from '../../../sample_data/sample_analysis_output.json'

interface AnalysisContextType {
  result: AnalysisResult | null
  loading: boolean
  error: string | null
  analyze: (file: File) => Promise<AnalysisResult>
  loadDemoData: () => void
  clearAnalysis: () => Promise<void>
  rehydrateResult: (jobId: string) => Promise<void>
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined)

export function AnalysisProvider({ children }: { children: React.ReactNode }) {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  // Rehydrate on mount
  useEffect(() => {
    const cached = localStorage.getItem('rupee_radar_result')
    if (cached) {
      try {
        setResult(JSON.parse(cached))
      } catch {
        localStorage.removeItem('rupee_radar_result')
      }
    }
  }, [])

  const analyze = useCallback(async (file: File) => {
    setLoading(true)
    setError(null)
    try {
      const data = await analyzeStatement(file)
      setResult(data)
      localStorage.setItem('rupee_radar_result', JSON.stringify(data))
      localStorage.setItem('rupee_radar_job_id', data.job_id)
      return data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Analysis failed'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const loadDemoData = useCallback(() => {
    const data = demoData as unknown as AnalysisResult
    setResult(data)
    localStorage.setItem('rupee_radar_result', JSON.stringify(data))
    localStorage.setItem('rupee_radar_job_id', data.job_id)
  }, [])

  const clearAnalysis = useCallback(async () => {
    const jobId = result?.job_id || localStorage.getItem('rupee_radar_job_id')
    if (jobId) {
      try {
        await deleteAnalysis(jobId)
      } catch (e) {
        console.error("Failed to delete analysis session from server:", e)
      }
    }
    setResult(null)
    setError(null)
    localStorage.removeItem('rupee_radar_result')
    localStorage.removeItem('rupee_radar_job_id')
  }, [result])

  const rehydrateResult = useCallback(async (jobId: string) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getAnalysis(jobId)
      setResult(data)
      localStorage.setItem('rupee_radar_result', JSON.stringify(data))
      localStorage.setItem('rupee_radar_job_id', data.job_id)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch analysis'
      setError(message)
      localStorage.removeItem('rupee_radar_result')
      localStorage.removeItem('rupee_radar_job_id')
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    React.createElement(
      AnalysisContext.Provider,
      { value: { result, loading, error, analyze, loadDemoData, clearAnalysis, rehydrateResult } },
      children
    )
  )
}

export function useAnalysis() {
  const context = useContext(AnalysisContext)
  if (context === undefined) {
    throw new Error('useAnalysis must be used within an AnalysisProvider')
  }
  return context
}
