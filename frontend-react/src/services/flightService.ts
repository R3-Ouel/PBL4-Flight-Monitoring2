import type { BufferKey, FlightPayload } from '../types/flight'
import { WS_URL } from './config'
import { useAppStore } from '../store/useAppStore'

const MAX_BUFFER_POINTS = 10_000
const RECONNECT_MS = 2000

type DataListener = (data: FlightPayload) => void
type BufferListener = () => void

function normalizeRaw(raw: Record<string, unknown>): FlightPayload {
  return {
    timestamp: Number(raw.timestamp_ms ?? 0) / 1000,
    altitude: Number(raw.altitude ?? 0),
    speed: Number(raw.vitesse ?? raw.speed ?? 0),
    ax: Number(raw.ax ?? 0),
    ay: Number(raw.ay ?? 0),
    az: Number(raw.az ?? 0),
    roll: Number(raw.roll ?? 0),
    pitch: Number(raw.pitch ?? 0),
    yaw: Number(raw.yaw ?? 0),
    phase: String(raw.phase ?? ''),
    flight_id: (raw.flight_id as string | null) ?? null,
    battery: Number(raw.battery ?? raw.batterie ?? 0),
    latitude: Number(raw.latitude ?? 0),
    longitude: Number(raw.longitude ?? 0),
  }
}

class FlightService {
  private ws: WebSocket | null = null
  private disposed = false
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null
  private readonly dataListeners = new Set<DataListener>()
  private readonly bufferListeners = new Set<BufferListener>()
  private readonly buffers: Partial<Record<BufferKey, [number, number][]>> = {}

  constructor() {
    this.connect()
  }

  subscribe(listener: DataListener): () => void {
    this.dataListeners.add(listener)
    return () => this.dataListeners.delete(listener)
  }

  subscribeBuffers(listener: BufferListener): () => void {
    this.bufferListeners.add(listener)
    return () => this.bufferListeners.delete(listener)
  }

  getBufferForKey(key: BufferKey): ReadonlyArray<readonly [number, number]> {
    return this.buffers[key] ?? []
  }

  resetBuffers(): void {
    for (const key of Object.keys(this.buffers) as BufferKey[]) {
      delete this.buffers[key]
    }
    this.notifyBuffers()
  }

  private connect(): void {
    if (this.disposed) return
    try {
      this.ws = new WebSocket(WS_URL)
      this.ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data as string) as Record<string, unknown>
          const normalized = normalizeRaw(raw)
          this.emitData(normalized)
          this.appendToBuffers(normalized)
        } catch {
          /* ignore malformed payloads */
        }
      }
      this.ws.onclose = () => this.scheduleReconnect()
      this.ws.onerror = () => this.scheduleReconnect()
    } catch {
      this.scheduleReconnect()
    }
  }

  private scheduleReconnect(): void {
    if (this.disposed) return
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      this.connect()
    }, RECONNECT_MS)
  }

  private emitData(data: FlightPayload): void {
    for (const listener of this.dataListeners) listener(data)
  }

  private notifyBuffers(): void {
    for (const listener of this.bufferListeners) listener()
  }

  private appendToBuffers(data: FlightPayload): void {
    if (!useAppStore.getState().isLive) return
    const ts = data.timestamp
    const keys: BufferKey[] = ['altitude', 'speed', 'az', 'roll', 'pitch', 'yaw']
    let changed = false
    for (const key of keys) {
      const v = data[key]
      const buf = this.buffers[key] ?? (this.buffers[key] = [])
      buf.push([ts, v])
      if (buf.length > MAX_BUFFER_POINTS) buf.shift()
      changed = true
    }
    if (changed) this.notifyBuffers()
  }

  dispose(): void {
    this.disposed = true
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.dataListeners.clear()
    this.bufferListeners.clear()
  }
}

export const flightService = new FlightService()
