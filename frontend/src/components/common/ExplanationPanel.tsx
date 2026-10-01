import React, { useState } from 'react'
import { Card, CardContent } from '../ui/Card'
import { ChevronDown, ChevronUp, ShieldCheck, HelpCircle } from 'lucide-react'

export interface ExplanationPanelProps {
  policyData?: {
    attendanceThresholdOverall?: number
    attendanceThresholdCourse?: number
    academicPassingBenchmark?: number
    smallSampleThreshold?: number
    governancePrinciple?: string
  }
}

export function ExplanationPanel({ policyData }: ExplanationPanelProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <Card className="border border-slate-200/90 bg-white overflow-hidden shadow-xs">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 sm:p-5 text-left bg-slate-50/50 hover:bg-slate-50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-100/80 flex items-center justify-center text-blue-700">
            <HelpCircle className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
              How is this calculated?
            </h4>
            <p className="text-xs text-slate-500">
              Transparent, evidence-based rules and non-punitive governance principles
            </p>
          </div>
        </div>
        <div className="text-slate-500">
          {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
        </div>
      </button>

      {expanded && (
        <CardContent className="p-5 border-t border-slate-200/80 bg-white space-y-4">
          <div className="rounded-lg bg-blue-50/70 border border-blue-200/60 p-3.5 text-xs text-blue-900 leading-relaxed flex items-start gap-2.5">
            <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-semibold">Core Governance Principle:</strong>{' '}
              {policyData?.governancePrinciple ||
                'Support signals exist to alert mentors and students to supportive opportunities early in the semester. They are non-punitive, evidence-based checkpoints and do not predict final course grades or exam outcomes.'}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-600">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <strong className="block font-semibold text-slate-800 mb-1">Attendance Pillar</strong>
              <p className="leading-relaxed">
                Evaluates overall attendance against the {policyData?.attendanceThresholdOverall || 70}% institutional benchmark and individual components against {policyData?.attendanceThresholdCourse || 70}%. Requires ≥ {policyData?.smallSampleThreshold || 5} sessions before triggering alerts.
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <strong className="block font-semibold text-slate-800 mb-1">Academic Pillar</strong>
              <p className="leading-relaxed">
                Screens midterm evaluations and assignments against a {policyData?.academicPassingBenchmark || 50}% benchmark. Highlights courses with declining velocity or low evaluation scores.
              </p>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
              <strong className="block font-semibold text-slate-800 mb-1">Engagement Independence</strong>
              <p className="leading-relaxed">
                Co-curricular activities are tracked independently for portfolio enrichment. Under academic fairness rules, event participation never masks low class attendance.
              </p>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  )
}
