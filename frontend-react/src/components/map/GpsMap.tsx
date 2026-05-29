import 'leaflet/dist/leaflet.css'
import { useEffect, useMemo } from 'react'
import { MapContainer, Marker, Polyline, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import type { LatLngTuple } from 'leaflet'
import { MapPin } from 'lucide-react'
import { useThemeColors } from '../../hooks/useThemeColors'

export interface GpsMapProps {
  lat: number
  lng: number
  yaw: number
  trail?: LatLngTuple[]
}

const DEFAULT_CENTER: LatLngTuple = [49.6116, 6.1319]
const TILE_ATTRIBUTION = '© OpenStreetMap © CartoDB'

function createDroneIcon(yaw: number, color: string): L.DivIcon {
  return L.divIcon({
    className: '',
    html: `<svg width="28" height="28" viewBox="0 0 28 28" style="transform:rotate(${yaw}deg);transform-origin:14px 14px">
      <polygon points="14,2 24,24 14,18 4,24" fill="${color}" stroke="${color}" stroke-width="1" opacity="0.95"/>
    </svg>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  })
}

function MapViewUpdater({
  lat,
  lng,
  hasFix,
}: {
  lat: number
  lng: number
  hasFix: boolean
}) {
  const map = useMap()
  useEffect(() => {
    if (hasFix) map.setView([lat, lng], map.getZoom(), { animate: true })
  }, [lat, lng, hasFix, map])
  return null
}

export function GpsMap({ lat, lng, yaw, trail = [] }: GpsMapProps) {
  const c = useThemeColors()
  const hasFix = lat !== 0 || lng !== 0

  const tileUrl =
    c.theme === 'dark'
      ? 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
      : 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

  const droneIcon = useMemo(
    () => createDroneIcon(yaw, c.accentCyan),
    [yaw, c.accentCyan],
  )

  return (
    <div className="relative h-full min-h-[280px] w-full overflow-hidden rounded-lg">
      <MapContainer
        center={hasFix ? [lat, lng] : DEFAULT_CENTER}
        zoom={15}
        className="h-full min-h-[280px] w-full rounded-lg"
        zoomControl={false}
        scrollWheelZoom
      >
        <TileLayer key={c.theme} url={tileUrl} attribution={TILE_ATTRIBUTION} />
        {hasFix && (
          <>
            <MapViewUpdater lat={lat} lng={lng} hasFix={hasFix} />
            {trail.length > 1 && (
              <Polyline
                positions={trail}
                pathOptions={{
                  color: c.mapTrailColor,
                  opacity: 0.6,
                  weight: 2,
                }}
              />
            )}
            <Marker position={[lat, lng]} icon={droneIcon} />
          </>
        )}
      </MapContainer>

      <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-3">
        <div className="flex items-start justify-between">
          <div
            className="flex items-center gap-1.5 text-[11px] tracking-[0.2em]"
            style={{ color: c.textLabel }}
          >
            <MapPin size={13} style={{ color: c.accentCyan }} />
            GPS MAP
          </div>
          <span
            className="rounded border px-2 py-0.5 text-[9px] tracking-[0.2em]"
            style={{
              color: c.accentCyan,
              borderColor: `${c.accentCyan}59`,
              backgroundColor: `${c.accentCyan}1a`,
            }}
          >
            SIMULÉ
          </span>
        </div>
      </div>

      {!hasFix && (
        <div
          className="pointer-events-none absolute inset-0 flex items-center justify-center rounded-lg"
          style={{ backgroundColor: c.overlayBg }}
        >
          <span
            className="text-sm font-bold tracking-[0.3em]"
            style={{ color: c.textPrimary }}
          >
            NO GPS FIX
          </span>
        </div>
      )}
    </div>
  )
}
