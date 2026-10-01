import React, { useState } from 'react'
import { ExplorerData, api, RecoveryResult } from '../../../api/client'
import { StatusBadge } from '../../common/StatusBadge'
import { EvidenceCard } from '../../common/EvidenceCard'
import { ActionCard } from '../../common/ActionCard'
import { ExplanationPanel } from '../../common/ExplanationPanel'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Input } from '../../ui/Input'
import {
  Compass,
  CalendarCheck,
  GraduationCap,
  Sparkles,
  Calculator,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ArrowRight,
  TrendingUp,
} from 'lucide-react'

export interface ExplorerPageProps {
  data: ExplorerData
  onRefresh?: () => void
  onNavigate?: (tab: any) => void
}

export function ExplorerPage({ data, onRefresh, onNavigate }: ExplorerPageProps) {
  const { overallSupportSignal, overallDisplayText, narrative, pillars, evidence, recommendations, howCalculated } =
    data

  // Interactive Recovery Simulator State
  const [targetPct, setTargetPct] = useState<number>(data.recoverySimulation?.defaultTargetPct || 70)
  const [remainingClasses, setRemainingClasses] = useState<number>(data.recoverySimulation?.defaultRemainingClasses || 35)
  const [recoveryResult, setRecoveryResult] = useState<RecoveryResult>(data.recoverySimulation?.result)
  const [isCalculating, setIsCalculating] = useState<boolean>(false)

  const handleRecalculateRecovery = async (newTarget = targetPct, newRemaining = remainingClasses) => {
    setIsCalculating(true)
    try {
      const res = await api.calculateRecovery({
        student_id: data.student.id,
        target_pct: newTarget,
        remaining_classes: newRemaining,
        present: pillars.attendance.present,
        total: pillars.attendance.total,
      })
      setRecoveryResult(res)
    } catch (err) {
      console.error('Error calculating recovery:', err)
    } finally {
      setIsCalculating(false)
    }
  }

  // Accent Colors based on overall support signal
  const isLow = overallSupportSignal === 'Low'
  const isHigh = overallSupportSignal === 'High'
  const isModerate = overallSupportSignal === 'Moderate'

  const borderAccent = isLow ? 'border-l-6 border-l-emerald-500' : isHigh ? 'border-l-6 border-l-rose-500' : 'border-l-6 border-l-amber-500'

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Compass className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Student Success Explorer
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Evidence-based view of where you may benefit from additional academic support.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <StatusBadge level={overallSupportSignal} className="text-sm py-1.5 px-4" />
        </div>
      </div>

      {/* 2. Executive Diagnostic Centerpiece Card */}
      <Card className={`border border-slate-200/90 bg-white shadow-sm ${borderAccent} p-0 overflow-hidden`}>
        <CardContent className="p-6 sm:p-8 space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span className="text-xs font-extrabold uppercase tracking-wider text-slate-500">
                Overall Support Signal
              </span>
              <StatusBadge level={overallSupportSignal} className="text-xs sm:text-sm font-bold" />
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
              <span className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200">
                Confidence: <strong className="text-slate-800">{data.coverage}</strong>
              </span>
              <span className="px-2.5 py-1 rounded bg-slate-100 border border-slate-200">
                As of {data.asOfDate}
              </span>
            </div>
          </div>

          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600 block mb-1">
              What was detected?
            </span>
            <p className="text-lg sm:text-xl font-bold text-slate-900 leading-snug">
              {narrative.whatDetected}
            </p>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              {narrative.whyDetected}
            </p>
          </div>

          <div className="rounded-lg bg-slate-50 border border-slate-200 p-3.5 text-xs text-slate-600 flex items-start gap-2.5">
            <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <span>
              <strong>Governance Principle:</strong> Support signals exist to alert mentors and students to supportive opportunities early in the semester. They are non-punitive, evidence-based checkpoints and do not predict final course grades or exam outcomes.
            </span>
          </div>
        </CardContent>
      </Card>

      {/* 3. Three Pillars (Attendance, Academic, Engagement) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Attendance Pillar */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Attendance Pillar</span>
              <StatusBadge level={pillars.attendance.signal} showIcon={false} className="text-[10px] py-0 px-2" />
            </div>
            <div className="text-2xl font-extrabold text-slate-900">
              {pillars.attendance.percentage !== null ? `${pillars.attendance.percentage.toFixed(1)}%` : 'N/A'}
            </div>
            <p className="text-xs text-slate-500">
              {pillars.attendance.present}/{pillars.attendance.total} sessions recorded • {pillars.attendance.belowThresholdCount} component(s) &lt; {pillars.attendance.threshold}%
            </p>
          </CardContent>
        </Card>

        {/* Academic Pillar */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Academic Pillar</span>
              <StatusBadge level={pillars.academic.signal} showIcon={false} className="text-[10px] py-0 px-2" />
            </div>
            <div className="text-2xl font-extrabold text-slate-900">
              {pillars.academic.evaluatedCount} Evaluated
            </div>
            <p className="text-xs text-slate-500">
              Coverage: <strong>{pillars.academic.coverage}</strong> • {pillars.academic.belowBenchmarkCount} subject(s) &lt; {pillars.academic.benchmark}% benchmark
            </p>
          </CardContent>
        </Card>

        {/* Engagement Portfolio */}
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Engagement Portfolio</span>
              <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {pillars.engagement.level}
              </span>
            </div>
            <div className="text-2xl font-extrabold text-slate-900">
              {pillars.engagement.points.toFixed(1)} pts
            </div>
            <p className="text-xs text-slate-500">
              {pillars.engagement.eventCount} confirmed events ({pillars.engagement.diversityCount} categories) • <em>Independent Indicator</em>
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 4. "WHY WAS THIS DETECTED?" - Scannable Evidence Cards */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
            <span>Why was this detected?</span>
            <span className="text-xs font-medium text-slate-500">(Signal Evidence & Traceability)</span>
          </h3>
          <p className="text-xs text-slate-500">
            Audit trail of contributing indicators with active thresholds, observed values, and provenance.
          </p>
        </div>

        {evidence.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {evidence.map((ev, idx) => (
              <EvidenceCard
                key={idx}
                indicator={ev.indicator}
                value={ev.value}
                direction={ev.direction}
                category={ev.category}
                threshold={ev.threshold}
                source={ev.source}
              />
            ))}
          </div>
        ) : (
          <div className="p-6 rounded-xl border border-emerald-200 bg-emerald-50/50 text-emerald-800 text-sm">
            ✓ All active indicators meet or exceed baseline expectations. No alerts triggered.
          </div>
        )}
      </div>

      {/* 5. "WHAT SHOULD I DO NEXT?" - Action Recommendations */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
            <span>What should I do next?</span>
            <span className="text-xs font-medium text-slate-500">(Action Recommendations)</span>
          </h3>
          <p className="text-xs text-slate-500">
            Actionable next steps prioritized for immediate academic momentum and supportive campus resources.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <ActionCard
            title="Prioritized Focus Areas"
            items={narrative.whatToDoNext}
            icon={<ArrowRight className="w-4 h-4 text-blue-600" />}
            variant="primary"
          />
          <ActionCard
            title="Campus Support & Mentorship Resources"
            items={[
              'Faculty Consultation: Visit subject professors during designated office hours to review difficult exam questions.',
              'Peer Tutoring Circles: Join department study circles in the central library to reinforce core problem-solving competencies.',
              'Skills Acceleration: Explore technical hackathons and practical workshops in the Engagement Catalogue.',
              'Scholarship Safeguards: Check the Scholarship Readiness Planner to maintain your academic renewal buffer.',
            ]}
            icon={<HelpCircle className="w-4 h-4 text-teal-600" />}
            variant="teal"
          />
        </div>
      </div>

      {/* 6. Interactive Attendance Recovery & Buffer Simulator */}
      <div className="space-y-3">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 flex items-center gap-2">
            <Calculator className="w-5 h-5 text-blue-600" />
            <span>Attendance Recovery & Buffer Calculator</span>
          </h3>
          <p className="text-xs text-slate-500">
            Interactive recovery simulator to calculate exact class attendance needed to reach or maintain institutional thresholds.
          </p>
        </div>

        <Card className="border-slate-200/90 bg-white shadow-xs">
          <CardContent className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
              {/* Controls */}
              <div className="lg:col-span-6 space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
                    <span>Target Attendance Threshold</span>
                    <span className="text-blue-600 font-bold">{targetPct}%</span>
                  </div>
                  <input
                    type="range"
                    min="60"
                    max="90"
                    step="1"
                    value={targetPct}
                    onChange={(e) => {
                      const val = Number(e.target.value)
                      setTargetPct(val)
                      handleRecalculateRecovery(val, remainingClasses)
                    }}
                    className="w-full accent-blue-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                    <span>60% (Minimum)</span>
                    <span>70% (Institutional Target)</span>
                    <span>90% (Distinction)</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1.5">
                    <span>Estimated Remaining Classes in Semester</span>
                    <span className="text-slate-900 font-bold">{remainingClasses} classes</span>
                  </div>
                  <Input
                    type="number"
                    min="1"
                    max="150"
                    value={remainingClasses}
                    onChange={(e) => {
                      const val = Number(e.target.value)
                      setRemainingClasses(val)
                      handleRecalculateRecovery(targetPct, val)
                    }}
                    className="h-9 text-xs"
                  />
                </div>
              </div>

              {/* Simulation Result */}
              <div className="lg:col-span-6">
                <div
                  className={`p-5 rounded-xl border ${
                    recoveryResult?.status === 'achieved'
                      ? 'border-emerald-200 bg-emerald-50/70 text-emerald-950'
                      : recoveryResult?.status === 'recoverable'
                      ? 'border-amber-200 bg-amber-50/70 text-amber-950'
                      : 'border-rose-200 bg-rose-50/70 text-rose-950'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider">Recovery Simulation Result</span>
                    <span
                      className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                        recoveryResult?.status === 'achieved'
                          ? 'bg-emerald-200 text-emerald-800'
                          : recoveryResult?.status === 'recoverable'
                          ? 'bg-amber-200 text-amber-800'
                          : 'bg-rose-200 text-rose-800'
                      }`}
                    >
                      {recoveryResult?.status === 'achieved' ? 'Target Satisfied' : 'Action Required'}
                    </span>
                  </div>

                  <p className="text-sm sm:text-base font-bold leading-snug mb-3">
                    {recoveryResult?.message}
                  </p>

                  <div className="grid grid-cols-2 gap-3 text-xs border-t border-slate-200/60 pt-3">
                    <div>
                      <span className="text-slate-500 block">Current Standing:</span>
                      <strong className="text-slate-800">
                        {recoveryResult?.currentPct?.toFixed(1)}% ({pillars.attendance.present}/{pillars.attendance.total})
                      </strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Classes Needed:</span>
                      <strong className="text-slate-800">
                        {recoveryResult?.neededConsecutive} consecutive session(s)
                      </strong>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-500 mt-2 italic">
                    Note: Any future absence changes this calculation.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 7. "HOW IS THIS CALCULATED?" - Expandable Transparent Explanation */}
      <ExplanationPanel policyData={howCalculated} />
    </div>
  )
}
