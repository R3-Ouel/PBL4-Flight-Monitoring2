import type { BufferKey } from '../types/flight'
import { getTokens, type ThemeMode } from './tokens'

export type { ThemeMode }

function t(theme: ThemeMode) {
  return getTokens(theme)
}

export function accentRed(theme: ThemeMode): string {
  return t(theme).accentRed
}

export function accentGreen(theme: ThemeMode): string {
  return t(theme).accentGreen
}

export function accentCyan(theme: ThemeMode): string {
  return t(theme).accentCyan
}

export function accentPink(theme: ThemeMode): string {
  return t(theme).accentPink
}

export function accentOrange(theme: ThemeMode): string {
  return t(theme).accentOrange
}

export function accentBlue(theme: ThemeMode): string {
  return t(theme).accentBlue
}

export function navInactive(theme: ThemeMode): string {
  return t(theme).navInactive
}

export function cardBg(theme: ThemeMode): string {
  return t(theme).cardBg
}

export function scaffoldBg(theme: ThemeMode): string {
  return t(theme).scaffoldBg
}

export function sidebarBg(theme: ThemeMode): string {
  return t(theme).sidebarBg
}

export function columnIdToKey(id: number): BufferKey | 'timestamp' | '' {
  switch (id) {
    case 0:
      return 'timestamp'
    case 1:
      return 'altitude'
    case 2:
      return 'speed'
    case 5:
      return 'az'
    case 6:
      return 'roll'
    case 7:
      return 'pitch'
    case 8:
      return 'yaw'
    default:
      return ''
  }
}
