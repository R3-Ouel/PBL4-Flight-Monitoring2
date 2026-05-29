import { create } from 'zustand'
import {
  applyThemeToDocument,
  loadStoredTheme,
  saveTheme,
  type ThemeMode,
} from '../styles/tokens'

interface AppState {
  isLive: boolean
  theme: ThemeMode
  setIsLive: (value: boolean) => void
  setTheme: (theme: ThemeMode) => void
  toggleTheme: () => void
}

const initialTheme = loadStoredTheme()
applyThemeToDocument(initialTheme)

export const useAppStore = create<AppState>((set) => ({
  isLive: true,
  theme: initialTheme,
  setIsLive: (value) => set({ isLive: value }),
  setTheme: (theme) => {
    saveTheme(theme)
    applyThemeToDocument(theme)
    set({ theme })
  },
  toggleTheme: () =>
    set((s) => {
      const next: ThemeMode = s.theme === 'dark' ? 'light' : 'dark'
      saveTheme(next)
      applyThemeToDocument(next)
      return { theme: next }
    }),
}))
