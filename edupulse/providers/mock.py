from typing import Any

from edupulse.domain.enums import (
    ComponentType,
    DailyAttendanceStatus,
    EngagementStatus,
)
from edupulse.domain.models import (
    Assessment,
    AttendanceHeadline,
    AttendanceRecord,
    Course,
    DailyAttendance,
    EngagementDeclaration,
    SemesterCourseResult,
    SemesterResult,
    Student,
    StudentEventParticipation,
)
from edupulse.providers.base import AcademicDataProvider

PERSONA_REGISTRY: dict[str, dict[str, Any]] = {
    "student_synth_strong": {
        "id": "student_synth_strong",
        "scenario_key": "SYNTH_STRONG",
        "name": "Priya Sharma",
        "archetype": "Strong Attendance & Academics",
        "provenance": "Demo data",
        "icon": "🌟",
        "external_id": "SYNTH-2026-001",
        "program": "B.Tech Computer Science (Synthetic)",
        "semester": 3,
        "academic_year": "2026-27",
        "academic_status": "Active Term • Assessment In Progress • Midterm 1 Logged",
        "description": "Exemplary academic and attendance record with active hackathon participation and strong grades.",
        "badge_class": "badge-low",
    },
    "student_synth_att_concern": {
        "id": "student_synth_att_concern",
        "scenario_key": "SYNTH_ATT_CONCERN",
        "name": "Rohan Verma",
        "archetype": "Attendance Concern",
        "provenance": "Demo data",
        "icon": "⚠️",
        "external_id": "SYNTH-2026-002",
        "program": "B.Tech Information Technology (Synthetic)",
        "semester": 3,
        "academic_year": "2026-27",
        "academic_status": "Active Term • Attendance Attention Alert",
        "description": "Attendance alert across 4 components (overall 68.4%) despite solid assessment performance.",
        "badge_class": "badge-high",
    },
    "student_synth_acad_concern": {
        "id": "student_synth_acad_concern",
        "scenario_key": "SYNTH_ACAD_CONCERN",
        "name": "Kabir Mehta",
        "archetype": "Academic Performance Concern",
        "provenance": "Demo data",
        "icon": "📉",
        "external_id": "SYNTH-2026-003",
        "program": "B.Tech Electronics & Comm. (Synthetic)",
        "semester": 3,
        "academic_year": "2026-27",
        "academic_status": "Active Term • Academic Attention Alert",
        "description": "Attention areas in core engineering subjects with declining SGPA trajectory.",
        "badge_class": "badge-high",
    },
    "student_synth_early": {
        "id": "student_synth_early",
        "scenario_key": "SYNTH_EARLY",
        "name": "Ananya Iyer",
        "archetype": "Insufficient Current Assessment Data",
        "provenance": "Demo data",
        "icon": "⏳",
        "external_id": "SYNTH-2026-004",
        "program": "B.Tech Artificial Intelligence (Synthetic)",
        "semester": 1,
        "academic_year": "2026-27",
        "academic_status": "Pre-Assessment • Awaiting First Assessment",
        "description": "Semester 1 entrant with high attendance, awaiting first midterms. Zero fabricated marks.",
        "badge_class": "badge-info",
    },
    "student_synth_improving": {
        "id": "student_synth_improving",
        "scenario_key": "SYNTH_IMPROVING",
        "name": "Devansh Joshi",
        "archetype": "Improving Multi-Semester Trajectory",
        "provenance": "Demo data",
        "icon": "📈",
        "external_id": "SYNTH-2026-005",
        "program": "B.Tech Mechanical Engineering (Synthetic)",
        "semester": 3,
        "academic_year": "2026-27",
        "academic_status": "Active Term • Upward Momentum",
        "description": "Positive momentum: SGPA increased from 6.50 to 7.80 (+1.30) with steady attendance.",
        "badge_class": "badge-low",
    },
    "student_synth_eng": {
        "id": "student_synth_eng",
        "scenario_key": "SYNTH_ENGAGED",
        "name": "Zara Mansuri",
        "archetype": "Engagement-Rich Leadership",
        "provenance": "Demo data",
        "icon": "🏆",
        "external_id": "SYNTH-2026-006",
        "program": "B.Tech Computer Engineering (Synthetic)",
        "semester": 3,
        "academic_status": "Active Term • High Co-Curricular Engagement",
        "description": "Active co-curricular portfolio (9.0 pts across 4 events) balanced with strong academic health.",
        "badge_class": "badge-low",
    },
    "student_s3": {
        "id": "student_s3",
        "scenario_key": "S3",
        "name": "Demo Student (Reference S3)",
        "archetype": "Reference / Validation Data",
        "provenance": "Reference / Validation Data",
        "icon": "🔬",
        "external_id": "DEMO-S3-001",
        "program": "B.Tech IT (demo)",
        "semester": 3,
        "academic_year": "2026-27",
        "academic_status": "Validation Benchmark • Reference Scenario",
        "description": "Validation benchmark derived from portal screenshot: headline 80% vs computed 76.5%, CPI (57.1%), FDSA Lab (63.6%), Sem 1 incomplete credits.",
        "badge_class": "badge-moderate",
    },
}


