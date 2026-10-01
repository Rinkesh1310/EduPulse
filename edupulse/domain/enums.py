from enum import Enum


class ComponentType(str, Enum):
    LECT = "LECT"
    LAB = "LAB"
    OTHER = "OTHER"


class DailyAttendanceStatus(str, Enum):
    P = "P"
    A = "A"
    NT = "NT"
    UNMARKED = "UNMARKED"


class EngagementStatus(str, Enum):
    NOT_PROVIDED = "NOT_PROVIDED"
    DECLARED_NONE = "DECLARED_NONE"
    HAS_EVENTS = "HAS_EVENTS"


class VerificationLevel(str, Enum):
    OFFICIAL_VERIFIED = "OFFICIAL_VERIFIED"
    SECONDARY_ONLY = "SECONDARY_ONLY"
    CONFLICTING = "CONFLICTING"
    UNVERIFIED = "UNVERIFIED"


class CriterionTrack(str, Enum):
    FRESH = "fresh"
    RENEWAL = "renewal"
    ALL = "all"


class CriterionResultStatus(str, Enum):
    MET = "MET"
    NOT_MET = "NOT_MET"
    UNKNOWN = "UNKNOWN"


class EvidenceBasis(str, Enum):
    OFFICIAL_IMPORT = "official_import"
    APP_ESTIMATE = "app_estimate"
    SELF_DECLARED = "self_declared"


class SupportLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    NEEDS_MORE_DATA = "Needs more data"


class AttendanceBand(str, Enum):
    STRONG = "Strong"
    MONITOR = "Monitor"
    ATTENTION = "Attention area"
    EARLY_DATA = "Early data"


class AcademicBand(str, Enum):
    STRONG = "Strong"
    MONITOR = "Monitor"
    ATTENTION = "Attention area"


class TrendDirection(str, Enum):
    IMPROVING = "Improving"
    DECLINING = "Declining"
    STABLE = "Stable"
    NOT_ENOUGH_HISTORY = "Not enough history"
    NOT_AVAILABLE = "Trend not available"


class CoverageStatus(str, Enum):
    COMPLETE = "Complete"
    PARTIAL = "Partial"
    WAITING = "Waiting"
