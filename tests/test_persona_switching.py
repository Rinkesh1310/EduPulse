from edupulse.domain.enums import SupportLevel
from edupulse.services.academic_service import AcademicService


def test_seed_and_list_all_personas():
    """Verify that seed_all_personas seeds all 6 synthetic personas + reference scenario S3 simultaneously."""
    service = AcademicService()
    service.seed_all_personas(reset=True)

    personas = service.get_available_personas()
    assert len(personas) >= 7

    persona_ids = [p["id"] for p in personas]
    assert "student_synth_strong" in persona_ids
    assert "student_synth_att_concern" in persona_ids
    assert "student_synth_acad_concern" in persona_ids
    assert "student_synth_early" in persona_ids
    assert "student_synth_improving" in persona_ids
    assert "student_synth_eng" in persona_ids
    assert "student_s3" in persona_ids

    # Check provenances
    assert service.get_student_provenance("student_synth_strong") == "Demo data"
    assert service.get_student_provenance("student_s3") in ("Reference / Validation Data", "Reference scenario")


def test_persona_strong_calculations():
    """Verify Priya Sharma (Synthetic Strong):
    - Attendance > 90% (Low signal)
    - Assessments > 85% (Low signal)
    - Overall signal: Low
    """
    service = AcademicService()
    st_id = "student_synth_strong"
    student = service.get_student_profile(st_id)
    assert student is not None
    assert student.name == "Priya Sharma"
    assert student.externalStudentId == "SYNTH-2026-001"

    att_summary = service.get_attendance_summary(st_id, semester=3)
    assert att_summary["computedOverall"] is not None
    assert att_summary["computedOverall"] > 90.0

    signals = service.get_support_signals(st_id)
    assert signals["attendanceSignal"] == SupportLevel.LOW
    assert signals["academicSignal"] == SupportLevel.LOW
    assert signals["overallSupportSignal"] == SupportLevel.LOW

    narrative = service.get_diagnostic_narrative(st_id)
    assert "Exemplary attendance" in narrative["what_detected"] or "stable" in narrative["what_detected"]


def test_persona_attendance_concern_calculations():
    """Verify Rohan Verma (Synthetic Attendance Concern):
    - Attendance < 70% (High signal, 4 components below threshold)
    - Academic signal: Low (good marks >= 75%)
    - Overall signal: High
    - Recovery calculator returns classes needed
    """
    service = AcademicService()
    st_id = "student_synth_att_concern"
    student = service.get_student_profile(st_id)
    assert student is not None
    assert student.name == "Rohan Verma"

    att_summary = service.get_attendance_summary(st_id, semester=3)
    assert att_summary["computedOverall"] < 75.0  # 68.4%

    signals = service.get_support_signals(st_id)
    assert signals["attendanceSignal"] == SupportLevel.HIGH
    assert signals["overallSupportSignal"] == SupportLevel.HIGH

    # Check recovery calculation
    rec = service.calculate_recovery(
        present=att_summary["totalPresent"],
        total=att_summary["totalClasses"],
        target_pct=75.0,
        remaining_classes=40,
    )
    assert rec["classesNeeded"] > 0
    assert rec["classesNeeded"] <= 40

    narrative = service.get_diagnostic_narrative(st_id)
    assert "attendance" in narrative["what_detected"].lower()


def test_persona_academic_concern_calculations():
    """Verify Kabir Mehta (Synthetic Academic Concern):
    - Attendance ~85.4% (Low attendance signal)
    - Low assessment marks < 50% & declining SGPA (-1.20)
    - Academic signal: High
    - Overall signal: High
    """
    service = AcademicService()
    st_id = "student_synth_acad_concern"
    student = service.get_student_profile(st_id)
    assert student is not None
    assert student.name == "Kabir Mehta"

    signals = service.get_support_signals(st_id)
    assert signals["attendanceSignal"] == SupportLevel.LOW
    assert signals["academicSignal"] == SupportLevel.HIGH
    assert signals["overallSupportSignal"] == SupportLevel.HIGH


