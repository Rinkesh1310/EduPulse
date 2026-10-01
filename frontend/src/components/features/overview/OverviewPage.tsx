import React from 'react'
import { OverviewData } from '../../../api/client'
import { MetricCard } from '../../common/MetricCard'
import { StatusBadge } from '../../common/StatusBadge'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import {
  CalendarCheck2,
  GraduationCap,
  Sparkles,
  Compass,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  Award,
  BookOpen,
} from 'lucide-react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

export interface OverviewPageProps {
  data: OverviewData
  onNavigate: (tab: any) => void
}

export function OverviewPage({ data, onNavigate }: OverviewPageProps) {
  const { metrics, attentionAreas, performanceTrend, recommendedActions, scholarshipReadiness } = data

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Hero Section: "Your academic snapshot" */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-blue-950 p-6 sm:p-8 text-white shadow-md">
        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
              <Compass className="w-3.5 h-3.5" />
              Academic Snapshot
            </span>
            <div className="flex items-center gap-2">
              <StatusBadge level={data.supportStatus} className="text-xs" />
            </div>
          </div>

          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white mb-2">
              Your academic snapshot
            </h1>
            <p className="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">
              {data.snapshotNarrative}
            </p>
          </div>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Button
              variant="primary"
              size="sm"
              onClick={() => onNavigate('explorer')}
              className="bg-blue-500 hover:bg-blue-600 text-white font-semibold text-xs sm:text-sm gap-2"
            >
              <span>Open Success Explorer</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('attendance')}
              className="bg-white/10 hover:bg-white/20 text-white border-white/20 text-xs sm:text-sm"
            >
              <span>View Attendance Intelligence</span>
            </Button>
          </div>
        </div>
      </div>

      {/* 2. Primary 4 Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Attendance"
          value={metrics.attendance.value}
          subtext={`${metrics.attendance.present}/${metrics.attendance.total} sessions recorded`}
          statusLevel={metrics.attendance.status}
          trend={metrics.attendance.trend}
          icon={CalendarCheck2}
          onClick={() => onNavigate('attendance')}
        />
        <MetricCard
          title="Academic Performance"
          value={metrics.academics.value}
          subtext={`${metrics.academics.belowBenchmarkCount} subject(s) below benchmark`}
          statusLevel={metrics.academics.status}
          icon={GraduationCap}
          onClick={() => onNavigate('academics')}
        />
        <MetricCard
          title="Engagement Portfolio"
          value={metrics.engagement.value}
          subtext={`${metrics.engagement.eventCount} confirmed event(s) • ${metrics.engagement.level}`}
          statusLevel={metrics.engagement.status}
          icon={Sparkles}
          onClick={() => onNavigate('engagement')}
        />
        <MetricCard
          title="Support Signal"
          value={metrics.supportSignal.badgeText}
          subtext={metrics.supportSignal.description}
          statusLevel={metrics.supportSignal.level}
          icon={Compass}
          onClick={() => onNavigate('explorer')}
        />
      </div>

      {/* 3. Attention Areas & Performance Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Academic Attention Areas */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="h-full border-slate-200/90 shadow-xs flex flex-col justify-between">
            <div>
              <CardHeader className="p-5 pb-3 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-amber-600">
                    <AlertTriangle className="w-4 h-4" />
                    <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900">
                      Attention Areas
                    </CardTitle>
                  </div>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                    {attentionAreas.totalAlerts} Alert{attentionAreas.totalAlerts !== 1 ? 's' : ''}
                  </span>
                </div>
              </CardHeader>

              <CardContent className="p-5 space-y-3">
                {attentionAreas.totalAlerts === 0 ? (
                  <div className="text-center py-8 text-slate-500 text-xs">
                    <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-2 font-bold">
                      ✓
                    </div>
                    All enrolled subjects and attendance components currently satisfy institutional benchmarks.
                  </div>
                ) : (
                  <>
                    {attentionAreas.attendanceAlerts.map((alt, idx) => (
                      <div
                        key={`att-${idx}`}
                        className="p-3 rounded-lg border border-rose-200 bg-rose-50/60 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-rose-900">{alt.courseName}</span>
                          <span className="font-extrabold text-rose-700">{alt.percentage.toFixed(1)}%</span>
                        </div>
                        <p className="text-rose-800">{alt.message}</p>
                      </div>
                    ))}

                    {attentionAreas.academicAlerts.map((alt, idx) => (
                      <div
                        key={`acad-${idx}`}
                        className="p-3 rounded-lg border border-amber-200 bg-amber-50/60 text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-amber-900">{alt.courseName} ({alt.assessmentType})</span>
                          <span className="font-extrabold text-amber-700">{alt.percentage.toFixed(1)}%</span>
                        </div>
                        <p className="text-amber-800">{alt.message}</p>
                      </div>
                    ))}
                  </>
                )}
              </CardContent>
            </div>

            <div className="p-4 border-t border-slate-100 bg-slate-50/50 rounded-b-xl">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onNavigate('explorer')}
                className="w-full text-xs text-blue-600 hover:text-blue-700 font-semibold gap-1.5"
              >
                <span>Review detailed evidence</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </Card>
        </div>

        {/* SGPA Performance Trend Chart */}
        <div className="lg:col-span-2">
          <Card className="h-full border-slate-200/90 shadow-xs flex flex-col justify-between">
            <CardHeader className="p-5 pb-2 flex flex-row items-center justify-between border-b border-slate-100">
              <div>
                <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-blue-600" />
                  Academic Progression (SGPA Trend)
                </CardTitle>
                <p className="text-xs text-slate-500 mt-0.5">
                  Multi-semester cumulative academic performance progression
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onNavigate('academics')}
                className="text-xs h-7"
              >
                Academics Details
              </Button>
            </CardHeader>

            <CardContent className="p-5 pt-4">
              {performanceTrend.sgpaHistory.length > 0 ? (
                <div className="h-56 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={performanceTrend.sgpaHistory} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="semester" stroke="#94a3b8" fontSize={11} tickLine={false} />
                      <YAxis domain={[5.0, 10.0]} stroke="#94a3b8" fontSize={11} tickLine={false} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0f172a',
                          borderRadius: '8px',
                          color: '#fff',
                          fontSize: '12px',
                          border: 'none',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="sgpa"
                        name="SGPA"
                        stroke="#2563eb"
                        strokeWidth={3}
                        dot={{ r: 5, fill: '#2563eb' }}
                        activeDot={{ r: 7 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="h-56 flex items-center justify-center text-xs text-slate-400">
                  No historical semester results available for current profile.
                </div>
              )}
            </CardContent>

            <div className="p-4 border-t border-slate-100 bg-slate-50/50 rounded-b-xl flex items-center justify-between text-xs text-slate-500">
              <span>Enrolled Courses: <strong>{performanceTrend.enrolledCoursesCount}</strong></span>
              <span>Grading Basis: 10-Point SGPA Scale</span>
            </div>
          </Card>
        </div>
      </div>

      {/* 4. Recommended Actions & Scholarship Readiness Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Recommended Actions */}
        <Card className="border-slate-200/90 shadow-xs">
          <CardHeader className="p-5 pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600" />
              Recommended Next Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 space-y-2.5">
            {recommendedActions.map((act, i) => (
              <div key={i} className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-700">
                <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <span className="leading-snug">{act}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Scholarship Readiness Snapshot */}
        <Card className="border-slate-200/90 shadow-xs flex flex-col justify-between">
          <CardHeader className="p-5 pb-3 border-b border-slate-100">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-600" />
                Scholarship Readiness Snapshot
              </CardTitle>
              {scholarshipReadiness && (
                <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  {scholarshipReadiness.verificationLevel.replace('_', ' ')}
                </span>
              )}
            </div>
          </CardHeader>
          <CardContent className="p-5 space-y-3">
            {scholarshipReadiness ? (
              <>
                <div>
                  <h4 className="font-bold text-slate-800 text-sm">{scholarshipReadiness.schemeName}</h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Official state scholarship eligibility audit based on local academic records.
                  </p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700">
                  Status: <strong>{scholarshipReadiness.summaryCounts}</strong>
                </div>
              </>
            ) : (
              <div className="text-xs text-slate-500 py-4">
                No active scholarship evaluation configured for this term.
              </div>
            )}
          </CardContent>
          <div className="p-4 border-t border-slate-100 bg-slate-50/50 rounded-b-xl">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('scholarship')}
              className="w-full text-xs font-semibold"
            >
              Open Scholarship Planner
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
