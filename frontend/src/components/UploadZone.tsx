interface UploadZoneProps {
  onFileSelect: (file: File) => void
  loading?: boolean
  accept?: string
}

export function UploadZone({
  onFileSelect,
  loading = false,
  accept = '.csv,.xlsx,.pdf',
}: UploadZoneProps) {
  return (
    <label
      className={`flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border bg-surface px-6 py-10 text-center transition hover:border-primary hover:bg-primary/5 ${loading ? 'pointer-events-none opacity-60' : ''}`}
    >
      <input
        type="file"
        className="hidden"
        accept={accept}
        disabled={loading}
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) onFileSelect(file)
        }}
      />
      <p className="text-lg font-semibold text-foreground">
        {loading ? 'Analyzing statement…' : 'Upload bank statement'}
      </p>
      <p className="mt-2 text-sm text-foreground/60">
        Drag & drop or click to select CSV (Excel & PDF in later phases)
      </p>
      <p className="mt-4 text-xs text-foreground/40">
        Your data is processed ephemerally and not stored permanently.
      </p>
    </label>
  )
}
