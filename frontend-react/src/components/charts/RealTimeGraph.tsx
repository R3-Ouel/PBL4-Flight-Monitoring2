import { useMemo, useRef } from 'react'
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { flightService } from '../../services/flightService'
import { useBufferRevision } from '../../hooks/useFlightStream'
import { useThemeColors } from '../../hooks/useThemeColors'
import { columnIdToKey } from '../../styles/colors'
import type { BufferKey } from '../../types/flight'

interface RealTimeGraphProps {
  columnIds: number[]
  colors: string[]
}

function formatElapsed(seconds: number, minX: number): string {
  const elapsed = Math.max(0, Math.round(seconds - minX))
  const h = Math.floor(elapsed / 3600)
  const m = Math.floor((elapsed % 3600) / 60)
  const s = elapsed % 60
  const pad = (n: number) => n.toString().padStart(2, '0')
  if (h > 0) return `${pad(h)}:${pad(m)}:${pad(s)}`
  return `${pad(m)}:${pad(s)}`
}

function buildChartRows(
  columnIds: number[],
): { rows: Record<string, number>[]; minX: number; maxX: number } {
  const series = columnIds.map((id) => {
    const key = columnIdToKey(id)
    if (!key || key === 'timestamp') return { key: '', points: [] as [number, number][] }
    return {
      key,
      points: [...flightService.getBufferForKey(key as BufferKey)],
    }
  })

  const allX = new Set<number>()
  for (const s of series) {
    for (const [x] of s.points) allX.add(x)
  }
  const sortedX = [...allX].sort((a, b) => a - b)
  if (sortedX.length === 0) return { rows: [], minX: 0, maxX: 1 }

  const minX = sortedX[0]
  const maxX = sortedX[sortedX.length - 1]
  const rows = sortedX.map((x) => {
    const row: Record<string, number> = { x }
    series.forEach((s, i) => {
      if (!s.key) return
      const match = s.points.find((p) => p[0] === x)
      if (match) row[`y${i}`] = match[1]
    })
    return row
  })

  return { rows, minX, maxX }
}

export function RealTimeGraph({ columnIds, colors }: RealTimeGraphProps) {
  const revision = useBufferRevision()
  const c = useThemeColors()
  const isDark = c.theme === 'dark'
  const minYCache = useRef<number | null>(null)
  const maxYCache = useRef<number | null>(null)

  const { rows, minX, maxX, yDomain } = useMemo(() => {
    void revision
    const built = buildChartRows(columnIds)
    if (built.rows.length === 0) {
      minYCache.current = null
      maxYCache.current = null
      return { ...built, yDomain: [0, 1] as [number, number] }
    }

    let minY = Infinity
    let maxY = -Infinity
    for (const row of built.rows) {
      for (const key of Object.keys(row)) {
        if (key === 'x') continue
        const v = row[key]
        minY = Math.min(minY, v)
        maxY = Math.max(maxY, v)
      }
    }
    if (!Number.isFinite(minY) || !Number.isFinite(maxY)) {
      minY = 0
      maxY = 1
    }
    if (minYCache.current == null || minY < minYCache.current) minYCache.current = minY
    if (maxYCache.current == null || maxY > maxYCache.current) maxYCache.current = maxY
    const usedMin = minYCache.current ?? minY
    const usedMax = maxYCache.current ?? maxY
    const span = Math.abs(usedMax - usedMin)
    const pad = span === 0 ? 1 : span * 0.12
    return {
      ...built,
      yDomain: [usedMin - pad, usedMax + pad] as [number, number],
    }
  }, [columnIds, revision])

  if (rows.length === 0) {
    return (
      <div className="flex h-full min-h-[180px] items-center justify-center">
        <div
          className="h-8 w-8 animate-spin rounded-full border-2 border-transparent"
          style={{
            borderTopColor: colors[0],
            borderRightColor: colors[0],
          }}
        />
      </div>
    )
  }

  const ticks = [minX, minX + (maxX - minX) * 0.25, minX + (maxX - minX) * 0.5, minX + (maxX - minX) * 0.75, maxX]

  return (
    <ResponsiveContainer width="100%" height="100%" minHeight={180}>
      <ComposedChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 4 }}>
        <CartesianGrid stroke={c.graphGrid} strokeDasharray="3 3" />
        <XAxis
          dataKey="x"
          type="number"
          domain={[minX, maxX]}
          ticks={ticks}
          tickFormatter={(v) => formatElapsed(Number(v), minX)}
          stroke={c.graphAxis}
          tick={{ fill: c.graphAxis, fontSize: 11 }}
        />
        <YAxis
          domain={yDomain}
          stroke={c.graphAxis}
          tick={{ fill: c.graphAxis, fontSize: 11 }}
          tickFormatter={(v) => Number(v).toFixed(0)}
          width={48}
        />
        <Tooltip
          contentStyle={{
            background: c.tooltipBg,
            border: 'none',
            borderRadius: 6,
            color: c.tooltipText,
            fontSize: 12,
          }}
          labelFormatter={(x) => formatElapsed(Number(x), minX)}
          formatter={(value) => [
            typeof value === 'number' ? value.toFixed(2) : String(value ?? ''),
            '',
          ]}
        />
        {columnIds.map((_, i) => (
          <g key={i}>
            <Area
              type="linear"
              dataKey={`y${i}`}
              stroke="none"
              fill={colors[i]}
              fillOpacity={isDark ? 0.06 : 0.03}
              connectNulls
            />
            <Line
              type="linear"
              dataKey={`y${i}`}
              stroke={colors[i]}
              strokeWidth={2}
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
          </g>
        ))}
      </ComposedChart>
    </ResponsiveContainer>
  )
}
