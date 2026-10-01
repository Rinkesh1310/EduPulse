from typing import Any

from edupulse.domain.enums import CoverageStatus, EngagementStatus, VerificationLevel
from edupulse.domain.models import (
    Assessment,
    AttendanceRecord,
    Course,
    Coverage,
    DailyAttendance,
    EngagementDeclaration,
    PolicyConfig,
    ScholarshipScheme,
    SemesterResult,
    StudentEventParticipation,
)


def resolve_data_availability(
    student_semester: int,
    courses: list[Course],
    attendance_records: list[AttendanceRecord],
    daily_records: list[DailyAttendance],
    assessments: list[Assessment],
    semester_results: list[SemesterResult],
    participations: list[StudentEventParticipation],
    declaration: EngagementDeclaration | None = None,
    policy: PolicyConfig | None = None,
    scholarships: list[ScholarshipScheme] | None = None,
) -> Coverage:
    """Resolves data availability across domains into a structured Coverage object."""
    chips: dict[str, str] = {}
    details: dict[str, Any] = {}

    # 1. Attendance Domain
    if not attendance_records:
        att_status = "none"
        chips["attendance"] = "No attendance data"
    elif daily_records:
        att_status = "snapshot+daily"
        chips["attendance"] = f"Summary ({len(attendance_records)} courses) + Daily records"
    else:
        att_status = "snapshot"
        chips["attendance"] = f"Summary only ({len(attendance_records)} courses)"
    details["attendance"] = att_status

    # 2. Marks Domain (current term)
    course_ids_with_marks: set[str] = {a.courseId for a in assessments}
    total_discovered_courses = len(courses)
    if not assessments:
        marks_status = "none"
        chips["marks"] = "Waiting for first assessment"
    elif total_discovered_courses > 0 and len(course_ids_with_marks) < total_discovered_courses:
        marks_status = f"partial ({len(course_ids_with_marks)} of {total_discovered_courses} subjects)"
        chips["marks"] = f"Partial marks ({len(course_ids_with_marks)}/{total_discovered_courses} subjects)"
    else:
        marks_status = "complete"
        chips["marks"] = f"Marks recorded ({len(assessments)} entries)"
    details["marks"] = marks_status

    # 3. Results & Semesters Domain
    published_sems = sorted([r.semester for r in semester_results])
    missing_sems = []
    if student_semester > 1:
        expected_prior_sems = list(range(1, student_semester))
        missing_sems = [s for s in expected_prior_sems if s not in published_sems]

    if not published_sems:
        results_status = "none"
        chips["results"] = "No historical results"
    elif missing_sems:
        results_status = f"semesters {published_sems}, gaps in {missing_sems}"
        chips["results"] = f"Prior results: Sem {published_sems} (Sem {missing_sems} not in supplied data)"
    else:
        results_status = f"complete (Sem {published_sems})"
        chips["results"] = f"Prior results: Sem {published_sems}"
    details["results"] = results_status
    details["missingSemesters"] = missing_sems

    # 4. Credits Domain
    credits_missing_in_results = [r.semester for r in semester_results if not r.creditsComplete and r.totalCreditsDeclared is None]
    if not semester_results:
        credits_status = "none"
        chips["credits"] = "No prior credits"
    elif credits_missing_in_results:
        credits_status = f"partial (unconfirmed in Sem {credits_missing_in_results})"
        chips["credits"] = f"Credits unconfirmed (Sem {credits_missing_in_results})"
    else:
        credits_status = "complete"
        chips["credits"] = "Credits confirmed"
    details["credits"] = credits_status

    # 5. Engagement Domain
    decl_status = declaration.status if declaration else EngagementStatus.NOT_PROVIDED
    if decl_status == EngagementStatus.NOT_PROVIDED and not participations:
        eng_status = "NOT_PROVIDED"
        chips["engagement"] = "Not provided"
    elif decl_status == EngagementStatus.DECLARED_NONE and not participations:
        eng_status = "DECLARED_NONE"
        chips["engagement"] = "Declared none this term"
    else:
        eng_status = "HAS_EVENTS"
        chips["engagement"] = f"{len(participations)} events confirmed"
    details["engagement"] = eng_status

    # 6. Policy Domain
    is_policy_verified = policy.verified if policy else False
    details["policy"] = "verified" if is_policy_verified else "unverified"
    chips["policy"] = "Policy verified" if is_policy_verified else "Policy unverified for institute"

    # 7. Scholarship Domain
    if scholarships:
        ver_levels = {s.verificationLevel for s in scholarships}
        details["scholarship"] = [v.value for v in ver_levels]
        if VerificationLevel.OFFICIAL_VERIFIED in ver_levels and len(ver_levels) == 1:
            chips["scholarship"] = "Official verified schemes"
        else:
            chips["scholarship"] = "Schemes require official verification"
    else:
        details["scholarship"] = "none"
        chips["scholarship"] = "No schemes loaded"

    # Overall Coverage Classification
    if att_status != "none" and marks_status == "complete" and results_status.startswith("complete"):
        overall_status = CoverageStatus.COMPLETE
    elif att_status == "none" and marks_status == "none" and results_status == "none":
        overall_status = CoverageStatus.WAITING
    else:
        overall_status = CoverageStatus.PARTIAL

    return Coverage(
        overall=overall_status,
        chips=chips,
        details=details,
    )
