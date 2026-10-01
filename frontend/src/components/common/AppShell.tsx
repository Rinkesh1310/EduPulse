import React, { useState } from 'react'
import { Sidebar, NavTab } from './Sidebar'
import { TopBar } from './TopBar'
import { StudentProfile } from '../../api/client'

export interface AppShellProps {
  currentTab: NavTab
  onSelectTab: (tab: NavTab) => void
  student: StudentProfile | null
  provenance?: string
  asOfDate?: string
  coverage?: string
  children: React.ReactNode
}

export function AppShell({
  currentTab,
  onSelectTab,
  student,
  provenance,
  asOfDate,
  coverage,
  children,
}: AppShellProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900 antialiased selection:bg-blue-600 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={onSelectTab}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Contextual Header */}
        <TopBar
          student={student}
          provenance={provenance}
          asOfDate={asOfDate}
          coverage={coverage}
          onToggleMobileMenu={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          onOpenDataWorkspace={() => onSelectTab('data')}
        />

        {/* Page Container */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
