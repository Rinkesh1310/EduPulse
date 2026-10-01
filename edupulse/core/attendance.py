import math
from fractions import Fraction

from edupulse.domain.enums import AttendanceBand, DailyAttendanceStatus, TrendDirection
from edupulse.domain.models import AttendanceRecord, DailyAttendance


def calculate_attendance_ratio(present: int, total: int) -> float | None:
    """Calculates exact attendance ratio formatted to 1 decimal place.
    Returns None if total is 0.
    """
    if total <= 0:
        return None
    return round((present / total) * 100.0, 1)


def compare_headline_with_computed(
    portal_reported_overall: float | None,
    computed_overall: float | None,
    threshold: float = 1.0,
) -> str | None:
    """Checks for headline mismatch between portal reported percentage and computed percentage.
    If |portalReportedOverall - computed overall| > threshold, returns neutral note.
    Never overwrites either value.
    """
    if portal_reported_overall is None or computed_overall is None:
        return None
    diff = abs(portal_reported_overall - computed_overall)
    if diff > threshold:
        return (
            f"Source reports {portal_reported_overall:.1f}%; "
            f"computed from the visible rows {computed_overall:.1f}%"
        )
    return None


def calculate_attendance_recovery(
    present: int,
    total: int,
    target_pct: float,
    remaining_classes: int | None = None,
) -> dict[str, object | None]:
    """Calculates recovery classes needed using exact integer/Fraction arithmetic.
    
    Formula:
        x = max(0, ceil((p*T - 100*P) / (100 - p))) for p < 100.
        For p = 100: x = 0 if P == T else impossible (None).
        
    Buffer (when 100*P >= p*T):
        m = floor((100*P - p*T) / p)
        
    With remaining classes R:
        recoverable iff x <= R; else "Cannot reach the target within the remaining R planned classes"
        Max misses within R: floor((100*(P+R) - p*(T+R)) / 100)
    """
    if total < 0 or present < 0 or present > total:
        raise ValueError("Invalid attendance counts")

    target_frac = Fraction(str(target_pct))
    if target_frac < 0 or target_frac > 100:
        raise ValueError("target_pct must be between 0 and 100")

    p = target_frac

    # 100% target special case
    if p == 100:
        if present == total:
            classes_needed = 0
            is_possible = True
        else:
            classes_needed = None
            is_possible = False
    else:
        # p < 100
        num = p * total - 100 * present
        denom = 100 - p
        if num <= 0:
            classes_needed = 0
        else:
            # ceil(num / denom) with Fraction
            div_val = num / denom
            classes_needed = math.ceil(div_val)
        is_possible = True

    # Resulting percentage if attended x classes
    resulting_pct = None
    if classes_needed is not None:
        new_p = present + classes_needed
        new_t = total + classes_needed
        resulting_pct = round(float(Fraction(new_p, new_t) * 100), 1)

    # Buffer: classes that could be missed before dropping below target
    buffer_classes = 0
    if 100 * present >= p * total and p > 0:
        buffer_classes = math.floor((100 * present - p * total) / p)
    elif p == 0:
        buffer_classes = 999999

    # Remaining classes feasibility
    is_recoverable_within_remaining = True
    max_misses_within_remaining = None
    remaining_message = None

    if remaining_classes is not None:
        if remaining_classes < 0:
            raise ValueError("remaining_classes cannot be negative")

        if classes_needed is None or classes_needed > remaining_classes:
            is_recoverable_within_remaining = False
            remaining_message = f"Cannot reach the target within the remaining {remaining_classes} planned classes"
        else:
            is_recoverable_within_remaining = True
            # Max misses within R: floor((100(P+R) - p(T+R)) / 100)
            misses_num = 100 * (present + remaining_classes) - p * (total + remaining_classes)
            max_misses_within_remaining = max(0, math.floor(misses_num / 100))

    return {
        "classesNeeded": classes_needed,
        "resultingPercentage": resulting_pct,
        "isPossible": is_possible,
        "bufferClasses": buffer_classes,
        "isRecoverableWithinRemaining": is_recoverable_within_remaining,
        "maxMissesWithinRemaining": max_misses_within_remaining,
        "remainingMessage": remaining_message,
        "notice": "Any future absence changes this.",
    }


