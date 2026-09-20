// useTheme.js — light/dark mode switching.
//
// Works by setting data-theme="dark" on the <html> element. All the colour
// tokens in styles/tokens.css are redefined under :root[data-theme='dark'],
// so every component that already uses var(--canvas), var(--ink) etc. picks
// up the dark palette automatically — no per-component changes needed.
//
// The choice is saved to localStorage so it survives a refresh. If the user
// has never chosen, we follow their operating system setting.

import { useCallback, useEffect, useState } from 'react'

const THEME_KEY = 'exportAgent.theme.v1'

function getInitialTheme() {
  try {
    const saved = localStorage.getItem(THEME_KEY)
    if (saved === 'light' || saved === 'dark') return saved
  } catch {
    // localStorage unavailable (private browsing) — fall through to default.
  }
  // No saved choice yet: always start in light mode, regardless of the
  // visitor's OS/browser dark-mode setting. Dark mode is opt-in only,
  // switched on by clicking the moon icon — never applied automatically.
  return 'light'
}

export function useTheme() {
  const [theme, setTheme] = useState(getInitialTheme)

  // Apply to <html> and persist whenever it changes.
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    try {
      localStorage.setItem(THEME_KEY, theme)
    } catch {
      /* persisting is best-effort — the theme still applies for this session */
    }
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }, [])

  return { theme, setTheme, toggleTheme, isDark: theme === 'dark' }
}