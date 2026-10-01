import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Settings, Shield, Sliders, Info, CheckCircle2 } from 'lucide-react'

export interface SettingsPageProps {
  onRefresh?: () => void
}

export function SettingsPage({ onRefresh }: SettingsPageProps) {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Settings className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Platform Settings & Privacy
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Policy thresholds, privacy guarantees, and system configuration.
          </p>
        </div>
      </div>

      {/* 2. Institutional Policy Thresholds */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-blue-600" />
            Active Institutional Academic Policy
          </CardTitle>
          <p className="text-xs text-slate-500">
            System thresholds configured for attendance alerts and academic evaluations.
          </p>
        </CardHeader>
        <CardContent className="p-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1">
              <span className="text-slate-500 font-semibold block">Overall Attendance</span>
              <div className="text-2xl font-bold text-slate-900">70.0%</div>
              <p className="text-slate-400">Institutional minimum compliance</p>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1">
              <span className="text-slate-500 font-semibold block">Per-Course Component</span>
              <div className="text-2xl font-bold text-slate-900">70.0%</div>
              <p className="text-slate-400">Individual lecture / lab standard</p>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1">
              <span className="text-slate-500 font-semibold block">Academic Benchmark</span>
              <div className="text-2xl font-bold text-slate-900">50.0%</div>
              <p className="text-slate-400">Midterm passing evaluation</p>
            </div>

            <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-1">
              <span className="text-slate-500 font-semibold block">Small-Sample Guard</span>
              <div className="text-2xl font-bold text-slate-900">≥ 5 sessions</div>
              <p className="text-slate-400">Prevents premature alerts</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 3. Security & Data Privacy Assurances */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            Security & Privacy Guarantees
          </CardTitle>
        </CardHeader>
        <CardContent className="p-5 space-y-3 text-xs sm:text-sm text-slate-700">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900">Zero Credential Retention:</strong> EduPulse never asks for, accepts, or stores university passwords, session tokens, or CAPTCHAs.
            </div>
          </div>

          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900">K-Anonymity Cohort Guard:</strong> In mentor analytics, any exploratory cluster with fewer than 5 members is automatically suppressed to protect individual privacy.
            </div>
          </div>

          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900">Local SQLite Storage:</strong> All student assessments, attendance records, and self-attested facts are processed strictly on your dedicated local system.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