def classify_attendance_band(
    percentage: float | None,
    threshold: float,
    is_overall: bool = False,
    total_classes: int | None = None,
    small_sample_threshold: int = 8,
) -> AttendanceBand:
    """Classifies an attendance percentage into Strong, Monitor, Attention area, or Early data."""
    if total_classes is not None and total_classes < small_sample_threshold:
        return AttendanceBand.EARLY_DATA

    if percentage is None:
        return AttendanceBand.EARLY_DATA

    if is_overall:
        # Overall: Attention < 75; Monitor 75 to <80; Strong >= 80
        if percentage < 75.0:
            return AttendanceBand.ATTENTION
        elif percentage < 80.0:
            return AttendanceBand.MONITOR
        else:
            return AttendanceBand.STRONG
    else:
        # Per-course/component: Attention < threshold; Monitor threshold to threshold+10; Strong >= threshold+10
        if percentage < threshold:
            return AttendanceBand.ATTENTION
        elif percentage < threshold + 10.0:
            return AttendanceBand.MONITOR
        else:
            return AttendanceBand.STRONG


def aggregate_course_combined(
    records: list[AttendanceRecord],
) -> dict[str, dict[str, object]]:
    """Aggregates component attendance rows (LECT, LAB, OTHER) into course-combined figures.
    Returns a mapping of courseId -> {present, total, percentage, records}.
    """
    course_groups: dict[str, dict[str, object]] = {}
    for r in records:
        if r.courseId not in course_groups:
            course_groups[r.courseId] = {
                "courseId": r.courseId,
                "present": 0,
                "total": 0,
                "records": [],
            }
        course_groups[r.courseId]["present"] += r.presentCount
        course_groups[r.courseId]["total"] += r.totalCount
        course_groups[r.courseId]["records"].append(r)

    for c_id, data in course_groups.items():
        tot = data["total"]
        pres = data["present"]
        data["percentage"] = calculate_attendance_ratio(pres, tot)

    return course_groups


def calculate_daily_attendance_counts(
    daily_records: list[DailyAttendance],
) -> dict[str, int]:
    """Tallies daily attendance records according to university rules:
    - P: counts as present and total
    - A: counts as absent and total
    - NT (Not Taught) and UNMARKED ('-'): strictly excluded from totals.
    """
    counts = {"P": 0, "A": 0, "NT": 0, "UNMARKED": 0, "present": 0, "total": 0}
    for rec in daily_records:
        status_val = rec.status
        if status_val == DailyAttendanceStatus.P:
            counts["P"] += 1
            counts["present"] += 1
            counts["total"] += 1
        elif status_val == DailyAttendanceStatus.A:
            counts["A"] += 1
            counts["total"] += 1
        elif status_val == DailyAttendanceStatus.NT:
            counts["NT"] += 1
        elif status_val == DailyAttendanceStatus.UNMARKED:
            counts["UNMARKED"] += 1
    return counts


def calculate_attendance_trend(
    points: list[float],
    threshold_diff: float = 3.0,
) -> tuple[TrendDirection, float | None]:
    """Calculates attendance trend from chronological percentage points.
    Requires >= 2 points, else TrendDirection.NOT_AVAILABLE.
    Delta = last - previous.
    """
    if len(points) < 2:
        return TrendDirection.NOT_AVAILABLE, None
    delta = points[-1] - points[0]
    if delta >= threshold_diff:
        return TrendDirection.IMPROVING, round(delta, 1)
    elif delta <= -threshold_diff:
        return TrendDirection.DECLINING, round(delta, 1)
    else:
        return TrendDirection.STABLE, round(delta, 1)
