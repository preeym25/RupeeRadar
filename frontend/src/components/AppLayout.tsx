import { NavLink, Outlet } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { Sun, Moon } from 'lucide-react'
import { RupeeRadarIcon } from './RupeeRadarIcon'

export function AppLayout() {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') !== 'light'
    }
    return true
  })

  useEffect(() => {
    const root = document.documentElement
    if (isDark) {
      root.classList.remove('light')
      localStorage.setItem('theme', 'dark')
    } else {
      root.classList.add('light')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  const toggleTheme = () => setIsDark(prev => !prev)

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      <header className="border-b border-border bg-surface-bright/50 backdrop-blur-xl transition-colors duration-200">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground transition-colors duration-200">
              <RupeeRadarIcon className="w-8 h-8" />
            </span>
            <div>
              <p className="text-lg font-bold text-foreground transition-colors duration-200">RupeeRadar</p>
              <p className="text-xs text-foreground/60 transition-colors duration-200">Personal finance insights</p>
            </div>
          </div>
          <nav className="flex items-center gap-2">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                  isActive ? 'bg-primary/10 text-primary' : 'text-foreground/70 hover:bg-surface-bright hover:text-foreground'
                }`
              }
              end
            >
              Upload
            </NavLink>
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                  isActive ? 'bg-primary/10 text-primary' : 'text-foreground/70 hover:bg-surface-bright hover:text-foreground'
                }`
              }
            >
              Dashboard
            </NavLink>
            <button
              onClick={toggleTheme}
              className="ml-4 rounded-full p-2 text-foreground/70 transition-colors hover:bg-surface-bright hover:text-foreground"
              aria-label="Toggle theme"
            >
              {isDark ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
