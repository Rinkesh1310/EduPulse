
from edupulse.domain.enums import AcademicBand, TrendDirection
from edupulse.domain.models import Assessment, SemesterResult


def calculate_subject_marks_percentage(assessments: list[Assessment]) -> float | None:
    """Calculates subject percentage as sum(obtained) / sum(total).
    NEVER the average of percentages!
    Returns None if no assessments or sum(total) == 0.
    """
    if not assessments:
        return None
    tot_obtained = sum(a.obtainedMarks for a in assessments)
    tot_marks = sum(a.totalMarks for a in assessments)
    if tot_marks <= 0:
        return None
    return round((tot_obtained / tot_marks) * 100.0, 1)


def classify_academic_band(
    percentage: float | None,
    attention_max: float = 50.0,
    monitor_max: float = 65.0,
) -> AcademicBand | None:
    """Classifies subject marks percentage into Strong, Monitor, or Attention area."""
    if percentage is None:
        return None
    if percentage < attention_max:
        return AcademicBand.ATTENTION
    elif percentage < monitor_max:
        return AcademicBand.MONITOR
    else:
        return AcademicBand.STRONG


def calculate_assessment_trend(
    assessments: list[Assessment],
    threshold_diff: float = 10.0,
) -> tuple[TrendDirection, float | None, bool]:
    """Calculates chronological assessment trend for a subject.
    Requires >= 2 assessments.
    Returns (trend_direction, delta_percentage_points, is_early_indication).
    """
    if len(assessments) < 2:
        return TrendDirection.NOT_AVAILABLE, None, False

    # Sort chronologically by date
    sorted_ass = sorted(assessments, key=lambda a: a.date)
    p_first = sorted_ass[0].percentage
    p_last = sorted_ass[-1].percentage
    delta = p_last - p_first
    is_early = len(sorted_ass) == 2

    if delta >= threshold_diff:
        return TrendDirection.IMPROVING, round(delta, 1), is_early
    elif delta <= -threshold_diff:
        return TrendDirection.DECLINING, round(delta, 1), is_early
    else:
        return TrendDirection.STABLE, round(delta, 1), is_early


def calculate_sgpa_trend(
    semester_results: list[SemesterResult],
    threshold_diff: float = 0.3,
) -> tuple[TrendDirection, float | None]:
    """Calculates SGPA trend across published semesters.
    Requires >= 2 published semesters.
    Returns (trend_direction, delta_sgpa).
    """
    if len(semester_results) < 2:
        return TrendDirection.NOT_ENOUGH_HISTORY, None

    sorted_results = sorted(semester_results, key=lambda r: r.semester)
    sgpa_prev = sorted_results[-2].sgpa
    sgpa_last = sorted_results[-1].sgpa
    delta = sgpa_last - sgpa_prev

    if delta >= threshold_diff:
        return TrendDirection.IMPROVING, round(delta, 2)
    elif delta <= -threshold_diff:
        return TrendDirection.DECLINING, round(delta, 2)
    else:
        return TrendDirection.STABLE, round(delta, 2)


def calculate_credit_weighted_cgpa(
    semester_results: list[SemesterResult],
    assume_equal_credits: bool = False,
) -> dict[str, object | None]:
    """Calculates credit-weighted CGPA over supplied semesters.
    CGPA = sum(SGPA_i * Credits_i) / sum(Credits_i)
    
    If credits are not complete for any semester, calculation is blocked unless
    assume_equal_credits is explicitly True.
    """
    if not semester_results:
        return {
            "cgpa": None,
            "totalCredits": 0.0,
            "isEstimate": False,
            "isBlocked": False,
            "message": "No published semester results supplied",
        }

    # Verify if credits are known for each semester
    missing_credits_semesters = []
    total_weighted_points = 0.0
    total_credits = 0.0
    sgpas = []

    for r in semester_results:
        sgpas.append(r.sgpa)
        # Semester credits either declared on result or sum of course credits
        c_val = r.totalCreditsDeclared
        if c_val is None and r.courses:
            c_val = sum(c.credits for c in r.courses)

        if c_val is None or c_val <= 0:
            missing_credits_semesters.append(r.semester)
        else:
            total_weighted_points += r.sgpa * c_val
            total_credits += c_val

    if missing_credits_semesters:
        if assume_equal_credits:
            # Fall back to unweighted average with explicit assumption
            avg_sgpa = round(sum(sgpas) / len(sgpas), 2)
            return {
                "cgpa": avg_sgpa,
                "totalCredits": None,
                "isEstimate": True,
                "isBlocked": False,
                "assumedEqualCredits": True,
                "label": "CGPA over supplied semesters (estimate: assumes equal credits) — official CGPA rules may differ",
            }
        else:
            return {
                "cgpa": None,
                "totalCredits": None,
                "isEstimate": False,
                "isBlocked": True,
                "missingSemesters": missing_credits_semesters,
                "message": (
                    f"Credits incomplete for Semester {missing_credits_semesters}. "
                    "Please enter total credits to calculate exact credit-weighted CGPA, "
                    "or confirm 'assume equal credits' assumption."
                ),
            }

    computed_cgpa = round(total_weighted_points / total_credits, 2)
    return {
        "cgpa": computed_cgpa,
        "totalCredits": total_credits,
        "isEstimate": True,
        "isBlocked": False,
        "assumedEqualCredits": False,
        "label": "CGPA over supplied semesters (estimate) — official CGPA rules may differ",
    }


def calculate_required_future_sgpa(
    current_cgpa: float,
    completed_credits: float,
    target_cgpa: float,
    future_credits: float,
    max_scale: float = 10.0,
) -> dict[str, object | None]:
    """Calculates the SGPA required in future semester(s) to reach target CGPA.
    
    Formula:
        S_req = (G* * (C + F) - G * C) / F
    
    If S_req > max_scale (default 10.0):
        Not reachable in one semester. Computes max achievable CGPA: (G*C + 10*F)/(C+F)
    If S_req <= 0:
        Already secured for this target.
    """
    if completed_credits <= 0 or future_credits <= 0:
        raise ValueError("Credits must be greater than zero")

    total_credits = completed_credits + future_credits
    num = target_cgpa * total_credits - current_cgpa * completed_credits
    s_req = num / future_credits

    max_achievable = round(
        (current_cgpa * completed_credits + max_scale * future_credits) / total_credits, 2
    )

    if s_req <= 0:
        return {
            "requiredSgpa": 0.0,
            "isReachable": True,
            "status": "already_secured",
            "message": f"Target CGPA {target_cgpa:.2f} is already secured even with 0.00 SGPA in future credits.",
            "maxAchievable": max_achievable,
        }
    elif s_req > max_scale:
        return {
            "requiredSgpa": round(s_req, 2),
            "isReachable": False,
            "status": "not_reachable_single_semester",
            "message": (
                f"Target CGPA {target_cgpa:.2f} requires SGPA {s_req:.2f}, which exceeds the maximum scale {max_scale:.1f}. "
                f"Maximum achievable CGPA in this term is {max_achievable:.2f}."
            ),
            "maxAchievable": max_achievable,
        }
    else:
        return {
            "requiredSgpa": round(s_req, 2),
            "isReachable": True,
            "status": "reachable",
            "message": f"Required SGPA in the next {future_credits:.0f} credits is {round(s_req, 2):.2f}.",
            "maxAchievable": max_achievable,
        }
