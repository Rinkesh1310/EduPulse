import React from 'react'
import { CohortAnalysisData } from '../../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Badge } from '../../ui/Badge'
import {
  Users2,
  Shield,
  ScatterChart as ScatterIcon,
  AlertCircle,
  HelpCircle,
  TrendingDown,
  Info,
} from 'lucide-react'
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts'

export interface MentorPageProps {
  data: CohortAnalysisData
}

export function MentorPage({ data }: MentorPageProps) {
  const { cohortSize, bestK, bestSilhouette, anomalyCount, privacyGuard, clusters, scatterPoints, methodologyNotice } =
    data

  // Color mapping for clusters
  const clusterColors = ['#2563eb', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Users2 className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Mentor Cohort Explorer
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Unsupervised multi-dimensional pattern analysis and exploratory cohort archetypes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="neutral" className="text-xs">
            Advisory Mode
          </Badge>
        </div>
      </div>

      {/* 2. Mandatory ML Honesty & Privacy Banner */}
      <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/80 text-blue-900 text-xs sm:text-sm flex items-start gap-3 shadow-2xs">
        <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="font-semibold">Machine Learning Methodology & Privacy Notice:</strong>{' '}
          {methodologyNotice}
        </div>
      </div>

      {/* 3. Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Cohort Size
            </span>
            <div className="text-3xl font-extrabold text-slate-900">{cohortSize} students</div>
            <p className="text-xs text-slate-500 mt-1">De-identified synthetic cohort</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Pattern Clusters
            </span>
            <div className="text-3xl font-extrabold text-blue-600">k = {bestK}</div>
            <p className="text-xs text-slate-500 mt-1">Optimal silhouette: {bestSilhouette.toFixed(3)}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Anomaly Candidates
            </span>
            <div className="text-3xl font-extrabold text-amber-600">{anomalyCount}</div>
            <p className="text-xs text-slate-500 mt-1">IsolationForest (5% contamination)</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Privacy Guard
            </span>
            <div className="text-xl font-extrabold text-emerald-600 mt-1 flex items-center gap-1.5">
              <Shield className="w-5 h-5" /> Active
            </div>
            <p className="text-xs text-slate-500 mt-2">{privacyGuard}</p>
          </CardContent>
        </Card>
      </div>

      {/* 4. Scatter Plot & Cluster Archetypes */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Scatter Chart */}
        <div className="lg:col-span-8">
          <Card className="border-slate-200/90 bg-white shadow-xs h-full flex flex-col justify-between">
            <CardHeader className="p-5 pb-2 border-b border-slate-100 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900 flex items-center gap-2">
                  <ScatterIcon className="w-4 h-4 text-blue-600" />
                  Multidimensional Pattern Space (Attendance vs Marks)
                </CardTitle>
                <p className="text-xs text-slate-500 mt-0.5">
                  Attendance (%) vs Average Marks (%) clustered by unsupervised KMeans.
                </p>
              </div>
            </CardHeader>

            <CardContent className="p-5">
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis
                      type="number"
                      dataKey="attendance_overall"
                      name="Attendance"
                      unit="%"
                      domain={[30, 100]}
                      stroke="#94a3b8"
                      fontSize={11}
                    />
                    <YAxis
                      type="number"
                      dataKey="mean_marks"
                      name="Marks"
                      unit="%"
                      domain={[20, 100]}
                      stroke="#94a3b8"
                      fontSize={11}
                    />
                    <ZAxis range={[30, 60]} />
                    <Tooltip
                      cursor={{ strokeDasharray: '3 3' }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const pt = payload[0].payload
                          return (
                            <div className="bg-slate-900 text-white p-3 rounded-lg text-xs shadow-lg space-y-1">
                              <div className="font-bold text-blue-300">{pt.student_id}</div>
                              <div>Attendance: <strong>{pt.attendance_overall}%</strong></div>
                              <div>Marks: <strong>{pt.mean_marks}%</strong></div>
                              <div>Cluster: <strong>Cluster {pt.cluster_id}</strong></div>
                              {pt.is_anomaly && (
                                <div className="text-amber-400 font-bold">⚠️ Anomaly Candidate</div>
                              )}
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <ReferenceLine y={50} stroke="#ef4444" strokeDasharray="4 4" label={{ value: '50% Benchmark', fill: '#ef4444', fontSize: 10, position: 'insideBottomRight' }} />
                    <ReferenceLine x={70} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: '70% Target', fill: '#f59e0b', fontSize: 10, position: 'insideTopLeft' }} />

                    {clusters.map((c, i) => {
                      const cPoints = scatterPoints.filter((p) => p.cluster_id === c.clusterId)
                      return (
                        <Scatter
                          key={c.clusterId}
                          name={c.label}
                          data={cPoints}
                          fill={clusterColors[i % clusterColors.length]}
                          opacity={0.8}
                        />
                      )
                    })}
                  </ScatterChart>
                </ResponsiveContainer>
              </div>

              <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-500 pt-2 border-t border-slate-100">
                {clusters.map((c, i) => (
                  <div key={c.clusterId} className="flex items-center gap-1.5">
                    <span
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: clusterColors[i % clusterColors.length] }}
                    />
                    <span>Cluster {c.clusterId} ({c.size} students)</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Cluster Summaries */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="border-slate-200/90 bg-white shadow-xs">
            <CardHeader className="p-5 pb-3 border-b border-slate-100">
              <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-900">
                Cohort Archetypes
              </CardTitle>
            </CardHeader>
            <CardContent className="p-5 space-y-3">
              {clusters.map((c, i) => {
                if (c.suppressed) {
                  return (
                    <div
                      key={c.clusterId}
                      className="p-3.5 rounded-lg border border-slate-200 bg-slate-50 text-xs text-slate-500 italic"
                    >
                      Cluster {c.clusterId}: Suppressed (Group &lt; 5 members under k-anonymity privacy rules)
                    </div>
                  )
                }

                return (
                  <div
                    key={c.clusterId}
                    className="p-4 rounded-xl border border-slate-200/80 bg-white shadow-2xs space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: clusterColors[i % clusterColors.length] }}
                        />
                        <h4 className="font-bold text-sm text-slate-900">Cluster {c.clusterId}</h4>
                      </div>
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {c.size} students
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-600 pt-1">
                      <div>
                        <span className="text-slate-400 block">Avg Attendance:</span>
                        <strong className="text-slate-800">{c.meanAttendance?.toFixed(1)}%</strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Avg Marks:</span>
                        <strong className="text-slate-800">{c.meanMarks?.toFixed(1)}%</strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Avg Engagement:</span>
                        <strong className="text-slate-800">{c.meanEngagement?.toFixed(1)} pts</strong>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Anomalies:</span>
                        <strong className="text-slate-800">{c.anomalyCount}</strong>
                      </div>
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
