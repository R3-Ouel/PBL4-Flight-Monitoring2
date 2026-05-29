import { useState } from 'react'
import { Download } from 'lucide-react'
import { StatHeader } from '../components/ui/StatHeader'
import { NeonCard } from '../components/ui/NeonCard'
import { RealTimeGraph } from '../components/charts/RealTimeGraph'
import { GraphLegend } from '../components/ui/GraphLegend'
import { useThemeColors } from '../hooks/useThemeColors'
import { downloadExcel, triggerBrowserDownload } from '../services/api'

interface GraphConfig {
  title: string
  columnIds: number[]
  legend?: { name: string; colorKey: 'blue' | 'orange' | 'green' }[]
}

export function AnalysePage() {
  const c = useThemeColors()
  const [toast, setToast] = useState<string | null>(null)
  const [downloading, setDownloading] = useState(false)

  const graphs: GraphConfig[] = [
    {
      title: 'PROFIL DE MONTÉE (Altitude)',
      columnIds: [1],
    },
    {
      title: 'VITESSE DE VOL',
      columnIds: [2],
    },
    {
      title: 'ACCÉLÉRATION VERTICALE (AZ)',
      columnIds: [5],
    },
    {
      title: 'ORIENTATION (Roll, Pitch, Yaw)',
      columnIds: [6, 7, 8],
      legend: [
        { name: 'Roll', colorKey: 'blue' },
        { name: 'Pitch', colorKey: 'orange' },
        { name: 'Yaw', colorKey: 'green' },
      ],
    },
  ]

  const colorForGraph = (columnIds: number[]): string[] => {
    if (columnIds.length === 1) {
      if (columnIds[0] === 1) return [c.accentCyan]
      if (columnIds[0] === 2) return [c.accentGreen]
      if (columnIds[0] === 5) return [c.accentPink]
    }
    return [c.accentBlue, c.accentOrange, c.accentGreen]
  }

  const legendColors = {
    blue: c.accentBlue,
    orange: c.accentOrange,
    green: c.accentGreen,
  }

  async function handleDownload() {
    setDownloading(true)
    try {
      const blob = await downloadExcel()
      triggerBrowserDownload(blob, 'flight_data.xlsx')
      setToast('Fichier Excel téléchargé: flight_data.xlsx')
    } catch (e) {
      setToast(`Erreur: ${e instanceof Error ? e.message : String(e)}`)
    } finally {
      setDownloading(false)
      setTimeout(() => setToast(null), 5000)
    }
  }

  return (
    <div className="space-y-4 p-4 md:p-6">
      <StatHeader />
      <button
        type="button"
        onClick={handleDownload}
        disabled={downloading}
        className="inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium shadow transition hover:opacity-90 disabled:opacity-60"
        style={{ backgroundColor: c.accentRed, color: c.textPrimary }}
      >
        <Download size={18} />
        {downloading
          ? 'Téléchargement…'
          : 'Télécharger Excel avec données et graphiques'}
      </button>
      {toast && (
        <p
          className="rounded-lg px-3 py-2 text-sm"
          style={{
            backgroundColor: 'var(--chip-bg)',
            color: c.textPrimary,
          }}
        >
          {toast}
        </p>
      )}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {graphs.map((g) => (
          <NeonCard key={g.title} className="flex h-[280px] flex-col">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <h3
                className="text-xs font-bold"
                style={{ color: c.textLabel }}
              >
                {g.title}
              </h3>
              {g.legend && (
                <GraphLegend
                  items={g.legend.map((l) => ({
                    name: l.name,
                    color: legendColors[l.colorKey],
                  }))}
                />
              )}
            </div>
            <div className="min-h-0 flex-1">
              <RealTimeGraph
                columnIds={g.columnIds}
                colors={colorForGraph(g.columnIds)}
              />
            </div>
          </NeonCard>
        ))}
      </div>
    </div>
  )
}
