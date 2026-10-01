import React from 'react'
import { DataSourceBadge } from './DataSourceBadge'
import { Bell, Menu, User, Calendar, Database } from 'lucide-react'
import { Button } from '../ui/Button'
import { StudentProfile } from '../../api/client'

export interface TopBarProps {
  student: StudentProfile | null
  provenance?: string
  asOfDate?: string
  coverage?: string
  onToggleMobileMenu: () => void
  onOpenDataWorkspace: () => void
}

export function TopBar({
  student,
  provenance = 'Demo data',
  asOfDate = '2026-09-30',
  coverage,
  onToggleMobileMenu,
  onOpenDataWorkspace,
}: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200/90 bg-white/95 px-4 sm:px-6 backdrop-blur-sm shadow-2xs">
      {/* Left: Mobile hamburger & Contextual Student Identity */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleMobileMenu}
          className="lg:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 cursor-pointer"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex w-9 h-9 rounded-full bg-blue-600/10 text-blue-700 font-bold text-sm items-center justify-center border border-blue-200">
            {student?.name ? student.name.charAt(0) : 'S'}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 text-sm sm:text-base leading-tight">
                {student?.name || 'Active Student Profile'}
              </span>
              <span className="text-xs text-slate-500 font-medium hidden md:inline">
                ({student?.externalStudentId || 'ID-001'})
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
              <span>{student?.program ? `${student.program} • Sem ${student.semester}` : 'Enrolled Academic Term'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right: Data Source Badge, As-of state & Actions */}
      <div className="flex items-center gap-2 sm:gap-3">
        <button
          type="button"
          onClick={onOpenDataWorkspace}
          className="cursor-pointer transition-transform active:scale-95"
          title="Click to view data provenance or change student profile"
        >
          <DataSourceBadge provenance={provenance} />
        </button>

        <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-500 px-2 py-1 rounded bg-slate-50 border border-slate-200/80">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>As of {asOfDate}</span>
        </div>

        {coverage && (
          <div className="hidden xl:inline-flex text-xs text-slate-600 font-medium px-2 py-1 rounded bg-slate-100 border border-slate-200">
            Coverage: <strong className="ml-1 text-slate-800">{coverage}</strong>
          </div>
        )}

        <Button
          variant="outline"
          size="sm"
          onClick={onOpenDataWorkspace}
          className="hidden sm:inline-flex gap-1.5 text-xs text-slate-700 h-8"
        >
          <Database className="w-3.5 h-3.5 text-blue-600" />
          <span>Data Workspace</span>
        </Button>
      </div>
    </header>
  )
}
