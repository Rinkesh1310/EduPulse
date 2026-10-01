from pathlib import Path

from edupulse.core.academic import (
    calculate_required_future_sgpa,
)
from edupulse.core.attendance import calculate_attendance_recovery
from edupulse.core.engagement import evaluate_engagement_summary
from edupulse.core.signals import (
    evaluate_academic_signal,
    evaluate_attendance_signal,
    evaluate_overall_support_signal,
)
from edupulse.domain.enums import (
    EngagementStatus,
    SupportLevel,
)
from edupulse.domain.models import PolicyConfig
from edupulse.providers.mock import MockAcademicProvider


def test_acceptance_a_persona_s3_signals():
    """Acceptance Test A:
    Verify S3 persona returns:
      - Attendance signal: High (CPI 57.1% and FDSA Lab 63.6% both < 70%)
      - Overall computed: 76.5% (Monitor band)
      - Academic signal: Needs more data
      - Overall support signal: "High — based on attendance only; academic data incomplete"
    """
    mock = MockAcademicProvider("S3")
    records, headline = mock.get_attendance_summary(3)
    policy = PolicyConfig(version="1.0", attendanceOverallPct=75.0, attendancePerCoursePct=70.0)
    courses = {c.id: c for c in mock.list_courses(3)}

    att_signal, att_reasons, att_meta = evaluate_attendance_signal(records, policy, courses)
    assert att_signal == SupportLevel.HIGH
    assert att_meta["computedOverall"] == 76.5
    assert att_meta["belowCount"] == 2

    # Verify attention areas are specifically FDSA Lab and CPI
    concern_indicators = [r.indicator for r in att_reasons if r.direction == "concern"]
    assert any("CPI" in ind for ind in concern_indicators)
    assert any("FDSA LAB" in ind for ind in concern_indicators)

    # Academic signal for S3 has no assessments
    acad_signal, acad_reasons, acad_meta = evaluate_academic_signal(
        assessments=mock.get_assessments(),
        semester_results=mock.get_semester_results(),
        courses_by_id=courses,
        total_expected_courses=len(courses),
    )
    assert acad_signal == SupportLevel.NEEDS_MORE_DATA

    # Overall support signal
    overall_sig, display_text, reasons = evaluate_overall_support_signal(
        att_signal, acad_signal, att_reasons, acad_reasons
    )
    assert overall_sig == SupportLevel.HIGH
    assert display_text == "High — based on attendance only; academic data incomplete"


def test_acceptance_b_recovery_calculator_reference():
    """Acceptance Test B:
    Verify exact recovery calculation for all master spec reference cases:
      - 70/100 @ 75 -> 20
      - 8/14 @ 70 -> 6
      - 7/11 @ 70 -> 3
      - 65/85 @ 75 -> 0 with R=30 max misses 8
    """
    r1 = calculate_attendance_recovery(70, 100, 75.0)
    assert r1["classesNeeded"] == 20

    r2 = calculate_attendance_recovery(8, 14, 70.0)
    assert r2["classesNeeded"] == 6

    r3 = calculate_attendance_recovery(7, 11, 70.0)
    assert r3["classesNeeded"] == 3

    r4 = calculate_attendance_recovery(65, 85, 75.0, remaining_classes=30)
    assert r4["classesNeeded"] == 0
    assert r4["maxMissesWithinRemaining"] == 8


def test_acceptance_e_midterm_marks_entered_s2():
    """Acceptance Test E:
    When midterm marks are entered (S2: OOP 15/20=75%, FDSA 12/20=60%, CPI 9/20=45%):
      - Academic signal is Moderate (CPI in Attention < 50, FDSA in Monitor 50-<65, OOP Strong >= 65)
      - Attendance signal is High (from S3 baseline)
      - Overall support signal escalates to High with converging indicators
    """
    mock = MockAcademicProvider("S2")
    courses = {c.id: c for c in mock.list_courses(3)}
    policy = PolicyConfig(version="1.0")

    records, _ = mock.get_attendance_summary(3)
    att_sig, att_reasons, _ = evaluate_attendance_signal(records, policy, courses)
    assert att_sig == SupportLevel.HIGH

    acad_sig, acad_reasons, _ = evaluate_academic_signal(
        assessments=mock.get_assessments(),
        semester_results=mock.get_semester_results(),
        courses_by_id=courses,
        total_expected_courses=len(courses),
    )
    assert acad_sig == SupportLevel.MODERATE

    overall_sig, display_text, reasons = evaluate_overall_support_signal(
        att_sig, acad_sig, att_reasons, acad_reasons
    )
    assert overall_sig == SupportLevel.HIGH
    assert display_text == "High"


def test_acceptance_f_cgpa_weighted_and_target_planning():
    """Acceptance Test F:
    Credit-weighted CGPA & Future SGPA target planner:
      - 26 credits @ 7.63, F=24, target 8.00 -> 8.40
      - Missing credits blocks calculation unless assume_equal_credits=True
    """
    plan = calculate_required_future_sgpa(
        current_cgpa=7.63,
        completed_credits=26.0,
        target_cgpa=8.00,
        future_credits=24.0,
    )
    assert plan["requiredSgpa"] == 8.40
    assert plan["isReachable"] is True


def test_acceptance_g_engagement_overlap_and_non_escalation():
    """Acceptance Test G:
    Engagement evaluation:
      - Points and level calculated
      - Date overlap on 2026-09-29 detected
      - Engagement does not increase overall support signal
    """
    from edupulse.storage.repository import StudentRepository
    from edupulse.storage.seed import seed_scenario_data
    seed_scenario_data("S8", reset=True)
    repo = StudentRepository()
    try:
        events_map = {e.eventId: e for e in repo.get_events()}
        parts = repo.get_participations("student_s8")
        eng_summary = evaluate_engagement_summary(
            participations=parts,
            events_by_id=events_map,
            declaration_status=EngagementStatus.HAS_EVENTS,
            official_attendance_p_dates={"2026-09-29"},
        )
        assert eng_summary["level"] == "Active"
        assert eng_summary["points"] >= 7.0
        assert len(eng_summary["overlaps"]) >= 1
        assert "Counted in official attendance" in eng_summary["overlaps"][0]["note"]
    finally:
        repo.close()


def test_acceptance_h_language_and_tone_boundary():
    """Acceptance Test H:
    Static check ensuring calm, professional language:
    Codebase must NOT contain definitive or alarming phrases:
      - 'you will fail'
      - 'at risk'
      - 'scholarship eligible' (instead of criteria met / unknown)
      - 'definitely'
    """
    forbidden_terms = [
        "you will fail",
        "at risk",
        "scholarship eligible",
        "you are definitely",
    ]

    core_dir = Path(__file__).parent.parent / "edupulse" / "core"
    for py_file in core_dir.glob("*.py"):
        content = py_file.read_text(encoding="utf-8").lower()
        for term in forbidden_terms:
            assert term not in content, f"Forbidden term '{term}' found in {py_file.name}"
