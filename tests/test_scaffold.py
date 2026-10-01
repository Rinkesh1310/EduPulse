import pytest

from edupulse.domain import (
    Assessment,
    AttendanceRecord,
    ComponentType,
    DailyAttendance,
    DailyAttendanceStatus,
    Student,
)


def test_domain_models_creation():
    student = Student(id="s1", externalStudentId="DEMO-S3-001")
    assert student.name == "Demo Student"
    assert student.externalStudentId == "DEMO-S3-001"

    rec = AttendanceRecord(
        studentId=student.id,
        courseId="c1",
        component=ComponentType.LECT,
        presentCount=14,
        totalCount=15,
        asOfDate="2026-09-30",
    )
    assert rec.computed_percentage == 93.3

    daily = DailyAttendance(
        studentId=student.id,
        courseId="c1",
        date="2026-09-30",
        status=DailyAttendanceStatus.UNMARKED,
        source="daily_test",
    )
    assert daily.status == DailyAttendanceStatus.UNMARKED


def test_assessment_validation():
    # Valid assessment
    ass = Assessment(
        id="a1",
        studentId="s1",
        courseId="c1",
        type="Midterm",
        date="2026-09-15",
        obtainedMarks=18.5,
        totalMarks=20.0,
    )
    assert ass.percentage == 92.5

    # Invalid marks: obtained > total
    with pytest.raises(ValueError, match="cannot exceed totalMarks"):
        Assessment(
            id="a2",
            studentId="s1",
            courseId="c1",
            type="Midterm",
            date="2026-09-15",
            obtainedMarks=25.0,
            totalMarks=20.0,
        )

    # Invalid marks: negative obtained
    with pytest.raises(ValueError, match="cannot be negative"):
        Assessment(
            id="a3",
            studentId="s1",
            courseId="c1",
            type="Midterm",
            date="2026-09-15",
            obtainedMarks=-1.0,
            totalMarks=20.0,
        )

    # Invalid marks: totalMarks <= 0
    with pytest.raises(ValueError, match="strictly greater than 0"):
        Assessment(
            id="a4",
            studentId="s1",
            courseId="c1",
            type="Midterm",
            date="2026-09-15",
            obtainedMarks=0.0,
            totalMarks=0.0,
        )
