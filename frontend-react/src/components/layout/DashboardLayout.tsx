import { useLocation, useOutlet } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { AppBar } from './AppBar'
import { NavSidebar } from './NavSidebar'
import { useThemeColors } from '../../hooks/useThemeColors'

const pageTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -6 },
  transition: { duration: 0.28, ease: 'easeOut' as const },
}

/**
 * AnimatePresence must wrap a *snapshot* of the matched route element, not a live
 * `<Outlet />`. A single Outlet always reflects the current URL, so during exit
 * animations the leaving and entering wrappers fight over the same outlet output.
 */
function AnimatedOutlet() {
  const location = useLocation()
  const outlet = useOutlet()

  if (outlet == null) {
    return null
  }

  return (
    <AnimatePresence initial={false} mode="wait">
      <motion.div
        key={location.pathname}
        initial={pageTransition.initial}
        animate={pageTransition.animate}
        exit={pageTransition.exit}
        transition={pageTransition.transition}
        className="h-full min-h-[calc(100vh-3.5rem)]"
        style={{ willChange: 'transform, opacity' }}
      >
        {outlet}
      </motion.div>
    </AnimatePresence>
  )
}

export function DashboardLayout() {
  const { scaffoldBg, textPrimary } = useThemeColors()

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
        <main className="dark-scrollbar relative min-h-0 flex-1 overflow-auto">
          <AnimatedOutlet />
        </main>
      </div>
    </div>
  )
}