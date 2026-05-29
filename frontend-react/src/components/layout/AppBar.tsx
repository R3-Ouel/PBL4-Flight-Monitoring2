import { motion } from 'framer-motion'
import { Moon, RotateCcw, Sun, Wifi } from 'lucide-react'
import { flightService } from '../../services/flightService'
import { useAppStore } from '../../store/useAppStore'
import { useThemeColors } from '../../hooks/useThemeColors'

export function AppBar() {
  const isLive = useAppStore((s) => s.isLive)
  const setIsLive = useAppStore((s) => s.setIsLive)
  const toggleTheme = useAppStore((s) => s.toggleTheme)
  const { theme, accentRed, accentGreen, navInactive, textPrimary } =
    useThemeColors()
  const isDark = theme === 'dark'

  return (
    <header
      className="flex h-14 shrink-0 items-center justify-between px-5"
      style={{
        backgroundColor: 'var(--topbar-bg)',
        borderBottom: '1px solid var(--topbar-border)',
        boxShadow: isDark
          ? '0 1px 0 var(--topbar-border)'
          : '0 1px 8px rgba(0,0,0,0.08)',
      }}
    >
      <h1
        className="text-lg font-bold tracking-[0.2em]"
        style={{ color: accentRed }}
      >
        FLIGHT CONTROL CENTER
      </h1>
      <div className="flex items-center gap-3">
        <Wifi
          size={18}
          style={{ color: isLive ? accentGreen : navInactive }}
        />
        <span
          className="text-xs font-bold"
          style={{ color: isLive ? accentGreen : navInactive }}
        >
          CONNECTÉ AU DRONE
        </span>
        <label className="relative inline-flex cursor-pointer items-center">
          <input
            type="checkbox"
            className="peer sr-only"
            checked={isLive}
            onChange={(e) => setIsLive(e.target.checked)}
          />
          <div
            className="h-6 w-11 rounded-full transition-colors peer-checked:bg-[var(--accent-green)]"
            style={{ backgroundColor: 'var(--toggle-track)' }}
          />
          <div
            className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full shadow transition-transform peer-checked:translate-x-5"
            style={{ backgroundColor: 'var(--toggle-thumb)' }}
          />
        </label>
        <motion.button
          type="button"
          whileHover={{ rotate: 15 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleTheme}
          className="rounded-lg p-2 transition-colors hover:opacity-80"
          style={{ color: textPrimary }}
          title={isDark ? 'Basculer en mode clair' : 'Basculer en mode sombre'}
        >
          {isDark ? <Moon size={20} /> : <Sun size={20} style={{ color: 'var(--accent-orange)' }} />}
        </motion.button>
        <motion.button
          type="button"
          whileHover={{ rotate: -90 }}
          whileTap={{ scale: 0.9 }}
          onClick={() => flightService.resetBuffers()}
          className="rounded-lg p-2 transition-colors hover:opacity-80"
          title="Reset graphs"
          style={{ color: navInactive }}
        >
          <RotateCcw size={20} />
        </motion.button>
      </div>
    </header>
  )
}
