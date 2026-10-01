import React from 'react'
import {
  LayoutDashboard,
  CalendarCheck2,
  GraduationCap,
  Sparkles,
  Compass,
  Award,
  Users2,
  Database,
  Settings,
  Shield,
  Activity,
  X,
} from 'lucide-react'
import { cn } from '../../lib/utils'

export type NavTab =
  | 'overview'
  | 'attendance'
  | 'academics'
  | 'engagement'
  | 'explorer'
  | 'scholarship'
  | 'mentor'
  | 'data'
  | 'settings'

export interface SidebarProps {
  currentTab: NavTab
  onSelectTab: (tab: NavTab) => void
  isMobileOpen?: boolean
  onCloseMobile?: () => void
}

export function Sidebar({ currentTab, onSelectTab, isMobileOpen = false, onCloseMobile }: SidebarProps) {
  const mainNavItems: Array<{ id: NavTab; label: string; icon: any; isHero?: boolean; badge?: string }> = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'attendance', label: 'Attendance', icon: CalendarCheck2 },
    { id: 'academics', label: 'Academics', icon: GraduationCap },
    { id: 'engagement', label: 'Engagement', icon: Sparkles },
    { id: 'explorer', label: 'Success Explorer', icon: Compass, isHero: true, badge: 'Hero' },
    { id: 'scholarship', label: 'Scholarship Planner', icon: Award },
    { id: 'mentor', label: 'Mentor Explorer', icon: Users2 },
  ]

  const bottomNavItems: Array<{ id: NavTab; label: string; icon: any }> = [
    { id: 'data', label: 'Data Workspace', icon: Database },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  const content = (
    <div className="flex h-full flex-col justify-between bg-slate-900 text-slate-100 w-64 select-none">
      {/* Brand Header */}
      <div>
        <div className="flex h-16 items-center justify-between px-5 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <div className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
                <span>EduPulse</span>
                <span className="text-[10px] bg-blue-500/30 text-blue-300 font-semibold px-1.5 py-0.5 rounded">
                  v2.0
                </span>
              </div>
              <div className="text-[11px] text-slate-400 font-medium">Academic Intelligence</div>
            </div>
          </div>

          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              aria-label="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Primary Navigation */}
        <div className="p-3 space-y-1">
          <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Student Intelligence
          </div>

          {mainNavItems.map((item) => {
            const Icon = item.icon
            const isActive = currentTab === item.id

            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id)
                  if (onCloseMobile) onCloseMobile()
                }}
                className={cn(
                  'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer',
                  isActive
                    ? item.isHero
                      ? 'bg-blue-600 text-white font-semibold shadow-md shadow-blue-600/30'
                      : 'bg-slate-800 text-white font-semibold'
                    : item.isHero
                    ? 'text-blue-300 hover:bg-slate-800/80 hover:text-white'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={cn(
                      'w-4 h-4',
                      isActive ? 'text-white' : item.isHero ? 'text-blue-400' : 'text-slate-400'
                    )}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge && (
                  <span
                    className={cn(
                      'text-[10px] font-bold px-1.5 py-0.2 rounded-full',
                      isActive ? 'bg-white/20 text-white' : 'bg-blue-500/20 text-blue-400'
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="p-3 border-t border-slate-800 space-y-1">
        <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Administration
        </div>
        {bottomNavItems.map((item) => {
          const Icon = item.icon
          const isActive = currentTab === item.id

          return (
            <button
              key={item.id}
              onClick={() => {
                onSelectTab(item.id)
                if (onCloseMobile) onCloseMobile()
              }}
              className={cn(
                'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer',
                isActive ? 'bg-slate-800 text-white font-semibold' : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              )}
            >
              <Icon className={cn('w-4 h-4', isActive ? 'text-white' : 'text-slate-400')} />
              <span>{item.label}</span>
            </button>
          )
        })}

        <div className="mt-3 pt-3 px-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
          <span className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span>Zero-Credential Safe</span>
          </span>
          <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">Offline Safe</span>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden lg:flex shrink-0 h-screen sticky top-0 z-40 border-r border-slate-800">
        {content}
      </aside>

      {/* Mobile Drawer Overlay */}
      {isMobileOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={onCloseMobile}
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-slate-900 shadow-xl z-50">
            {content}
          </div>
        </div>
      )}
    </>
  )
}
