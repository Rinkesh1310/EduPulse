from typing import Any

from edupulse.core.academic import (
    calculate_assessment_trend,
    calculate_sgpa_trend,
    calculate_subject_marks_percentage,
    classify_academic_band,
)
from edupulse.core.attendance import (
    calculate_attendance_ratio,
    classify_attendance_band,
)
from edupulse.domain.enums import (
    AcademicBand,
    AttendanceBand,
    SupportLevel,
    TrendDirection,
)
from edupulse.domain.models import (
    Assessment,
    AttendanceRecord,
    Course,
    PolicyConfig,
    SemesterResult,
    SignalReason,
)


def evaluate_attendance_signal(
    records: list[AttendanceRecord],
    policy: PolicyConfig,
    courses_by_id: dict[str, Course] | None = None,
) -> tuple[SupportLevel, list[SignalReason], dict[str, Any]]:
    """Evaluates attendance support signal.
    
    Rules:
      - High: overall < overall threshold (75) OR >= 2 components below per-course threshold (70) (excluding 'Early data')
      - Moderate: exactly 1 component below threshold OR overall in Monitor band (75 to <80)
      - Low: otherwise
      - Needs more data: no attendance records
    """
    reasons: list[SignalReason] = []
    c_map = courses_by_id or {}

    if not records:
        reasons.append(
            SignalReason(
                indicator="Attendance Records",
                value="No records",
                direction="info",
                source="Attendance Module",
            )
        )
        return SupportLevel.NEEDS_MORE_DATA, reasons, {"computedOverall": None, "belowCount": 0}

    tot_present = sum(r.presentCount for r in records)
    tot_classes = sum(r.totalCount for r in records)
    computed_overall = calculate_attendance_ratio(tot_present, tot_classes)

    overall_band = classify_attendance_band(
        computed_overall, threshold=policy.attendanceOverallPct, is_overall=True
    )

    below_threshold_components = []
    early_data_components = []

    for r in records:
        course_name = c_map.get(r.courseId).shortName if r.courseId in c_map else r.courseId
        comp_pct = r.computed_percentage
        band = classify_attendance_band(
            comp_pct,
            threshold=policy.attendancePerCoursePct,
            is_overall=False,
            total_classes=r.totalCount,
            small_sample_threshold=policy.smallSampleThreshold,
        )

        display_name = f"{course_name} {r.component.value}"

        if band == AttendanceBand.EARLY_DATA:
            early_data_components.append(r)
            reasons.append(
                SignalReason(
                    indicator=f"{display_name} attendance",
                    value=f"{comp_pct}% ({r.presentCount}/{r.totalCount} classes - Early data)",
                    direction="info",
                    source="Attendance record",
                )
            )
        elif band == AttendanceBand.ATTENTION:
            below_threshold_components.append(r)
            reasons.append(
                SignalReason(
                    indicator=f"{display_name} attendance",
                    value=f"{comp_pct}% (below {policy.attendancePerCoursePct:.0f}% course threshold)",
                    direction="concern",
                    source="Attendance record",
                )
            )
        elif band == AttendanceBand.STRONG:
            reasons.append(
                SignalReason(
                    indicator=f"{display_name} attendance",
                    value=f"{comp_pct}% (Strong >= {policy.attendancePerCoursePct + 10:.0f}%)",
                    direction="positive",
                    source="Attendance record",
                )
            )
        else:
            # Monitor
            reasons.append(
                SignalReason(
                    indicator=f"{display_name} attendance",
                    value=f"{comp_pct}% (Monitor)",
                    direction="info",
                    source="Attendance record",
                )
            )

    below_count = len(below_threshold_components)

    # Classify Signal
    if computed_overall is not None and computed_overall < policy.attendanceOverallPct:
        signal = SupportLevel.HIGH
        reasons.insert(
            0,
            SignalReason(
                indicator="Overall Attendance",
                value=f"{computed_overall}% (below {policy.attendanceOverallPct:.0f}% threshold)",
                direction="concern",
                source="Attendance overall",
            ),
        )
    elif below_count >= 2:
        signal = SupportLevel.HIGH
        reasons.insert(
            0,
            SignalReason(
                indicator="Component Alerts",
                value=f"{below_count} components below {policy.attendancePerCoursePct:.0f}% threshold",
                direction="concern",
                source="Attendance components",
            ),
        )
    elif below_count == 1:
        signal = SupportLevel.MODERATE
        reasons.insert(
            0,
            SignalReason(
                indicator="Component Alert",
                value=f"1 component below {policy.attendancePerCoursePct:.0f}% threshold",
                direction="concern",
                source="Attendance components",
            ),
        )
    elif overall_band == AttendanceBand.MONITOR:
        signal = SupportLevel.MODERATE
        reasons.insert(
            0,
            SignalReason(
                indicator="Overall Attendance",
                value=f"{computed_overall}% (Monitor band: 75% to <80%)",
                direction="info",
                source="Attendance overall",
            ),
        )
    else:
        signal = SupportLevel.LOW
        reasons.insert(
            0,
            SignalReason(
                indicator="Overall Attendance",
                value=f"{computed_overall}% (Healthy)",
                direction="positive",
                source="Attendance overall",
            ),
        )

    return signal, reasons, {
        "computedOverall": computed_overall,
        "belowCount": below_count,
        "earlyDataCount": len(early_data_components),
    }


