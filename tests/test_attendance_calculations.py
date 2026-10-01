from fractions import Fraction

from hypothesis import given, settings
from hypothesis import strategies as st

from edupulse.core.attendance import (
    aggregate_course_combined,
    calculate_attendance_ratio,
    calculate_attendance_recovery,
    calculate_attendance_trend,
    calculate_daily_attendance_counts,
    classify_attendance_band,
    compare_headline_with_computed,
)
from edupulse.domain.enums import (
    AttendanceBand,
    ComponentType,
    DailyAttendanceStatus,
    TrendDirection,
)
from edupulse.domain.models import AttendanceRecord, DailyAttendance


def test_calculate_attendance_ratio_exact_and_rounding():
    # 8/9 is 88.8888...% -> rounded to 88.9%, not truncated to 88%
    assert calculate_attendance_ratio(8, 9) == 88.9
    # 7/11 is 63.6363...% -> 63.6%
    assert calculate_attendance_ratio(7, 11) == 63.6
    # 14/15 is 93.333...% -> 93.3%
    assert calculate_attendance_ratio(14, 15) == 93.3
    # 0 total
    assert calculate_attendance_ratio(0, 0) is None


def test_compare_headline_with_computed():
    # Mismatch > 1 point
    note = compare_headline_with_computed(80.0, 76.5)
    assert note is not None
    assert "Source reports 80.0%" in note
    assert "computed from the visible rows 76.5%" in note

    # Match within 1 point
    assert compare_headline_with_computed(76.8, 76.5) is None
    assert compare_headline_with_computed(None, 76.5) is None


def test_attendance_recovery_reference_checks():
    # Reference 1: 70/100 @ 75% -> 20
    res1 = calculate_attendance_recovery(70, 100, 75.0)
    assert res1["classesNeeded"] == 20
    assert res1["resultingPercentage"] == 75.0

    # Reference 2: 8/14 @ 70% -> 6
    res2 = calculate_attendance_recovery(8, 14, 70.0)
    assert res2["classesNeeded"] == 6
    assert res2["resultingPercentage"] == 70.0

    # Reference 3: 7/11 @ 70% -> 3
    # With 3: (7+3)/(11+3) = 10/14 = 71.4% >= 70%
    # With 2: (7+2)/(11+2) = 9/13 = 69.2% < 70%
    res3 = calculate_attendance_recovery(7, 11, 70.0)
    assert res3["classesNeeded"] == 3
    assert res3["resultingPercentage"] == 71.4

    # Reference 4: 65/85 @ 75% -> 0 classes needed, and with R=30 max misses is 8
    res4 = calculate_attendance_recovery(65, 85, 75.0, remaining_classes=30)
    assert res4["classesNeeded"] == 0
    assert res4["maxMissesWithinRemaining"] == 8
    assert res4["isRecoverableWithinRemaining"] is True

    # 100% target check
    res_100_ok = calculate_attendance_recovery(10, 10, 100.0)
    assert res_100_ok["classesNeeded"] == 0
    assert res_100_ok["isPossible"] is True

    res_100_fail = calculate_attendance_recovery(9, 10, 100.0)
    assert res_100_fail["classesNeeded"] is None
    assert res_100_fail["isPossible"] is False


def test_attendance_recovery_unrecoverable_message():
    # 40/70 @ 75% with 10 remaining classes:
    # Need: (75*70 - 100*40) / (100 - 75) = (5250 - 4000)/25 = 1250/25 = 50 classes needed.
    # 50 > 10, so unrecoverable within 10 classes
    res = calculate_attendance_recovery(40, 70, 75.0, remaining_classes=10)
    assert res["classesNeeded"] == 50
    assert res["isRecoverableWithinRemaining"] is False
    assert "Cannot reach the target within the remaining 10 planned classes" in res["remainingMessage"]


