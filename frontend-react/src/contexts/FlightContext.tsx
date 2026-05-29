import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import type { FlightPayload } from '../types/flight'
import { flightService } from '../services/flightService'

interface FlightContextValue {
  lastPayload: FlightPayload | null
  connected: boolean
  elapsedSeconds: number
  history: FlightPayload[]
}

const FlightContext = createContext<FlightContextValue | undefined>(undefined)

export function FlightProvider({ children }: { children: ReactNode }) {
  const [lastPayload, setLastPayload] = useState<FlightPayload | null>(null)
  const [connected, setConnected] = useState(false)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [history, setHistory] = useState<FlightPayload[]>([])

  useEffect(() => {
    const unsubscribe = flightService.subscribe((payload) => {
      setLastPayload(payload)
      setConnected(true)
      setHistory((prev) => {
        const next = [...prev, payload]
        return next.length > 500 ? next.slice(-500) : next
      })
    })
    return unsubscribe
  }, [])

  useEffect(() => {
    if (!connected) return
    const interval = setInterval(
      () => setElapsedSeconds((s) => s + 1),
      1000,
    )
    return () => clearInterval(interval)
  }, [connected])

  return (
    <FlightContext.Provider
      value={{ lastPayload, connected, elapsedSeconds, history }}
    >
      {children}
    </FlightContext.Provider>
  )
}

export function useFlightContext(): FlightContextValue {
  const ctx = useContext(FlightContext)
  if (!ctx) {
    throw new Error('useFlightContext must be used within a FlightProvider')
  }
  return ctx
}

