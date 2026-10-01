"""
Integration tests for FastAPI Backend API endpoints.
Validates all routes, data contracts, dynamic recalculation, and security barriers.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "EduPulse" in data["service"]

def test_personas_and_active_student():
    res = client.get("/api/personas")
    assert res.status_code == 200
    personas = res.json()
    assert len(personas) >= 6
    assert any(p["id"] == "student_synth_strong" for p in personas)

    # Set active student
    res = client.post("/api/students/active", json={"student_id": "student_synth_att_concern"})
    assert res.status_code == 200
    assert res.json()["active_student_id"] == "student_synth_att_concern"

    # Reset back to strong for remaining tests
    client.post("/api/students/active", json={"student_id": "student_synth_strong"})

def test_overview_snapshot():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "attendance" in data["metrics"]
    assert "academics" in data["metrics"]
    assert "engagement" in data["metrics"]
    assert "supportSignal" in data["metrics"]
    assert "attentionAreas" in data
    assert "recommendedActions" in data

def test_success_explorer():
    res = client.get("/api/explorer")
    assert res.status_code == 200
    data = res.json()
    assert "overallSupportSignal" in data
    assert "narrative" in data
    assert "whatDetected" in data["narrative"]
    assert "whyDetected" in data["narrative"]
    assert "whatToDoNext" in data["narrative"]
    assert "pillars" in data
    assert "evidence" in data
    assert "recommendations" in data

def test_attendance_and_recovery():
    res = client.get("/api/attendance/summary")
    assert res.status_code == 200
    data = res.json()
    assert "computedOverall" in data
    assert "records" in data
    assert len(data["records"]) > 0

    # Recovery calculation
    res = client.post("/api/attendance/recovery", json={
        "target_pct": 75.0,
        "remaining_classes": 30,
        "present": 15,
        "total": 25
    })
    assert res.status_code == 200
    rec = res.json()
    assert rec["neededConsecutive"] == 15
    assert rec["isRecoverableWithinRemaining"] is True

def test_dynamic_marks_recalculation():
    # Set to low marks -> check signal
    res = client.post("/api/academics/assessments", json={
        "course_id": "CSUC201",
        "ass_type": "Midterm",
        "obtained_marks": 8.0,
        "total_marks": 20.0
    })
    assert res.status_code == 200
    assert res.json()["updatedSignals"]["academicSignal"] in ("Moderate", "High", "Needs more data")

    # Set to high marks -> check signal improves
    res = client.post("/api/academics/assessments", json={
        "course_id": "CSUC201",
        "ass_type": "Midterm",
        "obtained_marks": 19.0,
        "total_marks": 20.0
    })
    assert res.status_code == 200
    assert res.json()["updatedSignals"]["academicSignal"] == "Low"

def test_engagement_fairness_and_toggle():
    res = client.post("/api/engagement/toggle-participation", json={
        "event_id": "evt_hack_01",
        "participated": True
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["updatedSummary"]["points"] >= 2.0

def test_scholarship_schemes_and_evaluation():
    res = client.get("/api/scholarship/schemes")
    assert res.status_code == 200
    schemes = res.json()
    assert len(schemes) > 0
    scheme_id = schemes[0]["schemeId"]

    eval_res = client.get(f"/api/scholarship/evaluate?scheme_id={scheme_id}&track=renewal&remaining_classes=35")
    assert eval_res.status_code == 200
    edata = eval_res.json()
    assert "criteria" in edata
    assert "summaryCountsText" in edata

def test_cohort_ml_privacy_and_clustering():
    res = client.get("/api/cohort/analysis")
    assert res.status_code == 200
    cdata = res.json()
    assert cdata["cohortSize"] >= 100
    assert cdata["bestK"] >= 3
    assert len(cdata["clusters"]) >= 3
    # Check k-anonymity privacy guarantee
    for cl in cdata["clusters"]:
        if cl["size"] < 5:
            assert cl["suppressed"] is True

def test_authorized_connector_security_boundary():
    res = client.post("/api/data-workspace/authorized-connector-stub")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "security_boundary_verified"
    assert data["error_type"] == "NotAuthorizedError"