class MockAcademicProvider(AcademicDataProvider):
    """Scenario-driven mock provider supplying realistic demo and validation data."""

    def __init__(self, scenario_id: str = "SYNTH_STRONG"):
        self.scenario_id = scenario_id.upper()
        self._load_scenario(self.scenario_id)

    def capabilities(self) -> dict[str, bool]:
        return {
            "supports_live": False,
            "supports_daily": True,
            "supports_results": True,
            "is_authorized": False,
            "is_mock": True,
        }

    def source_metadata(self) -> dict[str, Any]:
        return {
            "source": f"MockAcademicProvider ({self.scenario_id})",
            "scenario": self.scenario_id,
            "asOfDate": "2026-09-30",
            "description": self._scenario_description,
        }

    def _load_scenario(self, s_id: str):
        self._courses: list[Course] = []
        self._attendance_records: list[AttendanceRecord] = []
        self._headline: AttendanceHeadline | None = None
        self._daily: list[DailyAttendance] = []
        self._results: list[SemesterResult] = []
        self._assessments: list[Assessment] = []
        self._participations: list[StudentEventParticipation] = []

        # Standard synthetic personas
        if s_id in ("SYNTH_STRONG", "STUDENT_SYNTH_STRONG"):
            self.scenario_id = "SYNTH_STRONG"
            self._setup_synth_strong()
        elif s_id in ("SYNTH_ATT_CONCERN", "STUDENT_SYNTH_ATT_CONCERN"):
            self.scenario_id = "SYNTH_ATT_CONCERN"
            self._setup_synth_att_concern()
        elif s_id in ("SYNTH_ACAD_CONCERN", "STUDENT_SYNTH_ACAD_CONCERN"):
            self.scenario_id = "SYNTH_ACAD_CONCERN"
            self._setup_synth_acad_concern()
        elif s_id in ("SYNTH_EARLY", "STUDENT_SYNTH_EARLY"):
            self.scenario_id = "SYNTH_EARLY"
            self._setup_synth_early()
        elif s_id in ("SYNTH_IMPROVING", "STUDENT_SYNTH_IMPROVING"):
            self.scenario_id = "SYNTH_IMPROVING"
            self._setup_synth_improving()
        elif s_id in ("SYNTH_ENGAGED", "STUDENT_SYNTH_ENG"):
            self.scenario_id = "SYNTH_ENGAGED"
            self._setup_synth_engaged()
        # Reference scenario
        elif s_id in ("S3", "STUDENT_S3", "REF_SCREENSHOT"):
            self.scenario_id = "S3"
            self._scenario_description = (
                "Reference Scenario S3 (Validation Benchmark): Semester 3 with headline 80% vs computed 76.5%, "
                "attendance attention in CPI and FDSA Lab, Sem 1 result with incomplete credits"
            )
            self._student = Student(
                id="student_s3",
                externalStudentId="DEMO-S3-001",
                name="Demo Student",
                program="B.Tech IT (demo)",
                semester=3,
                academicYear="2026-27",
            )
            self._declaration = EngagementDeclaration(
                studentId=self._student.id,
                term="2026-27-ODD",
                status=EngagementStatus.NOT_PROVIDED,
            )
            self._setup_s3()
        elif s_id == "S1":
            self.scenario_id = "S1"
            self._scenario_description = "New Semester 1 student: attendance only, no assessments, no prior results"
            self._student = Student(id="student_s1", externalStudentId="DEMO-S1-001", name="Demo Student S1", program="B.Tech IT (demo)", semester=1, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)
            self._setup_s1()
        elif s_id == "S2":
            self.scenario_id = "S2"
            self._scenario_description = "Midterm completed: attendance + first assessment marks in OOP, FDSA, CPI"
            self._student = Student(id="student_s2", externalStudentId="DEMO-S2-001", name="Demo Student S2", program="B.Tech IT (demo)", semester=3, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)
            self._setup_s2()
        elif s_id == "S4":
            self.scenario_id = "S4"
            self._scenario_description = "Multi-semester history: unequal credits (24 vs 26) with improving SGPA"
            self._student = Student(id="student_s4", externalStudentId="DEMO-S4-001", name="Demo Student S4", program="B.Tech IT (demo)", semester=3, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)
            self._setup_s4()
        elif s_id == "S5":
            self.scenario_id = "S5"
            self._scenario_description = "Declining academic performance: falling SGPA and lower assessment scores"
            self._student = Student(id="student_s5", externalStudentId="DEMO-S5-001", name="Demo Student S5", program="B.Tech IT (demo)", semester=3, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)
            self._setup_s5()
        elif s_id == "S6":
            self.scenario_id = "S6"
            self._scenario_description = "Partial data coverage: partial subject marks, missing semester credits"
            self._student = Student(id="student_s6", externalStudentId="DEMO-S6-001", name="Demo Student S6", program="B.Tech IT (demo)", semester=3, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)
            self._setup_s6()
        elif s_id == "S7":
            self.scenario_id = "S7"
            self._scenario_description = "Unrecoverable attendance: 40/70 with 10 remaining classes at 75% target"
            self._student = Student(id="student_s7", externalStudentId="DEMO-S7-001", name="Demo Student S7", program="B.Tech IT (demo)", semester=3, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)
            self._setup_s7()
        elif s_id == "S8":
            self.scenario_id = "S8"
            self._scenario_description = "Engagement showcase: 3 confirmed events with attendance date overlap"
            self._student = Student(id="student_s8", externalStudentId="DEMO-S8-001", name="Demo Student S8", program="B.Tech IT (demo)", semester=3, academicYear="2026-27")
            self._declaration = EngagementDeclaration(studentId=self._student.id, term="2026-27-ODD", status=EngagementStatus.HAS_EVENTS)
            self._setup_s8()
        else:
            # Fallback to SYNTH_STRONG
            self.scenario_id = "SYNTH_STRONG"
            self._setup_synth_strong()

    # --- SYNTHETIC PERSONAS ---

    def _setup_synth_strong(self):
        self._scenario_description = "Priya Sharma (Synthetic Demo): Strong attendance (92.7%), high academic marks, active hackathon participation."
        st_id = "student_synth_strong"
        self._student = Student(
            id=st_id,
            externalStudentId="SYNTH-2026-001",
            name="Priya Sharma",
            program="B.Tech Computer Science (Synthetic)",
            semester=3,
            academicYear="2026-27",
        )
        c1 = Course(id=f"{st_id}_CS301", code="CS301", shortName="DSA", fullName="Data Structures & Algorithms", credits=4.0, semester=3)
        c2 = Course(id=f"{st_id}_CS302", code="CS302", shortName="DBMS", fullName="Database Management Systems", credits=4.0, semester=3)
        c3 = Course(id=f"{st_id}_CS303", code="CS303", shortName="COA", fullName="Computer Organization & Architecture", credits=3.0, semester=3)
        c4 = Course(id=f"{st_id}_MA301", code="MA301", shortName="DM", fullName="Discrete Mathematics", credits=4.0, semester=3)
        c5 = Course(id=f"{st_id}_HS301", code="HS301", shortName="TC", fullName="Technical Communication", credits=2.0, semester=3)
        self._courses = [c1, c2, c3, c4, c5]

        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LECT, presentCount=27, totalCount=30, portalReportedPercentage=90.0, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LAB, presentCount=14, totalCount=15, portalReportedPercentage=93.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LECT, presentCount=26, totalCount=28, portalReportedPercentage=92.9, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LAB, presentCount=13, totalCount=14, portalReportedPercentage=92.9, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c3.id, component=ComponentType.LECT, presentCount=28, totalCount=30, portalReportedPercentage=93.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c4.id, component=ComponentType.LECT, presentCount=37, totalCount=40, portalReportedPercentage=92.5, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c5.id, component=ComponentType.LECT, presentCount=19, totalCount=20, portalReportedPercentage=95.0, asOfDate="2026-09-30"),
        ]
        # Total present = 27 + 14 + 26 + 13 + 28 + 37 + 19 = 164. Total count = 30 + 15 + 28 + 14 + 30 + 40 + 20 = 177.
        # 164 / 177 = 92.65% -> 92.7%
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=92.7, asOfDate="2026-09-30")

        self._assessments = [
            Assessment(id=f"{st_id}_ass_1", studentId=st_id, courseId=c1.id, type="Midterm", term="T1", date="2026-09-15", obtainedMarks=18.5, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_2", studentId=st_id, courseId=c1.id, type="Quiz", term="T1", date="2026-09-22", obtainedMarks=9.5, totalMarks=10.0),
            Assessment(id=f"{st_id}_ass_3", studentId=st_id, courseId=c2.id, type="Midterm", term="T1", date="2026-09-16", obtainedMarks=19.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_4", studentId=st_id, courseId=c3.id, type="Midterm", term="T1", date="2026-09-17", obtainedMarks=17.5, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_5", studentId=st_id, courseId=c4.id, type="Midterm", term="T1", date="2026-09-18", obtainedMarks=27.0, totalMarks=30.0),
            Assessment(id=f"{st_id}_ass_6", studentId=st_id, courseId=c5.id, type="Quiz", term="T1", date="2026-09-20", obtainedMarks=18.0, totalMarks=20.0),
        ]

        self._results = [
            SemesterResult(
                studentId=st_id, semester=1, monthYear="December 2024", sgpa=8.75,
                creditsComplete=True, totalCreditsDeclared=24.0, courses=[
                    SemesterCourseResult(courseName="Programming Fundamentals", courseType="THEORY", credits=5.0, grade="A+"),
                    SemesterCourseResult(courseName="Digital Electronics", courseType="THEORY", credits=4.0, grade="A"),
                    SemesterCourseResult(courseName="Calculus & Linear Algebra", courseType="THEORY", credits=4.0, grade="A+"),
                ]
            ),
            SemesterResult(
                studentId=st_id, semester=2, monthYear="May 2025", sgpa=8.90,
                creditsComplete=True, totalCreditsDeclared=24.0, courses=[
                    SemesterCourseResult(courseName="Object Oriented Methodology", courseType="THEORY", credits=5.0, grade="A+"),
                    SemesterCourseResult(courseName="Data Structures", courseType="THEORY", credits=5.0, grade="A+"),
                ]
            ),
        ]

        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.HAS_EVENTS)
        self._participations = [
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-001", confirmationDate="2026-09-29"),
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-002", confirmationDate="2026-08-15"),
        ]

        self._daily = [
            DailyAttendance(studentId=st_id, courseId=c1.id, date="2026-09-29", timeSlot="09:10-10:10", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
            DailyAttendance(studentId=st_id, courseId=c2.id, date="2026-09-29", timeSlot="10:15-11:15", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
            DailyAttendance(studentId=st_id, courseId=c3.id, date="2026-09-30", timeSlot="09:10-10:10", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
        ]

    def _setup_synth_att_concern(self):
        self._scenario_description = "Rohan Verma (Synthetic Demo): Attendance alert (68.4% overall, 4 components <70%) despite solid 80% marks."
        st_id = "student_synth_att_concern"
        self._student = Student(
            id=st_id,
            externalStudentId="SYNTH-2026-002",
            name="Rohan Verma",
            program="B.Tech Information Technology (Synthetic)",
            semester=3,
            academicYear="2026-27",
        )
        c1 = Course(id=f"{st_id}_IT301", code="IT301", shortName="OS", fullName="Operating Systems", credits=4.0, semester=3)
        c2 = Course(id=f"{st_id}_IT302", code="IT302", shortName="WE", fullName="Web Engineering", credits=4.0, semester=3)
        c3 = Course(id=f"{st_id}_IT303", code="IT303", shortName="SE", fullName="Software Engineering", credits=3.0, semester=3)
        c4 = Course(id=f"{st_id}_MA301", code="MA301", shortName="DM", fullName="Discrete Mathematics", credits=4.0, semester=3)
        self._courses = [c1, c2, c3, c4]

        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LECT, presentCount=16, totalCount=26, portalReportedPercentage=61.5, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LAB, presentCount=6, totalCount=11, portalReportedPercentage=54.5, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LECT, presentCount=19, totalCount=28, portalReportedPercentage=67.9, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c3.id, component=ComponentType.LECT, presentCount=24, totalCount=30, portalReportedPercentage=80.0, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c4.id, component=ComponentType.LECT, presentCount=26, totalCount=38, portalReportedPercentage=68.4, asOfDate="2026-09-30"),
        ]
        # Total present = 16 + 6 + 19 + 24 + 26 = 91. Total count = 26 + 11 + 28 + 30 + 38 = 133.
        # 91 / 133 = 68.42% -> 68.4%
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=68.4, asOfDate="2026-09-30")

        self._assessments = [
            Assessment(id=f"{st_id}_ass_1", studentId=st_id, courseId=c1.id, type="Midterm", term="T1", date="2026-09-15", obtainedMarks=16.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_2", studentId=st_id, courseId=c2.id, type="Midterm", term="T1", date="2026-09-16", obtainedMarks=15.5, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_3", studentId=st_id, courseId=c3.id, type="Midterm", term="T1", date="2026-09-17", obtainedMarks=17.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_4", studentId=st_id, courseId=c4.id, type="Midterm", term="T1", date="2026-09-18", obtainedMarks=24.0, totalMarks=30.0),
        ]

        self._results = [
            SemesterResult(studentId=st_id, semester=1, monthYear="Dec 2024", sgpa=7.50, creditsComplete=True, totalCreditsDeclared=24.0, courses=[]),
            SemesterResult(studentId=st_id, semester=2, monthYear="May 2025", sgpa=7.60, creditsComplete=True, totalCreditsDeclared=24.0, courses=[]),
        ]
        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)

    def _setup_synth_acad_concern(self):
        self._scenario_description = "Kabir Mehta (Synthetic Demo): Academic performance concern (low marks <50% and SGPA declining by -1.20) with 85.4% attendance."
        st_id = "student_synth_acad_concern"
        self._student = Student(
            id=st_id,
            externalStudentId="SYNTH-2026-003",
            name="Kabir Mehta",
            program="B.Tech Electronics & Comm. (Synthetic)",
            semester=3,
            academicYear="2026-27",
        )
        c1 = Course(id=f"{st_id}_EC301", code="EC301", shortName="SAS", fullName="Signals & Systems", credits=4.0, semester=3)
        c2 = Course(id=f"{st_id}_EC302", code="EC302", shortName="DC", fullName="Digital Circuits", credits=4.0, semester=3)
        c3 = Course(id=f"{st_id}_EC303", code="EC303", shortName="AE", fullName="Analog Electronics", credits=3.0, semester=3)
        c4 = Course(id=f"{st_id}_MA301", code="MA301", shortName="DM", fullName="Discrete Mathematics", credits=4.0, semester=3)
        self._courses = [c1, c2, c3, c4]

        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LECT, presentCount=27, totalCount=32, portalReportedPercentage=84.4, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LECT, presentCount=26, totalCount=30, portalReportedPercentage=86.7, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c3.id, component=ComponentType.LECT, presentCount=25, totalCount=30, portalReportedPercentage=83.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c4.id, component=ComponentType.LECT, presentCount=33, totalCount=38, portalReportedPercentage=86.8, asOfDate="2026-09-30"),
        ]
        # Total present = 111 / 130 = 85.38% -> 85.4%
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=85.4, asOfDate="2026-09-30")

        self._assessments = [
            Assessment(id=f"{st_id}_ass_1", studentId=st_id, courseId=c1.id, type="Quiz 1", date="2026-08-25", obtainedMarks=8.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_2", studentId=st_id, courseId=c1.id, type="Midterm", date="2026-09-20", obtainedMarks=7.5, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_3", studentId=st_id, courseId=c2.id, type="Midterm", date="2026-09-21", obtainedMarks=9.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_4", studentId=st_id, courseId=c3.id, type="Midterm", date="2026-09-22", obtainedMarks=10.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_5", studentId=st_id, courseId=c4.id, type="Midterm", date="2026-09-23", obtainedMarks=13.0, totalMarks=30.0),
        ]

        # Declining SGPA trend: 7.40 down to 6.20 (-1.20)
        self._results = [
            SemesterResult(studentId=st_id, semester=1, monthYear="Dec 2024", sgpa=7.40, creditsComplete=True, totalCreditsDeclared=24.0, courses=[]),
            SemesterResult(studentId=st_id, semester=2, monthYear="May 2025", sgpa=6.20, creditsComplete=True, totalCreditsDeclared=24.0, courses=[]),
        ]
        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.DECLARED_NONE)

    def _setup_synth_early(self):
        self._scenario_description = "Ananya Iyer (Synthetic Demo): Early semester entrant with 91.9% attendance, waiting for first assessments."
        st_id = "student_synth_early"
        self._student = Student(
            id=st_id,
            externalStudentId="SYNTH-2026-004",
            name="Ananya Iyer",
            program="B.Tech Artificial Intelligence (Synthetic)",
            semester=1,
            academicYear="2026-27",
        )
        c1 = Course(id=f"{st_id}_AI101", code="AI101", shortName="Intro AI", fullName="Introduction to AI & Python", credits=3.0, semester=1)
        c2 = Course(id=f"{st_id}_AI102", code="AI102", shortName="LinAlg", fullName="Linear Algebra & Calculus", credits=4.0, semester=1)
        c3 = Course(id=f"{st_id}_AI103", code="AI103", shortName="FC", fullName="Foundations of Computing", credits=3.0, semester=1)
        self._courses = [c1, c2, c3]

        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LECT, presentCount=11, totalCount=12, portalReportedPercentage=91.7, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LECT, presentCount=13, totalCount=14, portalReportedPercentage=92.9, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c3.id, component=ComponentType.LECT, presentCount=10, totalCount=11, portalReportedPercentage=90.9, asOfDate="2026-09-30"),
        ]
        # Total present = 34 / 37 = 91.89% -> 91.9%
        self._headline = AttendanceHeadline(studentId=st_id, semester=1, portalReportedOverall=91.9, asOfDate="2026-09-30")
        self._assessments = []
        self._results = []
        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.NOT_PROVIDED)

    def _setup_synth_improving(self):
        self._scenario_description = "Devansh Joshi (Synthetic Demo): Improving trajectory (SGPA 6.50 -> 7.80 with unequal credits) and rising marks."
        st_id = "student_synth_improving"
        self._student = Student(
            id=st_id,
            externalStudentId="SYNTH-2026-005",
            name="Devansh Joshi",
            program="B.Tech Mechanical Engineering (Synthetic)",
            semester=3,
            academicYear="2026-27",
        )
        c1 = Course(id=f"{st_id}_ME301", code="ME301", shortName="TD", fullName="Applied Thermodynamics", credits=4.0, semester=3)
        c2 = Course(id=f"{st_id}_ME302", code="ME302", shortName="FM", fullName="Fluid Mechanics", credits=3.0, semester=3)
        c3 = Course(id=f"{st_id}_ME303", code="ME303", shortName="KOM", fullName="Kinematics of Machines", credits=3.0, semester=3)
        self._courses = [c1, c2, c3]

        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LECT, presentCount=27, totalCount=32, portalReportedPercentage=84.4, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LECT, presentCount=25, totalCount=30, portalReportedPercentage=83.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c3.id, component=ComponentType.LECT, presentCount=26, totalCount=30, portalReportedPercentage=86.7, asOfDate="2026-09-30"),
        ]
        # Total present = 78 / 92 = 84.78% -> 84.8%
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=84.8, asOfDate="2026-09-30")

        # Rising marks trend in ME301: 70% -> 87.5% (+17.5% jump)
        self._assessments = [
            Assessment(id=f"{st_id}_ass_1", studentId=st_id, courseId=c1.id, type="Quiz 1", date="2026-08-20", obtainedMarks=14.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_2", studentId=st_id, courseId=c1.id, type="Midterm", date="2026-09-20", obtainedMarks=17.5, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_3", studentId=st_id, courseId=c2.id, type="Midterm", date="2026-09-21", obtainedMarks=16.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_4", studentId=st_id, courseId=c3.id, type="Midterm", date="2026-09-22", obtainedMarks=16.5, totalMarks=20.0),
        ]

        # Improving SGPA with unequal credits (22 and 26)
        self._results = [
            SemesterResult(studentId=st_id, semester=1, monthYear="Dec 2024", sgpa=6.50, creditsComplete=True, totalCreditsDeclared=22.0, courses=[]),
            SemesterResult(studentId=st_id, semester=2, monthYear="May 2025", sgpa=7.80, creditsComplete=True, totalCreditsDeclared=26.0, courses=[]),
        ]

        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.HAS_EVENTS)
        self._participations = [
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-005", confirmationDate="2026-09-10"),
        ]

    def _setup_synth_engaged(self):
        self._scenario_description = "Zara Mansuri (Synthetic Demo): Active co-curricular leadership (4 events, 9.0 pts, Highly active) with strong 85.2% attendance."
        st_id = "student_synth_eng"
        self._student = Student(
            id=st_id,
            externalStudentId="SYNTH-2026-006",
            name="Zara Mansuri",
            program="B.Tech Computer Engineering (Synthetic)",
            semester=3,
            academicYear="2026-27",
        )
        c1 = Course(id=f"{st_id}_CE301", code="CE301", shortName="CN", fullName="Computer Networks", credits=3.0, semester=3)
        c2 = Course(id=f"{st_id}_CE302", code="CE302", shortName="DBMS", fullName="Database Systems", credits=3.0, semester=3)
        c3 = Course(id=f"{st_id}_CE303", code="CE303", shortName="OS", fullName="Operating Systems", credits=3.0, semester=3)
        self._courses = [c1, c2, c3]

        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId=c1.id, component=ComponentType.LECT, presentCount=25, totalCount=30, portalReportedPercentage=83.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c2.id, component=ComponentType.LECT, presentCount=24, totalCount=28, portalReportedPercentage=85.7, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId=c3.id, component=ComponentType.LECT, presentCount=26, totalCount=30, portalReportedPercentage=86.7, asOfDate="2026-09-30"),
        ]
        # Total present = 75 / 88 = 85.22% -> 85.2%
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=85.2, asOfDate="2026-09-30")

        self._assessments = [
            Assessment(id=f"{st_id}_ass_1", studentId=st_id, courseId=c1.id, type="Midterm", date="2026-09-18", obtainedMarks=16.5, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_2", studentId=st_id, courseId=c2.id, type="Midterm", date="2026-09-19", obtainedMarks=17.0, totalMarks=20.0),
            Assessment(id=f"{st_id}_ass_3", studentId=st_id, courseId=c3.id, type="Midterm", date="2026-09-20", obtainedMarks=16.0, totalMarks=20.0),
        ]

        self._results = [
            SemesterResult(studentId=st_id, semester=1, monthYear="Dec 2024", sgpa=8.10, creditsComplete=True, totalCreditsDeclared=24.0, courses=[]),
            SemesterResult(studentId=st_id, semester=2, monthYear="May 2025", sgpa=8.30, creditsComplete=True, totalCreditsDeclared=24.0, courses=[]),
        ]

        # 4 events across 3 categories: 3.0 (hackathon) + 2.0 (workshop) + 3.0 (competition) + 1.0 (club) = 9.0 pts
        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.HAS_EVENTS)
        self._participations = [
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-001", confirmationDate="2026-09-29"),
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-002", confirmationDate="2026-08-15"),
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-003", confirmationDate="2026-09-13"),
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-006", confirmationDate="2026-07-25"),
        ]

        self._daily = [
            DailyAttendance(studentId=st_id, courseId=c1.id, date="2026-09-29", timeSlot="09:10-10:10", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
        ]

    # --- REFERENCE AND TEST SCENARIOS ---

    def _setup_s3(self):
        st_id = self._student.id

        # Discovered courses in Semester 3
        c_oop = Course(id="c_oop", code="CEUE203", shortName="OOP", fullName="Object Oriented Programming", semester=3)
        c_fdsa = Course(id="c_fdsa", code="CSUC201", shortName="FDSA", fullName="Data Structures & Algorithms", semester=3)
        c_cpi = Course(id="c_cpi", code="HSUV201", shortName="CPI", fullName="Critical Professional Identity", semester=3)
        c_dm = Course(id="c_dm", code="MSUD203", shortName="DM", fullName="Discrete Mathematics", semester=3)
        c_fcn = Course(id="c_fcn", code="ITUC201", shortName="FCN", fullName="Fundamentals of Computer Networks", semester=3)
        self._courses = [c_oop, c_fdsa, c_cpi, c_dm, c_fcn]

        # Attendance summary rows as of 2026-09-30
        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId="c_oop", component=ComponentType.LECT, presentCount=14, totalCount=15, portalReportedPercentage=93.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId="c_oop", component=ComponentType.LAB, presentCount=8, totalCount=9, portalReportedPercentage=88.0, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId="c_fdsa", component=ComponentType.LECT, presentCount=28, totalCount=36, portalReportedPercentage=77.0, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId="c_fdsa", component=ComponentType.LAB, presentCount=7, totalCount=11, portalReportedPercentage=63.0, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId="c_cpi", component=ComponentType.LECT, presentCount=8, totalCount=14, portalReportedPercentage=57.0, asOfDate="2026-09-30"),
        ]
        # Total present = 14 + 8 + 28 + 7 + 8 = 65. Total count = 15 + 9 + 36 + 11 + 14 = 85.
        # Computed overall = 65 / 85 = 76.47... -> 76.5%
        # Portal headline is 80.0% to demonstrate the mismatch note
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=80.0, asOfDate="2026-09-30")

        # Daily attendance records
        self._daily = [
            DailyAttendance(studentId=st_id, courseId="c_oop", date="2026-09-29", timeSlot="09:10-10:10", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
            DailyAttendance(studentId=st_id, courseId="c_fdsa", date="2026-09-29", timeSlot="10:15-11:15", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
            DailyAttendance(studentId=st_id, courseId="c_fcn", date="2026-09-30", timeSlot="09:10-10:10", component="LECT", status=DailyAttendanceStatus.P, source="daily_portal"),
            DailyAttendance(studentId=st_id, courseId="c_dm", date="2026-09-30", timeSlot="10:15-11:15", component="LECT", status=DailyAttendanceStatus.UNMARKED, source="daily_portal"),
            DailyAttendance(studentId=st_id, courseId="c_fdsa", date="2026-09-30", timeSlot="11:20-12:20", component="LAB", status=DailyAttendanceStatus.UNMARKED, source="daily_portal"),
        ]

        # Semester 1 result (published Dec 2025, SGPA 7.63, creditsComplete = False)
        sem1_courses = [
            SemesterCourseResult(courseName="Computer Concept and Programming", courseType="THEORY", credits=5.0, grade="B+"),
            SemesterCourseResult(courseName="Basics of Electronics and Electrical Engineering", courseType="THEORY", credits=4.0, grade="A"),
            SemesterCourseResult(courseName="Engineering Mathematics-I", courseType="THEORY", credits=4.0, grade="A"),
        ]
        self._results = [
            SemesterResult(
                studentId=st_id,
                semester=1,
                monthYear="December 2025",
                sgpa=7.63,
                creditsComplete=False,
                totalCreditsDeclared=None,
                source="portal_result",
                courses=sem1_courses,
            )
        ]
        self._assessments = []

    def _setup_s1(self):
        st_id = self._student.id
        c1 = Course(id="c_math1", code="MATH101", shortName="Math-I", fullName="Engineering Mathematics-I", semester=1)
        c2 = Course(id="c_prog1", code="CS101", shortName="Prog-I", fullName="Introduction to Programming", semester=1)
        self._courses = [c1, c2]
        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId="c_math1", component=ComponentType.LECT, presentCount=10, totalCount=12, portalReportedPercentage=83.3, asOfDate="2026-09-30"),
            AttendanceRecord(studentId=st_id, courseId="c_prog1", component=ComponentType.LECT, presentCount=12, totalCount=12, portalReportedPercentage=100.0, asOfDate="2026-09-30"),
        ]
        self._headline = AttendanceHeadline(studentId=st_id, semester=1, portalReportedOverall=91.7, asOfDate="2026-09-30")
        self._results = []
        self._assessments = []

    def _setup_s2(self):
        self._setup_s3()
        st_id = self._student.id
        self._assessments = [
            Assessment(id="ass_oop_1", studentId=st_id, courseId="c_oop", type="Midterm", term="T1", date="2026-09-15", obtainedMarks=15.0, totalMarks=20.0),
            Assessment(id="ass_fdsa_1", studentId=st_id, courseId="c_fdsa", type="Midterm", term="T1", date="2026-09-16", obtainedMarks=12.0, totalMarks=20.0),
            Assessment(id="ass_cpi_1", studentId=st_id, courseId="c_cpi", type="Midterm", term="T1", date="2026-09-17", obtainedMarks=9.0, totalMarks=20.0),
        ]

    def _setup_s4(self):
        st_id = self._student.id
        self._setup_s3()
        self._results = [
            SemesterResult(
                studentId=st_id, semester=1, monthYear="Dec 2024", sgpa=7.20,
                creditsComplete=True, totalCreditsDeclared=24.0, courses=[]
            ),
            SemesterResult(
                studentId=st_id, semester=2, monthYear="May 2025", sgpa=7.80,
                creditsComplete=True, totalCreditsDeclared=26.0, courses=[]
            ),
        ]

    def _setup_s5(self):
        st_id = self._student.id
        self._setup_s3()
        self._results = [
            SemesterResult(
                studentId=st_id, semester=1, monthYear="Dec 2024", sgpa=8.20,
                creditsComplete=True, totalCreditsDeclared=25.0, courses=[]
            ),
            SemesterResult(
                studentId=st_id, semester=2, monthYear="May 2025", sgpa=7.10,
                creditsComplete=True, totalCreditsDeclared=25.0, courses=[]
            ),
        ]
        self._assessments = [
            Assessment(id="a_cpi_1", studentId=st_id, courseId="c_cpi", type="Quiz 1", date="2026-08-10", obtainedMarks=16.0, totalMarks=20.0),
            Assessment(id="a_cpi_2", studentId=st_id, courseId="c_cpi", type="Midterm", date="2026-09-20", obtainedMarks=9.0, totalMarks=20.0),
        ]

    def _setup_s6(self):
        st_id = self._student.id
        self._setup_s3()
        self._assessments = [
            Assessment(id="a_oop_1", studentId=st_id, courseId="c_oop", type="Quiz", date="2026-09-10", obtainedMarks=18.0, totalMarks=20.0),
        ]

    def _setup_s7(self):
        st_id = self._student.id
        c1 = Course(id="c_crit", code="CRIT101", shortName="Critical Course", semester=3)
        self._courses = [c1]
        self._attendance_records = [
            AttendanceRecord(studentId=st_id, courseId="c_crit", component=ComponentType.LECT, presentCount=40, totalCount=70, portalReportedPercentage=57.1, asOfDate="2026-09-30")
        ]
        self._headline = AttendanceHeadline(studentId=st_id, semester=3, portalReportedOverall=57.1, asOfDate="2026-09-30")
        self._results = []
        self._assessments = []

    def _setup_s8(self):
        st_id = self._student.id
        self._setup_s3()
        self._declaration = EngagementDeclaration(studentId=st_id, term="2026-27-ODD", status=EngagementStatus.HAS_EVENTS)
        self._participations = [
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-001", confirmationDate="2026-09-29"),
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-002", confirmationDate="2026-08-15"),
            StudentEventParticipation(studentId=st_id, eventId="EVT-2026-003", confirmationDate="2026-09-13"),
        ]

    def get_profile(self) -> Student:
        return self._student

    def list_courses(self, semester: int) -> list[Course]:
        return [c for c in self._courses if c.semester == semester]

    def get_attendance_summary(
        self, semester: int
    ) -> tuple[list[AttendanceRecord], AttendanceHeadline | None]:
        return self._attendance_records, self._headline

    def get_daily_attendance(
        self, from_date: str | None = None, to_date: str | None = None
    ) -> list[DailyAttendance]:
        return self._daily

    def get_semester_results(self) -> list[SemesterResult]:
        return self._results

    def get_assessments(self) -> list[Assessment]:
        return self._assessments

    def get_participations(self) -> list[StudentEventParticipation]:
        return self._participations

    def get_declaration(self) -> EngagementDeclaration:
        return self._declaration
