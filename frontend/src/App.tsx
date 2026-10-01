import React, { useState } from 'react'
import { QueryClient, QueryClientProvider, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './api/client'
import { AppShell } from './components/common/AppShell'
import { NavTab } from './components/common/Sidebar'
import { OverviewPage } from './components/features/overview/OverviewPage'
import { ExplorerPage } from './components/features/explorer/ExplorerPage'
import { AttendancePage } from './components/features/attendance/AttendancePage'
import { AcademicsPage } from './components/features/academics/AcademicsPage'
import { EngagementPage } from './components/features/engagement/EngagementPage'
import { ScholarshipPage } from './components/features/scholarship/ScholarshipPage'
import { MentorPage } from './components/features/mentor/MentorPage'
import { DataWorkspacePage } from './components/features/data/DataWorkspacePage'
import { SettingsPage } from './components/features/settings/SettingsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 1000 * 30, // 30 seconds
    },
  },
})

function MainDashboard() {
  const [currentTab, setCurrentTab] = useState<NavTab>('overview')
  const client = useQueryClient()

  // 1. Active Student & Personas
  const { data: activeStudentData, isLoading: isLoadingStudent } = useQuery({
    queryKey: ['activeStudent'],
    queryFn: api.getActiveStudent,
  })

  const { data: personas = [] } = useQuery({
    queryKey: ['personas'],
    queryFn: api.getPersonas,
  })

  const studentId = activeStudentData?.active_student_id || 'student_synth_strong'
  const student = activeStudentData?.student || null
  const provenance = activeStudentData?.provenance || 'Demo data'
  const coverage = activeStudentData?.coverage || 'Complete'

  // Handle switching personas
  const handleSelectPersona = async (pid: string) => {
    try {
      await api.setActiveStudent(pid)
      await client.invalidateQueries()
    } catch (err) {
      console.error('Error switching active student:', err)
    }
  }

  // 2. Data queries for current active student
  const { data: overviewData, isLoading: isLoadingOverview } = useQuery({
    queryKey: ['overview', studentId],
    queryFn: () => api.getOverview(studentId),
    enabled: !!studentId,
  })

  const { data: explorerData, isLoading: isLoadingExplorer } = useQuery({
    queryKey: ['explorer', studentId],
    queryFn: () => api.getExplorer(studentId),
    enabled: !!studentId,
  })

  const { data: attendanceData, isLoading: isLoadingAttendance } = useQuery({
    queryKey: ['attendance', studentId],
    queryFn: () => api.getAttendanceSummary(studentId),
    enabled: !!studentId,
  })

  const { data: courses = [], isLoading: isLoadingCourses } = useQuery({
    queryKey: ['courses', studentId],
    queryFn: () => api.getCourses(studentId),
    enabled: !!studentId,
  })

  const { data: assessments = [], isLoading: isLoadingAssessments } = useQuery({
    queryKey: ['assessments', studentId],
    queryFn: () => api.getAssessments(studentId),
    enabled: !!studentId,
  })

  const { data: resultsData, isLoading: isLoadingResults } = useQuery({
    queryKey: ['results', studentId],
    queryFn: () => api.getSemesterResults(studentId),
    enabled: !!studentId,
  })

  const { data: engagementSummary, isLoading: isLoadingEngagement } = useQuery({
    queryKey: ['engagement', studentId],
    queryFn: () => api.getEngagementSummary(studentId),
    enabled: !!studentId,
  })

  const { data: events = [], isLoading: isLoadingEvents } = useQuery({
    queryKey: ['events', studentId],
    queryFn: () => api.getEvents(studentId),
    enabled: !!studentId,
  })

  const { data: schemes = [], isLoading: isLoadingSchemes } = useQuery({
    queryKey: ['schemes'],
    queryFn: api.getScholarships,
  })

  const { data: attestedFacts = {}, isLoading: isLoadingFacts } = useQuery({
    queryKey: ['attestedFacts', studentId],
    queryFn: () => api.getAttestedFacts(studentId),
    enabled: !!studentId,
  })

  const { data: cohortData, isLoading: isLoadingCohort } = useQuery({
    queryKey: ['cohort'],
    queryFn: () => api.getCohortAnalysis(),
  })

  const refreshAll = () => {
    client.invalidateQueries()
  }

  // Loading spinner during initial boot
  if (isLoadingStudent) {
    return (
      <div className="h-screen w-screen flex flex-col items-center justify-center bg-slate-900 text-white space-y-4">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <div className="font-extrabold text-lg tracking-tight">Loading EduPulse...</div>
        <div className="text-xs text-slate-400">Connecting to Python Academic Intelligence Engine</div>
      </div>
    )
  }

  return (
    <AppShell
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      student={student}
      provenance={provenance}
      asOfDate={overviewData?.asOfDate || '2026-09-30'}
      coverage={coverage}
    >
      {/* 1. Overview */}
      {currentTab === 'overview' && (
        isLoadingOverview ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading academic snapshot...</div>
        ) : overviewData ? (
          <OverviewPage data={overviewData} onNavigate={setCurrentTab} />
        ) : (
          <div className="p-8 text-center text-rose-500">Failed to load overview data.</div>
        )
      )}

      {/* 2. Success Explorer (HERO) */}
      {currentTab === 'explorer' && (
        isLoadingExplorer ? (
          <div className="p-12 text-center text-slate-400 text-sm">Analyzing diagnostic signals...</div>
        ) : explorerData ? (
          <ExplorerPage data={explorerData} onRefresh={refreshAll} onNavigate={setCurrentTab} />
        ) : (
          <div className="p-8 text-center text-rose-500">Failed to load Success Explorer.</div>
        )
      )}

      {/* 3. Attendance */}
      {currentTab === 'attendance' && (
        isLoadingAttendance ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading attendance records...</div>
        ) : attendanceData ? (
          <AttendancePage data={attendanceData} studentId={studentId} onRefresh={refreshAll} />
        ) : (
          <div className="p-8 text-center text-rose-500">Failed to load attendance records.</div>
        )
      )}

      {/* 4. Academics */}
      {currentTab === 'academics' && (
        isLoadingCourses || isLoadingAssessments ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading academic evaluations...</div>
        ) : (
          <AcademicsPage
            studentId={studentId}
            courses={courses}
            assessments={assessments}
            results={resultsData?.results || []}
            cgpa={resultsData?.cgpa ?? null}
            onRefresh={refreshAll}
            onNavigate={setCurrentTab}
          />
        )
      )}

      {/* 5. Engagement */}
      {currentTab === 'engagement' && (
        isLoadingEngagement || isLoadingEvents ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading activity catalogue...</div>
        ) : engagementSummary ? (
          <EngagementPage
            studentId={studentId}
            summary={engagementSummary}
            events={events}
            onRefresh={refreshAll}
          />
        ) : (
          <div className="p-8 text-center text-rose-500">Failed to load engagement portfolio.</div>
        )
      )}

      {/* 6. Scholarship */}
      {currentTab === 'scholarship' && (
        isLoadingSchemes ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading scholarship schemes...</div>
        ) : (
          <ScholarshipPage
            studentId={studentId}
            schemes={schemes}
            attestedFacts={attestedFacts}
            onRefresh={refreshAll}
          />
        )
      )}

      {/* 7. Mentor Explorer */}
      {currentTab === 'mentor' && (
        isLoadingCohort ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            Computing unsupervised cohort clusters (k=3-6, isolation forest)...
          </div>
        ) : cohortData ? (
          <MentorPage data={cohortData} />
        ) : (
          <div className="p-8 text-center text-rose-500">Failed to compute cohort analysis.</div>
        )
      )}

      {/* 8. Data Workspace */}
      {currentTab === 'data' && (
        <DataWorkspacePage
          personas={personas}
          activeStudentId={studentId}
          onSelectPersona={handleSelectPersona}
          onRefresh={refreshAll}
        />
      )}

      {/* 9. Settings */}
      {currentTab === 'settings' && <SettingsPage onRefresh={refreshAll} />}
    </AppShell>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainDashboard />
    </QueryClientProvider>
  )
}
