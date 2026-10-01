import React, { useState } from 'react'
import { EventItem, EngagementSummaryData, api } from '../../../api/client'
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/Card'
import { Button } from '../../ui/Button'
import { Input } from '../../ui/Input'
import { Badge } from '../../ui/Badge'
import {
  Sparkles,
  Search,
  CheckCircle2,
  Calendar,
  Clock,
  Award,
  ShieldCheck,
  Building,
  Filter,
} from 'lucide-react'

export interface EngagementPageProps {
  studentId: string
  summary: EngagementSummaryData
  events: EventItem[]
  onRefresh: () => void
}

export function EngagementPage({ studentId, summary, events, onRefresh }: EngagementPageProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [isUpdating, setIsUpdating] = useState<string | null>(null)

  // Categories list
  const categories = ['all', ...Array.from(new Set(events.map((e) => e.category)))]

  // Filtered Events
  const filteredEvents = events.filter((e) => {
    const matchesSearch =
      e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.organizer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      e.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || e.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  // Toggle Participation
  const handleToggleParticipation = async (event: EventItem) => {
    setIsUpdating(event.id)
    try {
      await api.toggleParticipation({
        student_id: studentId,
        event_id: event.id,
        participated: !event.participated,
      })
      onRefresh()
    } catch (err: any) {
      alert(`Failed to update event participation: ${err.message}`)
    } finally {
      setIsUpdating(null)
    }
  }

  // Handle Declaration
  const handleDeclareNone = async () => {
    try {
      await api.setDeclaration({
        student_id: studentId,
        term: '2026-27-ODD',
        status: 'DECLARED_NONE',
      })
      alert('Declared no co-curricular events for current term (Informational).')
      onRefresh()
    } catch (err: any) {
      alert(`Failed to set declaration: ${err.message}`)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/90 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Engagement & Co-Curricular
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Co-curricular portfolio tracking, competitive achievements, and skill-building activities.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleDeclareNone}
            className="text-xs border-slate-300 text-slate-700 h-8"
          >
            Declare No Events This Term
          </Button>
        </div>
      </div>

      {/* 2. Top Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Portfolio Status
            </span>
            <div className="text-2xl font-extrabold text-blue-600">{summary.level}</div>
            <p className="text-xs text-slate-500 mt-1">{summary.description}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Engagement Points
            </span>
            <div className="text-3xl font-extrabold text-slate-900">{summary.points.toFixed(1)}</div>
            <p className="text-xs text-slate-500 mt-1">Weight × duration factor</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Confirmed Events
            </span>
            <div className="text-3xl font-extrabold text-slate-900">{summary.eventCount}</div>
            <p className="text-xs text-slate-500 mt-1">Current academic term</p>
          </CardContent>
        </Card>

        <Card className="border-slate-200/90 shadow-xs bg-white">
          <CardContent className="p-5">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-1">
              Activity Diversity
            </span>
            <div className="text-3xl font-extrabold text-slate-900">{summary.diversityCount}</div>
            <p className="text-xs text-slate-500 mt-1">Distinct categories</p>
          </CardContent>
        </Card>
      </div>

      {/* 3. Academic Fairness & Independence Guarantee Banner */}
      <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/70 text-blue-900 text-xs sm:text-sm flex items-start gap-3 shadow-2xs">
        <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="font-semibold">Academic Fairness & Independence Principle:</strong> Co-curricular
          activities celebrate student initiative and holistic growth. Engagement metrics{' '}
          <strong>never directly increase or decrease the academic support signal</strong>, nor do they excuse
          required class attendance.
        </div>
      </div>

      {summary.overlaps && summary.overlaps.length > 0 && (
        <div className="p-3.5 rounded-lg border border-amber-200 bg-amber-50 text-amber-900 text-xs space-y-1">
          {summary.overlaps.map((ov, idx) => (
            <div key={idx}>
              <strong>Attendance Overlap:</strong> Event '{ov.name}' on {ov.date} matches an official Present session. <em>{ov.note}</em>
            </div>
          ))}
        </div>
      )}

      {/* 4. Activity Catalogue Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 uppercase tracking-wider">
              Campus Activity Catalogue
            </h3>
            <p className="text-xs text-slate-500">
              Browse sanctioned university competitions, hackathons, and technical workshops.
            </p>
          </div>

          {/* Search & Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative w-48 sm:w-64">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
              <Input
                placeholder="Search events or organizers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 h-8 text-xs"
              />
            </div>

            <div className="flex items-center gap-1 overflow-x-auto py-1">
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors capitalize whitespace-nowrap cursor-pointer ${
                    selectedCategory === cat
                      ? 'bg-blue-600 text-white font-semibold'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Event Cards Grid */}
        {filteredEvents.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs bg-white rounded-xl border border-slate-200">
            No activities match your current search or category filter.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredEvents.map((evt) => {
              const isParticipating = evt.participated
              const isBusy = isUpdating === evt.id

              return (
                <Card
                  key={evt.id}
                  className={`bg-white border transition-all ${
                    isParticipating
                      ? 'border-blue-400/80 shadow-xs ring-1 ring-blue-500/20'
                      : 'border-slate-200/90 shadow-2xs hover:shadow-xs'
                  }`}
                >
                  <CardContent className="p-5 flex flex-col justify-between h-full space-y-4">
                    <div className="space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 px-2 py-0.5 rounded bg-blue-50 border border-blue-200">
                          {evt.category}
                        </span>
                        {isParticipating && (
                          <Badge variant="low" className="text-[10px] py-0 px-2">
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            Confirmed
                          </Badge>
                        )}
                      </div>

                      <h4 className="font-bold text-sm text-slate-900 leading-snug">{evt.name}</h4>

                      <div className="space-y-1 text-xs text-slate-500 pt-1">
                        <div className="flex items-center gap-1.5">
                          <Building className="w-3.5 h-3.5 text-slate-400" />
                          <span>{evt.organizer}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          <span>{evt.date}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-slate-400" />
                          <span>{evt.durationHours} hours • Weight {evt.weight}x</span>
                        </div>
                      </div>

                      {evt.notes && (
                        <p className="text-xs text-slate-600 italic bg-slate-50 p-2 rounded border border-slate-100 mt-2">
                          "{evt.notes}"
                        </p>
                      )}
                    </div>

                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                      <Button
                        variant={isParticipating ? 'secondary' : 'primary'}
                        size="sm"
                        isLoading={isBusy}
                        onClick={() => handleToggleParticipation(evt)}
                        className="w-full text-xs font-semibold h-8"
                      >
                        {isParticipating ? 'Remove from Portfolio' : 'Mark as Participated'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
