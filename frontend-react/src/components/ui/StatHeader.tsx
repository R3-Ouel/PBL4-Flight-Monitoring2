import { NeonCard } from './NeonCard'
import { RealTimeValue } from './RealTimeValue'
import { useThemeColors } from '../../hooks/useThemeColors'
import { useFlightContext } from '../../contexts/FlightContext'

function StatBox({
  label,
  columnId,
  unit,
  color,
  isTimestamp,
  isPhase,
  emphasized,
  size,
  dynamicBattery,
  dynamicMotorTemp,
  dynamicPhase,
}: {
  label: string
  columnId: number
  unit: string
  color: string
  isTimestamp?: boolean
  isPhase?: boolean
  emphasized?: boolean
  size?: 'sm' | 'md' | 'lg'
  dynamicBattery?: boolean
  dynamicMotorTemp?: boolean
  dynamicPhase?: boolean
}) {
  const c = useThemeColors()

  return (
    <NeonCard className="min-w-0 flex-1" emphasized={emphasized}>
      <p
        className="truncate text-[9px] font-bold tracking-wide"
        style={{ color: c.textLabel }}
      >
        {label}
      </p>
      <div className="mt-1">
        <RealTimeValue
          columnId={columnId}
          unit={unit}
          color={color}
          isTimestamp={isTimestamp}
          isPhase={isPhase}
          size={size}
          dynamicBattery={dynamicBattery}
          dynamicMotorTemp={dynamicMotorTemp}
          dynamicPhase={dynamicPhase}
        />
      </div>
    </NeonCard>
  )
}

export function StatHeader() {
  const c = useThemeColors()
  const { elapsedSeconds } = useFlightContext()

  const formatElapsed = (seconds: number): string => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    const pad = (n: number) => n.toString().padStart(2, '0')
    if (h > 0) return `${pad(h)}:${pad(m)}:${pad(s)}`
    return `${pad(m)}:${pad(s)}`
  }

  return (
    <div className="flex flex-wrap gap-2 lg:flex-nowrap">
      <StatBox
        label="ALTITUDE"
        columnId={1}
        unit="m"
        color={c.accentCyan}
        size="lg"
      />
      <StatBox
        label="TEMP. MOTEURS"
        columnId={10}
        unit="°C"
        color={c.statusOk}
        size="sm"
        dynamicMotorTemp
      />
      <StatBox
        label="BATTERIE"
        columnId={11}
        unit="%"
        color={c.statusOk}
        emphasized
        dynamicBattery
      />
      <NeonCard className="min-w-0 flex-1" emphasized>
        <p
          className="truncate text-[9px] font-bold tracking-wide"
          style={{ color: c.textLabel }}
        >
          TEMPS DE VOL
        </p>
        <div className="mt-1">
          <span className="font-bold text-lg" style={{ color: c.accentGreen }}>
            {formatElapsed(elapsedSeconds)}
          </span>
        </div>
      </NeonCard>
      <StatBox
        label="PHASE DE VOL"
        columnId={12}
        unit=""
        color={c.accentOrange}
        isPhase
        emphasized
        dynamicPhase
      />
    </div>
  )
}
