import { useCallback, useMemo, useSyncExternalStore } from 'react'

export interface CaptureItem {
  id: string
  src: string
  timestamp: string
}

type Listener = () => void

let storePhotos: CaptureItem[] = []
const listeners = new Set<Listener>()

function emitChange(): void {
  for (const l of listeners) l()
}

function nowTimestamp(): string {
  const d = new Date()
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

function canvasToObjectUrl(canvas: HTMLCanvasElement): Promise<string> {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        resolve(URL.createObjectURL(new Blob()))
        return
      }
      resolve(URL.createObjectURL(blob))
    }, 'image/png')
  })
}

async function makeThumb(timestamp: string): Promise<string> {
  const canvas = document.createElement('canvas')
  canvas.width = 160
  canvas.height = 120

  const ctx = canvas.getContext('2d')
  if (!ctx) {
    return URL.createObjectURL(new Blob())
  }

  ctx.fillStyle = '#000000'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  ctx.fillStyle = 'rgba(0,229,255,0.85)'
  ctx.font = 'bold 16px Segoe UI, system-ui, -apple-system, sans-serif'
  ctx.fillText(timestamp, 18, 64)

  return await canvasToObjectUrl(canvas)
}

function subscribe(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

function getSnapshot(): CaptureItem[] {
  return storePhotos
}

export function useCameraCapture() {
  const photos = useSyncExternalStore(subscribe, getSnapshot, getSnapshot)

  const capturePhoto = useCallback(() => {
    void (async () => {
      const timestamp = nowTimestamp()
      const src = await makeThumb(timestamp)
      const item: CaptureItem = {
        id: crypto.randomUUID(),
        src,
        timestamp,
      }
      console.log('capturePhoto()', item)
      storePhotos = [item, ...storePhotos]
      emitChange()
    })()
  }, [])

  const clearAll = useCallback(() => {
    console.log('clearAll()')
    storePhotos = []
    emitChange()
  }, [])

  return useMemo(
    () => ({ photos, capturePhoto, clearAll }),
    [photos, capturePhoto, clearAll],
  )
}

