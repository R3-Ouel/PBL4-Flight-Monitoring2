import { NavLink } from 'react-router-dom'
import { BarChart3, Camera, Map } from 'lucide-react'
import { motion } from 'framer-motion'
import { useThemeColors } from '../../hooks/useThemeColors'

const navItems = [
  { to: '/analyse', label: 'Analyse', icon: BarChart3 },
  { to: '/navigation', label: 'Navigation', icon: Map },
  { to: '/camera', label: 'Caméra', icon: Camera },
] as const

export function NavSidebar() {
  const { sidebarBg, accentRed, navInactive } = useThemeColors()

  return (
    <aside
      className="flex w-20 shrink-0 flex-col items-center justify-center gap-2 py-4"
      style={{ backgroundColor: sidebarBg }}
    >
      {navItems.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          title={label}
          className="group relative"
        >
          {({ isActive }) => (
            <motion.div
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              className="flex h-14 w-14 items-center justify-center rounded-xl border transition-colors duration-200"
              style={{
                backgroundColor: isActive ? `${accentRed}26` : 'transparent',
                borderColor: isActive ? `${accentRed}b3` : 'transparent',
              }}
            >
              <Icon
                size={26}
                style={{ color: isActive ? accentRed : navInactive }}
              />
            </motion.div>
          )}
        </NavLink>
      ))}
    </aside>
  )
}
