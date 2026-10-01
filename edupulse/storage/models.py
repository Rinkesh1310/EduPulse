import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from edupulse.storage.database import Base


class StudentDB(Base):
    __tablename__ = "students"

    id = Column(String(64), primary_key=True)
    external_student_id = Column(String(64), nullable=False)
    name = Column(String(128), default="Demo Student", nullable=False)
    program = Column(String(128), default="B.Tech IT (demo)", nullable=False)
    semester = Column(Integer, default=3, nullable=False)
    academic_year = Column(String(32), default="2026-27", nullable=False)
    created_at = Column(String(32), default=lambda: datetime.datetime.now().isoformat())


class CourseDB(Base):
    __tablename__ = "courses"

    id = Column(String(64), primary_key=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    code = Column(String(32), nullable=False)
    short_name = Column(String(64), nullable=False)
    full_name = Column(String(256), nullable=True)
    course_type = Column(String(32), default="THEORY", nullable=False)
    credits = Column(Float, nullable=True)
    semester = Column(Integer, default=3, nullable=False)


class AttendanceRecordDB(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    course_id = Column(String(64), nullable=False)
    component = Column(String(16), nullable=False)  # LECT, LAB, OTHER
    present_count = Column(Integer, nullable=False)
    total_count = Column(Integer, nullable=False)
    portal_reported_percentage = Column(Float, nullable=True)
    as_of_date = Column(String(32), nullable=False)
    source = Column(String(64), default="mock", nullable=False)
    import_batch_id = Column(String(64), nullable=True)

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", "component", name="uq_student_course_component"),
    )


class AttendanceHeadlineDB(Base):
    __tablename__ = "attendance_headlines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    portal_reported_overall = Column(Float, nullable=False)
    as_of_date = Column(String(32), nullable=False)
    source = Column(String(64), default="portal_header", nullable=False)


class DailyAttendanceDB(Base):
    __tablename__ = "daily_attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    course_id = Column(String(64), nullable=False)
    date = Column(String(32), nullable=False)
    time_slot = Column(String(32), nullable=True)
    component = Column(String(16), nullable=True)
    status = Column(String(16), nullable=False)  # P, A, NT, UNMARKED
    source = Column(String(64), default="daily_import", nullable=False)


class SemesterResultDB(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    month_year = Column(String(32), nullable=False)
    sgpa = Column(Float, nullable=False)
    credits_complete = Column(Boolean, default=False, nullable=False)
    total_credits_declared = Column(Float, nullable=True)
    source = Column(String(64), default="portal_result", nullable=False)
    published_at = Column(String(32), nullable=True)


class SemesterCourseResultDB(Base):
    __tablename__ = "semester_course_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    semester_result_id = Column(Integer, ForeignKey("semester_results.id"), nullable=False)
    course_name = Column(String(256), nullable=False)
    course_type = Column(String(32), default="THEORY", nullable=False)
    credits = Column(Float, nullable=False)
    grade = Column(String(16), nullable=False)
    grade_point = Column(Float, nullable=True)


class AssessmentDB(Base):
    __tablename__ = "assessments"

    id = Column(String(64), primary_key=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    course_id = Column(String(64), nullable=False)
    type = Column(String(64), nullable=False)
    term = Column(String(32), nullable=True)
    date = Column(String(32), nullable=False)
    obtained_marks = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)


class EventDB(Base):
    __tablename__ = "events"

    event_id = Column(String(64), primary_key=True)
    name = Column(String(256), nullable=False)
    date = Column(String(32), nullable=False)
    end_date = Column(String(32), nullable=True)
    activity_type = Column(String(64), nullable=False)
    duration_type = Column(String(32), nullable=False)
    hours = Column(Float, nullable=True)
    organizer = Column(String(128), nullable=False)
    source = Column(String(64), default="demo catalogue", nullable=False)


class StudentEventParticipationDB(Base):
    __tablename__ = "student_event_participations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    event_id = Column(String(64), ForeignKey("events.event_id"), nullable=False)
    confirmed = Column(Boolean, default=True, nullable=False)
    confirmation_date = Column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "event_id", name="uq_student_event"),
    )


class EngagementDeclarationDB(Base):
    __tablename__ = "engagement_declarations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    term = Column(String(32), nullable=False)
    status = Column(String(32), default="NOT_PROVIDED", nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "term", name="uq_student_term_declaration"),
    )


class UserAttestedFactDB(Base):
    __tablename__ = "user_attested_facts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(64), ForeignKey("students.id"), nullable=False)
    key = Column(String(64), nullable=False)
    value_json = Column(Text, nullable=False)
    attested_at = Column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "key", name="uq_student_attested_key"),
    )


class ImportBatchDB(Base):
    __tablename__ = "import_batches"

    id = Column(String(64), primary_key=True)
    source = Column(String(64), nullable=False)
    timestamp = Column(String(32), nullable=False)
    row_count = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)
    errors_json = Column(Text, default="[]", nullable=False)
