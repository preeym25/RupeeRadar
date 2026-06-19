interface ReportViewProps {
  jobId: string | null
}

export function ReportView({ jobId }: ReportViewProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
      {jobId
        ? 'Report export will be available in Phase 4.'
        : 'Run an analysis to generate a shareable report.'}
    </div>
  )
}
