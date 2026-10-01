from edupulse.core.engagement import (
    calculate_event_points,
    evaluate_engagement_summary,
)
from edupulse.domain.enums import EngagementStatus
from edupulse.domain.models import Event, StudentEventParticipation


def test_event_points_calculation():
    # Hackathon full day: 3.0 * 1.0 = 3.0
    evt_hack = Event(
        eventId="e1", name="Hackathon", date="2026-09-29",
        activityType="hackathon", durationType="full-day", organizer="Club", source="demo"
    )
    assert calculate_event_points(evt_hack) == 3.0

    # Workshop 2 hours: weight 2.0 * min(2/4, 1.0) = 2.0 * 0.5 = 1.0
    evt_ws = Event(
        eventId="e2", name="Workshop", date="2026-08-14",
        activityType="workshop", durationType="hours", hours=2.0, organizer="Dept", source="demo"
    )
    assert calculate_event_points(evt_ws) == 1.0

    # Seminar 0.5 hours: weight 1.0 * max(0.25, 0.5/4=0.125) = 1.0 * 0.25 = 0.25
    evt_sem = Event(
        eventId="e3", name="Seminar", date="2026-07-28",
        activityType="seminar", durationType="hours", hours=0.5, organizer="Cell", source="demo"
    )
    assert calculate_event_points(evt_sem) == 0.25


def test_engagement_summary_states():
    # 1. NOT_PROVIDED
    res_none = evaluate_engagement_summary([], {}, declaration_status=EngagementStatus.NOT_PROVIDED)
    assert res_none["status"] == EngagementStatus.NOT_PROVIDED.value
    assert res_none["level"] == "Insufficient data"

    # 2. DECLARED_NONE
    res_decl_none = evaluate_engagement_summary([], {}, declaration_status=EngagementStatus.DECLARED_NONE)
    assert res_decl_none["status"] == EngagementStatus.DECLARED_NONE.value
    assert res_decl_none["level"] == "No participation recorded (informational)"

    # 3. HAS_EVENTS - Active (e.g. 3 events)
    e1 = Event(eventId="e1", name="H1", date="2026-09-29", activityType="hackathon", durationType="full-day", organizer="O", source="s")
    e2 = Event(eventId="e2", name="C1", date="2026-09-12", activityType="competition", durationType="hours", hours=4.0, organizer="O", source="s")
    e3 = Event(eventId="e3", name="W1", date="2026-08-14", activityType="workshop", durationType="hours", hours=4.0, organizer="O", source="s")
    events_map = {"e1": e1, "e2": e2, "e3": e3}

    parts = [
        StudentEventParticipation(studentId="s1", eventId="e1", confirmationDate="2026-09-30"),
        StudentEventParticipation(studentId="s1", eventId="e2", confirmationDate="2026-09-30"),
        StudentEventParticipation(studentId="s1", eventId="e3", confirmationDate="2026-09-30"),
    ]
    # Points: 3.0 + 3.0 + 2.0 = 8.0 points, 3 events, 3 types -> Active (since points < 10)
    res_active = evaluate_engagement_summary(parts, events_map, official_attendance_p_dates={"2026-09-29"})
    assert res_active["level"] == "Active"
    assert res_active["points"] == 8.0
    assert len(res_active["overlaps"]) == 1
    assert "Counted in official attendance" in res_active["overlaps"][0]["note"]

    # 4. Highly active (>= 10 points across >= 3 activity types)
    e4 = Event(eventId="e4", name="P1", date="2026-10-15", activityType="project", durationType="full-day", organizer="O", source="s")
    events_map["e4"] = e4
    parts.append(StudentEventParticipation(studentId="s1", eventId="e4", confirmationDate="2026-09-30"))
    # Points: 8.0 + 3.0 = 11.0 points, 4 types -> Highly active!
    res_high = evaluate_engagement_summary(parts, events_map)
    assert res_high["level"] == "Highly active"
    assert res_high["points"] == 11.0
    assert res_high["diversityCount"] == 4