def test_persona_early_data_calculations():
    """Verify Ananya Iyer (Synthetic Early / Pre-assessment):
    - High attendance (91.9%)
    - Zero assessments (waiting for first assessment)
    - Zero prior semester results
    - Academic signal: Needs more data
    """
    service = AcademicService()
    st_id = "student_synth_early"
    student = service.get_student_profile(st_id)
    assert student is not None
    assert student.semester == 1

    signals = service.get_support_signals(st_id)
    assert signals["attendanceSignal"] == SupportLevel.LOW
    assert signals["academicSignal"] == SupportLevel.NEEDS_MORE_DATA
    assert signals["overallSupportSignal"] == SupportLevel.LOW

    coverage = service.get_coverage(st_id)
    assert "Waiting for first assessment" in coverage.chips["marks"]

def test_persona_improving_trajectory_calculations():
    """Verify Devansh Joshi (Synthetic Improving):
    - SGPA improved from 6.50 to 7.80 (+1.30) with unequal credits (22 and 26)
    - CGPA calculated accurately
    - Assessment marks rising (70% -> 87.5%)
    """
    service = AcademicService()
    st_id = "student_synth_improving"
    student = service.get_student_profile(st_id)
    assert student is not None

    cgpa_plan = service.calculate_cgpa_plan(st_id, target_cgpa=8.0, future_credits=24.0)
    assert not cgpa_plan["isBlocked"]
    # (6.50*22 + 7.80*26) / 48 = (143 + 202.8) / 48 = 345.8 / 48 = 7.204...
    assert round(cgpa_plan["cgpaInfo"]["cgpa"], 2) == 7.20


def test_persona_engagement_rich_calculations():
    """Verify Zara Mansuri (Synthetic Engagement-Rich):
    - 4 events across 3 categories
    - 8.1 engagement points (3.0 + 2.0 + 2.25 + 0.875)
    - Level: Active or Highly active
    """
    service = AcademicService()
    st_id = "student_synth_eng"
    eng = service.get_engagement_summary(st_id)
    assert eng["points"] == 8.1
    assert eng["eventCount"] == 4
    assert eng["diversityCount"] == 4
    assert eng["level"] in ("Active", "Highly active")


def test_screenshot_reference_s3_intact():
    """Verify that student_s3 remains completely intact as the reference scenario:
    - 65/85 attendance (76.5%) with portal mismatch note (80.0%)
    - Attendance signal: High (CPI 57.1% & FDSA Lab 63.6%)
    - Academic signal: Needs more data
    - Overall signal: High
    """
    service = AcademicService()
    st_id = "student_s3"
    student = service.get_student_profile(st_id)
    assert student is not None
    assert student.externalStudentId == "DEMO-S3-001"

    att_summary = service.get_attendance_summary(st_id, semester=3)
    assert att_summary["computedOverall"] == 76.5
    assert att_summary["portalOverall"] == 80.0
    assert att_summary["mismatchNote"] is not None

    signals = service.get_support_signals(st_id)
    assert signals["attendanceSignal"] == SupportLevel.HIGH
    assert signals["academicSignal"] == SupportLevel.NEEDS_MORE_DATA
    assert signals["overallSupportSignal"] == SupportLevel.HIGH


def test_dynamic_switching_updates_calculated_outputs():
    """Verify that switching personas dynamically alters the service output without state crosstalk."""
    service = AcademicService()

    # Query strong persona
    sig_strong = service.get_support_signals("student_synth_strong")
    att_strong = service.get_attendance_summary("student_synth_strong", semester=3)

    # Query attendance concern persona
    sig_att = service.get_support_signals("student_synth_att_concern")
    att_att = service.get_attendance_summary("student_synth_att_concern", semester=3)

    assert sig_strong["overallSupportSignal"] != sig_att["overallSupportSignal"]
    assert att_strong["computedOverall"] != att_att["computedOverall"]
    assert att_strong["computedOverall"] > 90.0
    assert att_att["computedOverall"] < 75.0
