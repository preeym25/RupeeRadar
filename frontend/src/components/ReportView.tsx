import { useRef } from 'react'
import { Printer } from 'lucide-react'

interface ReportViewProps {
  jobId: string | null
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function ReportView({ jobId }: ReportViewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null)

  const handlePrint = () => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      iframeRef.current.contentWindow.focus()
      iframeRef.current.contentWindow.print()
    }
  }

  if (!jobId) {
    return (
      <div className="rounded-xl border border-border bg-surface p-8 text-center text-sm text-foreground/60">
        Run an analysis to generate a shareable report.
      </div>
    )
  }

  const reportUrl = `${API_URL}/api/v1/analyze/${jobId}/report`

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <button
          onClick={handlePrint}
          className="flex items-center gap-2 rounded-md bg-brand-active px-4 py-2 text-sm font-medium text-white hover:opacity-90 transition-opacity"
        >
          <Printer size={16} />
          Print / Save PDF
        </button>
      </div>
      <div className="overflow-hidden rounded-xl border border-border bg-white shadow-sm h-[800px]">
        <iframe
          ref={iframeRef}
          src={reportUrl}
          className="h-full w-full border-0 bg-white"
          title="Financial Report"
        />
      </div>
    </div>
  )
}
