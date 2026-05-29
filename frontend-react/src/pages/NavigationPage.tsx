import { useEffect, useRef, useState } from 'react'
import type { LatLngTuple } from 'leaflet'
import { Camera } from 'lucide-react'
import { StatHeader } from '../components/ui/StatHeader'
import { NeonCard } from '../components/ui/NeonCard'
import { RealTimeValue } from '../components/ui/RealTimeValue'
import { GpsMap } from '../components/map/GpsMap'
import { useThemeColors } from '../hooks/useThemeColors'
import { useFlightContext } from '../contexts/FlightContext'
import { useCameraCapture } from '../hooks/useCameraCapture'

const MAX_TRAIL_POINTS = 200

function ParamCard({
  label,
  columnId,
  unit,
  color,
}: {
  label: string
  columnId: number
  unit: string
  color: string
}) {
  return (
    <NeonCard>
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-bold" style={{ color: 'var(--text-label)' }}>
          {label}
        </span>
        <RealTimeValue columnId={columnId} unit={unit} color={color} />
      </div>
    </NeonCard>
  )
}

export function NavigationPage() {
  const c = useThemeColors()
  const { lastPayload } = useFlightContext()
  const { capturePhoto } = useCameraCapture()
  const [trail, setTrail] = useState<LatLngTuple[]>([])
  const lastPointRef = useRef<LatLngTuple | null>(null)

  const lat = lastPayload?.latitude ?? 0
  const lng = lastPayload?.longitude ?? 0
  const yaw = lastPayload?.yaw ?? 0

  useEffect(() => {
    if (lat === 0 && lng === 0) return
    const point: LatLngTuple = [lat, lng]
    const prev = lastPointRef.current
    if (prev && prev[0] === point[0] && prev[1] === point[1]) return
    lastPointRef.current = point
    setTrail((t) => {
      const next = [...t, point]
      return next.length > MAX_TRAIL_POINTS ? next.slice(-MAX_TRAIL_POINTS) : next
    })
  }, [lat, lng])

  const params = [
    { label: 'ALTITUDE', columnId: 1, unit: 'm', color: c.accentCyan },
    { label: 'VITESSE', columnId: 2, unit: 'm/s', color: c.accentCyan },
    { label: 'AZ', columnId: 5, unit: 'm/s²', color: c.accentPink },
    { label: 'ROLL', columnId: 6, unit: '°', color: c.accentBlue },
    { label: 'PITCH', columnId: 7, unit: '°', color: c.accentOrange },
    { label: 'YAW', columnId: 8, unit: '°', color: c.accentGreen },
  ] as const

  return (
    <div className="flex h-full min-h-[calc(100vh-3.5rem)] flex-col gap-4 p-4 md:p-6">
      <StatHeader />
      <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 lg:grid-cols-[1fr_230px]">
        <NeonCard className="relative min-h-[320px] p-2">
          <GpsMap lat={lat} lng={lng} yaw={yaw} trail={trail} />
          <button
            type="button"
            onClick={capturePhoto}
            title="Prendre une photo"
            className="absolute bottom-3 right-3 flex h-[44px] w-[44px] items-center justify-center rounded-full border transition hover:scale-[1.05]"
            style={{
              backgroundColor: '#00000099',
              borderColor: c.accentCyan,
            }}
          >
            <Camera size={18} style={{ color: c.accentCyan }} />
          </button>
        </NeonCard>
        <div className="flex flex-col gap-2">
          {params.map((p) => (
            <ParamCard key={p.label} {...p} />
          ))}
        </div>
      </div>
    </div>
  )
}