def test_attendance_bands_and_early_data():
    # Component row with total < 8 is EARLY_DATA
    assert classify_attendance_band(50.0, 70.0, is_overall=False, total_classes=7) == AttendanceBand.EARLY_DATA
    assert classify_attendance_band(95.0, 70.0, is_overall=False, total_classes=5) == AttendanceBand.EARLY_DATA

    # Component row with total >= 8
    assert classify_attendance_band(69.9, 70.0, is_overall=False, total_classes=10) == AttendanceBand.ATTENTION
    assert classify_attendance_band(70.0, 70.0, is_overall=False, total_classes=10) == AttendanceBand.MONITOR
    assert classify_attendance_band(79.9, 70.0, is_overall=False, total_classes=10) == AttendanceBand.MONITOR
    assert classify_attendance_band(80.0, 70.0, is_overall=False, total_classes=10) == AttendanceBand.STRONG

    # Overall bands
    assert classify_attendance_band(74.9, 75.0, is_overall=True) == AttendanceBand.ATTENTION
    assert classify_attendance_band(75.0, 75.0, is_overall=True) == AttendanceBand.MONITOR
    assert classify_attendance_band(79.9, 75.0, is_overall=True) == AttendanceBand.MONITOR
    assert classify_attendance_band(80.0, 75.0, is_overall=True) == AttendanceBand.STRONG


def test_daily_attendance_counting_excludes_unmarked_and_nt():
    records = [
        DailyAttendance(studentId="s1", courseId="c1", date="2026-09-01", status=DailyAttendanceStatus.P),
        DailyAttendance(studentId="s1", courseId="c1", date="2026-09-02", status=DailyAttendanceStatus.P),
        DailyAttendance(studentId="s1", courseId="c1", date="2026-09-03", status=DailyAttendanceStatus.A),
        DailyAttendance(studentId="s1", courseId="c1", date="2026-09-04", status=DailyAttendanceStatus.NT),
        DailyAttendance(studentId="s1", courseId="c1", date="2026-09-05", status=DailyAttendanceStatus.UNMARKED),
    ]
    counts = calculate_daily_attendance_counts(records)
    assert counts["P"] == 2
    assert counts["A"] == 1
    assert counts["NT"] == 1
    assert counts["UNMARKED"] == 1
    assert counts["present"] == 2
    assert counts["total"] == 3  # strictly 2 P + 1 A, NT and UNMARKED excluded!


def test_aggregate_course_combined():
    records = [
        AttendanceRecord(
            studentId="s1", courseId="CSUC201", component=ComponentType.LECT,
            presentCount=28, totalCount=36, asOfDate="2026-09-30"
        ),
        AttendanceRecord(
            studentId="s1", courseId="CSUC201", component=ComponentType.LAB,
            presentCount=7, totalCount=11, asOfDate="2026-09-30"
        ),
    ]
    combined = aggregate_course_combined(records)
    c_data = combined["CSUC201"]
    assert c_data["present"] == 35
    assert c_data["total"] == 47
    # 35 / 47 = 74.468... -> 74.5%
    assert c_data["percentage"] == 74.5


def test_attendance_trend():
    assert calculate_attendance_trend([75.0])[0] == TrendDirection.NOT_AVAILABLE
    assert calculate_attendance_trend([72.0, 76.0])[0] == TrendDirection.IMPROVING
    assert calculate_attendance_trend([76.0, 72.0])[0] == TrendDirection.DECLINING
    assert calculate_attendance_trend([75.0, 76.0])[0] == TrendDirection.STABLE


# Property-based testing with Hypothesis for attendance recovery:
# (P+x)/(T+x) >= p and (P+x-1)/(T+x-1) < p when x > 0
@settings(max_examples=100)
@given(
    present=st.integers(min_value=0, max_value=200),
    additional=st.integers(min_value=0, max_value=200),
    target=st.integers(min_value=1, max_value=99),
)
def test_hypothesis_attendance_recovery_property(present: int, additional: int, target: int):
    total = present + additional
    if total == 0:
        return
    res = calculate_attendance_recovery(present, total, float(target))
    x = res["classesNeeded"]
    assert x is not None
    assert x >= 0

    p_frac = Fraction(target, 100)

    # 1. Resulting ratio must be >= target
    resulting_ratio = Fraction(present + x, total + x)
    assert resulting_ratio >= p_frac

    # 2. If x > 0, then attending x - 1 classes must fall strictly below target
    if x > 0:
        prev_ratio = Fraction(present + x - 1, total + x - 1)
        assert prev_ratio < p_frac
