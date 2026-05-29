import { useRef } from 'react'
import { useThemeColors } from '../../hooks/useThemeColors'
import {
  batteryColorKey,
  motorTempColorKey,
  phaseColorKey,
} from '../../styles/tokens'
import type { FlightPayload } from '../../types/flight'
import { useFlightContext } from '../../contexts/FlightContext'

interface RealTimeValueProps {
  columnId: number
  unit: string
  color: string
  isTimestamp?: boolean
  isPhase?: boolean
  size?: 'sm' | 'md' | 'lg'
  dynamicBattery?: boolean
  dynamicMotorTemp?: boolean
  dynamicPhase?: boolean
}

function extractValue(data: FlightPayload, columnId: number): number | null {
  switch (columnId) {
    case 0:
      return data.timestamp
    case 1:
      return data.altitude
    case 2:
      return data.speed
    case 5:
      return data.az
    case 6:
      return data.roll
    case 7:
      return data.pitch
    case 8:
      return data.yaw
    case 10:
      return 42 + data.speed * 6 + Math.abs(data.roll) * 0.4
    case 11:
      return data.battery != null && data.battery > 0
        ? data.battery
        : Math.max(15, 100 - data.timestamp * 0.05)
    default:
      return null
  }
}

function formatElapsed(seconds: number, startTs: number): string {
  const elapsedSec = Math.max(0, Math.round(seconds - startTs))
  const h = Math.floor(elapsedSec / 3600)
  const m = Math.floor((elapsedSec % 3600) / 60)
  const s = elapsedSec % 60
  const pad = (n: number) => n.toString().padStart(2, '0')
  if (h > 0) return `${pad(h)}:${pad(m)}:${pad(s)}`
  return `${pad(m)}:${pad(s)}`
}

const sizeClasses = {
  sm: 'text-sm',
  md: 'text-lg',
  lg: 'text-xl',
} as const

export function RealTimeValue({
  columnId,
  unit,
  color,
  isTimestamp = false,
  isPhase = false,
  size = 'md',
  dynamicBattery = false,
  dynamicMotorTemp = false,
  dynamicPhase = false,
}: RealTimeValueProps) {
  const { lastPayload, connected } = useFlightContext()
  const c = useThemeColors()
  const lastValueRef = useRef(0)
  const lastPhaseRef = useRef('--')
  const startTsRef = useRef<number | null>(null)

  if (lastPayload) {
    if (isPhase) {
      lastPhaseRef.current = lastPayload.phase || lastPhaseRef.current
    } else {
      const v = extractValue(lastPayload, columnId)
      if (v != null) {
        if (isTimestamp && startTsRef.current == null) startTsRef.current = v
        lastValueRef.current = v
      }
    }
  }

  const dotColor = connected ? c.accentGreen : c.accentRed
  const fontClass = sizeClasses[size]

  let valueColor = color
  let pulseClass = ''

  if (dynamicBattery) {
    const key = batteryColorKey(lastValueRef.current)
    valueColor = c[key]
    if (key === 'statusCritical') pulseClass = 'animate-pulse-critical'
  }

  if (dynamicMotorTemp) {
    const key = motorTempColorKey(lastValueRef.current)
    valueColor = c[key]
  }

  if (isPhase) {
    if (dynamicPhase) {
      const key = phaseColorKey(lastPhaseRef.current)
      valueColor = c[key]
    }
    const phaseDotColor = dynamicPhase
      ? c[phaseColorKey(lastPhaseRef.current)]
      : dotColor

    return (
      <div className="flex min-w-0 items-center gap-1">
        <span
          className="inline-block h-1.5 w-1.5 shrink-0 rounded-full"
          style={{
            backgroundColor: phaseDotColor,
            boxShadow: `0 0 4px ${phaseDotColor}99`,
          }}
        />
        <span
          className={`truncate font-bold ${fontClass}`}
          style={{ color: valueColor }}
          title={lastPhaseRef.current}
        >
          {lastPhaseRef.current}
        </span>
      </div>
    )
  }

  if (isTimestamp) {
    const start = startTsRef.current ?? lastValueRef.current
    return (
      <div className="flex items-center gap-1">
        <span
          className="inline-block h-1.5 w-1.5 rounded-full"
          style={{
            backgroundColor: dotColor,
            boxShadow: `0 0 4px ${dotColor}99`,
          }}
        />
        <span className={`font-bold ${fontClass}`} style={{ color: valueColor }}>
          {formatElapsed(lastValueRef.current, start)}
        </span>
      </div>
    )
  }

  return (
    <span
      className={`font-bold ${fontClass} ${pulseClass}`}
      style={{ color: valueColor }}
    >
      {lastValueRef.current.toFixed(1)}
      {unit}
    </span>
  )
}
