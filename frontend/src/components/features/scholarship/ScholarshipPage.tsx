import React, { useState } from 'react'
import { ScholarshipSchemeItem, ScholarshipEvaluationData, api } from '../../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Input } from '../../ui/Input'
import { Select } from '../../ui/Select'
import { Badge } from '../../ui/Badge'
import {
  Award,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  HelpCircle,
  FileText,
  Sliders,
  ExternalLink,
} from 'lucide-react'

export interface ScholarshipPageProps {
  studentId: string
  schemes: ScholarshipSchemeItem[]
  attestedFacts: Record<string, any>
  onRefresh: () => void
}

export function ScholarshipPage({ studentId, schemes, attestedFacts, onRefresh }: ScholarshipPageProps) {
  const [selectedSchemeId, setSelectedSchemeId] = useState<string>(schemes[0]?.schemeId || '')
  const [track, setTrack] = useState<'renewal' | 'fresh'>('renewal')
  const [remClasses, setRemClasses] = useState<number>(35)
  const [evaluation, setEvaluation] = useState<ScholarshipEvaluationData | null>(null)
  const [isLoadingEval, setIsLoadingEval] = useState<boolean>(false)

  // Attested Facts Form State
  const [income, setIncome] = useState<number>(attestedFacts?.annualFamilyIncome || 450000)
  const [domicile, setDomicile] = useState<boolean>(
    attestedFacts?.domicileGujarat !== undefined ? attestedFacts.domicileGujarat : true
  )
  const [marksPct, setMarksPct] = useState<number>(attestedFacts?.previousYearMarksPercent || 68.5)
  const [currentlyReceiving, setCurrentlyReceiving] = useState<boolean>(
    attestedFacts?.currentlyReceivingScheme !== undefined ? attestedFacts.currentlyReceivingScheme : true
  )
  const [isSavingFacts, setIsSavingFacts] = useState<boolean>(false)
  const [factSavedMsg, setFactSavedMsg] = useState<string | null>(null)

  // Active Scheme definition
  const activeScheme = schemes.find((s) => s.schemeId === selectedSchemeId) || schemes[0]

  // Evaluate Scholarship
  const handleEvaluate = async (sid = selectedSchemeId, trk = track, rem = remClasses) => {
    if (!sid) return
    setIsLoadingEval(true)
    try {
      const res = await api.evaluateScholarship(sid, studentId, trk, rem)
      setEvaluation(res)
    } catch (err) {
      console.error('Failed to evaluate scholarship:', err)
    } finally {
      setIsLoadingEval(false)
    }
  }

  // Initial load
  React.useEffect(() => {
    if (selectedSchemeId) {
      handleEvaluate(selectedSchemeId, track, remClasses)
    }
  }, [selectedSchemeId, track])

  // Save Facts
  const handleSaveFacts = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSavingFacts(true)
    setFactSavedMsg(null)
    try {
      await api.saveAttestedFacts({
        student_id: studentId,
        annualFamilyIncome: income,
        domicileGujarat: domicile,
        previousYearMarksPercent: marksPct,
        currentlyReceivingScheme: currentlyReceiving,
      })
      setFactSavedMsg('Self-attested criteria updated successfully.')
      handleEvaluate(selectedSchemeId, track, remClasses)
      onRefresh()
    } catch (err: any) {
      alert(`Failed to save facts: ${err.message}`)
    } finally {
      setIsSavingFacts(false)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Award className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Scholarship Readiness Planner
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Eligibility audit checklists, criteria verification, and future target planning.
          </p>
        </div>
      </div>

      {/* 2. Scheme Selector & Track Bar */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardContent className="p-5">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            <div className="md:col-span-6">
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Select Scholarship Scheme
              </label>
              <Select
                value={selectedSchemeId}
                onChange={(e) => setSelectedSchemeId(e.target.value)}
                className="text-xs"
              >
                {schemes.map((s) => (
                  <option key={s.schemeId} value={s.schemeId}>
                    {s.name} ({s.academicYear})
                  </option>
                ))}
              </Select>
            </div>

            <div className="md:col-span-3">
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Application Track
              </label>
              <div className="flex rounded-md bg-slate-100 p-1 border border-slate-200">
                <button
                  type="button"
                  onClick={() => setTrack('renewal')}
                  className={`flex-1 py-1 text-xs font-semibold rounded transition-all cursor-pointer ${
                    track === 'renewal' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
                  }`}
                >
                  Renewal Track
                </button>
                <button
                  type="button"
                  onClick={() => setTrack('fresh')}
                  className={`flex-1 py-1 text-xs font-semibold rounded transition-all cursor-pointer ${
                    track === 'fresh' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
                  }`}
                >
                  Fresh Track
                </button>
              </div>
            </div>

            <div className="md:col-span-3">
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Verification State
              </label>
              <div className="flex items-center gap-1.5 pt-1">
                <Badge
                  variant={
                    activeScheme?.verificationLevel === 'OFFICIAL_VERIFIED'
                      ? 'low'
                      : activeScheme?.verificationLevel === 'SECONDARY_ONLY'
                      ? 'moderate'
                      : 'neutral'
                  }
                  className="text-xs py-1"
                >
                  {activeScheme?.verificationLevel?.replace('_', ' ') || 'Unverified'}
                </Badge>
                {activeScheme?.officialSourceUrl && (
                  <a
                    href={activeScheme.officialSourceUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1 text-slate-400 hover:text-blue-600 rounded"
                    title="Official Portal Guidelines"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scheme Disclaimer Banner */}
      <div className="p-3.5 rounded-xl border border-amber-200 bg-amber-50/70 text-amber-900 text-xs flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong>Scheme Verification Notice:</strong> Criteria synthesized from official state and institutional guidelines. Official verification is required by university administration prior to final submission. EduPulse provides audit planning, not official legal approval.
        </div>
      </div>

      {/* 3. Self-Attested Facts Form */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900">
              Self-Attested Criteria Inputs
            </CardTitle>
            <p className="text-xs text-slate-500">
              Provide necessary family income and marksheet facts for scheme eligibility auditing. Stored locally.
            </p>
          </div>
          {factSavedMsg && <span className="text-xs text-emerald-600 font-semibold">{factSavedMsg}</span>}
        </CardHeader>
        <CardContent className="p-5">
          <form onSubmit={handleSaveFacts} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Annual Family Income (INR)
              </label>
              <Input
                type="number"
                step="25000"
                min="0"
                max="5000000"
                value={income}
                onChange={(e) => setIncome(Number(e.target.value))}
                className="text-xs"
              />
              <span className="text-[10px] text-slate-400">e.g. MYSY limit: ≤ ₹6,00,000</span>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Previous Marksheet Percentage (%)
              </label>
              <Input
                type="number"
                step="0.5"
                min="0"
                max="100"
                value={marksPct}
                onChange={(e) => setMarksPct(Number(e.target.value))}
                className="text-xs"
              />
              <span className="text-[10px] text-slate-400">From official qualifying marksheet</span>
            </div>

            <div className="space-y-2 pt-2">
              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={domicile}
                  onChange={(e) => setDomicile(e.target.checked)}
                  className="rounded text-blue-600 accent-blue-600"
                />
                <span>State Domicile Confirmed</span>
              </label>

              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={currentlyReceiving}
                  onChange={(e) => setCurrentlyReceiving(e.target.checked)}
                  className="rounded text-blue-600 accent-blue-600"
                />
                <span>Currently an Approved Beneficiary</span>
              </label>
            </div>

            <div className="flex items-end">
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={isSavingFacts}
                className="w-full text-xs font-semibold h-9"
              >
                Update Attested Facts
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* 4. Readiness Audit Results */}
      <Card className="border-slate-200/90 bg-white shadow-xs">
        <CardHeader className="p-5 pb-3 border-b border-slate-100 flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900">
              Readiness Audit: {evaluation?.schemeName || activeScheme?.name}
            </CardTitle>
            <p className="text-xs text-slate-500 mt-0.5">
              Readiness Summary: <strong>{evaluation?.summaryCountsText || 'Auditing local evidence...'}</strong>
            </p>
          </div>
        </CardHeader>
        <CardContent className="p-5 space-y-3">
          {evaluation?.criteria.map((crit, idx) => {
            const isMet = crit.status === 'MET'
            const isNotMet = crit.status === 'NOT_MET'

            const borderCol = isMet
              ? 'border-l-4 border-l-emerald-500'
              : isNotMet
              ? 'border-l-4 border-l-rose-500'
              : 'border-l-4 border-l-amber-500'

            return (
              <div
                key={idx}
                className={`p-4 rounded-xl border border-slate-200/90 bg-white shadow-2xs space-y-1.5 ${borderCol}`}
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-slate-900">{crit.label}</h4>
                  <Badge variant={isMet ? 'low' : isNotMet ? 'high' : 'moderate'} className="text-[10px]">
                    {crit.status}
                  </Badge>
                </div>
                <p className="text-xs text-slate-700 leading-relaxed">{crit.details}</p>
                <div className="text-[11px] text-slate-400 pt-1 flex flex-wrap gap-3">
                  <span>Basis: <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-600">{crit.basis}</code></span>
                  <span>Verification: {crit.verification}</span>
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>

      {/* 5. Required Verifiable Documents Checklist */}
      {evaluation?.missingDocuments && evaluation.missingDocuments.length > 0 && (
        <Card className="border-slate-200/90 bg-white shadow-xs">
          <CardHeader className="p-5 pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-600" />
              Verifiable Documents Checklist
            </CardTitle>
          </CardHeader>
          <CardContent className="p-5 space-y-2">
            {evaluation.missingDocuments.map((doc, idx) => (
              <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-700">
                <span className="w-4 h-4 rounded text-blue-600 mt-0.5 shrink-0">📄</span>
                <div>
                  <strong className="text-slate-800">{doc.name}</strong>: <em>{doc.note}</em>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
