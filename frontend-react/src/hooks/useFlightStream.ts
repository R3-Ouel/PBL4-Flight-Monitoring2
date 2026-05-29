import { useEffect, useState } from 'react'
import type { FlightPayload } from '../types/flight'
import { flightService } from '../services/flightService'

export function useFlightStream(): {
  lastPayload: FlightPayload | null
  connected: boolean
} {
  const [lastPayload, setLastPayload] = useState<FlightPayload | null>(null)
  const [connected, setConnected] = useState(true)

  useEffect(() => {
    const unsub = flightService.subscribe((data) => {
      setLastPayload(data)
      setConnected(true)
    })
    return unsub
  }, [])

  return { lastPayload, connected }
}

export function useBufferRevision(): number {
  const [revision, setRevision] = useState(0)

  useEffect(() => {
    return flightService.subscribeBuffers(() => {
      setRevision((r) => r + 1)
    })
  }, [])

  return revision
}
