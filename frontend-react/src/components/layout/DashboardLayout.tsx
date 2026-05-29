import { Outlet } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { useLocation } from 'react-router-dom'
import { AppBar } from './AppBar'
import { NavSidebar } from './NavSidebar'
import { useThemeColors } from '../../hooks/useThemeColors'

export function DashboardLayout() {
  const { scaffoldBg, textPrimary } = useThemeColors()
  const location = useLocation()

  return (
    <div
      className="flex h-full min-h-screen flex-col transition-colors duration-450"
      style={{ backgroundColor: scaffoldBg, color: textPrimary }}
    >
      <AppBar />
      <div className="flex min-h-0 flex-1">
        <NavSidebar />
        <div
          className="w-px shrink-0"
          style={{ backgroundColor: 'var(--divider)' }}
        />
        <main className="dark-scrollbar min-h-0 flex-1 overflow-auto">
          <AnimatePresence initial={false} mode="sync">
            <motion.div
              // Using `location.key` avoids edge cases where transitions don't
              // re-run when navigating to the same path with different state.
              key={location.key}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.28, ease: 'easeOut' }}
              className="h-full min-h-[calc(100vh-3.5rem)]"
              style={{ willChange: 'transform, opacity' }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
