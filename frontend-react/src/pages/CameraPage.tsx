import { useMemo, useState, useEffect } from 'react'
import { NeonCard } from '../components/ui/NeonCard'
import { useThemeColors } from '../hooks/useThemeColors'
import { useCameraCapture } from '../hooks/useCameraCapture'

function InlineCameraIcon({ color }: { color: string }) {
  return (
    <svg width="56" height="56" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 7.5A2.5 2.5 0 0 1 6.5 5h2l1-1h5l1 1h2A2.5 2.5 0 0 1 20 7.5v9A2.5 2.5 0 0 1 17.5 19h-11A2.5 2.5 0 0 1 4 16.5v-9Z"
        stroke={color}
        strokeWidth="1.5"
        opacity="0.35"
      />
      <path
        d="M12 16a3.2 3.2 0 1 0 0-6.4A3.2 3.2 0 0 0 12 16Z"
        stroke={color}
        strokeWidth="1.5"
        opacity="0.35"
      />
      <path
        d="M18 9.2h.01"
        stroke={color}
        strokeWidth="2.8"
        strokeLinecap="round"
        opacity="0.35"
      />
    </svg>
  )
}

function InlineImageIcon({ color }: { color: string }) {
  return (
    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 7a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7Z"
        stroke={color}
        strokeWidth="1.5"
        opacity="0.6"
      />
      <path
        d="M7.5 14.5 10 12l2.5 2.5 2-2L18.5 17"
        stroke={color}
        strokeWidth="1.5"
        opacity="0.6"
      />
      <path
        d="M9 10.2h.01"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
        opacity="0.6"
      />
    </svg>
  )
}

function LiveBadge() {
  const c = useThemeColors()
  return (
    <div className="inline-flex items-center gap-2 rounded-md border px-2 py-1 text-[10px] font-bold tracking-[0.2em]"
      style={{ borderColor: 'var(--border-default)', backgroundColor: 'var(--chip-bg)', color: c.textPrimary }}
    >
      <span
        className="inline-block h-2 w-2 rounded-full"
        style={{
          backgroundColor: 'var(--status-critical)',
          boxShadow: `0 0 10px var(--status-critical)`,
          animation: 'pulse-live-dot 1.2s ease-in-out infinite',
        }}
      />
      LIVE
      <span style={{ color: c.textMuted, letterSpacing: '0.18em' }}>OV9281</span>
    </div>
  )
}

const RASPBERRY_URL = "http://192.168.137.66:8000"

