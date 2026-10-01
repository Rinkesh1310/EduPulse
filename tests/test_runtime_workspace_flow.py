from datetime import datetime

from edupulse.domain.enums import SupportLevel
from edupulse.services.academic_service import AcademicService


def test_runtime_workspace_full_lifecycle_a_to_k():
    """Automated verification flow proving Steps A through K:

    A. Initial student data
    B. Enter marks
    C. Submit / save
    D. Analytics change
    E. Select activities
    F. Engagement changes (while attendance/support remains independent)
    G. Open Success Explorer / calculate signals
    H. Change marks again
    I. Explorer recalculates again
    J. Switch student / scenario
    K. Complete dashboard / signals change accordingly
    """
    service = AcademicService()
    service.seed_all_personas(reset=True)

    # -------------------------------------------------------------
    # Step A: Initial student data (Priya Sharma - Strong)
    # -------------------------------------------------------------
    student_id = "student_synth_strong"
    initial_record = service.get_student_academic_record(student_id)
    student = initial_record["student"]
    assert student is not None
    assert student.name == "Priya Sharma"
    assert student.program == "B.Tech Computer Science (Synthetic)"
    assert student.semester == 3
    assert initial_record["provenance"] == "Demo data"
    assert "Assessment In Progress" in initial_record["academicStatus"]

    init_signals = service.get_support_signals(student_id)
    assert init_signals["attendanceSignal"].value == "Low"
    assert init_signals["academicSignal"].value == "Low"
    assert init_signals["overallSupportSignal"].value == "Low"
    init_eng = init_signals["engagementSummary"]
    init_points = init_eng["points"]

    # -------------------------------------------------------------
    # Step B & C & D: Enter marks, Submit, Analytics change
    # -------------------------------------------------------------
    courses = service.list_courses(student_id, semester=3)
    assert len(courses) >= 3

    # Enter low marks (<50%) for courses (e.g. OOP 8/20, FDSA 9/20, CPI 7/20)
    for c in courses:
        service.save_or_update_course_assessment(
            student_id=student_id,
            course_id=c.id,
            ass_type="Midterm",
            obtained_marks=8.0,
            total_marks=20.0,
            date="2026-09-22",
            term="T1",
        )

    # Verify analytics have changed
    updated_signals = service.get_support_signals(student_id)
    assert updated_signals["academicSignal"].value == "High"
    assert updated_signals["overallSupportSignal"].value == "High"
    # Verify reasons contain academic concerns
    reasons_text = " ".join(r.indicator for r in updated_signals["reasons"]).lower()
    assert "marks" in reasons_text or "academic" in reasons_text or "score" in reasons_text

    # -------------------------------------------------------------
    # Step E & F: Select activities, Engagement changes independently
    # -------------------------------------------------------------
    all_events = service.get_events()
    assert len(all_events) > 0
    test_event = all_events[0]

    # Confirm participation in an additional event
    service.toggle_event_participation(
        student_id=student_id,
        event_id=test_event.eventId,
        confirmed=True,
        confirmation_date=datetime.now().strftime("%Y-%m-%d"),
    )

    new_eng_summary = service.get_engagement_summary(student_id)
    assert new_eng_summary["points"] >= init_points
    assert new_eng_summary["eventCount"] >= 1

    # Verify engagement change did NOT alter the academic or attendance signal
    signals_after_eng = service.get_support_signals(student_id)
    assert signals_after_eng["academicSignal"].value == "High"
    assert signals_after_eng["attendanceSignal"].value == "Low"
    assert signals_after_eng["overallSupportSignal"].value == "High"

    # -------------------------------------------------------------
    # Step G & H & I: Open Success Explorer, Change marks again, Recalculate
    # -------------------------------------------------------------
    # Student improves marks to high score (>85%)
    for c in courses:
        service.save_or_update_course_assessment(
            student_id=student_id,
            course_id=c.id,
            ass_type="Midterm",
            obtained_marks=19.0,
            total_marks=20.0,
            date="2026-09-28",
            term="T1",
        )

    recovered_signals = service.get_support_signals(student_id)
    assert recovered_signals["academicSignal"].value == "Low"
    assert recovered_signals["overallSupportSignal"].value == "Low"

    # -------------------------------------------------------------
    # Step J & K: Switch student/scenario, Dashboard changes accordingly
    # -------------------------------------------------------------
    # 1. Switch to Attendance Concern persona
    att_student_id = "student_synth_att_concern"
    att_signals = service.get_support_signals(att_student_id)
    assert att_signals["attendanceSignal"].value == "High"
    assert att_signals["overallSupportSignal"].value == "High"

    # 2. Switch to Early Semester 1 persona (no assessments yet)
    early_student_id = "student_synth_early"
    early_record = service.get_student_academic_record(early_student_id)
    assert early_record["student"].semester == 1
    early_signals = service.get_support_signals(early_student_id)
    # Missing assessment keeps academic analysis unavailable
    assert early_signals["academicSignal"].value == SupportLevel.NEEDS_MORE_DATA.value
    # Missing data is NOT converted to 0.0
    for c in early_record["courses"]:
        assert c["hasAssessment"] is False
        assert len(c["assessments"]) == 0

    # 3. Switch to Reference Validation persona
    ref_student_id = "student_s3"
    ref_record = service.get_student_academic_record(ref_student_id)
    assert ref_record["provenance"] == "Reference / Validation Data"
    assert ref_record["attendanceSummary"]["mismatchNote"] is not None


def test_missing_data_integrity_and_zero_prevention():
    """Verify that absent marks/records remain None/empty and are never cast to zero."""
    service = AcademicService()
    service.seed_all_personas(reset=False)

    record = service.get_student_academic_record("student_synth_early")
    courses = record["courses"]
    for c in courses:
        assert c["hasAssessment"] is False
        assert len(c["assessments"]) == 0

    signals = service.get_support_signals("student_synth_early")
    assert signals["academicSignal"] == SupportLevel.NEEDS_MORE_DATA
    # Overall signal defaults to attendance signal when academic needs data
    assert signals["overallSupportSignal"] == SupportLevel.LOW


def test_attendance_and_engagement_independence():
    """Verify that engagement changes never artificially raise or suppress attendance or support signals."""
    service = AcademicService()
    service.seed_all_personas(reset=False)

    student_id = "student_synth_strong"
    base_signals = service.get_support_signals(student_id)
    base_att = base_signals["attendanceSignal"]
    base_overall = base_signals["overallSupportSignal"]

    # Toggle off all events
    parts = service.get_participations(student_id)
    for p in parts:
        service.toggle_event_participation(student_id, p.eventId, confirmed=False, confirmation_date="")

    signals_no_eng = service.get_support_signals(student_id)
    assert signals_no_eng["attendanceSignal"] == base_att
    assert signals_no_eng["overallSupportSignal"] == base_overall
    assert signals_no_eng["engagementSummary"]["points"] == 0.0
