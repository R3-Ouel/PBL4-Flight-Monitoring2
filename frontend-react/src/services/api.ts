import { API_BASE } from './config'

export async function downloadExcel(): Promise<Blob> {
  const response = await fetch(`${API_BASE}/download-excel`)
  if (!response.ok) {
    // Try to surface backend error payload (FastAPI usually returns JSON on failure).
    const details = await response.text().catch(() => '')
    const suffix = details ? `: ${details}` : ''
    throw new Error(`Download failed (${response.status})${suffix}`)
  }
  return response.blob()
}

export function triggerBrowserDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}