export function CameraPage() {
  const c = useThemeColors()
  const { photos, capturePhoto, clearAll } = useCameraCapture()
  const [recording, setRecording] = useState(false)
  
  // Nouvel état : null = pas connecté, string = connecté
  const [streamUrl, setStreamUrl] = useState<string | null>(null)

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>

    async function testerConnexion() {
      try {
        // On appelle un endpoint léger "/ping" pour vérifier que le serveur répond
        const res = await fetch(`${RASPBERRY_URL}/ping`, { signal: AbortSignal.timeout(2000) })
        if (res.ok) {
          setStreamUrl(`${RASPBERRY_URL}/video`)  // ✅ serveur dispo → on active le flux
        } else {
          setStreamUrl(null)                       // ❌ serveur répond mais erreur
        }
      } catch {
        setStreamUrl(null)                         // ❌ serveur injoignable
      }
    }

    testerConnexion()                        // test immédiat au chargement
    interval = setInterval(testerConnexion, 5000)  // re-teste toutes les 5 secondes

    return () => clearInterval(interval)     // nettoyage quand on quitte la page
  }, [])

  const galleryTitle = useMemo(() => `GALERIE (${photos.length})`, [photos.length])

  function toggleRecording(): void {
    setRecording((r) => {
      const next = !r
      console.log('toggleRecording()', next)
      return next
    })
  }



  return (
    <div className="flex h-full min-h-[calc(100vh-3.5rem)] flex-col gap-4 p-4 md:p-6">
      <div className="flex min-h-0 flex-1 flex-col gap-4 md:flex-row">
        <div className="flex min-h-[340px] flex-1 md:basis-[65%]">
          <NeonCard className="relative flex min-h-0 w-full flex-col overflow-hidden p-0">
            <div className="absolute left-3 top-3 z-10">
              <LiveBadge />
            </div>

            <div
              className="relative flex min-h-0 flex-1 items-center justify-center"
              style={{
                backgroundColor: 'var(--surface-deep)',
                backgroundImage:
                  'repeating-linear-gradient(to bottom, rgba(255,255,255,0.035), rgba(255,255,255,0.035) 1px, rgba(0,0,0,0) 6px, rgba(0,0,0,0) 9px)',
              }}
            >
              {streamUrl ? (
                <img
                  src={streamUrl}
                  alt="Flux caméra"
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex flex-col items-center gap-2 px-6 text-center">
                  <InlineCameraIcon color={c.accentCyan} />
                  <p
                    className="text-xs font-bold tracking-[0.25em]"
                    style={{ color: c.textMuted }}
                  >
                    FLUX VIDÉO NON DISPONIBLE
                  </p>
                  <p className="text-[11px]" style={{ color: c.textMuted }}>
                    En attente de connexion au flux RTSP...
                  </p>
                </div>
              )}

              <div
                className="pointer-events-none absolute bottom-0 left-0 right-0 flex items-center justify-between px-3 py-2 text-[10px]"
                style={{ backgroundColor: '#00000088', color: c.textPrimary }}
              >
                <span style={{ color: c.textMuted }}>1280×800 | MONO | 60fps</span>
                <span style={{ color: c.textMuted }}>-- ms</span>
              </div>
            </div>
          </NeonCard>
        </div>

        <div className="flex min-h-[340px] flex-1 md:basis-[35%]">
          <NeonCard className="flex min-h-0 w-full flex-col">
            <div className="flex flex-col gap-3">
              <p className="text-[10px] font-bold tracking-[0.28em]" style={{ color: c.textMuted }}>
                CAPTURE
              </p>

              <button
                type="button"
                onClick={capturePhoto}
                className="w-full rounded-lg border px-4 py-3 text-sm font-bold tracking-[0.18em] transition hover:opacity-90"
                style={{
                  borderColor: c.accentCyan,
                  backgroundColor: `${c.accentCyan}26`,
                  color: c.accentCyan,
                }}
              >
                📷 PRENDRE UNE PHOTO
              </button>

              <button
                type="button"
                onClick={toggleRecording}
                className={`w-full rounded-lg border px-4 py-3 text-sm font-bold tracking-[0.18em] transition hover:opacity-90 ${recording ? 'animate-pulse-critical' : ''}`}
                style={{
                  borderColor: c.accentRed,
                  backgroundColor: `${c.accentRed}26`,
                  color: c.accentRed,
                }}
              >
                {recording ? '⏹ ARRÊTER' : '⏺ DÉMARRER ENREGISTREMENT'}
              </button>

              <p className="text-xs" style={{ color: c.textMuted }}>
                Photos : {photos.length} | Vidéos : 0
              </p>
            </div>

            <div className="my-4 h-px w-full" style={{ backgroundColor: 'var(--divider)' }} />

            <div className="flex min-h-0 flex-1 flex-col">
              <div className="mb-3 flex items-center justify-between gap-2">
                <p className="text-[10px] font-bold tracking-[0.28em]" style={{ color: c.textMuted }}>
                  {galleryTitle}
                </p>
              </div>

              {photos.length === 0 ? (
                <div className="flex flex-1 flex-col items-center justify-center gap-2 rounded-lg"
                  style={{ backgroundColor: 'var(--chip-bg)' }}
                >
                  <InlineImageIcon color={c.textMuted} />
                  <p className="text-xs font-bold tracking-[0.2em]" style={{ color: c.textMuted }}>
                    Aucune capture
                  </p>
                </div>
              ) : (
                <div className="min-h-0 flex-1 overflow-auto pr-1">
                  <div
                    className="grid gap-[6px]"
                    style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}
                  >
                    {photos.map((p) => (
                      <div
                        key={p.id}
                        className="group relative overflow-hidden rounded-md border"
                        style={{
                          aspectRatio: '1 / 1',
                          backgroundColor: 'var(--surface-card)',
                          borderColor: 'var(--border-default)',
                        }}
                      >
                        <img
                          src={p.src}
                          alt={`Capture ${p.timestamp}`}
                          className="h-full w-full object-cover opacity-90 transition group-hover:opacity-100"
                        />
                        <div
                          className="absolute bottom-0 left-0 right-0 px-1.5 py-1"
                          style={{ backgroundColor: '#00000088' }}
                        >
                          <span className="text-[9px] text-white">{p.timestamp}</span>
                        </div>
                        <div
                          className="absolute inset-0 rounded-md border opacity-0 transition group-hover:opacity-100"
                          style={{ borderColor: c.accentCyan, boxShadow: `0 0 10px ${c.accentCyan}30` }}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {photos.length > 0 && (
                <div className="mt-3 flex items-center justify-end">
                  <button
                    type="button"
                    onClick={clearAll}
                    className="text-xs font-bold tracking-[0.18em] hover:opacity-80"
                    style={{ color: c.accentRed, background: 'transparent' }}
                  >
                    TOUT EFFACER
                  </button>
                </div>
              )}
            </div>
          </NeonCard>
        </div>
      </div>

    </div>
  )
}

