import React, { useState } from 'react'
import { CourseItem, AssessmentItem, SemesterResultItem, api } from '../../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Input } from '../../ui/Input'
import { Select } from '../../ui/Select'
import { Badge } from '../../ui/Badge'
import {
  GraduationCap,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Calculator,
  PlusCircle,
  Trash2,
  Layers,
  ArrowRight,
} from 'lucide-react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

export interface AcademicsPageProps {
  studentId: string
  courses: CourseItem[]
  assessments: AssessmentItem[]
  results: SemesterResultItem[]
  cgpa: number | null
  onRefresh: () => void
  onNavigate?: (tab: any) => void
}

export function AcademicsPage({
  studentId,
  courses,
  assessments,
  results,
  cgpa,
  onRefresh,
  onNavigate,
}: AcademicsPageProps) {
  const [activeTab, setActiveTab] = useState<'assessments' | 'history' | 'cgpa'>('assessments')

  // Assessment Entry State
  const [selectedCourseId, setSelectedCourseId] = useState<string>(courses[0]?.id || '')
  const [assType, setAssType] = useState<string>('Midterm')
  const [obtainedMarks, setObtainedMarks] = useState<number>(15)
  const [totalMarks, setTotalMarks] = useState<number>(20)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [lastUpdatedSignals, setLastUpdatedSignals] = useState<any>(null)

  // CGPA Planner State
  const [targetCgpa, setTargetCgpa] = useState<number>(7.5)
  const [futureCredits, setFutureCredits] = useState<number>(24.0)
  const [cgpaPlanResult, setCgpaPlanResult] = useState<any>(null)
  const [isPlanning, setIsPlanning] = useState<boolean>(false)

  // Handle Assessment Save / Update
  const handleSaveAssessment = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (obtainedMarks > totalMarks) {
      alert(`Obtained marks (${obtainedMarks}) cannot exceed total marks (${totalMarks}).`)
      return
    }

    setIsSubmitting(true)
    setStatusMessage(null)

    try {
      const res = await api.saveAssessment({
        student_id: studentId,
        course_id: selectedCourseId,
        ass_type: assType,
        obtained_marks: obtainedMarks,
        total_marks: totalMarks,
        date: '2026-09-20',
        term: 'T1',
      })

      setLastUpdatedSignals(res.updatedSignals)
      setStatusMessage(
        `✓ Academic health recalculated! Standing: ${res.updatedSignals.academicSignal}, Overall Support: ${res.updatedSignals.overallSupportSignal}.`
      )
      onRefresh()
    } catch (err: any) {
      setStatusMessage(`Error updating assessment: ${err.message}`)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Handle Assessment Delete
  const handleDeleteAssessment = async (assId: string) => {
    try {
      const res = await api.deleteAssessment(assId, studentId)
      setLastUpdatedSignals(res.updatedSignals)
      setStatusMessage(`Assessment removed and academic signals refreshed.`)
      onRefresh()
    } catch (err: any) {
      alert(`Failed to delete assessment: ${err.message}`)
    }
  }

  // Handle CGPA Plan Calculation
  const handleCalculateCgpaPlan = async (tCgpa = targetCgpa, fCreds = futureCredits) => {
    setIsPlanning(true)
    try {
      const res = await api.calculateCgpaPlan({
        student_id: studentId,
        target_cgpa: tCgpa,
        future_credits: fCreds,
      })
      setCgpaPlanResult(res)
    } catch (err) {
      console.error('Failed to plan CGPA:', err)
    } finally {
      setIsPlanning(false)
    }
  }

  React.useEffect(() => {
    if (activeTab === 'cgpa' && !cgpaPlanResult) {
      handleCalculateCgpaPlan(targetCgpa, futureCredits)
    }
  }, [activeTab])

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <GraduationCap className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Academic Performance
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Evaluation analytics, runtime marks entry, and multi-semester SGPA progression.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="inline-flex rounded-lg bg-slate-100 p-1 border border-slate-200">
          <button
            onClick={() => setActiveTab('assessments')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'assessments' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Assessments & Entry
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'history' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Results & SGPA
          </button>
          <button
            onClick={() => setActiveTab('cgpa')}
            className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'cgpa' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            CGPA Planner
          </button>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* TAB 1: Current Assessments & Runtime Entry */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'assessments' && (
        <div className="space-y-6">
          {/* Signal Feedback Banner */}
          {statusMessage && (
            <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/80 text-blue-900 text-xs sm:text-sm flex items-start justify-between gap-3 shadow-2xs">
              <div className="flex items-start gap-2.5">
                <Sparkles className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold">{statusMessage}</div>
                  {lastUpdatedSignals && (
                    <div className="text-xs text-blue-800 mt-1">
                      {lastUpdatedSignals.whatDetected}
                    </div>
                  )}
                </div>
              </div>
              {onNavigate && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onNavigate('explorer')}
                  className="bg-white text-blue-700 border-blue-300 text-xs shrink-0"
                >
                  View in Explorer
                </Button>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: Interactive Runtime Marks Entry Form */}
            <div className="lg:col-span-5">
              <Card className="border-slate-200/90 bg-white shadow-xs">
                <CardHeader className="p-5 pb-3 border-b border-slate-100">
                  <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    Enter / Adjust Assessment Marks
                  </CardTitle>
                  <p className="text-xs text-slate-500">
                    Test how changing scores (e.g. 9/20 vs 18/20) recalculates academic support signals in real-time.
                  </p>
                </CardHeader>
                <CardContent className="p-5">
                  <form onSubmit={handleSaveAssessment} className="space-y-4">
                    <div>
                      <label className="text-xs font-semibold text-slate-700 block mb-1">
                        Select Enrolled Subject
                      </label>
                      <Select
                        value={selectedCourseId}
                        onChange={(e) => setSelectedCourseId(e.target.value)}
                        className="text-xs"
                      >
                        {courses.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.shortName} ({c.code})
                          </option>
                        ))}
                      </Select>
                    </div>

                    <div>
                      <label className="text-xs font-semibold text-slate-700 block mb-1">
                        Assessment Type
                      </label>
                      <Select
                        value={assType}
                        onChange={(e) => setAssType(e.target.value)}
                        className="text-xs"
                      >
                        <option value="Midterm">Midterm Examination</option>
                        <option value="Assignment">Continuous Assignment</option>
                        <option value="Quiz">Class Quiz</option>
                      </Select>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-semibold text-slate-700 block mb-1">
                          Obtained Marks
                        </label>
                        <Input
                          type="number"
                          step="0.5"
                          min="0"
                          max={totalMarks}
                          value={obtainedMarks}
                          onChange={(e) => setObtainedMarks(Number(e.target.value))}
                          className="text-xs"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-semibold text-slate-700 block mb-1">
                          Maximum Marks
                        </label>
                        <Input
                          type="number"
                          step="1"
                          min="1"
                          max="100"
                          value={totalMarks}
                          onChange={(e) => setTotalMarks(Number(e.target.value))}
                          className="text-xs"
                        />
                      </div>
                    </div>

                    {/* Quick Scenario Buttons */}
                    <div className="pt-2">
                      <span className="text-[11px] font-semibold text-slate-500 block mb-1.5">
                        Quick Scenarios:
                      </span>
                      <div className="flex gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setObtainedMarks(9)
                            setTotalMarks(20)
                          }}
                          className="text-xs py-1 h-7 border-rose-200 text-rose-700 bg-rose-50/50 hover:bg-rose-100"
                        >
                          9 / 20 (Below 50%)
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setObtainedMarks(18)
                            setTotalMarks(20)
                          }}
                          className="text-xs py-1 h-7 border-emerald-200 text-emerald-700 bg-emerald-50/50 hover:bg-emerald-100"
                        >
                          18 / 20 (Strong 90%)
                        </Button>
                      </div>
                    </div>

                    <Button
                      type="submit"
                      variant="primary"
                      isLoading={isSubmitting}
                      className="w-full text-xs font-semibold mt-4 h-9 gap-2"
                    >
                      <Sparkles className="w-4 h-4" />
                      <span>Analyze Academic Health</span>
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Right: Active Assessment Evaluation Matrix */}
            <div className="lg:col-span-7">
              <Card className="border-slate-200/90 bg-white shadow-xs">
                <CardHeader className="p-5 pb-3 border-b border-slate-100">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900">
                        Current Semester Assessments
                      </CardTitle>
                      <p className="text-xs text-slate-500">
                        Evaluated courses and recorded scores contributing to diagnostic signals.
                      </p>
                    </div>
                    <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                      {assessments.length} Record{assessments.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  {assessments.length === 0 ? (
                    <div className="text-center py-12 text-slate-400 text-xs">
                      No evaluations recorded yet for this semester. Enter marks using the form on the left.
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs text-slate-700">
                        <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-[10px] tracking-wider border-b border-slate-200">
                          <tr>
                            <th className="p-3.5">Course</th>
                            <th className="p-3.5">Evaluation</th>
                            <th className="p-3.5">Score</th>
                            <th className="p-3.5">Percentage</th>
                            <th className="p-3.5">Status</th>
                            <th className="p-3.5 text-right">Delete</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {assessments.map((ass) => {
                            const rawPct = typeof ass.percentage === 'number' ? ass.percentage : (ass.totalMarks > 0 ? (ass.obtainedMarks / ass.totalMarks * 100) : null)
                            const pct = rawPct !== null && !isNaN(rawPct) ? rawPct : null
                            const isBelow = pct !== null && pct < 50.0
                            return (
                              <tr key={ass.id} className="hover:bg-slate-50/70 transition-colors">
                                <td className="p-3.5 font-semibold text-slate-900">
                                  {ass.courseName || ass.courseId}
                                  <span className="block text-[10px] font-normal text-slate-400">
                                    {ass.courseId}
                                  </span>
                                </td>
                                <td className="p-3.5 font-medium">{ass.assessmentType || (ass as any).type || 'Evaluation'}</td>
                                <td className="p-3.5 font-bold text-slate-800">
                                  {ass.obtainedMarks} / {ass.totalMarks}
                                </td>
                                <td className="p-3.5">
                                  <span className={`font-bold ${isBelow ? 'text-rose-600' : 'text-slate-800'}`}>
                                    {pct !== null ? `${pct.toFixed(1)}%` : 'N/A'}
                                  </span>
                                </td>
                                <td className="p-3.5">
                                  <Badge variant={isBelow ? 'high' : 'low'} className="text-[10px] py-0 px-2">
                                    {isBelow ? 'Below 50%' : 'Compliant'}
                                  </Badge>
                                </td>
                                <td className="p-3.5 text-right">
                                  <button
                                    onClick={() => handleDeleteAssessment(ass.id)}
                                    className="p-1 text-slate-400 hover:text-rose-600 rounded transition-colors cursor-pointer"
                                    title="Delete assessment"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" />
                                  </button>
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 2: Historical SGPA Progression */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="border-slate-200/90 bg-white shadow-xs">
              <CardContent className="p-5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Cumulative CGPA
                </span>
                <div className="text-3xl font-extrabold text-blue-600">
                  {cgpa !== null ? cgpa.toFixed(2) : 'N/A'}
                </div>
                <p className="text-xs text-slate-500 mt-1">Weighted across all completed credits</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200/90 bg-white shadow-xs">
              <CardContent className="p-5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Completed Terms
                </span>
                <div className="text-3xl font-extrabold text-slate-900">{results.length} Semesters</div>
                <p className="text-xs text-slate-500 mt-1">Officially declared marksheets</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200/90 bg-white shadow-xs">
              <CardContent className="p-5">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Total Earned Credits
                </span>
                <div className="text-3xl font-extrabold text-slate-900">
                  {results.reduce((acc, r) => acc + (r.creditsComplete || 0), 0)}
                </div>
                <p className="text-xs text-slate-500 mt-1">University credit requirements</p>
              </CardContent>
            </Card>
          </div>

          <Card className="border-slate-200/90 bg-white shadow-xs">
            <CardHeader className="p-5 pb-2">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900">
                Multi-Semester Performance History
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5">
              {results.length > 0 ? (
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={results} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="semester" tickFormatter={(v) => `Sem ${v}`} stroke="#94a3b8" fontSize={11} />
                      <YAxis domain={[5.0, 10.0]} stroke="#94a3b8" fontSize={11} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0f172a',
                          borderRadius: '8px',
                          color: '#fff',
                          fontSize: '12px',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="sgpa"
                        name="SGPA"
                        stroke="#2563eb"
                        strokeWidth={3}
                        dot={{ r: 5, fill: '#2563eb' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400 text-xs">
                  No historical semester results available.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* TAB 3: CGPA What-If Planner */}
      {/* ------------------------------------------------------------- */}
      {activeTab === 'cgpa' && (
        <Card className="border-slate-200/90 bg-white shadow-xs">
          <CardHeader className="p-5 pb-3 border-b border-slate-100">
            <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
              <Calculator className="w-4 h-4 text-blue-600" />
              CGPA Target & What-If Planner
            </CardTitle>
            <p className="text-xs text-slate-500">
              Calculate the required future SGPA needed to graduate with or achieve your target cumulative CGPA.
            </p>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-6 space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                    <span>Target Cumulative CGPA</span>
                    <span className="text-blue-600 font-bold">{targetCgpa.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="6.0"
                    max="9.5"
                    step="0.05"
                    value={targetCgpa}
                    onChange={(e) => {
                      const val = Number(e.target.value)
                      setTargetCgpa(val)
                      handleCalculateCgpaPlan(val, futureCredits)
                    }}
                    className="w-full accent-blue-600 cursor-pointer"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-700 block mb-1">
                    Planned Future Semester Credits
                  </label>
                  <Input
                    type="number"
                    min="10"
                    max="60"
                    step="1"
                    value={futureCredits}
                    onChange={(e) => {
                      const val = Number(e.target.value)
                      setFutureCredits(val)
                      handleCalculateCgpaPlan(targetCgpa, val)
                    }}
                    className="text-xs"
                  />
                </div>
              </div>

              <div className="lg:col-span-6">
                <div className="p-5 rounded-xl border border-blue-200 bg-blue-50/70 text-blue-950 h-full flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-700 block mb-1">
                      Target Feasibility Analysis
                    </span>
                    <p className="text-sm font-bold leading-relaxed">
                      {cgpaPlanResult?.futurePlan?.message ||
                        cgpaPlanResult?.cgpaInfo?.message ||
                        'Calculating required performance...'}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs border-t border-blue-200 pt-3 mt-4">
                    <div>
                      <span className="text-blue-600 block">Current CGPA:</span>
                      <strong className="text-blue-900">{cgpa !== null ? cgpa.toFixed(2) : 'N/A'}</strong>
                    </div>
                    <div>
                      <span className="text-blue-600 block">Target CGPA:</span>
                      <strong className="text-blue-900">{targetCgpa.toFixed(2)}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
