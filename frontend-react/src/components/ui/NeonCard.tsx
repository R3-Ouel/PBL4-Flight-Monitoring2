import type { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { useThemeColors } from '../../hooks/useThemeColors'

interface NeonCardProps {
  children: ReactNode
  className?: string
  emphasized?: boolean
}

export function NeonCard({
  children,
  className = '',
  emphasized = false,
}: NeonCardProps) {
  const c = useThemeColors()

  return (
    <motion.div
      layout
      className={`rounded-xl border p-3 ${className}`}
      style={{
        backgroundColor: c.cardBg,
        borderColor: emphasized ? c.borderEmphasis : c.borderDefault,
        boxShadow: c.cardShadow,
        color: c.textPrimary,
      }}
    >
      {children}
    </motion.div>
  )
}
