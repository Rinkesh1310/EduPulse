import pytest

from edupulse.domain.enums import DailyAttendanceStatus
from edupulse.providers.authorized_charusat import AuthorizedCharusatProvider
from edupulse.providers.base import NotAuthorizedError
from edupulse.providers.file_import import FileImportProvider
from edupulse.providers.mock import MockAcademicProvider
from edupulse.providers.paste_import import PasteImportProvider
from edupulse.storage.repository import StudentRepository
from edupulse.storage.seed import seed_scenario_data


def test_authorized_charusat_provider_raises_not_authorized():
    provider = AuthorizedCharusatProvider()
    caps = provider.capabilities()
    assert caps["is_authorized"] is False
    assert caps["requires_university_sso"] is True

    with pytest.raises(NotAuthorizedError, match="requires an official university-sanctioned API/SSO/export"):
        provider.get_profile()

    with pytest.raises(NotAuthorizedError):
        provider.list_courses(3)

    with pytest.raises(NotAuthorizedError):
        provider.get_attendance_summary(3)

    with pytest.raises(NotAuthorizedError):
        provider.get_daily_attendance()

    with pytest.raises(NotAuthorizedError):
        provider.get_semester_results()


def test_mock_scenarios_load_and_s3_persona():
    # S3 Persona checks
    p_s3 = MockAcademicProvider("S3")
    student = p_s3.get_profile()
    assert student.name == "Demo Student"
    assert student.externalStudentId == "DEMO-S3-001"

    records, headline = p_s3.get_attendance_summary(3)
    assert len(records) == 5
    tot_p = sum(r.presentCount for r in records)
    tot_c = sum(r.totalCount for r in records)
    assert tot_p == 65
    assert tot_c == 85
    assert headline is not None
    assert headline.portalReportedOverall == 80.0

    # Test all scenarios initialize without error
    for s_id in ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"]:
        prov = MockAcademicProvider(s_id)
        assert prov.get_profile() is not None
        assert prov.capabilities()["is_mock"] is True


def test_seed_scenario_data_in_storage():
    seed_scenario_data("S3", reset=True)
    repo = StudentRepository()
    try:
        st = repo.get_student("student_s3")
        assert st is not None
        assert st.name == "Demo Student"

        courses = repo.list_courses(st.id, semester=3)
        assert len(courses) >= 5

        records = repo.get_attendance_records(st.id)
        assert len(records) == 5

        headline = repo.get_attendance_headline(st.id, 3)
        assert headline is not None
        assert headline.portalReportedOverall == 80.0

        daily = repo.get_daily_attendance(st.id)
        assert len(daily) >= 5

        # Check Sem 1 result exists, Sem 2 absent
        results = repo.get_semester_results(st.id)
        assert len(results) == 1
        assert results[0].semester == 1
        assert results[0].sgpa == 7.63
        assert results[0].creditsComplete is False

        # Events catalogue loaded
        events = repo.get_events()
        assert len(events) >= 10
    finally:
        repo.close()


def test_file_import_provider_valid_and_row_errors():
    # 1. Download templates
    att_template = FileImportProvider.generate_attendance_csv_template()
    assert "course_code" in att_template
    assert "CEUE203" in att_template

    # 2. Preview valid CSV
    preview_valid = FileImportProvider.preview_attendance_csv(att_template, "student_test")
    assert preview_valid["valid"] is True
    assert preview_valid["rowCount"] == 5
    assert len(preview_valid["errors"]) == 0

    # 3. Preview invalid CSV with row-level errors
    bad_csv = (
        "course_code,component,present_count,total_count\n"
        "CEUE203,LECT,16,15\n"      # present > total
        "CSUC201,INVALID,-2,10\n"    # invalid component & negative count
        "HSUV201,LAB,abc,20\n"       # non-integer
    )
    preview_bad = FileImportProvider.preview_attendance_csv(bad_csv, "student_test")
    assert preview_bad["valid"] is False
    assert len(preview_bad["errors"]) >= 3
    assert any("exceeds total_count" in err for err in preview_bad["errors"])
    assert any("Invalid component" in err for err in preview_bad["errors"])
    assert any("must be integers" in err for err in preview_bad["errors"])


def test_paste_import_provider_valid_and_unmarked():
    pasted_text = (
        "CEUE203 / OOP | LECT | 14 / 15 | 93.3%\n"
        "CSUC201 / FDSA | LAB | 7 / 11 | 63.6%\n"
    )
    res = PasteImportProvider.parse_attendance_paste(pasted_text, "student_test")
    assert res["valid"] is True
    assert len(res["records"]) == 2
    assert res["records"][0].presentCount == 14
    assert res["records"][0].totalCount == 15

    # Daily timetable paste with '-' mapped to UNMARKED
    daily_paste = (
        "09:10-10:10 | CEUE203 / OOP | P\n"
        "10:15-11:15 | MSUD203 / DM | -\n"
        "11:20-12:20 | CSUC201 / FDSA | A\n"
    )
    daily_res = PasteImportProvider.parse_daily_timetable_paste(daily_paste, "student_test", default_date="2026-09-30")
    assert daily_res["valid"] is True
    assert len(daily_res["records"]) == 3
    assert daily_res["records"][0].status == DailyAttendanceStatus.P
    assert daily_res["records"][1].status == DailyAttendanceStatus.UNMARKED
    assert daily_res["records"][2].status == DailyAttendanceStatus.A