def evaluate_academic_signal(
    assessments: list[Assessment],
    semester_results: list[SemesterResult],
    courses_by_id: dict[str, Course] | None = None,
    total_expected_courses: int = 0,
) -> tuple[SupportLevel, list[SignalReason], dict[str, Any]]:
    """Evaluates academic support signal based on current marks and semester results.
    
    Rules:
      - Needs more data: no assessments AND no SGPA history
      - High: >= 2 subjects in Attention (<50) OR (>= 1 Attention subject AND declining trend)
      - Moderate: 1 Attention subject OR SGPA declining OR >= 2 Monitor subjects (50 to <65)
      - Low: otherwise (if only some subjects evaluated, labeled partial)
    """
    reasons: list[SignalReason] = []
    c_map = courses_by_id or {}

    if not assessments and not semester_results:
        reasons.append(
            SignalReason(
                indicator="Academic Assessments",
                value="Waiting for first assessment",
                direction="info",
                source="Academic Module",
            )
        )
        return SupportLevel.NEEDS_MORE_DATA, reasons, {"coverage": "none"}

    # Evaluate SGPA trend if historical results exist
    sgpa_trend_dir, sgpa_delta = calculate_sgpa_trend(semester_results)
    if sgpa_trend_dir == TrendDirection.DECLINING:
        reasons.append(
            SignalReason(
                indicator="SGPA Trend",
                value=f"Declining by {abs(sgpa_delta):.2f} grade points",
                direction="concern",
                source="Published Results",
            )
        )
    elif sgpa_trend_dir == TrendDirection.IMPROVING:
        reasons.append(
            SignalReason(
                indicator="SGPA Trend",
                value=f"Improving by +{sgpa_delta:.2f} grade points",
                direction="positive",
                source="Published Results",
            )
        )

    # Group assessments by course
    course_assessments: dict[str, list[Assessment]] = {}
    for a in assessments:
        course_assessments.setdefault(a.courseId, []).append(a)

    attention_subjects = []
    monitor_subjects = []
    strong_subjects = []
    has_declining_assessment_trend = False

    for c_id, a_list in course_assessments.items():
        c_name = c_map.get(c_id).shortName if c_id in c_map else c_id
        pct = calculate_subject_marks_percentage(a_list)
        band = classify_academic_band(pct)
        a_dir, a_delta, is_early = calculate_assessment_trend(a_list)

        if a_dir == TrendDirection.DECLINING:
            has_declining_assessment_trend = True

        trend_note = f" (trend: {a_dir.value})" if a_dir in (TrendDirection.IMPROVING, TrendDirection.DECLINING) else ""

        if band == AcademicBand.ATTENTION:
            attention_subjects.append(c_name)
            reasons.append(
                SignalReason(
                    indicator=f"{c_name} marks",
                    value=f"{pct:.1f}% (Attention area < 50%){trend_note}",
                    direction="concern",
                    source="Assessments",
                )
            )
        elif band == AcademicBand.MONITOR:
            monitor_subjects.append(c_name)
            reasons.append(
                SignalReason(
                    indicator=f"{c_name} marks",
                    value=f"{pct:.1f}% (Monitor: 50% to <65%){trend_note}",
                    direction="info",
                    source="Assessments",
                )
            )
        elif band == AcademicBand.STRONG:
            strong_subjects.append(c_name)
            reasons.append(
                SignalReason(
                    indicator=f"{c_name} marks",
                    value=f"{pct:.1f}% (Strong >= 65%){trend_note}",
                    direction="positive",
                    source="Assessments",
                )
            )

    num_courses_evaluated = len(course_assessments)
    is_partial = total_expected_courses > 0 and num_courses_evaluated < total_expected_courses

    declining_overall_trend = (sgpa_trend_dir == TrendDirection.DECLINING) or has_declining_assessment_trend

    # Classification
    if len(attention_subjects) >= 2 or (len(attention_subjects) >= 1 and declining_overall_trend):
        signal = SupportLevel.HIGH
    elif len(attention_subjects) == 1 or sgpa_trend_dir == TrendDirection.DECLINING or len(monitor_subjects) >= 2:
        signal = SupportLevel.MODERATE
    elif num_courses_evaluated == 0 and sgpa_trend_dir == TrendDirection.NOT_ENOUGH_HISTORY:
        signal = SupportLevel.NEEDS_MORE_DATA
    else:
        signal = SupportLevel.LOW

    coverage_label = f"based on {num_courses_evaluated} of {total_expected_courses} subjects" if is_partial else "complete"

    return signal, reasons, {
        "coverage": coverage_label,
        "isPartial": is_partial,
        "evaluatedCount": num_courses_evaluated,
    }


