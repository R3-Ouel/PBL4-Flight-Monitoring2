import { useAppStore } from '../store/useAppStore'
import { getTokens } from '../styles/tokens'
import * as colors from '../styles/colors'

export function useThemeColors() {
  const theme = useAppStore((s) => s.theme)
  const tokens = getTokens(theme)
  return {
    theme,
    ...tokens,
    accentRed: colors.accentRed(theme),
    accentGreen: colors.accentGreen(theme),
    accentCyan: colors.accentCyan(theme),
    accentPink: colors.accentPink(theme),
    accentOrange: colors.accentOrange(theme),
    accentBlue: colors.accentBlue(theme),
    navInactive: colors.navInactive(theme),
    cardBg: colors.cardBg(theme),
    scaffoldBg: colors.scaffoldBg(theme),
    sidebarBg: colors.sidebarBg(theme),
  }
}
