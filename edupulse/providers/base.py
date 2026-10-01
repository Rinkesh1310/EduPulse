from abc import ABC, abstractmethod
from typing import Any

from edupulse.domain.models import (
    AttendanceHeadline,
    AttendanceRecord,
    Course,
    DailyAttendance,
    SemesterResult,
    Student,
)


class NotAuthorizedError(Exception):
    """Raised when an unauthorized university integration attempt is made."""


class AcademicDataProvider(ABC):
    """Abstract base provider for accessing academic data."""

    @abstractmethod
    def capabilities(self) -> dict[str, bool]:
        """Returns feature capabilities of the provider."""

    @abstractmethod
    def get_profile(self) -> Student:
        """Returns the student profile."""

    @abstractmethod
    def list_courses(self, semester: int) -> list[Course]:
        """Returns courses for the given semester."""

    @abstractmethod
    def get_attendance_summary(
        self, semester: int
    ) -> tuple[list[AttendanceRecord], AttendanceHeadline | None]:
        """Returns attendance component records and headline percentage."""

    @abstractmethod
    def get_daily_attendance(
        self, from_date: str | None = None, to_date: str | None = None
    ) -> list[DailyAttendance]:
        """Returns daily attendance records."""

    @abstractmethod
    def get_semester_results(self) -> list[SemesterResult]:
        """Returns historical semester results."""

    @abstractmethod
    def source_metadata(self) -> dict[str, Any]:
        """Returns source provenance and audit metadata."""