def evaluate_overall_support_signal(
    att_signal: SupportLevel,
    acad_signal: SupportLevel,
    att_reasons: list[SignalReason],
    acad_reasons: list[SignalReason],
) -> tuple[SupportLevel, str, list[SignalReason]]:
    """Combines attendance and academic signals into the Overall Support Signal.
    
    Rules:
      - Takes highest severity among available primary signals
      - Escalate one level when >= 2 primary signals are Moderate or higher (converging evidence)
      - If all primary signals are 'Needs more data' -> 'Needs more data'
      - If a primary signal is missing append 'based on attendance only' (or academic only)
      - Never uses the word 'risk'
    """
    severity_order = {
        SupportLevel.NEEDS_MORE_DATA: 0,
        SupportLevel.LOW: 1,
        SupportLevel.MODERATE: 2,
        SupportLevel.HIGH: 3,
    }

    reasons = [r for r in att_reasons if r.direction == "concern"] + [r for r in acad_reasons if r.direction == "concern"]
    if not reasons:
        # Include positive/info if no concerns
        reasons = [r for r in att_reasons if r.direction != "info"] + [r for r in acad_reasons if r.direction != "info"]

    att_rank = severity_order[att_signal]
    acad_rank = severity_order[acad_signal]

    if att_signal == SupportLevel.NEEDS_MORE_DATA and acad_signal == SupportLevel.NEEDS_MORE_DATA:
        return SupportLevel.NEEDS_MORE_DATA, "Needs more data — waiting for academic and attendance inputs", reasons

    # Missing one signal qualification
    qualification = ""
    if acad_signal == SupportLevel.NEEDS_MORE_DATA:
        qualification = " — based on attendance only; academic data incomplete"
    elif att_signal == SupportLevel.NEEDS_MORE_DATA:
        qualification = " — based on academic data only; attendance data incomplete"

    # Base severity is the highest among available
    max_rank = max(att_rank, acad_rank)

    # Escalation: if >= 2 signals are Moderate or higher, escalate one level
    if att_rank >= 2 and acad_rank >= 2:
        max_rank = min(3, max_rank + 1)

    rank_to_level = {
        0: SupportLevel.NEEDS_MORE_DATA,
        1: SupportLevel.LOW,
        2: SupportLevel.MODERATE,
        3: SupportLevel.HIGH,
    }
    final_signal = rank_to_level[max_rank]
    display_title = f"{final_signal.value}{qualification}"

    return final_signal, display_title, reasons
