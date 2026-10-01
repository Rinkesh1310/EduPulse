"""
EduPulse Academic Intelligence Platform - FastAPI Backend
Provides typed, validated REST API endpoints for all core academic, attendance,
engagement, scholarship, cohort ML, and data import services.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np
from fastapi import FastAPI, HTTPException, Query, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from edupulse.domain.models import Student, Course, Assessment, AttendanceRecord, SemesterResult
from edupulse.domain.enums import SupportLevel, EngagementStatus, CoverageStatus, VerificationLevel
from edupulse.services.academic_service import AcademicService
from edupulse.ml.cohort_generator import generate_synthetic_cohort
from edupulse.ml.unsupervised import run_unsupervised_cohort_analysis
from edupulse.providers.file_import import FileImportProvider
from edupulse.providers.paste_import import PasteImportProvider
from edupulse.providers.authorized_charusat import AuthorizedCharusatProvider, NotAuthorizedError


app = FastAPI(
    title="EduPulse Academic Intelligence API",
    description="Backend API connecting the modern React frontend to the EduPulse Python intelligence engine.",
    version="1.0.0",
)

# Enable CORS for React frontend (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service Singleton
service = AcademicService()

# Ensure personas are seeded
if not service.get_student_profile("student_synth_strong"):
    service.seed_all_personas(reset=True)

# In-memory active student ID
_state = {
    "active_student_id": "student_synth_strong"
}

def get_current_student_id(override_id: Optional[str] = None) -> str:
    if override_id and override_id.strip():
        return override_id.strip()
    return _state["active_student_id"]

def sanitize_value(val: Any) -> Any:
    """Helper to ensure clean JSON serialization for numpy, enums, etc."""
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val) if not np.isnan(val) else None
    if isinstance(val, (np.bool_,)):
        return bool(val)
    if isinstance(val, (SupportLevel, EngagementStatus, CoverageStatus, VerificationLevel)):
        return val.value
    if hasattr(val, "model_dump"):
        return sanitize_value(val.model_dump())
    if isinstance(val, dict):
        return {k: sanitize_value(v) for k, v in val.items()}
    if isinstance(val, list):
        return [sanitize_value(v) for v in val]
    return val


# -------------------------------------------------------------
# Request & Response Models
# -------------------------------------------------------------
class SetActiveStudentRequest(BaseModel):
    student_id: str

class AssessmentInputRequest(BaseModel):
    student_id: Optional[str] = None
    course_id: str
    ass_type: str = "Midterm"
    obtained_marks: float = Field(..., ge=0.0)
    total_marks: float = Field(..., gt=0.0)
    date: str = "2026-09-20"
    term: str = "T1"

class ToggleParticipationRequest(BaseModel):
    student_id: Optional[str] = None
    event_id: str
    participated: bool

class SetDeclarationRequest(BaseModel):
    student_id: Optional[str] = None
    term: str = "2026-27-ODD"
    status: str = "DECLARED_NONE"

class RecoveryCalculationRequest(BaseModel):
    student_id: Optional[str] = None
    course_id: Optional[str] = None
    target_pct: float = Field(70.0, ge=40.0, le=100.0)
    remaining_classes: int = Field(35, ge=1, le=200)
    present: Optional[int] = None
    total: Optional[int] = None

class CgpaPlanRequest(BaseModel):
    student_id: Optional[str] = None
    target_cgpa: float = Field(7.5, ge=4.0, le=10.0)
    future_credits: float = Field(24.0, ge=1.0, le=120.0)

class AttestedFactsRequest(BaseModel):
    student_id: Optional[str] = None
    annualFamilyIncome: Optional[float] = None
    domicileGujarat: Optional[bool] = None
    previousYearMarksPercent: Optional[float] = None
    currentlyReceivingScheme: Optional[bool] = None

class FileImportRequest(BaseModel):
    content: str
    student_name: str = "Imported Student"
    program: str = "B.Tech IT (Imported)"
    semester: int = 3
    academic_year: str = "2026-27"

class PasteImportRequest(BaseModel):
    text: str
    student_id: Optional[str] = None


# -------------------------------------------------------------
# System & Persona Endpoints
# -------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "EduPulse Academic Intelligence Engine",
        "version": "1.0.0",
        "active_student_id": _state["active_student_id"]
    }

@app.get("/api/personas")
def get_personas():
    personas = service.get_available_personas()
    active_id = _state["active_student_id"]
    res = []
    for p in personas:
        p_copy = dict(p)
        p_copy["is_active"] = (p["id"] == active_id)
        res.append(p_copy)
    return res

@app.get("/api/students/active")
def get_active_student():
    student_id = _state["active_student_id"]
    student = service.get_student_profile(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Active student profile not found")
    
    provenance = service.get_student_provenance(student_id)
    coverage = service.get_coverage(student_id)
    
    return {
        "student": student.model_dump(),
        "provenance": provenance,
        "coverage": coverage.overall.value,
        "active_student_id": student_id
    }

@app.post("/api/students/active")
def set_active_student(req: SetActiveStudentRequest):
    student = service.get_student_profile(req.student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID '{req.student_id}' does not exist")
    _state["active_student_id"] = req.student_id
    return {
        "success": True,
        "active_student_id": req.student_id,
        "name": student.name
    }


# -------------------------------------------------------------
# Overview Endpoint (Aggregated Snapshot)
# -------------------------------------------------------------
@app.get("/api/overview")
def get_overview(student_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    student = service.get_student_profile(st_id)
    if not student:
        service.seed_all_personas(reset=False)
        student = service.get_student_profile(st_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

    sem = student.semester or 3
    signals = service.get_support_signals(st_id)
    att_summary = service.get_attendance_summary(st_id, sem)
    coverage = service.get_coverage(st_id)
    provenance = service.get_student_provenance(st_id)
    narrative = service.get_diagnostic_narrative(st_id)
    courses = service.list_courses(st_id, sem)
    results = service.get_semester_results(st_id)
    policy = service.get_policy()

    # Academic Attention Areas
    att_alerts = []
    for r in att_summary.get("records", []):
        if r.computed_percentage is not None and r.computed_percentage < policy.attendancePerCoursePct:
            att_alerts.append({
                "type": "attendance",
                "courseId": r.courseId,
                "courseName": r.courseName or r.courseId,
                "component": r.component.value,
                "percentage": r.computed_percentage,
                "present": r.presentCount,
                "total": r.totalCount,
                "threshold": policy.attendancePerCoursePct,
                "severity": "high" if r.computed_percentage < 60.0 else "moderate",
                "message": f"{r.courseName or r.courseId} ({r.component.value}) is at {r.computed_percentage:.1f}%, below the {policy.attendancePerCoursePct:.0f}% policy threshold."
            })

    acad_alerts = []
    assessments = service.get_assessments(st_id)
    for a in assessments:
        if a.percentage is not None and a.percentage < 50.0:
            c = next((crs for crs in courses if crs.id == a.courseId), None)
            c_name = c.shortName if c else a.courseId
            acad_alerts.append({
                "type": "academic",
                "courseId": a.courseId,
                "courseName": c_name,
                "assessmentType": a.assessmentType,
                "obtained": a.obtainedMarks,
                "total": a.totalMarks,
                "percentage": a.percentage,
                "threshold": 50.0,
                "severity": "high" if a.percentage < 40.0 else "moderate",
                "message": f"{c_name} {a.assessmentType}: {a.obtainedMarks}/{a.totalMarks} ({a.percentage:.1f}%) is below the 50% benchmark."
            })

    # SGPA Progression Trend
    sgpa_trend = []
    for r in results:
        sgpa_trend.append({
            "semester": f"Sem {r.semester}",
            "sgpa": r.sgpa,
            "credits": r.creditsComplete,
            "status": "Published"
        })

    # Scholarship Snapshot
    schemes = service.get_scholarships()
    scholarship_readiness = None
    if schemes:
        primary_scheme = schemes[0]
        eval_res = service.evaluate_scholarship(st_id, primary_scheme.schemeId, "renewal", 35)
        scholarship_readiness = {
            "schemeId": primary_scheme.schemeId,
            "schemeName": primary_scheme.name,
            "summaryCounts": eval_res["summaryCountsText"],
            "verificationLevel": primary_scheme.verificationLevel.value
        }

    return sanitize_value({
        "student": student.model_dump(),
        "provenance": provenance,
        "asOfDate": att_summary.get("asOfDate", "2026-09-30"),
        "coverage": coverage.overall.value,
        "supportStatus": signals["overallSupportSignal"].value,
        "supportDisplayText": signals["overallDisplayText"],
        "snapshotNarrative": narrative["what_detected"],
        "metrics": {
            "attendance": {
                "value": f"{att_summary['computedOverall']:.1f}%" if att_summary["computedOverall"] is not None else "N/A",
                "present": att_summary["totalPresent"],
                "total": att_summary["totalClasses"],
                "status": signals["attendanceSignal"].value,
                "trend": "Stable" if att_summary["computedOverall"] and att_summary["computedOverall"] >= 75.0 else "Attention"
            },
            "academics": {
                "value": f"{signals['academicMeta'].get('evaluatedCount', 0)}/{len(courses)} Evaluated",
                "status": signals["academicSignal"].value,
                "coverage": signals["academicMeta"].get("coverage", "N/A"),
                "belowBenchmarkCount": signals["academicMeta"].get("belowCount", 0)
            },
            "engagement": {
                "value": f"{signals['engagementSummary']['points']:.1f} pts",
                "level": signals["engagementSummary"]["level"],
                "status": "Healthy" if signals["engagementSummary"]["points"] >= 4.0 else "Developing",
                "eventCount": signals["engagementSummary"]["eventCount"],
                "diversityCount": signals["engagementSummary"]["diversityCount"]
            },
            "supportSignal": {
                "level": signals["overallSupportSignal"].value,
                "badgeText": signals["overallSupportSignal"].value.upper(),
                "description": signals["overallDisplayText"]
            }
        },
        "attentionAreas": {
            "attendanceAlerts": att_alerts,
            "academicAlerts": acad_alerts,
            "totalAlerts": len(att_alerts) + len(acad_alerts)
        },
        "performanceTrend": {
            "sgpaHistory": sgpa_trend,
            "enrolledCoursesCount": len(courses)
        },
        "recommendedActions": narrative["what_to_do_next"],
        "scholarshipReadiness": scholarship_readiness
    })


# -------------------------------------------------------------
# Student Success Explorer Endpoint (HERO FEATURE)
# -------------------------------------------------------------
@app.get("/api/explorer")
def get_success_explorer(student_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    student = service.get_student_profile(st_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    sem = student.semester or 3
    signals = service.get_support_signals(st_id)
    policy = signals["policy"]
    provenance = service.get_student_provenance(st_id)
    narrative = service.get_diagnostic_narrative(st_id)
    att_summary = service.get_attendance_summary(st_id, sem)
    coverage = service.get_coverage(st_id)

    # Format Evidence Cards
    evidence = []
    for r in signals["reasons"]:
        threshold_note = "Evaluation Standard: Institutional Policy"
        if "attendance" in r.indicator.lower():
            threshold_note = f"Policy Threshold: ≥ {policy.attendancePerCoursePct:.0f}% course / {policy.attendanceOverallPct:.0f}% overall"
        elif "marks" in r.indicator.lower() or "score" in r.indicator.lower():
            threshold_note = "Benchmark: ≥ 50% passing threshold / ≥ 65% strong"

        evidence.append({
            "indicator": r.indicator,
            "value": r.value,
            "direction": r.direction,  # 'concern' | 'positive' | 'neutral'
            "category": "Attendance" if "attendance" in r.indicator.lower() else ("Academic" if "mark" in r.indicator.lower() or "course" in r.indicator.lower() or "assessment" in r.indicator.lower() else "Engagement"),
            "threshold": threshold_note,
            "source": f"{r.source} ({provenance})"
        })

    # Default Attendance Recovery Simulation
    tot_p = att_summary["totalPresent"] or 0
    tot_c = att_summary["totalClasses"] or 0
    recovery_default = service.calculate_recovery(
        present=tot_p,
        total=tot_c,
        target_pct=float(policy.attendanceOverallPct),
        remaining_classes=35
    )

    return sanitize_value({
        "student": student.model_dump(),
        "provenance": provenance,
        "asOfDate": att_summary.get("asOfDate", "2026-09-30"),
        "coverage": coverage.overall.value,
        "overallSupportSignal": signals["overallSupportSignal"].value,
        "overallDisplayText": signals["overallDisplayText"],
        "narrative": {
            "whatDetected": narrative["what_detected"],
            "whyDetected": narrative["why_detected"],
            "whatToDoNext": narrative["what_to_do_next"]
        },
        "pillars": {
            "attendance": {
                "signal": signals["attendanceSignal"].value,
                "percentage": att_summary["computedOverall"],
                "present": tot_p,
                "total": tot_c,
                "belowThresholdCount": signals["attendanceMeta"].get("belowCount", 0),
                "threshold": policy.attendanceOverallPct
            },
            "academic": {
                "signal": signals["academicSignal"].value,
                "evaluatedCount": signals["academicMeta"].get("evaluatedCount", 0),
                "coverage": signals["academicMeta"].get("coverage", "N/A"),
                "belowBenchmarkCount": signals["academicMeta"].get("belowCount", 0),
                "benchmark": 50.0
            },
            "engagement": {
                "level": signals["engagementSummary"]["level"],
                "points": signals["engagementSummary"]["points"],
                "eventCount": signals["engagementSummary"]["eventCount"],
                "diversityCount": signals["engagementSummary"]["diversityCount"]
            }
        },
        "evidence": evidence,
        "recommendations": narrative["what_to_do_next"],
        "howCalculated": {
            "attendanceThresholdOverall": policy.attendanceOverallPct,
            "attendanceThresholdCourse": policy.attendancePerCoursePct,
            "academicPassingBenchmark": 50.0,
            "smallSampleThreshold": policy.smallSampleThreshold,
            "governancePrinciple": (
                "Support signals exist to alert mentors and students to supportive opportunities early in the semester. "
                "They are non-punitive, evidence-based checkpoints and do not predict final course grades or exam outcomes."
            )
        },
        "recoverySimulation": {
            "currentPresent": tot_p,
            "currentTotal": tot_c,
            "defaultTargetPct": policy.attendanceOverallPct,
            "defaultRemainingClasses": 35,
            "result": recovery_default
        }
    })


# -------------------------------------------------------------
# Attendance Endpoints
# -------------------------------------------------------------
@app.get("/api/attendance/summary")
def get_attendance_summary(
    student_id: Optional[str] = None,
    semester: Optional[int] = None
):
    st_id = get_current_student_id(student_id)
    student = service.get_student_profile(st_id)
    sem = semester or (student.semester if student else 3)
    
    summary = service.get_attendance_summary(st_id, sem)
    policy = service.get_policy()
    daily = service.get_daily_attendance(st_id)

    # Format records
    formatted_records = []
    for r in summary.get("records", []):
        pct = r.computed_percentage
        status = "healthy"
        if pct is not None:
            if pct < policy.attendancePerCoursePct:
                status = "critical" if pct < 60.0 else "warning"
            elif pct >= 85.0:
                status = "excellent"

        formatted_records.append({
            "id": r.id,
            "courseId": r.courseId,
            "courseName": r.courseName or r.courseId,
            "component": r.component.value,
            "presentCount": r.presentCount,
            "totalCount": r.totalCount,
            "computedPercentage": pct,
            "status": status,
            "asOfDate": r.asOfDate
        })

    return sanitize_value({
        "computedOverall": summary["computedOverall"],
        "portalOverall": summary["portalOverall"],
        "totalPresent": summary["totalPresent"],
        "totalClasses": summary["totalClasses"],
        "headline": summary["headline"],
        "mismatchNote": summary.get("mismatchNote"),
        "asOfDate": summary.get("asOfDate", "2026-09-30"),
        "targetPct": policy.attendanceOverallPct,
        "courseTargetPct": policy.attendancePerCoursePct,
        "records": formatted_records,
        "dailyTimeline": daily[:20] if daily else []
    })

@app.post("/api/attendance/recovery")
def calculate_recovery(req: RecoveryCalculationRequest):
    st_id = get_current_student_id(req.student_id)
    
    present = req.present
    total = req.total
    
    if present is None or total is None:
        student = service.get_student_profile(st_id)
        sem = student.semester if student else 3
        summary = service.get_attendance_summary(st_id, sem)
        present = summary["totalPresent"] or 0
        total = summary["totalClasses"] or 0

    res = service.calculate_recovery(
        present=present,
        total=total,
        target_pct=req.target_pct,
        remaining_classes=req.remaining_classes
    )
    return sanitize_value(res)


# -------------------------------------------------------------
# Academics Endpoints
# -------------------------------------------------------------
@app.get("/api/academics/courses")
def list_courses(student_id: Optional[str] = None, semester: Optional[int] = None):
    st_id = get_current_student_id(student_id)
    student = service.get_student_profile(st_id)
    sem = semester or (student.semester if student else 3)
    courses = service.list_courses(st_id, sem)
    return sanitize_value([c.model_dump() for c in courses])

@app.get("/api/academics/assessments")
def get_assessments(student_id: Optional[str] = None, course_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    assessments = service.get_assessments(st_id, course_id)
    courses = service.list_courses(st_id)
    c_map = {c.id: c.shortName for c in courses}
    
    res = []
    for a in assessments:
        item = a.model_dump()
        item["courseName"] = c_map.get(a.courseId, a.courseId)
        res.append(item)
    return sanitize_value(res)

@app.post("/api/academics/assessments")
def save_assessment(req: AssessmentInputRequest):
    st_id = get_current_student_id(req.student_id)
    if req.obtained_marks > req.total_marks:
        raise HTTPException(status_code=400, detail="Obtained marks cannot exceed total marks")
        
    assessment = service.save_or_update_course_assessment(
        student_id=st_id,
        course_id=req.course_id,
        ass_type=req.ass_type,
        obtained_marks=req.obtained_marks,
        total_marks=req.total_marks,
        date=req.date,
        term=req.term
    )
    
    # Recalculate support signals and narrative immediately!
    signals = service.get_support_signals(st_id)
    narrative = service.get_diagnostic_narrative(st_id)

    return sanitize_value({
        "success": True,
        "assessment": assessment.model_dump(),
        "updatedSignals": {
            "overallSupportSignal": signals["overallSupportSignal"].value,
            "academicSignal": signals["academicSignal"].value,
            "overallDisplayText": signals["overallDisplayText"],
            "whatDetected": narrative["what_detected"]
        }
    })

@app.delete("/api/academics/assessments/{assessment_id}")
def delete_assessment(assessment_id: str, student_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    service.delete_assessment(assessment_id)
    signals = service.get_support_signals(st_id)
    narrative = service.get_diagnostic_narrative(st_id)
    return sanitize_value({
        "success": True,
        "deletedId": assessment_id,
        "updatedSignals": {
            "overallSupportSignal": signals["overallSupportSignal"].value,
            "academicSignal": signals["academicSignal"].value,
            "whatDetected": narrative["what_detected"]
        }
    })

@app.get("/api/academics/results")
def get_semester_results(student_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    results = service.get_semester_results(st_id)
    
    total_credits = sum(r.creditsComplete for r in results)
    weighted_pts = sum(r.sgpa * r.creditsComplete for r in results)
    cgpa = (weighted_pts / total_credits) if total_credits > 0 else None

    return sanitize_value({
        "results": [r.model_dump() for r in results],
        "cgpa": round(cgpa, 2) if cgpa is not None else None,
        "totalCreditsEarned": total_credits
    })

@app.post("/api/academics/cgpa-plan")
def calculate_cgpa_plan(req: CgpaPlanRequest):
    st_id = get_current_student_id(req.student_id)
    plan = service.calculate_cgpa_plan(
        st_id,
        target_cgpa=req.target_cgpa,
        future_credits=req.future_credits
    )
    return sanitize_value(plan)


# -------------------------------------------------------------
# Engagement Endpoints
# -------------------------------------------------------------
@app.get("/api/engagement/summary")
def get_engagement_summary(student_id: Optional[str] = None, term: str = "2026-27-ODD"):
    st_id = get_current_student_id(student_id)
    summary = service.get_engagement_summary(st_id, term)
    return sanitize_value(summary)

@app.get("/api/engagement/events")
def get_events(student_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    events = service.get_events()
    participations = {p.eventId: p for p in service.get_participations(st_id)}
    
    res = []
    for e in events:
        item = e.model_dump()
        part = participations.get(e.id)
        item["participated"] = (part is not None and part.confirmed)
        item["confirmedAt"] = part.confirmedAt if part else None
        res.append(item)
    return sanitize_value(res)

@app.post("/api/engagement/toggle-participation")
def toggle_participation(req: ToggleParticipationRequest):
    st_id = get_current_student_id(req.student_id)
    service.toggle_event_participation(
        student_id=st_id,
        event_id=req.event_id,
        participated=req.participated
    )
    summary = service.get_engagement_summary(st_id)
    return sanitize_value({
        "success": True,
        "eventId": req.event_id,
        "participated": req.participated,
        "updatedSummary": summary
    })

@app.post("/api/engagement/declaration")
def set_declaration(req: SetDeclarationRequest):
    st_id = get_current_student_id(req.student_id)
    status_enum = getattr(EngagementStatus, req.status, EngagementStatus.DECLARED_NONE)
    service.set_engagement_declaration(st_id, req.term, status_enum)
    summary = service.get_engagement_summary(st_id, req.term)
    return sanitize_value({
        "success": True,
        "status": status_enum.value,
        "updatedSummary": summary
    })


# -------------------------------------------------------------
# Scholarship Planner Endpoints
# -------------------------------------------------------------
@app.get("/api/scholarship/schemes")
def get_scholarships():
    schemes = service.get_scholarships()
    return sanitize_value([s.model_dump() for s in schemes])

@app.get("/api/scholarship/evaluate")
def evaluate_scholarship(
    scheme_id: str,
    student_id: Optional[str] = None,
    track: str = "renewal",
    remaining_classes: int = 35
):
    st_id = get_current_student_id(student_id)
    eval_res = service.evaluate_scholarship(
        student_id=st_id,
        scheme_id=scheme_id,
        selected_track=track,
        planned_remaining_classes=remaining_classes
    )
    return sanitize_value(eval_res)

@app.get("/api/scholarship/attested-facts")
def get_attested_facts(student_id: Optional[str] = None):
    st_id = get_current_student_id(student_id)
    facts = service.get_attested_facts(st_id)
    return sanitize_value(facts)

@app.post("/api/scholarship/attested-facts")
def save_attested_facts(req: AttestedFactsRequest):
    st_id = get_current_student_id(req.student_id)
    now_str = datetime.now().isoformat()
    
    if req.annualFamilyIncome is not None:
        service.save_attested_fact(st_id, "annualFamilyIncome", req.annualFamilyIncome, now_str)
    if req.domicileGujarat is not None:
        service.save_attested_fact(st_id, "domicileGujarat", req.domicileGujarat, now_str)
    if req.previousYearMarksPercent is not None:
        service.save_attested_fact(st_id, "previousYearMarksPercent", req.previousYearMarksPercent, now_str)
    if req.currentlyReceivingScheme is not None:
        service.save_attested_fact(st_id, "currentlyReceivingScheme", req.currentlyReceivingScheme, now_str)
        
    updated = service.get_attested_facts(st_id)
    return sanitize_value({
        "success": True,
        "facts": updated
    })


# -------------------------------------------------------------
# Mentor Explorer & Cohort ML Endpoints
# -------------------------------------------------------------
_cached_cohort_analysis = None

@app.get("/api/cohort/analysis")
def get_cohort_analysis(recompute: bool = False):
    global _cached_cohort_analysis
    if _cached_cohort_analysis is None or recompute:
        df = generate_synthetic_cohort(n=300, seed=42)
        analysis = run_unsupervised_cohort_analysis(df, min_k=3, max_k=6)
        df_analyzed = analysis["analyzedData"]
        
        # Prepare points for scatter plot (max 300 points)
        points = []
        for _, row in df_analyzed.iterrows():
            points.append({
                "student_id": row["student_id"],
                "attendance_overall": round(float(row["attendance_overall"]), 1),
                "mean_marks": round(float(row["mean_marks"]), 1),
                "cluster_id": int(row["cluster_id"]),
                "is_anomaly": bool(row["is_anomaly"]),
                "lowest_component_att": round(float(row["lowest_component_att"]), 1),
                "engagement_points": round(float(row["engagement_points"]), 1),
                "rule_based_signal": str(row["rule_based_signal"])
            })

        # Calculate cluster summaries
        cluster_summaries = []
        for c_id in sorted(df_analyzed["cluster_id"].unique()):
            c_df = df_analyzed[df_analyzed["cluster_id"] == c_id]
            size = len(c_df)
            if size < 5:
                # k-anonymity privacy guarantee
                cluster_summaries.append({
                    "clusterId": int(c_id),
                    "size": size,
                    "suppressed": True,
                    "label": f"Cluster {c_id} (Suppressed < 5 members)"
                })
            else:
                cluster_summaries.append({
                    "clusterId": int(c_id),
                    "size": size,
                    "suppressed": False,
                    "meanAttendance": round(float(c_df["attendance_overall"].mean()), 1),
                    "meanMarks": round(float(c_df["mean_marks"].mean()), 1),
                    "meanEngagement": round(float(c_df["engagement_points"].mean()), 1),
                    "anomalyCount": int(c_df["is_anomaly"].sum()),
                    "label": f"Cluster {c_id}"
                })

        _cached_cohort_analysis = {
            "cohortSize": len(df_analyzed),
            "bestK": int(analysis["bestK"]),
            "bestSilhouette": round(float(analysis["bestSilhouette"]), 3),
            "anomalyCount": int(analysis["anomalyCount"]),
            "privacyGuard": "k-anonymity (n < 5 suppressed)",
            "clusters": cluster_summaries,
            "scatterPoints": points,
            "methodologyNotice": (
                "Synthetic data • exploratory patterns • not a validated predictor. "
                "Unsupervised clustering identifies emergent behavior groups without circular pseudo-labels. "
                "Any pattern group with fewer than 5 members is automatically suppressed under k-anonymity rules."
            )
        }

    return sanitize_value(_cached_cohort_analysis)


# -------------------------------------------------------------
# Data Workspace Endpoints (Connect / Import / Paste / Provider)
# -------------------------------------------------------------
@app.post("/api/data-workspace/preview-file")
def preview_file(req: FileImportRequest):
    target_id = f"student_imported_{abs(hash(req.student_name)) % 10000}"
    preview = FileImportProvider.preview_attendance_csv(req.content, target_id)
    
    records_clean = []
    if preview.get("valid") and preview.get("records"):
        for r in preview["records"]:
            records_clean.append({
                "courseId": r.courseId,
                "courseName": r.courseName or r.courseId,
                "component": r.component.value,
                "presentCount": r.presentCount,
                "totalCount": r.totalCount,
                "percentage": r.computed_percentage
            })

    return sanitize_value({
        "valid": preview["valid"],
        "rowCount": preview["rowCount"],
        "checksum": preview.get("checksum"),
        "errors": preview.get("errors", []),
        "records": records_clean
    })

@app.post("/api/data-workspace/commit-file")
def commit_file(req: FileImportRequest):
    target_id = f"student_imported_{abs(hash(req.student_name)) % 10000}"
    preview = FileImportProvider.preview_attendance_csv(req.content, target_id)
    
    if not preview["valid"]:
        raise HTTPException(status_code=400, detail="Uploaded file failed validation: " + "; ".join(preview["errors"]))

    imported_student = Student(
        id=target_id,
        externalStudentId=f"IMP-{abs(hash(req.student_name)) % 1000:03d}",
        name=req.student_name,
        program=req.program,
        semester=req.semester,
        academicYear=req.academic_year,
    )
    service.repo.save_student(imported_student)

    for rec in preview["records"]:
        service.repo.save_attendance_record(rec)

    _state["active_student_id"] = target_id
    
    return sanitize_value({
        "success": True,
        "studentId": target_id,
        "studentName": req.student_name,
        "recordsCount": len(preview["records"])
    })

@app.post("/api/data-workspace/preview-paste")
def preview_paste(req: PasteImportRequest):
    st_id = get_current_student_id(req.student_id)
    parsed = PasteImportProvider.parse_attendance_paste(req.text, st_id)
    
    records_clean = []
    if parsed.get("valid") and parsed.get("records"):
        for r in parsed["records"]:
            records_clean.append({
                "courseId": r.courseId,
                "courseName": r.courseName or r.courseId,
                "component": r.component.value,
                "presentCount": r.presentCount,
                "totalCount": r.totalCount,
                "percentage": r.computed_percentage
            })

    return sanitize_value({
        "valid": parsed["valid"],
        "rowCount": parsed["rowCount"],
        "errors": parsed.get("errors", []),
        "records": records_clean
    })

@app.post("/api/data-workspace/commit-paste")
def commit_paste(req: PasteImportRequest):
    st_id = get_current_student_id(req.student_id)
    parsed = PasteImportProvider.parse_attendance_paste(req.text, st_id)
    
    if not parsed["valid"]:
        raise HTTPException(status_code=400, detail="Pasted text failed parsing: " + "; ".join(parsed["errors"]))

    for r in parsed["records"]:
        service.repo.save_attendance_record(r)

    return sanitize_value({
        "success": True,
        "studentId": st_id,
        "recordsCommitted": len(parsed["records"])
    })

@app.get("/api/data-workspace/templates/{template_type}")
def download_template(template_type: str):
    if template_type == "attendance":
        content = FileImportProvider.generate_attendance_csv_template()
        filename = "attendance_template.csv"
    elif template_type == "marks":
        content = FileImportProvider.generate_marks_csv_template()
        filename = "marks_template.csv"
    elif template_type == "daily":
        content = FileImportProvider.generate_daily_csv_template()
        filename = "daily_timetable_template.csv"
    else:
        raise HTTPException(status_code=404, detail="Unknown template type")

    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/api/data-workspace/reset")
def reset_workspace(scenario: str = Body("student_synth_strong", embed=True)):
    service.seed_all_personas(reset=True)
    _state["active_student_id"] = scenario
    return {
        "success": True,
        "active_student_id": scenario,
        "message": "Reset all persona databases to initial state successfully."
    }

@app.post("/api/data-workspace/authorized-connector-stub")
def test_authorized_connector():
    """Verifies that the live CHARUSAT connector safely raises NotAuthorizedError."""
    try:
        provider = AuthorizedCharusatProvider()
        provider.get_profile()
        return {"status": "unexpected_success", "message": "Expected NotAuthorizedError"}
    except NotAuthorizedError as e:
        return {
            "status": "security_boundary_verified",
            "error_type": "NotAuthorizedError",
            "message": str(e),
            "explanation": "Confirmed: EduPulse cleanly rejects unauthorized scraping and requires an official institutional integration."
        }
