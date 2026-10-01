from typing import Any

from edupulse.domain.enums import EngagementStatus
from edupulse.domain.models import Event, StudentEventParticipation

DEFAULT_WEIGHTS = {
    "hackathon": 3.0,
    "competition": 3.0,
    "project": 3.0,
    "workshop": 2.0,
    "academic_activity": 2.0,
    "seminar": 1.0,
    "club": 1.0,
}


def calculate_event_points(
    event: Event,
    weights: dict[str, float] | None = None,
) -> float:
    """Calculates points for a single event: points = type_weight * duration_factor.
    
    Duration factor:
      - full-day: 1.0
      - hours: min(hours / 4.0, 1.0) with floor 0.25
    """
    w_map = weights or DEFAULT_WEIGHTS
    type_weight = w_map.get(event.activityType.lower(), 1.0)

    if event.durationType == "full-day":
        duration_factor = 1.0
    else:
        hrs = event.hours or 1.0
        duration_factor = max(0.25, min(hrs / 4.0, 1.0))

    return round(type_weight * duration_factor, 2)


def evaluate_engagement_summary(
    participations: list[StudentEventParticipation],
    events_by_id: dict[str, Event],
    declaration_status: EngagementStatus = EngagementStatus.NOT_PROVIDED,
    official_attendance_p_dates: set[str] | None = None,
) -> dict[str, Any]:
    """Evaluates student engagement based on confirmed events and declaration status.
    
    States:
      - NOT_PROVIDED: "Insufficient data"
      - DECLARED_NONE: "No participation recorded (informational)"
      - HAS_EVENTS: Level determined by points, event count, and activity type diversity.
      
    Levels:
      - 1-2 events or <4 points: "Getting started"
      - >=4 points or >=3 events: "Active"
      - >=10 points across >=3 distinct activity types: "Highly active"
      
    Engagement NEVER raises support signals; it provides positive indicators/context only.
    """
    if declaration_status == EngagementStatus.NOT_PROVIDED and not participations:
        return {
            "status": EngagementStatus.NOT_PROVIDED.value,
            "level": "Insufficient data",
            "points": 0.0,
            "eventCount": 0,
            "diversityCount": 0,
            "distinctTypes": [],
            "overlaps": [],
            "description": "No engagement or participation data provided yet.",
        }

    if declaration_status == EngagementStatus.DECLARED_NONE and not participations:
        return {
            "status": EngagementStatus.DECLARED_NONE.value,
            "level": "No participation recorded (informational)",
            "points": 0.0,
            "eventCount": 0,
            "diversityCount": 0,
            "distinctTypes": [],
            "overlaps": [],
            "description": "Student declared no extra-curricular or co-curricular participation for this term.",
        }

    confirmed_participations = [p for p in participations if p.confirmed]
    if not confirmed_participations:
        return {
            "status": declaration_status.value,
            "level": "Insufficient data" if declaration_status == EngagementStatus.NOT_PROVIDED else "No participation recorded (informational)",
            "points": 0.0,
            "eventCount": 0,
            "diversityCount": 0,
            "distinctTypes": [],
            "overlaps": [],
            "description": "No confirmed events.",
        }

    total_points = 0.0
    distinct_types: set[str] = set()
    overlaps: list[dict[str, str]] = []
    p_dates = official_attendance_p_dates or set()

    for part in confirmed_participations:
        evt = events_by_id.get(part.eventId)
        if not evt:
            continue
        pts = calculate_event_points(evt)
        total_points += pts
        distinct_types.add(evt.activityType.lower())

        if evt.date in p_dates:
            overlaps.append({
                "eventId": evt.eventId,
                "name": evt.name,
                "date": evt.date,
                "note": "Counted in official attendance; adds to engagement only",
            })

    total_points = round(total_points, 1)
    event_count = len(confirmed_participations)
    diversity_count = len(distinct_types)

    # Classify level
    if total_points >= 10.0 and diversity_count >= 3:
        level = "Highly active"
        desc = ">=10 points across >=3 distinct activity types"
    elif total_points >= 4.0 or event_count >= 3:
        level = "Active"
        desc = ">=4 points or >=3 events"
    else:
        level = "Getting started"
        desc = "1–2 events or <4 points"

    return {
        "status": EngagementStatus.HAS_EVENTS.value,
        "level": level,
        "points": total_points,
        "eventCount": event_count,
        "diversityCount": diversity_count,
        "distinctTypes": sorted(list(distinct_types)),
        "overlaps": overlaps,
        "description": desc,
    }
