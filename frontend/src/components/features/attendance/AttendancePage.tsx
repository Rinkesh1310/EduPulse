import React, { useState } from 'react'
import { AttendanceSummaryData, api, RecoveryResult } from '../../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Input } from '../../ui/Input'
import { Select } from '../../ui/Select'
import { Badge } from '../../ui/Badge'
import {
  CalendarCheck2,
  AlertTriangle,
  Calculator,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
} from 'lucide-react'

export interface AttendancePageProps {
  data: AttendanceSummaryData
  studentId: string
  onRefresh?: () => void
}

export function AttendancePage({ data, studentId, onRefresh }: AttendancePageProps) {
  const { computedOverall, portalOverall, totalPresent, totalClasses, headline, targetPct, courseTargetPct, records, mismatchNote, dailyTimeline } =
    data

  // Recovery Calculator State
  const [selectedComponentId, setSelectedComponentId] = useState<string>('overall')
  const [targetSlider, setTargetSlider] = useState<number>(targetPct || 70)
  const [futureClasses, setFutureClasses] = useState<number>(35)
  const [recoveryResult, setRecoveryResult] = useState<RecoveryResult | null>(null)
  const [isSimulating, setIsSimulating] = useState<boolean>(false)

  // Determine current present/total based on selection
  const currentSelection = records.find((r) => r.id === selectedComponentId)
  const curP = currentSelection ? currentSelection.presentCount : totalPresent
  const curT = currentSelection ? currentSelection.totalCount : totalClasses

  const handleSimulate = async (tPct = targetSlider, rem = futureClasses, compId = selectedComponentId) => {
    setIsSimulating(true)
    const sel = records.find((r) => r.id === compId)
    const p = sel ? sel.presentCount : totalPresent
    const t = sel ? sel.totalCount : totalClasses

    try {
      const res = await api.calculateRecovery({
        student_id: studentId,
        target_pct: tPct,
        remaining_classes: rem,
        present: p,
        total: t,
      })
      setRecoveryResult(res)
    } catch (err) {
      console.error('Failed to calculate attendance recovery:', err)
    } finally {
      setIsSimulating(false)
    }
  }

  // Trigger initial simulation once
  React.useEffect(() => {
    handleSimulate(targetSlider, futureClasses, selectedComponentId)
  }, [selectedComponentId])

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header & Overall Overview Card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <CalendarCheck2 className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Attendance Intelligence
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Component-level tracking, threshold monitoring, and dynamic recovery simulations.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
          <span className="px-3 py-1 rounded-full bg-slate-100 border border-slate-200">
            Policy Benchmark: <strong>{targetPct}% Overall</strong> / <strong>{courseTargetPct}% Course</strong>
          </span>
        </div>
      </div>

      {/* 2. Top Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Overall Attendance
            </span>
            <div className="text-3xl font-extrabold text-slate-900">
              {computedOverall !== null ? `${computedOverall.toFixed(1)}%` : 'N/A'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {totalPresent} of {totalClasses} classes attended
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Standing Status
            </span>
            <div className="text-xl font-extrabold text-slate-900 mt-1">
              {computedOverall && computedOverall >= targetPct ? (
                <span className="text-emerald-600 flex items-center gap-1.5">
                  <CheckCircle2 className="w-5 h-5" /> Compliant
                </span>
              ) : (
                <span className="text-rose-600 flex items-center gap-1.5">
                  <AlertTriangle className="w-5 h-5" /> Below Target
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Target threshold is {targetPct}%
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Evaluated Components
            </span>
            <div className="text-3xl font-extrabold text-slate-900">{records.length}</div>
            <p className="text-xs text-slate-500 mt-1">
              Lectures, Labs & Practicals
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Attention Count
            </span>
            <div className="text-3xl font-extrabold text-amber-600">
              {records.filter((r) => r.computedPercentage !== null && r.computedPercentage < courseTargetPct).length}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Components below {courseTargetPct}%
            </p>
          </CardContent>
        </Card>
      </div>

      {mismatchNote && (
        <div className="p-3.5 rounded-lg border border-amber-200 bg-amber-50 text-amber-900 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-600" />
          <span>{mismatchNote}</span>
        </div>
      )}

      {/* 3. Component Breakdown Table */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Course & Component Breakdown
            </CardTitle>
            <p className="text-xs text-slate-500 mt-0.5">
              Live attendance records broken down by lecture, laboratory, and tutorial sessions.
            </p>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-[10px] tracking-wider border-b border-slate-200">
                <tr>
                  <th className="p-4">Course</th>
                  <th className="p-4">Component</th>
                  <th className="p-4">Attended / Total</th>
                  <th className="p-4">Percentage</th>
                  <th className="p-4">Status</th>
                  <th className="p-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {records.map((rec) => {
                  const pct = rec.computedPercentage
                  const isBelow = pct !== null && pct < courseTargetPct
                  return (
                    <tr key={rec.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="p-4 font-semibold text-slate-900">
                        {rec.courseName}
                        <span className="block text-[11px] font-normal text-slate-400">{rec.courseId}</span>
                      </td>
                      <td className="p-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                          {rec.component}
                        </span>
                      </td>
                      <td className="p-4 font-medium">
                        {rec.presentCount} / {rec.totalCount}
                      </td>
                      <td className="p-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
                            <div
                              className={`h-full rounded-full ${
                                isBelow ? 'bg-rose-500' : pct && pct >= 85 ? 'bg-emerald-500' : 'bg-blue-600'
                              }`}
                              style={{ width: `${Math.min(100, Math.max(0, pct || 0))}%` }}
                            />
                          </div>
                          <span className={`font-bold ${isBelow ? 'text-rose-700' : 'text-slate-800'}`}>
                            {pct !== null ? `${pct.toFixed(1)}%` : 'N/A'}
                          </span>
                        </div>
                      </td>
                      <td className="p-4">
                        <Badge
                          variant={rec.status === 'critical' ? 'high' : rec.status === 'warning' ? 'moderate' : 'low'}
                          className="text-[10px] py-0.5 px-2"
                        >
                          {rec.status === 'critical'
                            ? 'Critical'
                            : rec.status === 'warning'
                            ? 'Attention'
                            : 'Healthy'}
                        </Badge>
                      </td>
                      <td className="p-4 text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedComponentId(rec.id)
                            handleSimulate(targetSlider, futureClasses, rec.id)
                          }}
                          className="text-xs text-blue-600 hover:text-blue-700 h-7 px-2"
                        >
                          Simulate
                        </Button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* 4. Interactive Recovery & Safe Buffer Calculator */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3 border-b border-slate-100">
          <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
            <Calculator className="w-4 h-4 text-blue-600" />
            Interactive Attendance Recovery Simulator
          </CardTitle>
          <p className="text-xs text-slate-500">
            Calculate exactly how many consecutive sessions you must attend to meet or retain your attendance threshold.
          </p>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6 space-y-4">
              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Simulation Target Component
                </label>
                <Select
                  value={selectedComponentId}
                  onChange={(e) => {
                    const id = e.target.value
                    setSelectedComponentId(id)
                    handleSimulate(targetSlider, futureClasses, id)
                  }}
                  className="h-9 text-xs"
                >
                  <option value="overall">All Classes Combined (Overall Cumulative)</option>
                  {records.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.courseName} ({r.component}) — {r.presentCount}/{r.totalCount} ({r.computedPercentage?.toFixed(1)}%)
                    </option>
                  ))}
                </Select>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span>Target Threshold Percentage</span>
                  <span className="text-blue-600 font-bold">{targetSlider}%</span>
                </div>
                <input
                  type="range"
                  min="60"
                  max="90"
                  step="1"
                  value={targetSlider}
                  onChange={(e) => {
                    const val = Number(e.target.value)
                    setTargetSlider(val)
                    handleSimulate(val, futureClasses, selectedComponentId)
                  }}
                  className="w-full accent-blue-600 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                  <span>60% (Minimum)</span>
                  <span>70% (Institutional Standard)</span>
                  <span>90% (Distinction)</span>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-700 block mb-1">
                  Estimated Remaining Classes in Semester
                </label>
                <Input
                  type="number"
                  min="1"
                  max="120"
                  value={futureClasses}
                  onChange={(e) => {
                    const val = Number(e.target.value)
                    setFutureClasses(val)
                    handleSimulate(targetSlider, val, selectedComponentId)
                  }}
                  className="h-9 text-xs"
                />
              </div>
            </div>

            {/* Simulation Results Display */}
            <div className="lg:col-span-6">
              <div
                className={`p-5 rounded-xl border h-full flex flex-col justify-between ${
                  recoveryResult?.status === 'achieved'
                    ? 'border-emerald-200 bg-emerald-50/70 text-emerald-950'
                    : recoveryResult?.status === 'recoverable'
                    ? 'border-amber-200 bg-amber-50/70 text-amber-950'
                    : 'border-rose-200 bg-rose-50/70 text-rose-950'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider">Simulation Output</span>
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                        recoveryResult?.status === 'achieved'
                          ? 'bg-emerald-200 text-emerald-800'
                          : recoveryResult?.status === 'recoverable'
                          ? 'bg-amber-200 text-amber-800'
                          : 'bg-rose-200 text-rose-800'
                      }`}
                    >
                      {recoveryResult?.status === 'achieved' ? 'Target Achieved' : 'Action Needed'}
                    </span>
                  </div>

                  <p className="text-sm font-bold leading-relaxed mb-3">
                    {recoveryResult?.message || 'Calculating simulation...'}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs border-t border-slate-200/60 pt-3 mt-4">
                  <div>
                    <span className="text-slate-500 block">Current Standing:</span>
                    <strong className="text-slate-800">
                      {recoveryResult?.currentPct?.toFixed(1)}% ({curP}/{curT})
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Classes Needed:</span>
                    <strong className="text-slate-800">
                      {recoveryResult?.neededConsecutive} consecutive session(s)
                    </strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
