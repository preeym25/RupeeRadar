import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Radar, LayoutDashboard, Upload, HelpCircle, LogOut, Search, Bell, Settings, Plus } from 'lucide-react'

export function AppLayout() {
  const location = useLocation()
  
  // Only show sidebar when not on upload screen if we wanted to, but we'll keep sidebar everywhere as per dashboard design
  
  return (
    <div className="flex min-h-screen bg-surface-container-lowest text-on-surface">
      {/* Ambient Glow Backgrounds */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-primary/5 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[20%] -right-[5%] w-[40%] h-[40%] bg-secondary/5 blur-[100px] rounded-full"></div>
      </div>

      {/* SideNavBar */}
      <aside className="h-screen sticky top-0 left-0 w-64 flex flex-col bg-surface-container-low border-r border-outline-variant/10 shadow-md z-50 py-lg gap-sm glass-panel">
        <div className="px-lg mb-xl mt-4">
          <div className="flex items-center gap-sm">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground shadow-lg shadow-primary/20">
              <Radar size={24} />
            </div>
            <div>
              <h1 className="font-headline-lg text-title-md font-black text-primary leading-tight">RupeeRadar</h1>
              <p className="text-[10px] text-on-surface-variant tracking-widest uppercase">Wealth Management</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-md flex flex-col gap-base mt-4">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              `flex items-center gap-md px-md py-sm rounded-r-lg group transition-all duration-150 active:scale-95 ${
                isActive || location.pathname === '/dashboard'
                  ? 'text-primary font-bold border-r-4 border-primary bg-primary-container/40'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
              }`
            }
          >
            <LayoutDashboard size={20} />
            <span className="text-body-md">Overview</span>
          </NavLink>
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-md px-md py-sm rounded-r-lg group transition-all duration-150 active:scale-95 ${
                isActive
                  ? 'text-primary font-bold border-r-4 border-primary bg-primary-container/40'
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
              }`
            }
          >
            <Upload size={20} />
            <span className="text-body-md">Upload Data</span>
          </NavLink>
        </nav>

        <div className="px-md mt-auto mb-4">
          <NavLink to="/">
            <button className="w-full py-md px-lg bg-primary text-primary-foreground font-bold rounded-xl shadow-lg shadow-primary/10 hover:bg-primary/90 transition-all flex items-center justify-center gap-sm active:scale-95">
              <Plus size={20} />
              <span>Add Transaction</span>
            </button>
          </NavLink>
        </div>

        <footer className="mt-xl px-md border-t border-outline-variant/10 pt-lg pb-4 flex flex-col gap-base">
          <button className="flex items-center gap-md text-on-surface-variant hover:text-on-surface px-md py-sm hover:bg-surface-container-high transition-all rounded-lg group text-left">
            <HelpCircle size={20} />
            <span className="text-body-md">Help</span>
          </button>
          <button className="flex items-center gap-md text-on-surface-variant hover:text-on-surface px-md py-sm hover:bg-surface-container-high transition-all rounded-lg group text-left">
            <LogOut size={20} />
            <span className="text-body-md">Sign Out</span>
          </button>
        </footer>
      </aside>

      {/* Main Content Canvas */}
      <main className="flex-1 flex flex-col overflow-y-auto custom-scrollbar h-screen relative z-10">
        {/* TopNavBar */}
        <header className="w-full sticky top-0 z-40 bg-surface/80 backdrop-blur-xl shadow-sm border-b border-outline-variant/10 flex items-center justify-between px-lg py-4">
          <div className="flex items-center gap-lg">
            <div className="relative flex items-center">
              <Search className="absolute left-4 text-on-surface-variant" size={18} />
              <input
                className="bg-surface-container-highest/50 border-none rounded-full pl-12 pr-4 py-2 w-80 text-body-md focus:ring-1 focus:ring-primary transition-all outline-none"
                placeholder="Search capital flows..."
                type="text"
              />
            </div>
          </div>
          <div className="flex items-center gap-md">
            <button className="w-10 h-10 flex items-center justify-center rounded-full text-on-surface-variant hover:bg-surface-container-highest transition-colors duration-200 active:scale-95">
              <Bell size={20} />
            </button>
            <button className="w-10 h-10 flex items-center justify-center rounded-full text-on-surface-variant hover:bg-surface-container-highest transition-colors duration-200 active:scale-95">
              <Settings size={20} />
            </button>
            <div className="h-8 w-[1px] bg-outline-variant/20 mx-2"></div>
            <div className="flex items-center gap-sm pl-2 cursor-pointer group">
              <span className="text-right">
                <p className="text-sm font-bold text-on-surface block group-hover:text-primary transition-colors">V. Malhotra</p>
                <p className="text-[10px] text-on-surface-variant font-medium uppercase tracking-tighter">Gold Tier Member</p>
              </span>
              <div className="w-10 h-10 rounded-full border border-primary/20 p-[2px] ml-3">
                <img
                  className="w-full h-full rounded-full object-cover"
                  alt="Profile"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCXKwwDE_0syqhDav7CrH-pOMD9_ptwC-iV6oyVD6UxcmrmZ2HnG_juubCFWC6mqpTgCkMB7rhGriO3kuP10d7XJWqM6It9gb6k_nYEhNM0HFtg7H9MlST7zO_5Q_xA6hSF7llb9mknBFdPkArYIerq2d4vHldAYbgBNJ5Y-YLEZNykk6fB3BK-kwUEsi6TTFKEJBvxA9TL5kfvjhi_ZqjA6C_HNmag4Xh1RCcij7zbsmqXGQorPfp9QFSTvM6MjcNVTnvB0IpKIu0"
                />
              </div>
            </div>
          </div>
        </header>

        <section className="p-lg lg:p-xl mx-auto w-full max-w-[1400px]">
          <Outlet />
        </section>
        
        {/* Footer Visual Decor */}
        <footer className="p-lg mt-auto flex justify-between items-center opacity-40">
          <p className="text-[10px] tracking-widest uppercase">RUPEERADAR INSTITUTIONAL v4.2.0</p>
          <div className="flex gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-outline-variant"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-outline-variant"></div>
          </div>
        </footer>
      </main>
    </div>
  )
}
