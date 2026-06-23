import { useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Radar, LayoutDashboard, Upload, HelpCircle, LogOut, Search, Bell, Settings, Plus, Lock, ListOrdered, Repeat, PieChart, FileText, ChevronLeft, ChevronRight } from 'lucide-react'
import { useAnalysis } from '../hooks/useAnalysis'

export function AppLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { result, clearAnalysis } = useAnalysis()
  const hasData = result !== null

  const [isCollapsed, setIsCollapsed] = useState(() => {
    return localStorage.getItem('sidebar_collapsed') === 'true'
  })

  const toggleSidebar = () => {
    setIsCollapsed(prev => {
      const next = !prev
      localStorage.setItem('sidebar_collapsed', String(next))
      return next
    })
  }

  const handleSignOut = async () => {
    await clearAnalysis()
    navigate('/')
  }

  const renderSidebarLink = (tabId: string, label: string, icon: React.ReactNode, path: string) => {
    if (hasData) {
      const currentPath = location.pathname + location.search
      const isActive = currentPath === path || (tabId === 'overview' && location.pathname === '/dashboard' && !location.search.includes('tab='));
      return (
        <NavLink
          key={tabId}
          to={path}
          className={`flex items-center rounded-lg group transition-all duration-150 active:scale-95 ${
            isCollapsed ? 'justify-center p-sm mx-auto w-10 h-10' : 'gap-md px-md py-sm rounded-r-lg'
          } ${
            isActive
              ? 'text-primary font-bold bg-primary-container/40' + (isCollapsed ? '' : ' border-r-4 border-primary')
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
          }`}
          title={isCollapsed ? label : undefined}
        >
          {icon}
          {!isCollapsed && <span className="text-body-md">{label}</span>}
        </NavLink>
      )
    } else {
      return (
        <div
          key={tabId}
          className={`flex items-center rounded-lg text-on-surface-variant/40 cursor-not-allowed select-none group relative ${
            isCollapsed ? 'justify-center p-sm mx-auto w-10 h-10' : 'justify-between px-md py-sm rounded-r-lg'
          }`}
          title={isCollapsed ? `${label} (Locked)` : "Upload a statement to unlock"}
        >
          <div className="flex items-center gap-md">
            {icon}
            {!isCollapsed && <span className="text-body-md transition-colors group-hover:text-on-surface-variant/60">{label}</span>}
          </div>
          {!isCollapsed && <Lock size={14} className="text-on-surface-variant/30 group-hover:text-on-surface-variant/50 transition-colors" />}
          {isCollapsed && <Lock size={10} className="absolute bottom-1 right-1 text-on-surface-variant/30" />}
        </div>
      )
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-surface-container-lowest text-on-surface">
      {/* Ambient Glow Backgrounds */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-primary/5 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[20%] -right-[5%] w-[40%] h-[40%] bg-secondary/5 blur-[100px] rounded-full"></div>
      </div>

      <aside className={`h-full flex flex-col bg-surface-container-low border-r border-outline-variant/10 shadow-md z-50 py-md gap-xs glass-panel overflow-y-auto custom-scrollbar transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'}`}>
        <div className={`mt-2 mb-md ${isCollapsed ? 'flex justify-center px-xs' : 'px-lg'}`}>
          <div className="flex items-center gap-sm">
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-foreground shadow-lg shadow-primary/20 shrink-0">
              <Radar size={24} />
            </div>
            {!isCollapsed && (
              <div>
                <h1 className="font-headline-lg text-title-md font-black text-primary leading-tight">RupeeRadar</h1>
                <p className="text-[10px] text-on-surface-variant tracking-widest uppercase">Wealth Management</p>
              </div>
            )}
          </div>
        </div>

        <nav className={`flex flex-col mt-2 ${isCollapsed ? 'px-xs gap-2' : 'px-md gap-xs'}`}>
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center rounded-lg group transition-all duration-150 active:scale-95 ${
                isCollapsed ? 'justify-center p-sm mx-auto w-10 h-10' : 'gap-md px-md py-sm rounded-r-lg'
              } ${
                isActive
                  ? 'text-primary font-bold bg-primary-container/40' + (isCollapsed ? '' : ' border-r-4 border-primary')
                  : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
              }`
            }
            title={isCollapsed ? "Upload Data" : undefined}
          >
            <Upload size={20} />
            {!isCollapsed && <span className="text-body-md">Upload Data</span>}
          </NavLink>
          
          <div className="h-[1px] bg-outline-variant/10 my-1"></div>
          
          {renderSidebarLink('overview', 'Overview', <LayoutDashboard size={20} />, '/dashboard?tab=overview')}
          {renderSidebarLink('transactions', 'Ledger', <ListOrdered size={20} />, '/dashboard?tab=transactions')}
          {renderSidebarLink('recurring', 'Recurring', <Repeat size={20} />, '/dashboard?tab=recurring')}
          {renderSidebarLink('portfolio_audit', 'Portfolio Audit', <PieChart size={20} />, '/dashboard?tab=portfolio_audit')}
          {renderSidebarLink('report', 'Report Summary', <FileText size={20} />, '/dashboard?tab=report')}
        </nav>

        <div className={isCollapsed ? 'px-xs mt-auto mb-2 text-center' : 'px-md mt-auto mb-2'}>
          <NavLink to="/">
            {isCollapsed ? (
              <button 
                className="w-10 h-10 bg-primary text-primary-foreground font-bold rounded-full shadow-lg shadow-primary/10 hover:bg-primary/90 transition-all flex items-center justify-center active:scale-95 mx-auto cursor-pointer"
                title="Add Transaction"
              >
                <Plus size={20} />
              </button>
            ) : (
              <button className="w-full py-sm px-md bg-primary text-primary-foreground font-bold rounded-xl shadow-lg shadow-primary/10 hover:bg-primary/90 transition-all flex items-center justify-center gap-sm active:scale-95 cursor-pointer">
                <Plus size={20} />
                <span>Add Transaction</span>
              </button>
            )}
          </NavLink>
        </div>

        <footer className={`mt-auto border-t border-outline-variant/10 pt-sm pb-sm flex flex-col gap-xs ${isCollapsed ? 'px-xs items-center' : 'px-md'}`}>
          <button 
            className={`flex items-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all rounded-lg group text-left ${
              isCollapsed ? 'justify-center w-10 h-10 p-0' : 'gap-md px-md py-xs w-full'
            }`}
            title={isCollapsed ? "Help" : undefined}
          >
            <HelpCircle size={20} />
            {!isCollapsed && <span className="text-body-md">Help</span>}
          </button>
          
          <button 
            onClick={handleSignOut}
            className={`flex items-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all rounded-lg group text-left cursor-pointer ${
              isCollapsed ? 'justify-center w-10 h-10 p-0' : 'gap-md px-md py-xs w-full'
            }`}
            title={isCollapsed ? "Sign Out" : undefined}
          >
            <LogOut size={20} />
            {!isCollapsed && <span className="text-body-md">Sign Out</span>}
          </button>

          <div className="h-[1px] bg-outline-variant/10 w-full my-1"></div>

          <button
            onClick={toggleSidebar}
            className={`flex items-center text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all rounded-lg group text-left cursor-pointer ${
              isCollapsed ? 'justify-center w-10 h-10 p-0' : 'gap-md px-md py-xs w-full'
            }`}
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
            {!isCollapsed && <span className="text-body-md">Collapse</span>}
          </button>
        </footer>
      </aside>

      {/* Main Content Canvas */}
      <main className="flex-1 flex flex-col overflow-y-auto custom-scrollbar h-full relative z-10">
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
