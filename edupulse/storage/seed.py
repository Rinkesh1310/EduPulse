import json
from pathlib import Path

from edupulse.domain.models import Event
from edupulse.providers.mock import MockAcademicProvider
from edupulse.storage.repository import StudentRepository, init_db, reset_db


def seed_events_catalogue(repo: StudentRepository | None = None):
    r = repo or StudentRepository()
    events_json_path = Path(__file__).parent.parent / "config" / "events_demo.json"
    if events_json_path.exists():
        data = json.loads(events_json_path.read_text(encoding="utf-8"))
        for item in data:
            evt = Event(**item)
            r.save_event(evt)
    if not repo:
        r.close()


def _seed_single_mock(repo: StudentRepository, scenario_key: str):
    mock = MockAcademicProvider(scenario_key)
    student = mock.get_profile()
    repo.save_student(student)

    # Courses
    for c in mock.list_courses(student.semester):
        repo.save_course(student.id, c)

    # Attendance summary & headline
    records, headline = mock.get_attendance_summary(student.semester)
    for rec in records:
        repo.save_attendance_record(rec)
    if headline:
        repo.save_attendance_headline(headline)

    # Daily attendance
    daily_records = mock.get_daily_attendance()
    repo.save_daily_attendance(daily_records)

    # Semester results
    results = mock.get_semester_results()
    for res in results:
        repo.save_semester_result(res)

    # Assessments
    for ass in mock.get_assessments():
        repo.save_assessment(ass)

    # Participations & declaration
    for part in mock.get_participations():
        repo.save_participation(part)
    repo.save_engagement_declaration(mock.get_declaration())


def seed_all_demo_personas(reset: bool = True):
    """Seeds all 6 synthetic student personas PLUS the screenshot reference scenario (S3)."""
    if reset:
        reset_db()
    else:
        init_db()

    repo = StudentRepository()
    try:
        seed_events_catalogue(repo)

        scenarios = [
            "SYNTH_STRONG",
            "SYNTH_ATT_CONCERN",
            "SYNTH_ACAD_CONCERN",
            "SYNTH_EARLY",
            "SYNTH_IMPROVING",
            "SYNTH_ENGAGED",
            "S3",  # Screenshot Reference validation persona
        ]
        for key in scenarios:
            _seed_single_mock(repo, key)
    finally:
        repo.close()


def seed_scenario_data(scenario_id: str = "ALL", reset: bool = True):
    """Initializes the database and seeds it with data from the specified scenario or all personas."""
    if scenario_id.upper() == "ALL":
        seed_all_demo_personas(reset=reset)
        return

    if reset:
        reset_db()
    else:
        init_db()

    repo = StudentRepository()
    try:
        seed_events_catalogue(repo)
        _seed_single_mock(repo, scenario_id)
    finally:
        repo.close()
