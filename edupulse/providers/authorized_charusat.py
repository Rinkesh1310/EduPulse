from typing import Any

from edupulse.domain.models import (
    AttendanceHeadline,
    AttendanceRecord,
    Course,
    DailyAttendance,
    SemesterResult,
    Student,
)
from edupulse.providers.base import AcademicDataProvider, NotAuthorizedError


class AuthorizedCharusatProvider(AcademicDataProvider):
    """Stub provider representing an official, sanctioned university integration.
    
    SECURITY NOTICE:
    In accordance with Security Boundary Rule 0.1, EduPulse does NOT store university credentials,
    does NOT automate or scrape portals, and does NOT bypass authentication or CAPTCHAs.
    This provider is feature-flagged OFF and raises NotAuthorizedError on every operation.
    """

    FEATURE_FLAG_ENABLED = False

    def __init__(self):
        # Always disabled without official institutional agreement and OAuth/SSO
        pass

    def capabilities(self) -> dict[str, bool]:
        return {
            "supports_live": False,
            "supports_daily": False,
            "supports_results": False,
            "is_authorized": False,
            "requires_university_sso": True,
        }

    def _guard(self):
        raise NotAuthorizedError(
            "AuthorizedCharusatProvider requires an official university-sanctioned API/SSO/export; "
            "future architecture, not available today. Security boundary prevents portal scraping."
        )

    def get_profile(self) -> Student:
        self._guard()

    def list_courses(self, semester: int) -> list[Course]:
        self._guard()

    def get_attendance_summary(
        self, semester: int
    ) -> tuple[list[AttendanceRecord], AttendanceHeadline | None]:
        self._guard()

    def get_daily_attendance(
        self, from_date: str | None = None, to_date: str | None = None
    ) -> list[DailyAttendance]:
        self._guard()

    def get_semester_results(self) -> list[SemesterResult]:
        self._guard()

    def source_metadata(self) -> dict[str, Any]:
        return {
            "source": "AuthorizedCharusatProvider (stub)",
            "status": "Disabled / Stub Only",
            "reason": "Requires official university-sanctioned API/SSO/export",
        }
