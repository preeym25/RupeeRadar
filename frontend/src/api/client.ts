import type { AnalysisResult, HealthResponse } from '../types/finance'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const detail = typeof body.detail === 'string' ? body.detail : response.statusText
    throw new Error(detail || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/v1/health')
}

export async function analyzeStatement(_file: File): Promise<AnalysisResult> {
  const formData = new FormData()
  formData.append('file', _file)
  return request<AnalysisResult>('/api/v1/analyze', {
    method: 'POST',
    body: formData,
  })
}

export async function getAnalysis(jobId: string): Promise<AnalysisResult> {
  return request<AnalysisResult>(`/api/v1/analyze/${jobId}`)
}

export async function deleteAnalysis(jobId: string): Promise<void> {
  await request<void>(`/api/v1/analyze/${jobId}`, { method: 'DELETE' })
}

export { API_BASE }
