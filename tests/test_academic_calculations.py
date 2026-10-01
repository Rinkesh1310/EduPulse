from edupulse.core.academic import (
    calculate_assessment_trend,
    calculate_credit_weighted_cgpa,
    calculate_required_future_sgpa,
    calculate_sgpa_trend,
    calculate_subject_marks_percentage,
    classify_academic_band,
)
from edupulse.domain.enums import AcademicBand, TrendDirection
from edupulse.domain.models import Assessment, SemesterResult


def test_subject_marks_is_sum_not_average_of_percentages():
    # Assessment 1: 10/10 (100%)
    # Assessment 2: 10/40 (25%)
    # Average of percentages would be (100 + 25) / 2 = 62.5%
    # Actual sum(obtained)/sum(total) is (10 + 10) / (10 + 40) = 20 / 50 = 40.0%
    assessments = [
        Assessment(id="a1", studentId="s1", courseId="c1", type="Quiz", date="2026-08-01", obtainedMarks=10.0, totalMarks=10.0),
        Assessment(id="a2", studentId="s1", courseId="c1", type="Exam", date="2026-09-01", obtainedMarks=10.0, totalMarks=40.0),
    ]
    pct = calculate_subject_marks_percentage(assessments)
    assert pct == 40.0
    assert pct != 62.5


def test_academic_bands():
    assert classify_academic_band(49.9) == AcademicBand.ATTENTION
    assert classify_academic_band(50.0) == AcademicBand.MONITOR
    assert classify_academic_band(64.9) == AcademicBand.MONITOR
    assert classify_academic_band(65.0) == AcademicBand.STRONG
    assert classify_academic_band(None) is None


def test_assessment_trend():
    # Only 1 assessment
    ass_single = [
        Assessment(id="a1", studentId="s1", courseId="c1", type="Quiz", date="2026-08-01", obtainedMarks=15.0, totalMarks=20.0),
    ]
    assert calculate_assessment_trend(ass_single)[0] == TrendDirection.NOT_AVAILABLE

    # 2 assessments: improving by >= 10 points with is_early_indication True
    # Ass 1: 10/20 = 50%, Ass 2: 15/20 = 75% -> delta +25%
    ass_improving = [
        Assessment(id="a1", studentId="s1", courseId="c1", type="Quiz 1", date="2026-08-01", obtainedMarks=10.0, totalMarks=20.0),
        Assessment(id="a2", studentId="s1", courseId="c1", type="Quiz 2", date="2026-09-01", obtainedMarks=15.0, totalMarks=20.0),
    ]
    dir_imp, delta_imp, is_early = calculate_assessment_trend(ass_improving)
    assert dir_imp == TrendDirection.IMPROVING
    assert delta_imp == 25.0
    assert is_early is True

    # Declining
    ass_declining = [
        Assessment(id="a1", studentId="s1", courseId="c1", type="Quiz 1", date="2026-08-01", obtainedMarks=18.0, totalMarks=20.0),
        Assessment(id="a2", studentId="s1", courseId="c1", type="Quiz 2", date="2026-09-01", obtainedMarks=10.0, totalMarks=20.0),
    ]
    dir_dec, delta_dec, _ = calculate_assessment_trend(ass_declining)
    assert dir_dec == TrendDirection.DECLINING
    assert delta_dec == -40.0


def test_sgpa_trend():
    # Single semester
    res_single = [SemesterResult(studentId="s1", semester=1, monthYear="Dec 2025", sgpa=7.63)]
    assert calculate_sgpa_trend(res_single)[0] == TrendDirection.NOT_ENOUGH_HISTORY

    # Two semesters: improving (7.20 -> 7.60 = +0.40 >= +0.30)
    res_imp = [
        SemesterResult(studentId="s1", semester=1, monthYear="Dec 2024", sgpa=7.20),
        SemesterResult(studentId="s1", semester=2, monthYear="May 2025", sgpa=7.60),
    ]
    dir_imp, delta = calculate_sgpa_trend(res_imp)
    assert dir_imp == TrendDirection.IMPROVING
    assert delta == 0.40

    # Declining (7.80 -> 7.40 = -0.40 <= -0.30)
    res_dec = [
        SemesterResult(studentId="s1", semester=1, monthYear="Dec 2024", sgpa=7.80),
        SemesterResult(studentId="s1", semester=2, monthYear="May 2025", sgpa=7.40),
    ]
    dir_dec, delta = calculate_sgpa_trend(res_dec)
    assert dir_dec == TrendDirection.DECLINING
    assert delta == -0.40


def test_credit_weighted_cgpa_and_future_sgpa_planning():
    # Illustrative specification example: 26 credits @ 7.63, F=24, target 8.00 -> 8.40
    # CGPA calculation with complete credits
    sem1 = SemesterResult(
        studentId="s1", semester=1, monthYear="Dec 2025", sgpa=7.63,
        creditsComplete=True, totalCreditsDeclared=26.0
    )
    cgpa_res = calculate_credit_weighted_cgpa([sem1])
    assert cgpa_res["cgpa"] == 7.63
    assert cgpa_res["isBlocked"] is False

    # Required future SGPA for target 8.00 with F=24
    plan = calculate_required_future_sgpa(
        current_cgpa=7.63,
        completed_credits=26.0,
        target_cgpa=8.00,
        future_credits=24.0,
    )
    assert plan["requiredSgpa"] == 8.40
    assert plan["isReachable"] is True

    # Target already secured: target 7.00 when current is 8.00 with 20 credits and F=2
    # 7.0*(22) - 8.0*20 = 154 - 160 = -6 -> s_req <= 0
    secured_plan = calculate_required_future_sgpa(
        current_cgpa=8.00,
        completed_credits=20.0,
        target_cgpa=7.00,
        future_credits=2.0,
    )
    assert secured_plan["status"] == "already_secured"
    assert secured_plan["isReachable"] is True

    # Unreachable in single semester: target 9.50 when current is 6.00 with 50 credits, F=20
    # 9.50*70 - 6.0*50 = 665 - 300 = 365 / 20 = 18.25 > 10.0
    unreach_plan = calculate_required_future_sgpa(
        current_cgpa=6.00,
        completed_credits=50.0,
        target_cgpa=9.50,
        future_credits=20.0,
    )
    assert unreach_plan["status"] == "not_reachable_single_semester"
    assert unreach_plan["isReachable"] is False
    assert unreach_plan["maxAchievable"] == round((6.0 * 50 + 10.0 * 20) / 70.0, 2)


def test_cgpa_blocked_when_credits_missing_unless_explicitly_assumed():
    sem_incomplete = SemesterResult(
        studentId="s1", semester=1, monthYear="Dec 2025", sgpa=7.63,
        creditsComplete=False, totalCreditsDeclared=None
    )
    blocked_res = calculate_credit_weighted_cgpa([sem_incomplete], assume_equal_credits=False)
    assert blocked_res["isBlocked"] is True
    assert "Credits incomplete" in blocked_res["message"]

    unblocked_res = calculate_credit_weighted_cgpa([sem_incomplete], assume_equal_credits=True)
    assert unblocked_res["isBlocked"] is False
    assert unblocked_res["cgpa"] == 7.63
    assert unblocked_res["assumedEqualCredits"] is True
