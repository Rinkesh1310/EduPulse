import json
from typing import Any

from sqlalchemy.orm import Session

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
    Event,
    ImportBatch,
    SemesterCourseResult,
    SemesterResult,
    Student,
    StudentEventParticipation,
    UserAttestedFact,
)
from edupulse.storage.database import Base, SessionLocal, engine
from edupulse.storage.models import (
    AssessmentDB,
    AttendanceHeadlineDB,
    AttendanceRecordDB,
    CourseDB,
    DailyAttendanceDB,
    EngagementDeclarationDB,
    EventDB,
    ImportBatchDB,
    SemesterCourseResultDB,
    SemesterResultDB,
    StudentDB,
    StudentEventParticipationDB,
    UserAttestedFactDB,
)


def init_db():
    Base.metadata.create_all(bind=engine)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


class StudentRepository:
    def __init__(self, session: Session | None = None):
        self._session = session or SessionLocal()
        self._external_session = session is not None

    def close(self):
        if not self._external_session:
            self._session.close()

    def get_student(self, student_id: str) -> Student | None:
        db_s = self._session.query(StudentDB).filter(StudentDB.id == student_id).first()
        if not db_s:
            return None
        return Student(
            id=db_s.id,
            externalStudentId=db_s.external_student_id,
            name=db_s.name,
            program=db_s.program,
            semester=db_s.semester,
            academicYear=db_s.academic_year,
        )

    def save_student(self, student: Student) -> Student:
        existing = self._session.query(StudentDB).filter(StudentDB.id == student.id).first()
        if existing:
            existing.external_student_id = student.externalStudentId
            existing.name = student.name
            existing.program = student.program
            existing.semester = student.semester
            existing.academic_year = student.academicYear
        else:
            new_s = StudentDB(
                id=student.id,
                external_student_id=student.externalStudentId,
                name=student.name,
                program=student.program,
                semester=student.semester,
                academic_year=student.academicYear,
            )
            self._session.add(new_s)
        self._session.commit()
        return student

    def list_students(self) -> list[Student]:
        rows = self._session.query(StudentDB).all()
        return [
            Student(
                id=db_s.id,
                externalStudentId=db_s.external_student_id,
                name=db_s.name,
                program=db_s.program,
                semester=db_s.semester,
                academicYear=db_s.academic_year,
            )
            for db_s in rows
        ]

    def list_courses(self, student_id: str, semester: int | None = None) -> list[Course]:
        q = self._session.query(CourseDB).filter(CourseDB.student_id == student_id)
        if semester is not None:
            q = q.filter(CourseDB.semester == semester)
        rows = q.all()
        return [
            Course(
                id=r.id,
                code=r.code,
                shortName=r.short_name,
                fullName=r.full_name,
                courseType=r.course_type,
                credits=r.credits,
                semester=r.semester,
            )
            for r in rows
        ]

    def save_course(self, student_id: str, course: Course):
        existing = self._session.query(CourseDB).filter(CourseDB.id == course.id, CourseDB.student_id == student_id).first()
        if existing:
            existing.code = course.code
            existing.short_name = course.shortName
            existing.full_name = course.fullName
            existing.course_type = course.courseType
            existing.credits = course.credits
            existing.semester = course.semester
        else:
            new_c = CourseDB(
                id=course.id,
                student_id=student_id,
                code=course.code,
                short_name=course.shortName,
                full_name=course.fullName,
                course_type=course.courseType,
                credits=course.credits,
                semester=course.semester,
            )
            self._session.add(new_c)
        self._session.commit()

    def get_attendance_records(self, student_id: str) -> list[AttendanceRecord]:
        rows = self._session.query(AttendanceRecordDB).filter(AttendanceRecordDB.student_id == student_id).all()
        return [
            AttendanceRecord(
                studentId=r.student_id,
                courseId=r.course_id,
                component=ComponentType(r.component),
                presentCount=r.present_count,
                totalCount=r.total_count,
                portalReportedPercentage=r.portal_reported_percentage,
                asOfDate=r.as_of_date,
                source=r.source,
                importBatchId=r.import_batch_id,
            )
            for r in rows
        ]

    def save_attendance_record(self, record: AttendanceRecord):
        existing = (
            self._session.query(AttendanceRecordDB)
            .filter(
                AttendanceRecordDB.student_id == record.studentId,
                AttendanceRecordDB.course_id == record.courseId,
                AttendanceRecordDB.component == record.component.value,
            )
            .first()
        )
        if existing:
            existing.present_count = record.presentCount
            existing.total_count = record.totalCount
            existing.portal_reported_percentage = record.portalReportedPercentage
            existing.as_of_date = record.asOfDate
            existing.source = record.source
            existing.import_batch_id = record.importBatchId
        else:
            new_r = AttendanceRecordDB(
                student_id=record.studentId,
                course_id=record.courseId,
                component=record.component.value,
                present_count=record.presentCount,
                total_count=record.totalCount,
                portal_reported_percentage=record.portalReportedPercentage,
                as_of_date=record.asOfDate,
                source=record.source,
                import_batch_id=record.importBatchId,
            )
            self._session.add(new_r)
        self._session.commit()

    def get_attendance_headline(self, student_id: str, semester: int) -> AttendanceHeadline | None:
        row = (
            self._session.query(AttendanceHeadlineDB)
            .filter(
                AttendanceHeadlineDB.student_id == student_id,
                AttendanceHeadlineDB.semester == semester,
            )
            .first()
        )
        if not row:
            return None
        return AttendanceHeadline(
            studentId=row.student_id,
            semester=row.semester,
            portalReportedOverall=row.portal_reported_overall,
            asOfDate=row.as_of_date,
            source=row.source,
        )

    def save_attendance_headline(self, headline: AttendanceHeadline):
        existing = (
            self._session.query(AttendanceHeadlineDB)
            .filter(
                AttendanceHeadlineDB.student_id == headline.studentId,
                AttendanceHeadlineDB.semester == headline.semester,
            )
            .first()
        )
        if existing:
            existing.portal_reported_overall = headline.portalReportedOverall
            existing.as_of_date = headline.asOfDate
            existing.source = headline.source
        else:
            self._session.add(
                AttendanceHeadlineDB(
                    student_id=headline.studentId,
                    semester=headline.semester,
                    portal_reported_overall=headline.portalReportedOverall,
                    as_of_date=headline.asOfDate,
                    source=headline.source,
                )
            )
        self._session.commit()

    def get_daily_attendance(
        self, student_id: str, from_date: str | None = None, to_date: str | None = None
    ) -> list[DailyAttendance]:
        q = self._session.query(DailyAttendanceDB).filter(DailyAttendanceDB.student_id == student_id)
        if from_date:
            q = q.filter(DailyAttendanceDB.date >= from_date)
        if to_date:
            q = q.filter(DailyAttendanceDB.date <= to_date)
        rows = q.order_by(DailyAttendanceDB.date.asc()).all()
        return [
            DailyAttendance(
                studentId=r.student_id,
                courseId=r.course_id,
                date=r.date,
                timeSlot=r.time_slot,
                component=r.component,
                status=DailyAttendanceStatus(r.status),
                source=r.source,
            )
            for r in rows
        ]

    def save_daily_attendance(self, records: list[DailyAttendance]):
        for r in records:
            self._session.add(
                DailyAttendanceDB(
                    student_id=r.studentId,
                    course_id=r.courseId,
                    date=r.date,
                    time_slot=r.timeSlot,
                    component=r.component,
                    status=r.status.value,
                    source=r.source,
                )
            )
        self._session.commit()

    def get_semester_results(self, student_id: str) -> list[SemesterResult]:
        rows = (
            self._session.query(SemesterResultDB)
            .filter(SemesterResultDB.student_id == student_id)
            .order_by(SemesterResultDB.semester.asc())
            .all()
        )
        results = []
        for r in rows:
            course_rows = (
                self._session.query(SemesterCourseResultDB)
                .filter(SemesterCourseResultDB.semester_result_id == r.id)
                .all()
            )
            courses = [
                SemesterCourseResult(
                    courseName=cr.course_name,
                    courseType=cr.course_type,
                    credits=cr.credits,
                    grade=cr.grade,
                    gradePoint=cr.grade_point,
                )
                for cr in course_rows
            ]
            results.append(
                SemesterResult(
                    studentId=r.student_id,
                    semester=r.semester,
                    monthYear=r.month_year,
                    sgpa=r.sgpa,
                    creditsComplete=r.credits_complete,
                    totalCreditsDeclared=r.total_credits_declared,
                    source=r.source,
                    publishedAt=r.published_at,
                    courses=courses,
                )
            )
        return results

    def save_semester_result(self, result: SemesterResult):
        # Remove previous result for same semester if any
        prev = (
            self._session.query(SemesterResultDB)
            .filter(
                SemesterResultDB.student_id == result.studentId,
                SemesterResultDB.semester == result.semester,
            )
            .first()
        )
        if prev:
            self._session.query(SemesterCourseResultDB).filter(
                SemesterCourseResultDB.semester_result_id == prev.id
            ).delete()
            self._session.delete(prev)
            self._session.commit()

        new_res = SemesterResultDB(
            student_id=result.studentId,
            semester=result.semester,
            month_year=result.monthYear,
            sgpa=result.sgpa,
            credits_complete=result.creditsComplete,
            total_credits_declared=result.totalCreditsDeclared,
            source=result.source,
            published_at=result.publishedAt,
        )
        self._session.add(new_res)
        self._session.flush()

        for c in result.courses:
            self._session.add(
                SemesterCourseResultDB(
                    semester_result_id=new_res.id,
                    course_name=c.courseName,
                    course_type=c.courseType,
                    credits=c.credits,
                    grade=c.grade,
                    grade_point=c.gradePoint,
                )
            )
        self._session.commit()

    def get_assessments(self, student_id: str, course_id: str | None = None) -> list[Assessment]:
        q = self._session.query(AssessmentDB).filter(AssessmentDB.student_id == student_id)
        if course_id:
            q = q.filter(AssessmentDB.course_id == course_id)
        rows = q.order_by(AssessmentDB.date.asc()).all()
        return [
            Assessment(
                id=r.id,
                studentId=r.student_id,
                courseId=r.course_id,
                type=r.type,
                term=r.term,
                date=r.date,
                obtainedMarks=r.obtained_marks,
                totalMarks=r.total_marks,
            )
            for r in rows
        ]

    def save_assessment(self, assessment: Assessment):
        existing = self._session.query(AssessmentDB).filter(AssessmentDB.id == assessment.id).first()
        if existing:
            existing.course_id = assessment.courseId
            existing.type = assessment.type
            existing.term = assessment.term
            existing.date = assessment.date
            existing.obtained_marks = assessment.obtainedMarks
            existing.total_marks = assessment.totalMarks
        else:
            self._session.add(
                AssessmentDB(
                    id=assessment.id,
                    student_id=assessment.studentId,
                    course_id=assessment.courseId,
                    type=assessment.type,
                    term=assessment.term,
                    date=assessment.date,
                    obtained_marks=assessment.obtainedMarks,
                    total_marks=assessment.totalMarks,
                )
            )
        self._session.commit()

    def delete_assessment(self, assessment_id: str):
        self._session.query(AssessmentDB).filter(AssessmentDB.id == assessment_id).delete()
        self._session.commit()

    def get_events(self) -> list[Event]:
        rows = self._session.query(EventDB).order_by(EventDB.date.asc()).all()
        return [
            Event(
                eventId=r.event_id,
                name=r.name,
                date=r.date,
                endDate=r.end_date,
                activityType=r.activity_type,
                durationType=r.duration_type,
                hours=r.hours,
                organizer=r.organizer,
                source=r.source,
            )
            for r in rows
        ]

    def save_event(self, event: Event):
        existing = self._session.query(EventDB).filter(EventDB.event_id == event.eventId).first()
        if existing:
            existing.name = event.name
            existing.date = event.date
            existing.end_date = event.endDate
            existing.activity_type = event.activityType
            existing.duration_type = event.durationType
            existing.hours = event.hours
            existing.organizer = event.organizer
            existing.source = event.source
        else:
            self._session.add(
                EventDB(
                    event_id=event.eventId,
                    name=event.name,
                    date=event.date,
                    end_date=event.endDate,
                    activity_type=event.activityType,
                    duration_type=event.durationType,
                    hours=event.hours,
                    organizer=event.organizer,
                    source=event.source,
                )
            )
        self._session.commit()

    def get_participations(self, student_id: str) -> list[StudentEventParticipation]:
        rows = (
            self._session.query(StudentEventParticipationDB)
            .filter(StudentEventParticipationDB.student_id == student_id)
            .all()
        )
        return [
            StudentEventParticipation(
                studentId=r.student_id,
                eventId=r.event_id,
                confirmed=r.confirmed,
                confirmationDate=r.confirmation_date,
            )
            for r in rows
        ]

    def save_participation(self, part: StudentEventParticipation):
        existing = (
            self._session.query(StudentEventParticipationDB)
            .filter(
                StudentEventParticipationDB.student_id == part.studentId,
                StudentEventParticipationDB.event_id == part.eventId,
            )
            .first()
        )
        if existing:
            existing.confirmed = part.confirmed
            existing.confirmation_date = part.confirmationDate
        else:
            self._session.add(
                StudentEventParticipationDB(
                    student_id=part.studentId,
                    event_id=part.eventId,
                    confirmed=part.confirmed,
                    confirmation_date=part.confirmationDate,
                )
            )
        self._session.commit()

    def remove_participation(self, student_id: str, event_id: str):
        self._session.query(StudentEventParticipationDB).filter(
            StudentEventParticipationDB.student_id == student_id,
            StudentEventParticipationDB.event_id == event_id,
        ).delete()
        self._session.commit()

    def get_engagement_declaration(self, student_id: str, term: str) -> EngagementDeclaration:
        row = (
            self._session.query(EngagementDeclarationDB)
            .filter(
                EngagementDeclarationDB.student_id == student_id,
                EngagementDeclarationDB.term == term,
            )
            .first()
        )
        if not row:
            return EngagementDeclaration(studentId=student_id, term=term, status=EngagementStatus.NOT_PROVIDED)
        return EngagementDeclaration(
            studentId=row.student_id,
            term=row.term,
            status=EngagementStatus(row.status),
        )

    def save_engagement_declaration(self, decl: EngagementDeclaration):
        existing = (
            self._session.query(EngagementDeclarationDB)
            .filter(
                EngagementDeclarationDB.student_id == decl.studentId,
                EngagementDeclarationDB.term == decl.term,
            )
            .first()
        )
        if existing:
            existing.status = decl.status.value
        else:
            self._session.add(
                EngagementDeclarationDB(
                    student_id=decl.studentId,
                    term=decl.term,
                    status=decl.status.value,
                )
            )
        self._session.commit()

    def get_attested_facts(self, student_id: str) -> dict[str, Any]:
        rows = (
            self._session.query(UserAttestedFactDB)
            .filter(UserAttestedFactDB.student_id == student_id)
            .all()
        )
        result = {}
        for r in rows:
            try:
                result[r.key] = json.loads(r.value_json)
            except Exception:
                result[r.key] = r.value_json
        return result

    def save_attested_fact(self, fact: UserAttestedFact):
        val_json = json.dumps(fact.value)
        existing = (
            self._session.query(UserAttestedFactDB)
            .filter(
                UserAttestedFactDB.student_id == fact.studentId,
                UserAttestedFactDB.key == fact.key,
            )
            .first()
        )
        if existing:
            existing.value_json = val_json
            existing.attested_at = fact.attestedAt
        else:
            self._session.add(
                UserAttestedFactDB(
                    student_id=fact.studentId,
                    key=fact.key,
                    value_json=val_json,
                    attested_at=fact.attestedAt,
                )
            )
        self._session.commit()

    def save_import_batch(self, batch: ImportBatch):
        existing = self._session.query(ImportBatchDB).filter(ImportBatchDB.id == batch.id).first()
        if existing:
            existing.source = batch.source
            existing.timestamp = batch.timestamp
            existing.row_count = batch.rowCount
            existing.checksum = batch.checksum
            existing.status = batch.status
            existing.errors_json = json.dumps(batch.errors)
        else:
            self._session.add(
                ImportBatchDB(
                    id=batch.id,
                    source=batch.source,
                    timestamp=batch.timestamp,
                    row_count=batch.rowCount,
                    checksum=batch.checksum,
                    status=batch.status,
                    errors_json=json.dumps(batch.errors),
                )
            )
        self._session.commit()

    def get_import_batches(self) -> list[ImportBatch]:
        rows = self._session.query(ImportBatchDB).order_by(ImportBatchDB.timestamp.desc()).all()
        return [
            ImportBatch(
                id=r.id,
                source=r.source,
                timestamp=r.timestamp,
                rowCount=r.row_count,
                checksum=r.checksum,
                status=r.status,
                errors=json.loads(r.errors_json) if r.errors_json else [],
            )
            for r in rows
        ]
