from typing import Any

from pydantic import BaseModel, Field, model_validator

from edupulse.domain.enums import (
    ComponentType,
    CoverageStatus,
    DailyAttendanceStatus,
    EngagementStatus,
    SupportLevel,
    VerificationLevel,
)


class Student(BaseModel):
    id: str
    externalStudentId: str
    name: str = "Demo Student"
    program: str = "B.Tech IT (demo)"
    semester: int = 3
    academicYear: str = "2026-27"


class Course(BaseModel):
    id: str
    code: str
    shortName: str
    fullName: str | None = None
    courseType: str = "THEORY"
    credits: float | None = None
    semester: int = 3


class AttendanceRecord(BaseModel):
    studentId: str
    courseId: str
    component: ComponentType
    presentCount: int
    totalCount: int
    portalReportedPercentage: float | None = None
    asOfDate: str
    source: str = "mock"
    importBatchId: str | None = None

    @model_validator(mode="after")
    def validate_counts(self) -> "AttendanceRecord":
        if self.presentCount < 0:
            raise ValueError("presentCount cannot be negative")
        if self.totalCount < 0:
            raise ValueError("totalCount cannot be negative")
        if self.presentCount > self.totalCount:
            raise ValueError(f"presentCount ({self.presentCount}) cannot exceed totalCount ({self.totalCount})")
        return self

    @property
    def computed_percentage(self) -> float | None:
        if self.totalCount == 0:
            return None
        return round((self.presentCount / self.totalCount) * 100.0, 1)


class AttendanceHeadline(BaseModel):
    studentId: str
    semester: int
    portalReportedOverall: float
    asOfDate: str
    source: str = "portal_header"


class DailyAttendance(BaseModel):
    studentId: str
    courseId: str
    date: str
    timeSlot: str | None = None
    component: str | None = None
    status: DailyAttendanceStatus
    source: str = "daily_import"


class SemesterCourseResult(BaseModel):
    courseName: str
    courseType: str
    credits: float
    grade: str
    gradePoint: float | None = None


class SemesterResult(BaseModel):
    studentId: str
    semester: int
    monthYear: str
    sgpa: float
    creditsComplete: bool = False
    totalCreditsDeclared: float | None = None
    source: str = "portal_result"
    publishedAt: str | None = None
    courses: list[SemesterCourseResult] = Field(default_factory=list)


class Assessment(BaseModel):
    id: str
    studentId: str
    courseId: str
    type: str
    term: str | None = None
    date: str
    obtainedMarks: float
    totalMarks: float

    @model_validator(mode="after")
    def validate_marks(self) -> "Assessment":
        if self.totalMarks <= 0:
            raise ValueError(f"totalMarks must be strictly greater than 0, got {self.totalMarks}")
        if self.obtainedMarks < 0:
            raise ValueError(f"obtainedMarks cannot be negative, got {self.obtainedMarks}")
        if self.obtainedMarks > self.totalMarks:
            raise ValueError(f"obtainedMarks ({self.obtainedMarks}) cannot exceed totalMarks ({self.totalMarks})")
        return self

    @property
    def percentage(self) -> float:
        return (self.obtainedMarks / self.totalMarks) * 100.0


class Event(BaseModel):
    eventId: str
    name: str
    date: str
    endDate: str | None = None
    activityType: str  # hackathon, workshop, competition, project, academic_activity, seminar, club
    durationType: str  # full-day, hours
    hours: float | None = None
    organizer: str
    source: str = "demo catalogue"


class StudentEventParticipation(BaseModel):
    studentId: str
    eventId: str
    confirmed: bool = True
    confirmationDate: str


class EngagementDeclaration(BaseModel):
    studentId: str
    term: str
    status: EngagementStatus = EngagementStatus.NOT_PROVIDED


class PolicyConfig(BaseModel):
    version: str
    attendanceOverallPct: float = 75.0
    attendancePerCoursePct: float = 70.0
    aggregationLevel: str = "component"
    verified: bool = False
    sourceUrl: str | None = None
    sourceNote: str = "Demo default from CHARUSAT student handbook (CMPICA), unverified for your institute"
    lastVerifiedAt: str | None = None
    smallSampleThreshold: int = 8


class ScholarshipCriterion(BaseModel):
    id: str
    label: str
    track: str = "renewal"  # fresh, renewal, all
    type: str
    operator: str
    value: Any
    unit: str
    requiredDataFields: list[str] = Field(default_factory=list)
    verification: str
    notes: str


class ScholarshipScheme(BaseModel):
    schemeId: str
    name: str
    academicYear: str
    version: str = "1.0"
    verificationLevel: VerificationLevel = VerificationLevel.UNVERIFIED
    officialSourceUrl: str | None = None
    officialSourceTitle: str | None = None
    lastVerifiedAt: str | None = None
    supersedes: str | None = None
    notes: str | None = None
    criteria: list[ScholarshipCriterion] = Field(default_factory=list)


class UserAttestedFact(BaseModel):
    studentId: str
    key: str
    value: Any
    attestedAt: str


class SignalReason(BaseModel):
    indicator: str
    value: str
    direction: str  # concern | positive | info
    source: str


class AnalysisSnapshot(BaseModel):
    studentId: str
    attendanceSignal: SupportLevel
    academicSignal: SupportLevel
    engagementInfo: dict[str, Any]
    overallSupportSignal: SupportLevel
    reasons: list[SignalReason]
    dataCoverage: dict[str, Any]
    policyVersion: str
    engineVersion: str = "1.0.0"
    createdAt: str


class ImportBatch(BaseModel):
    id: str
    source: str
    timestamp: str
    rowCount: int
    checksum: str
    status: str
    errors: list[str] = Field(default_factory=list)


class Coverage(BaseModel):
    overall: CoverageStatus
    chips: dict[str, str]
    details: dict[str, Any]
