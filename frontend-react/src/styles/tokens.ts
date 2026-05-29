export type ThemeMode = 'dark' | 'light'

export interface ThemeTokens {
  scaffoldBg: string
  cardBg: string
  sidebarBg: string
  borderDefault: string
  borderEmphasis: string
  textPrimary: string
  textLabel: string
  textMuted: string
  accentRed: string
  accentGreen: string
  accentCyan: string
  accentOrange: string
  accentPink: string
  accentBlue: string
  navInactive: string
  cardShadow: string
  armDisarmedBg: string
  armDisarmedBorder: string
  armArmedBg: string
  armArmedBorder: string
  overlayBg: string
  mapTrailColor: string
  statusOk: string
  statusWarn: string
  statusCritical: string
  chipBg: string
  divider: string
  toggleTrack: string
  toggleThumb: string
  graphGrid: string
  graphAxis: string
  tooltipBg: string
  tooltipText: string
}

const darkTokens: ThemeTokens = {
  scaffoldBg: '#0d0f14',
  cardBg: '#13161f',
  sidebarBg: '#0a0c12',
  borderDefault: 'rgba(255,255,255,0.1)',
  borderEmphasis: 'rgba(0,229,255,0.35)',
  textPrimary: '#ffffff',
  textLabel: 'rgba(255,255,255,0.55)',
  textMuted: 'rgba(255,255,255,0.4)',
  accentRed: '#ff3c5a',
  accentGreen: '#00ff88',
  accentCyan: '#00e5ff',
  accentOrange: '#ffa657',
  accentPink: '#ff3c5a',
  accentBlue: '#448aff',
  navInactive: 'rgba(255,255,255,0.7)',
  cardShadow: '0 0 12px 1px rgba(255,60,90,0.12)',
  armDisarmedBg: '#3d0a0a',
  armDisarmedBorder: '#ff3c5a',
  armArmedBg: '#0a3d1a',
  armArmedBorder: '#00ff88',
  overlayBg: 'rgba(13,15,20,0.75)',
  mapTrailColor: '#00e5ff',
  statusOk: '#00ff88',
  statusWarn: '#ffa657',
  statusCritical: '#ff3c5a',
  chipBg: 'rgba(19,22,31,0.85)',
  divider: 'rgba(255,255,255,0.1)',
  toggleTrack: 'rgba(255,255,255,0.2)',
  toggleThumb: '#ffffff',
  graphGrid: 'rgba(255,255,255,0.06)',
  graphAxis: 'rgba(255,255,255,0.7)',
  tooltipBg: 'rgba(0,0,0,0.87)',
  tooltipText: '#ffffff',
}

const lightTokens: ThemeTokens = {
  scaffoldBg: '#f0f2f7',
  cardBg: '#ffffff',
  sidebarBg: '#e8ebf2',
  borderDefault: 'rgba(26,26,46,0.12)',
  borderEmphasis: 'rgba(0,179,204,0.45)',
  textPrimary: '#1a1a2e',
  textLabel: '#1a1a2e',
  textMuted: 'rgba(26,26,46,0.45)',
  accentRed: '#cc3048',
  accentGreen: '#00b360',
  accentCyan: '#00b3cc',
  accentOrange: '#b3743c',
  accentPink: '#cc3048',
  accentBlue: '#3066cc',
  navInactive: 'rgba(26,26,46,0.54)',
  cardShadow: '0 2px 12px rgba(26,26,46,0.08)',
  armDisarmedBg: '#fde8eb',
  armDisarmedBorder: '#cc3048',
  armArmedBg: '#e6f9ef',
  armArmedBorder: '#00b360',
  overlayBg: 'rgba(240,242,247,0.85)',
  mapTrailColor: '#00b3cc',
  statusOk: '#00b360',
  statusWarn: '#b3743c',
  statusCritical: '#cc3048',
  chipBg: 'rgba(255,255,255,0.92)',
  divider: 'rgba(26,26,46,0.12)',
  toggleTrack: 'rgba(26,26,46,0.15)',
  toggleThumb: '#ffffff',
  graphGrid: 'rgba(26,26,46,0.08)',
  graphAxis: '#1a1a2e',
  tooltipBg: 'rgba(255,255,255,0.96)',
  tooltipText: '#1a1a2e',
}

export function getTokens(theme: ThemeMode): ThemeTokens {
  return theme === 'dark' ? darkTokens : lightTokens
}

export const THEME_STORAGE_KEY = 'flight-control-theme'

export function loadStoredTheme(): ThemeMode {
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {
    /* ignore */
  }
  return 'dark'
}

export function saveTheme(theme: ThemeMode): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, theme)
  } catch {
    /* ignore */
  }
}

export function applyThemeToDocument(theme: ThemeMode): void {
  document.documentElement.setAttribute('data-theme', theme)
  const tokens = getTokens(theme)
  const root = document.documentElement.style
  for (const [key, value] of Object.entries(tokens)) {
    root.setProperty(`--${camelToKebab(key)}`, value)
  }
}

function camelToKebab(str: string): string {
  return str.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`)
}

/** Phase → accent color token key */
export function phaseColorKey(phase: string): keyof Pick<
  ThemeTokens,
  'accentOrange' | 'accentCyan' | 'accentGreen' | 'accentRed' | 'textMuted'
> {
  const p = phase.toUpperCase().trim()
  if (p.includes('ARM')) return 'accentOrange'
  if (p.includes('VOL') || p.includes('FLY')) return 'accentCyan'
  if (p.includes('TERM') || p.includes('FIN') || p.includes('DONE')) return 'accentGreen'
  if (p.includes('ERR') || p.includes('FAIL')) return 'accentRed'
  return 'textMuted'
}

/** Battery level → status color key */
export function batteryColorKey(level: number): keyof Pick<
  ThemeTokens,
  'statusOk' | 'statusWarn' | 'statusCritical'
> {
  if (level > 50) return 'statusOk'
  if (level >= 20) return 'statusWarn'
  return 'statusCritical'
}

/** Motor temp → status color key */
export function motorTempColorKey(temp: number): keyof Pick<
  ThemeTokens,
  'statusOk' | 'statusWarn' | 'statusCritical'
> {
  if (temp < 60) return 'statusOk'
  if (temp <= 80) return 'statusWarn'
  return 'statusCritical'
}
