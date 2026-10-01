/**
 * EduPulse API Client
 * Typed fetch client connecting the React UI to the FastAPI Python intelligence backend.
 */

/**
 * Resolves the API base URL dynamically based on environment configuration.
 * - In development (Vite local proxy): defaults to '/api'.
 * - In production (e.g. on Vercel): reads VITE_API_BASE_URL (e.g. 'https://api.edupulse.example.com').
 * Gracefully handles trailing slashes and ensures the standard /api prefix is retained.
 */
export function resolveApiBase(): string {
  const envUrl = (import.meta.env.VITE_API_BASE_URL || '').trim()
  if (!envUrl) {
    return '/api'
  }
  const clean = envUrl.replace(/\/+$/, '')
  return clean.endsWith('/api') ? clean : `${clean}/api`
}

export const API_BASE = resolveApiBase()

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  const url = `${API_BASE}${cleanEndpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }

  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    let errMsg = `Request failed: ${res.status} ${res.statusText}`
    try {
      const errJson = await res.json()
      if (errJson.detail) errMsg = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail)
    } catch {
      // ignore
    }
    throw new Error(errMsg)
  }
  return res.json()
}

// -------------------------------------------------------------
// Type Definitions
// -------------------------------------------------------------
export interface Persona {
  id: string
  name: string
  external_id: string
  archetype: string
  semester: number
  program: string
  provenance: string
  academic_status: string
  description: string
  badge_class?: string
  is_active?: boolean
}

export interface StudentProfile {
  id: string
  externalStudentId: string
  name: string
  program: string
  semester: number
  academicYear: string
}

export interface OverviewMetrics {
  attendance: {
    value: string
    present: number
    total: number
    status: string
    trend: string
  }
  academics: {
    value: string
    status: string
    coverage: string
    belowBenchmarkCount: number
  }
  engagement: {
    value: string
    level: string
    status: string
    eventCount: number
    diversityCount: number
  }
  supportSignal: {
    level: 'Low' | 'Moderate' | 'High' | 'Needs more data'
    badgeText: string
    description: string
  }
}

export interface AttentionAlert {
  type: 'attendance' | 'academic'
  courseId: string
  courseName: string
  component?: string
  assessmentType?: string
  percentage: number
  present?: number
  total?: number
  obtained?: number
  threshold: number
  severity: 'high' | 'moderate'
  message: string
}

export interface OverviewData {
  student: StudentProfile
  provenance: string
  asOfDate: string
  coverage: string
  supportStatus: 'Low' | 'Moderate' | 'High' | 'Needs more data'
  supportDisplayText: string
  snapshotNarrative: string
  metrics: OverviewMetrics
  attentionAreas: {
    attendanceAlerts: AttentionAlert[]
    academicAlerts: AttentionAlert[]
    totalAlerts: number
  }
  performanceTrend: {
    sgpaHistory: Array<{ semester: string; sgpa: number; credits: number; status: string }>
    enrolledCoursesCount: number
  }
  recommendedActions: string[]
  scholarshipReadiness: {
    schemeId: string
    schemeName: string
    summaryCounts: string
    verificationLevel: string
  } | null
}

export interface ExplorerData {
  student: StudentProfile
  provenance: string
  asOfDate: string
  coverage: string
  overallSupportSignal: 'Low' | 'Moderate' | 'High' | 'Needs more data'
  overallDisplayText: string
  narrative: {
    whatDetected: string
    whyDetected: string
    whatToDoNext: string[]
  }
  pillars: {
    attendance: {
      signal: string
      percentage: number | null
      present: number
      total: number
      belowThresholdCount: number
      threshold: number
    }
    academic: {
      signal: string
      evaluatedCount: number
      coverage: string
      belowBenchmarkCount: number
      benchmark: number
    }
    engagement: {
      level: string
      points: number
      eventCount: number
      diversityCount: number
    }
  }
  evidence: Array<{
    indicator: string
    value: string
    direction: 'concern' | 'positive' | 'neutral'
    category: string
    threshold: string
    source: string
  }>
  recommendations: string[]
  howCalculated: {
    attendanceThresholdOverall: number
    attendanceThresholdCourse: number
    academicPassingBenchmark: number
    smallSampleThreshold: number
    governancePrinciple: string
  }
  recoverySimulation: {
    currentPresent: number
    currentTotal: number
    defaultTargetPct: number
    defaultRemainingClasses: number
    result: RecoveryResult
  }
}

export interface AttendanceRecordItem {
  id: string
  courseId: string
  courseName: string
  component: string
  presentCount: number
  totalCount: number
  computedPercentage: number | null
  status: 'healthy' | 'critical' | 'warning' | 'excellent'
  asOfDate?: string
}

export interface AttendanceSummaryData {
  computedOverall: number | null
  portalOverall: number | null
  totalPresent: number
  totalClasses: number
  headline: string
  mismatchNote?: string
  asOfDate: string
  targetPct: number
  courseTargetPct: number
  records: AttendanceRecordItem[]
  dailyTimeline?: any[]
}

export interface RecoveryResult {
  classesNeeded: number
  neededConsecutive: number
  resultingPercentage: number
  isPossible: boolean
  bufferClasses: number
  isRecoverableWithinRemaining: boolean
  maxMissesWithinRemaining: number
  remainingMessage?: string | null
  notice: string
  currentPresent: number
  currentTotal: number
  currentPct: number
  targetPct: number
  remainingClasses: number
  message: string
  status: 'achieved' | 'recoverable' | 'impossible' | 'unrecoverable_in_term'
}

export interface CourseItem {
  id: string
  code: string
  shortName: string
  fullName: string
  semester: number
  credits: number
}

export interface AssessmentItem {
  id: string
  studentId: string
  courseId: string
  courseName?: string
  assessmentType: string
  obtainedMarks: number
  totalMarks: number
  percentage: number | null
  date: string
  term: string
}

export interface SemesterResultItem {
  semester: number
  sgpa: number
  creditsComplete: number
  totalCreditsDeclared: number
  monthYear: string
}

export interface EventItem {
  id: string
  name: string
  category: string
  date: string
  organizer: string
  durationHours: number
  weight: number
  participated: boolean
  confirmedAt?: string
  notes?: string
}

export interface EngagementSummaryData {
  level: string
  points: number
  description: string
  status: string
  eventCount: number
  diversityCount: number
  overlaps?: Array<{ name: string; date: string; note: string }>
}

export interface ScholarshipSchemeItem {
  schemeId: string
  name: string
  academicYear: string
  verificationLevel: string
  officialSourceUrl?: string
  notes?: string
}

export interface ScholarshipCriterion {
  label: string
  status: 'MET' | 'NOT_MET' | 'UNKNOWN'
  details: string
  basis: string
  verification: string
}

export interface ScholarshipEvaluationData {
  schemeId: string
  schemeName: string
  selectedTrack: string
  summaryCountsText: string
  criteria: ScholarshipCriterion[]
  missingDocuments: Array<{ name: string; note: string }>
}

export interface CohortAnalysisData {
  cohortSize: number
  bestK: number
  bestSilhouette: number
  anomalyCount: number
  privacyGuard: string
  clusters: Array<{
    clusterId: number
    size: number
    suppressed: boolean
    meanAttendance?: number
    meanMarks?: number
    meanEngagement?: number
    anomalyCount?: number
    label: string
  }>
  scatterPoints: Array<{
    student_id: string
    attendance_overall: number
    mean_marks: number
    cluster_id: number
    is_anomaly: boolean
    lowest_component_att: number
    engagement_points: number
    rule_based_signal: string
  }>
  methodologyNotice: string
}

// -------------------------------------------------------------
// API Methods
// -------------------------------------------------------------
export const api = {
  // System / Personas
  getHealth: () => request<{ status: string; service: string; active_student_id: string }>('/health'),
  getPersonas: () => request<Persona[]>('/personas'),
  getActiveStudent: () => request<{ student: StudentProfile; provenance: string; coverage: string; active_student_id: string }>('/students/active'),
  setActiveStudent: (studentId: string) => request<{ success: boolean; active_student_id: string; name: string }>('/students/active', {
    method: 'POST',
    body: JSON.stringify({ student_id: studentId }),
  }),

  // Overview
  getOverview: (studentId?: string) => {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : ''
    return request<OverviewData>(`/overview${q}`)
  },

  // Success Explorer
  getExplorer: (studentId?: string) => {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : ''
    return request<ExplorerData>(`/explorer${q}`)
  },

  // Attendance
  getAttendanceSummary: (studentId?: string, semester?: number) => {
    const params = new URLSearchParams()
    if (studentId) params.append('student_id', studentId)
    if (semester) params.append('semester', semester.toString())
    const q = params.toString() ? `?${params.toString()}` : ''
    return request<AttendanceSummaryData>(`/attendance/summary${q}`)
  },
  calculateRecovery: (payload: {
    student_id?: string
    course_id?: string
    target_pct: number
    remaining_classes: number
    present?: number
    total?: number
  }) => request<RecoveryResult>('/attendance/recovery', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // Academics
  getCourses: (studentId?: string, semester?: number) => {
    const params = new URLSearchParams()
    if (studentId) params.append('student_id', studentId)
    if (semester) params.append('semester', semester.toString())
    const q = params.toString() ? `?${params.toString()}` : ''
    return request<CourseItem[]>(`/academics/courses${q}`)
  },
  getAssessments: (studentId?: string, courseId?: string) => {
    const params = new URLSearchParams()
    if (studentId) params.append('student_id', studentId)
    if (courseId) params.append('course_id', courseId)
    const q = params.toString() ? `?${params.toString()}` : ''
    return request<AssessmentItem[]>(`/academics/assessments${q}`)
  },
  saveAssessment: (payload: {
    student_id?: string
    course_id: string
    ass_type?: string
    obtained_marks: number
    total_marks: number
    date?: string
    term?: string
  }) => request<{
    success: boolean
    assessment: AssessmentItem
    updatedSignals: {
      overallSupportSignal: string
      academicSignal: string
      overallDisplayText: string
      whatDetected: string
    }
  }>('/academics/assessments', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),
  deleteAssessment: (assessmentId: string, studentId?: string) => {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : ''
    return request<{
      success: boolean
      deletedId: string
      updatedSignals?: {
        overallSupportSignal: string
        academicSignal: string
        whatDetected: string
      }
    }>(`/academics/assessments/${encodeURIComponent(assessmentId)}${q}`, {
      method: 'DELETE',
    })
  },
  getSemesterResults: (studentId?: string) => {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : ''
    return request<{ results: SemesterResultItem[]; cgpa: number | null; totalCreditsEarned: number }>(`/academics/results${q}`)
  },
  calculateCgpaPlan: (payload: { student_id?: string; target_cgpa: number; future_credits: number }) =>
    request<any>('/academics/cgpa-plan', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Engagement
  getEngagementSummary: (studentId?: string, term = '2026-27-ODD') => {
    const q = `?term=${encodeURIComponent(term)}${studentId ? `&student_id=${encodeURIComponent(studentId)}` : ''}`
    return request<EngagementSummaryData>(`/engagement/summary${q}`)
  },
  getEvents: (studentId?: string) => {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : ''
    return request<EventItem[]>(`/engagement/events${q}`)
  },
  toggleParticipation: (payload: { student_id?: string; event_id: string; participated: boolean }) =>
    request<{ success: boolean; eventId: string; participated: boolean; updatedSummary: EngagementSummaryData }>('/engagement/toggle-participation', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  setDeclaration: (payload: { student_id?: string; term?: string; status: string }) =>
    request<any>('/engagement/declaration', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Scholarship
  getScholarships: () => request<ScholarshipSchemeItem[]>('/scholarship/schemes'),
  evaluateScholarship: (schemeId: string, studentId?: string, track = 'renewal', remainingClasses = 35) => {
    const params = new URLSearchParams({
      scheme_id: schemeId,
      track,
      remaining_classes: remainingClasses.toString(),
    })
    if (studentId) params.append('student_id', studentId)
    return request<ScholarshipEvaluationData>(`/scholarship/evaluate?${params.toString()}`)
  },
  getAttestedFacts: (studentId?: string) => {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : ''
    return request<Record<string, any>>(`/scholarship/attested-facts${q}`)
  },
  saveAttestedFacts: (payload: {
    student_id?: string
    annualFamilyIncome?: number
    domicileGujarat?: boolean
    previousYearMarksPercent?: number
    currentlyReceivingScheme?: boolean
  }) => request<any>('/scholarship/attested-facts', {
    method: 'POST',
    body: JSON.stringify(payload),
  }),

  // Mentor Explorer & Cohort ML
  getCohortAnalysis: (recompute = false) => request<CohortAnalysisData>(`/cohort/analysis${recompute ? '?recompute=true' : ''}`),

  // Data Workspace
  previewFile: (payload: { content: string; student_name?: string; program?: string; semester?: number; academic_year?: string }) =>
    request<any>('/data-workspace/preview-file', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  commitFile: (payload: { content: string; student_name: string; program: string; semester: number; academic_year: string }) =>
    request<any>('/data-workspace/commit-file', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  previewPaste: (payload: { text: string; student_id?: string }) =>
    request<any>('/data-workspace/preview-paste', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  commitPaste: (payload: { text: string; student_id?: string }) =>
    request<any>('/data-workspace/commit-paste', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  resetWorkspace: (scenario = 'student_synth_strong') =>
    request<any>('/data-workspace/reset', {
      method: 'POST',
      body: JSON.stringify(scenario),
    }),
  getTemplateUrl: (templateType: 'attendance' | 'marks' | 'daily') => `${API_BASE}/data-workspace/templates/${templateType}`,
  testAuthorizedConnector: () => request<{
    status: string
    error_type: string
    message: string
    explanation: string
  }>('/data-workspace/authorized-connector-stub', {
    method: 'POST',
  }),
}
