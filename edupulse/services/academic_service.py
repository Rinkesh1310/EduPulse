import json
import uuid
from pathlib import Path
from typing import Any

from edupulse.core.academic import (
    calculate_credit_weighted_cgpa,
    calculate_required_future_sgpa,
)
from edupulse.core.attendance import (
    aggregate_course_combined,
    calculate_attendance_recovery,
    compare_headline_with_computed,
)
from edupulse.core.availability import resolve_data_availability
from edupulse.core.engagement import evaluate_engagement_summary
from edupulse.core.signals import (
    evaluate_academic_signal,
    evaluate_attendance_signal,
    evaluate_overall_support_signal,
)
from edupulse.domain.enums import EngagementStatus
from edupulse.domain.models import (
    Assessment,
    Course,
    Coverage,
    DailyAttendance,
    EngagementDeclaration,
    Event,
    PolicyConfig,
    ScholarshipScheme,
    SemesterResult,
    Student,
    StudentEventParticipation,
    UserAttestedFact,
)
from edupulse.storage.repository import StudentRepository, reset_db
from edupulse.storage.seed import seed_scenario_data


class AcademicService:
    """Core application service providing typed API contracts for the UI."""

    def __init__(self, repo: StudentRepository | None = None):
        self.repo = repo or StudentRepository()
        self._policy = self._load_policy()
        self._scholarships = self._load_scholarship_schemes()

    def _load_policy(self) -> PolicyConfig:
        policy_path = Path(__file__).parent.parent / "config" / "policy.json"
        if policy_path.exists():
            data = json.loads(policy_path.read_text(encoding="utf-8"))
            return PolicyConfig(**data)
        return PolicyConfig(version="1.0.0")

    def _load_scholarship_schemes(self) -> list[ScholarshipScheme]:
        sch_dir = Path(__file__).parent.parent / "config" / "scholarship"
        schemes = []
        if sch_dir.exists():
            for p in sch_dir.glob("*.json"):
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    schemes.append(ScholarshipScheme(**data))
                except Exception:
                    pass
        return schemes

    def get_policy(self) -> PolicyConfig:
        return self._policy

    def get_student_profile(self, student_id: str) -> Student | None:
        return self.repo.get_student(student_id)

    def list_courses(self, student_id: str, semester: int | None = None) -> list[Course]:
        return self.repo.list_courses(student_id, semester)

    def get_attendance_summary(
        self, student_id: str, semester: int
    ) -> dict[str, Any]:
        records = self.repo.get_attendance_records(student_id)
        headline = self.repo.get_attendance_headline(student_id, semester)
        tot_p = sum(r.presentCount for r in records)
        tot_c = sum(r.totalCount for r in records)
        computed_overall = round((tot_p / tot_c) * 100.0, 1) if tot_c > 0 else None
        portal_overall = headline.portalReportedOverall if headline else None

        mismatch_note = compare_headline_with_computed(portal_overall, computed_overall)
        combined_groups = aggregate_course_combined(records)

        return {
            "records": records,
            "headline": headline,
            "computedOverall": computed_overall,
            "portalOverall": portal_overall,
            "totalPresent": tot_p,
            "totalClasses": tot_c,
            "mismatchNote": mismatch_note,
            "combinedByCourse": combined_groups,
            "asOfDate": headline.asOfDate if headline else (records[0].asOfDate if records else "2026-09-30"),
        }

    def get_daily_attendance(
        self, student_id: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[DailyAttendance]:
        return self.repo.get_daily_attendance(student_id, from_date, to_date)

    def calculate_recovery(
        self,
        present: int,
        total: int,
        target_pct: float,
        remaining_classes: int | None = None,
    ) -> dict[str, Any]:
        return calculate_attendance_recovery(present, total, target_pct, remaining_classes)

    def get_assessments(self, student_id: str, course_id: str | None = None) -> list[Assessment]:
        return self.repo.get_assessments(student_id, course_id)

    def add_assessment(
        self,
        student_id: str,
        course_id: str,
        ass_type: str,
        date: str,
        obtained_marks: float,
        total_marks: float,
        term: str | None = None,
    ) -> Assessment:
        ass = Assessment(
            id=f"ass_{course_id}_{uuid.uuid4().hex[:8]}",
            studentId=student_id,
            courseId=course_id,
            type=ass_type,
            term=term,
            date=date,
            obtainedMarks=obtained_marks,
            totalMarks=total_marks,
        )
        self.repo.save_assessment(ass)
        return ass

    def save_or_update_course_assessment(
        self,
        student_id: str,
        course_id: str,
        ass_type: str,
        obtained_marks: float,
        total_marks: float,
        date: str | None = None,
        term: str | None = "T1",
    ) -> Assessment:
        """Saves a new assessment or updates existing assessment marks for the course and type in place."""
        existing = self.repo.get_assessments(student_id, course_id)
        match = next((a for a in existing if a.type == ass_type), None)
        ass_date = date or "2026-09-20"
        if match:
            match.obtainedMarks = obtained_marks
            match.totalMarks = total_marks
            match.date = ass_date
            if term:
                match.term = term
            self.repo.save_assessment(match)
            return match
        else:
            return self.add_assessment(
                student_id=student_id,
                course_id=course_id,
                ass_type=ass_type,
                date=ass_date,
                obtained_marks=obtained_marks,
                total_marks=total_marks,
                term=term,
            )

    def delete_assessment(self, assessment_id: str):
        self.repo.delete_assessment(assessment_id)

    def get_student_academic_record(self, student_id: str) -> dict[str, Any]:
        """Compiles the complete student academic record including profile, courses, attendance, current assessments, historical results, and engagement."""
        from edupulse.core.attendance import classify_attendance_band
        from edupulse.providers.mock import PERSONA_REGISTRY

        student = self.repo.get_student(student_id)
        sem = student.semester if student else 3
        courses = self.repo.list_courses(student_id, sem)
        att_summary = self.get_attendance_summary(student_id, sem)
        records = att_summary["records"]
        combined = att_summary["combinedByCourse"]
        assessments = self.repo.get_assessments(student_id)
        results = self.repo.get_semester_results(student_id)
        eng_summary = self.get_engagement_summary(student_id)
        signals = self.get_support_signals(student_id)
        coverage = self.get_coverage(student_id)
        provenance = self.get_student_provenance(student_id)
        policy = self.get_policy()

        # Build course academic details
        course_details = []
        for c in courses:
            c_records = [r for r in records if r.courseId == c.id]
            c_assessments = [a for a in assessments if a.courseId == c.id]
            c_combined = combined.get(c.id, {"present": 0, "total": 0, "percentage": None})

            comp_list = []
            for r in c_records:
                band = classify_attendance_band(
                    r.computed_percentage,
                    threshold=policy.attendancePerCoursePct,
                    is_overall=False,
                    total_classes=r.totalCount,
                    small_sample_threshold=policy.smallSampleThreshold,
                )
                comp_list.append({
                    "component": r.component.value,
                    "present": r.presentCount,
                    "total": r.totalCount,
                    "percentage": r.computed_percentage,
                    "band": band.value,
                })

            ass_list = []
            for a in c_assessments:
                pct = round((a.obtainedMarks / a.totalMarks) * 100.0, 1) if a.totalMarks > 0 else 0.0
                ass_list.append({
                    "id": a.id,
                    "type": a.type,
                    "term": a.term,
                    "date": a.date,
                    "obtained": a.obtainedMarks,
                    "total": a.totalMarks,
                    "percentage": pct,
                })

            course_details.append({
                "id": c.id,
                "code": c.code,
                "shortName": c.shortName,
                "fullName": c.fullName or c.shortName,
                "credits": c.credits or 0.0,
                "semester": c.semester,
                "components": comp_list,
                "combined": c_combined,
                "assessments": ass_list,
                "hasAssessment": len(ass_list) > 0,
            })

        persona_meta = PERSONA_REGISTRY.get(student_id, {})
        status_label = persona_meta.get("academic_status", "Active Term • Record Ready")

        return {
            "student": student,
            "provenance": provenance,
            "academicStatus": status_label,
            "courses": course_details,
            "attendanceSummary": att_summary,
            "results": results,
            "engagementSummary": eng_summary,
            "signals": signals,
            "coverage": coverage,
            "policy": policy,
        }

    def get_events(self) -> list[Event]:
        return self.repo.get_events()

    def get_participations(self, student_id: str) -> list[StudentEventParticipation]:
        return self.repo.get_participations(student_id)

    def toggle_event_participation(
        self, student_id: str, event_id: str, confirmed: bool, confirmation_date: str
    ):
        if confirmed:
            part = StudentEventParticipation(
                studentId=student_id,
                eventId=event_id,
                confirmed=True,
                confirmationDate=confirmation_date,
            )
            self.repo.save_participation(part)
        else:
            self.repo.remove_participation(student_id, event_id)

    def get_engagement_declaration(self, student_id: str, term: str) -> EngagementDeclaration:
        return self.repo.get_engagement_declaration(student_id, term)

    def set_engagement_declaration(self, student_id: str, term: str, status: EngagementStatus):
        decl = EngagementDeclaration(studentId=student_id, term=term, status=status)
        self.repo.save_engagement_declaration(decl)

    def get_engagement_summary(self, student_id: str, term: str = "2026-27-ODD") -> dict[str, Any]:
        parts = self.repo.get_participations(student_id)
        events = {e.eventId: e for e in self.repo.get_events()}
        decl = self.repo.get_engagement_declaration(student_id, term)

        # Get official attendance P dates
        daily = self.repo.get_daily_attendance(student_id)
        p_dates = {d.date for d in daily if d.status.value == "P"}

        return evaluate_engagement_summary(
            participations=parts,
            events_by_id=events,
            declaration_status=decl.status,
            official_attendance_p_dates=p_dates,
        )

    def get_semester_results(self, student_id: str) -> list[SemesterResult]:
        return self.repo.get_semester_results(student_id)

    def calculate_cgpa_plan(
        self,
        student_id: str,
        target_cgpa: float,
        future_credits: float,
        assume_equal_credits: bool = False,
    ) -> dict[str, Any]:
        results = self.repo.get_semester_results(student_id)
        cgpa_info = calculate_credit_weighted_cgpa(results, assume_equal_credits)

        if cgpa_info["isBlocked"] or cgpa_info["cgpa"] is None:
            return {
                "cgpaInfo": cgpa_info,
                "futurePlan": None,
                "isBlocked": True,
            }

        curr_cgpa = cgpa_info["cgpa"]
        completed_c = cgpa_info["totalCredits"] or (len(results) * 25.0)

        plan = calculate_required_future_sgpa(
            current_cgpa=curr_cgpa,
            completed_credits=completed_c,
            target_cgpa=target_cgpa,
            future_credits=future_credits,
        )
        return {
            "cgpaInfo": cgpa_info,
            "futurePlan": plan,
            "isBlocked": False,
        }

    def get_coverage(self, student_id: str) -> Coverage:
        student = self.repo.get_student(student_id)
        sem = student.semester if student else 3
        courses = self.repo.list_courses(student_id, sem)
        records = self.repo.get_attendance_records(student_id)
        daily = self.repo.get_daily_attendance(student_id)
        assessments = self.repo.get_assessments(student_id)
        results = self.repo.get_semester_results(student_id)
        parts = self.repo.get_participations(student_id)
        decl = self.repo.get_engagement_declaration(student_id, "2026-27-ODD")

        return resolve_data_availability(
            student_semester=sem,
            courses=courses,
            attendance_records=records,
            daily_records=daily,
            assessments=assessments,
            semester_results=results,
            participations=parts,
            declaration=decl,
            policy=self._policy,
            scholarships=self._scholarships,
        )

    def get_support_signals(self, student_id: str) -> dict[str, Any]:
        student = self.repo.get_student(student_id)
        sem = student.semester if student else 3
        courses = {c.id: c for c in self.repo.list_courses(student_id, sem)}
        records = self.repo.get_attendance_records(student_id)
        assessments = self.repo.get_assessments(student_id)
        results = self.repo.get_semester_results(student_id)

        att_sig, att_reasons, att_meta = evaluate_attendance_signal(
            records=records,
            policy=self._policy,
            courses_by_id=courses,
        )

        acad_sig, acad_reasons, acad_meta = evaluate_academic_signal(
            assessments=assessments,
            semester_results=results,
            courses_by_id=courses,
            total_expected_courses=len(courses),
        )

        overall_sig, display_text, reasons = evaluate_overall_support_signal(
            att_sig, acad_sig, att_reasons, acad_reasons
        )

        eng_summary = self.get_engagement_summary(student_id)

        return {
            "attendanceSignal": att_sig,
            "academicSignal": acad_sig,
            "overallSupportSignal": overall_sig,
            "overallDisplayText": display_text,
            "reasons": reasons,
            "attendanceReasons": att_reasons,
            "academicReasons": acad_reasons,
            "attendanceMeta": att_meta,
            "academicMeta": acad_meta,
            "engagementSummary": eng_summary,
            "policy": self._policy,
        }

    def get_attested_facts(self, student_id: str) -> dict[str, Any]:
        return self.repo.get_attested_facts(student_id)

    def save_attested_fact(self, student_id: str, key: str, value: Any, attested_at: str):
        fact = UserAttestedFact(studentId=student_id, key=key, value=value, attestedAt=attested_at)
        self.repo.save_attested_fact(fact)

    def evaluate_scholarship(
        self,
        student_id: str,
        scheme_id: str,
        selected_track: str = "renewal",
        planned_remaining_classes: int = 30,
    ) -> dict[str, Any]:
        from edupulse.core.scholarship import evaluate_scholarship_scheme

        scheme = next((s for s in self._scholarships if s.schemeId == scheme_id), None)
        if not scheme:
            raise ValueError(f"Scholarship scheme '{scheme_id}' not found")

        student = self.repo.get_student(student_id)
        sem = student.semester if student else 3
        att_summary = self.get_attendance_summary(student_id, sem)
        results = self.repo.get_semester_results(student_id)
        attested_facts = self.repo.get_attested_facts(student_id)

        return evaluate_scholarship_scheme(
            scheme=scheme,
            selected_track=selected_track,
            overall_attendance_pct=att_summary["computedOverall"],
            total_present=att_summary["totalPresent"],
            total_classes=att_summary["totalClasses"],
            semester_results=results,
            attested_facts=attested_facts,
            planned_remaining_classes=planned_remaining_classes,
        )

    def get_scholarships(self) -> list[ScholarshipScheme]:
        return self._scholarships

    def get_available_personas(self) -> list[dict[str, Any]]:
        from edupulse.providers.mock import PERSONA_REGISTRY

        ordered_keys = [
            "student_synth_strong",
            "student_synth_att_concern",
            "student_synth_acad_concern",
            "student_synth_early",
            "student_synth_improving",
            "student_synth_eng",
            "student_s3",
        ]
        result = []
        for k in ordered_keys:
            if k in PERSONA_REGISTRY:
                result.append(PERSONA_REGISTRY[k])

        # Add any other students in database (e.g., imported)
        existing_ids = {p["id"] for p in result}
        for st in self.repo.list_students():
            if st.id not in existing_ids:
                result.append({
                    "id": st.id,
                    "scenario_key": "IMPORTED",
                    "name": st.name,
                    "archetype": "Imported Profile",
                    "provenance": "Imported data",
                    "icon": "📥",
                    "external_id": st.externalStudentId,
                    "program": st.program,
                    "semester": st.semester,
                    "academic_year": st.academicYear,
                    "description": "Custom self-supplied academic data imported via CSV/JSON or paste table.",
                    "badge_class": "badge-info",
                })
        return result

    def get_student_provenance(self, student_id: str) -> str:
        from edupulse.providers.mock import PERSONA_REGISTRY

        if student_id == "student_s3":
            return "Reference / Validation Data"
        if student_id in PERSONA_REGISTRY:
            return PERSONA_REGISTRY[student_id].get("provenance", "Demo data")
        if "import" in student_id.lower():
            return "Imported data"
        return "Demo data"

    def get_diagnostic_narrative(self, student_id: str) -> dict[str, Any]:
        """Provides an explainable summary answering WHAT was detected, WHY it was detected, and WHAT the student can do next."""
        signals = self.get_support_signals(student_id)
        student = self.repo.get_student(student_id)
        sem = student.semester if student else 3
        att_summary = self.get_attendance_summary(student_id, sem)
        policy = self.get_policy()

        acad_sig = signals["academicSignal"]
        overall_sig = signals["overallSupportSignal"]
        reasons = signals["reasons"]

        attention_components = [
            r for r in att_summary["records"]
            if r.computed_percentage is not None
            and r.computed_percentage < policy.attendancePerCoursePct
            and r.totalCount >= policy.smallSampleThreshold
        ]
        computed_att = att_summary["computedOverall"]

        # 1. WHAT WAS DETECTED
        what_parts = []
        if overall_sig.value == "Low":
            if computed_att and computed_att >= 85:
                what_parts.append(f"Exemplary attendance trajectory ({computed_att:.1f}%) and healthy academic standing.")
            else:
                what_parts.append("All attendance and academic indicators are currently within stable baseline ranges.")
        elif overall_sig.value == "High":
            if len(attention_components) >= 2 or (computed_att and computed_att < policy.attendanceOverallPct):
                what_parts.append(f"Critical attendance alerts across {len(attention_components)} subject components with overall attendance at {computed_att or 0:.1f}%.")
            if acad_sig.value == "High":
                what_parts.append("Academic attention areas detected with assessment scores below benchmark.")
            if not what_parts:
                what_parts.append(f"Support Signal escalated to {overall_sig.value} based on converging indicators.")
        elif overall_sig.value == "Moderate":
            what_parts.append("Moderate support signal detected requiring timely monitoring before upcoming assessments.")
        else:
            what_parts.append("Pre-assessment profile: Attendance data active while awaiting first assessment scores.")

        what_detected = " ".join(what_parts)

        # 2. WHY IT WAS DETECTED
        why_detected = []
        for r in reasons:
            direction_prefix = "Concern" if r.direction == "concern" else ("Positive" if r.direction == "positive" else "Info")
            why_detected.append(f"[{direction_prefix}] {r.indicator}: {r.value} (Source: {r.source})")

        if not why_detected:
            if computed_att:
                why_detected.append(f"Overall computed attendance is {computed_att:.1f}% vs {policy.attendanceOverallPct:.0f}% policy threshold.")
            why_detected.append("Subject marks and historical credits comply with active institutional standards.")

        # 3. WHAT THE STUDENT CAN DO NEXT
        what_to_do_next = []
        if attention_components:
            names = ", ".join(f"{r.courseId} ({r.component.value})" for r in attention_components[:3])
            what_to_do_next.append(f"Prioritize upcoming laboratory and lecture sessions in: {names}.")
            what_to_do_next.append("Open the Attendance Intelligence page to calculate exact consecutive classes needed to recover.")

        if acad_sig.value in ("High", "Moderate"):
            what_to_do_next.append("Schedule guidance with subject mentors to review midterm concepts.")
            what_to_do_next.append("Form a peer study circle or consult faculty during designated office hours.")

        if acad_sig.value == "Needs more data":
            what_to_do_next.append("Log your first midterm or quiz scores as soon as they are returned to activate academic diagnostics.")

        if overall_sig.value == "Low":
            what_to_do_next.append("Maintain your current attendance streak to preserve your buffer margin.")
            what_to_do_next.append("Explore hackathons or technical workshops in the Engagement Catalogue to build project leadership.")

        what_to_do_next.append("Check the Scholarship Readiness Planner to verify that renewal documentation is up to date.")

        return {
            "what_detected": what_detected,
            "why_detected": why_detected,
            "what_to_do_next": what_to_do_next,
        }

    def seed_all_personas(self, reset: bool = True):
        from edupulse.storage.seed import seed_all_demo_personas
        seed_all_demo_personas(reset=reset)

    def reset_to_scenario(self, scenario_id: str):
        seed_scenario_data(scenario_id, reset=True)

    def delete_all_data(self):
        reset_db()
