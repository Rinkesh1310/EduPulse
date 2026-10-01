import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def call_api(method: str, path: str, data: dict = None, expected_status: int = 200):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"} if data else {}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            content = resp.read().decode("utf-8")
            res_json = json.loads(content) if "application/json" in resp.headers.get("Content-Type", "") else content
            assert status == expected_status, f"Expected {expected_status}, got {status}"
            return True, status, res_json
    except urllib.error.HTTPError as e:
        status = e.code
        content = e.read().decode("utf-8")
        try:
            res_json = json.loads(content)
        except Exception:
            res_json = content
        if status == expected_status:
            return True, status, res_json
        return False, status, res_json

def run_audit():
    results = []

    # 1. /api/health
    ok, st, data = call_api("GET", "/api/health")
    valid = ok and data.get("status") == "healthy"
    results.append(("/api/health", "GET", st, "PASS" if valid else "FAIL"))

    # 2. /api/personas
    ok, st, data = call_api("GET", "/api/personas")
    valid = ok and isinstance(data, list) and len(data) >= 6
    results.append(("/api/personas", "GET", st, "PASS" if valid else "FAIL"))

    # 3. /api/students/active (GET & POST)
    ok, st, data = call_api("GET", "/api/students/active")
    valid = ok and "student" in data and "active_student_id" in data
    results.append(("/api/students/active", "GET", st, "PASS" if valid else "FAIL"))

    ok, st, data = call_api("POST", "/api/students/active", {"student_id": "student_synth_strong"})
    valid = ok and data.get("success") is True
    results.append(("/api/students/active", "POST", st, "PASS" if valid else "FAIL"))

    # 4. /api/overview
    ok, st, data = call_api("GET", "/api/overview")
    valid = ok and "metrics" in data and "attendance" in data["metrics"]
    results.append(("/api/overview", "GET", st, "PASS" if valid else "FAIL"))

    # 5. /api/explorer
    ok, st, data = call_api("GET", "/api/explorer")
    valid = ok and "overallSupportSignal" in data and "narrative" in data
    results.append(("/api/explorer", "GET", st, "PASS" if valid else "FAIL"))

    # 6. /api/attendance/summary
    ok, st, data = call_api("GET", "/api/attendance/summary")
    valid = ok and "computedOverall" in data and "records" in data
    results.append(("/api/attendance/summary", "GET", st, "PASS" if valid else "FAIL"))

    # 7. /api/attendance/recovery
    ok, st, data = call_api("POST", "/api/attendance/recovery", {
        "target_pct": 75.0,
        "remaining_classes": 35,
        "present": 35,
        "total": 50
    })
    valid = ok and "isPossible" in data and "classesNeeded" in data
    results.append(("/api/attendance/recovery", "POST", st, "PASS" if valid else "FAIL"))

    # 8. /api/academics/courses
    ok, st, data = call_api("GET", "/api/academics/courses")
    valid = ok and isinstance(data, list) and len(data) > 0
    results.append(("/api/academics/courses", "GET", st, "PASS" if valid else "FAIL"))

    # 9. /api/academics/assessments (GET & POST)
    ok, st, data = call_api("GET", "/api/academics/assessments")
    valid = ok and isinstance(data, list)
    results.append(("/api/academics/assessments", "GET", st, "PASS" if valid else "FAIL"))

    ok, st, data = call_api("POST", "/api/academics/assessments", {
        "course_id": "CSUC201",
        "ass_type": "Midterm",
        "obtained_marks": 18.0,
        "total_marks": 20.0
    })
    valid = ok and data.get("success") is True
    results.append(("/api/academics/assessments", "POST", st, "PASS" if valid else "FAIL"))

    # 10. /api/academics/results
    ok, st, data = call_api("GET", "/api/academics/results")
    valid = ok and "results" in data and "cgpa" in data
    results.append(("/api/academics/results", "GET", st, "PASS" if valid else "FAIL"))

    # 11. /api/academics/cgpa-plan
    ok, st, data = call_api("POST", "/api/academics/cgpa-plan", {
        "target_cgpa": 8.0,
        "future_credits": 24.0
    })
    valid = ok and "futurePlan" in data and "cgpaInfo" in data
    results.append(("/api/academics/cgpa-plan", "POST", st, "PASS" if valid else "FAIL"))

    # 12. /api/engagement/summary
    ok, st, data = call_api("GET", "/api/engagement/summary")
    valid = ok and "status" in data and "points" in data
    results.append(("/api/engagement/summary", "GET", st, "PASS" if valid else "FAIL"))

    # 13. /api/engagement/events
    ok, st, data = call_api("GET", "/api/engagement/events")
    valid = ok and isinstance(data, list) and len(data) > 0
    results.append(("/api/engagement/events", "GET", st, "PASS" if valid else "FAIL"))

    # 14. /api/engagement/toggle-participation
    ok, st, data = call_api("POST", "/api/engagement/toggle-participation", {
        "event_id": "EVT_DEV_HACK",
        "participated": True
    })
    valid = ok and data.get("success") is True
    results.append(("/api/engagement/toggle-participation", "POST", st, "PASS" if valid else "FAIL"))

    # 15. /api/engagement/declaration
    ok, st, data = call_api("POST", "/api/engagement/declaration", {
        "term": "2026-27-ODD",
        "status": "SELF_REPORTED_HOURS"
    })
    valid = ok and data.get("success") is True
    results.append(("/api/engagement/declaration", "POST", st, "PASS" if valid else "FAIL"))

    # 16. /api/scholarship/schemes
    ok, st, data = call_api("GET", "/api/scholarship/schemes")
    valid = ok and isinstance(data, list) and len(data) > 0
    results.append(("/api/scholarship/schemes", "GET", st, "PASS" if valid else "FAIL"))

    # 17. /api/scholarship/evaluate
    ok, st, data = call_api("GET", "/api/scholarship/evaluate?scheme_id=mysy_2026_27")
    valid = ok and "schemeId" in data and "criteria" in data
    results.append(("/api/scholarship/evaluate", "GET", st, "PASS" if valid else "FAIL"))

    # 17b. /api/scholarship/evaluate (404 expected for non-existent scheme)
    ok_404, st_404, _ = call_api("GET", "/api/scholarship/evaluate?scheme_id=nonexistent_scheme_xyz", expected_status=404)
    results.append(("/api/scholarship/evaluate (invalid ID)", "GET", st_404, "PASS" if ok_404 else "FAIL"))

    # 18. /api/scholarship/attested-facts (GET & POST)
    ok, st, data = call_api("GET", "/api/scholarship/attested-facts")
    valid = ok and isinstance(data, dict)
    results.append(("/api/scholarship/attested-facts", "GET", st, "PASS" if valid else "FAIL"))

    ok, st, data = call_api("POST", "/api/scholarship/attested-facts", {
        "annualFamilyIncome": 450000.0,
        "domicileGujarat": True
    })
    valid = ok and data.get("success") is True
    results.append(("/api/scholarship/attested-facts", "POST", st, "PASS" if valid else "FAIL"))

    # 19. /api/cohort/analysis
    ok, st, data = call_api("GET", "/api/cohort/analysis")
    valid = ok and "cohortSize" in data and "clusters" in data
    results.append(("/api/cohort/analysis", "GET", st, "PASS" if valid else "FAIL"))

    # 20. /api/data-workspace/preview-file
    ok, st, data = call_api("POST", "/api/data-workspace/preview-file", {
        "content": "course_code,component,present_count,total_count\nCEUE203,LECT,14,15",
        "student_name": "Rinkesh",
        "program": "B.Tech IT"
    })
    valid = ok and data.get("valid") is True and data.get("rowCount") == 1
    results.append(("/api/data-workspace/preview-file", "POST", st, "PASS" if valid else "FAIL"))

    # 21. /api/data-workspace/commit-file
    ok, st, data = call_api("POST", "/api/data-workspace/commit-file", {
        "content": "course_code,component,present_count,total_count\nCEUE203,LECT,14,15",
        "student_name": "Rinkesh",
        "program": "B.Tech IT",
        "semester": 3,
        "academic_year": "2026-27"
    })
    valid = ok and data.get("success") is True
    results.append(("/api/data-workspace/commit-file", "POST", st, "PASS" if valid else "FAIL"))

    # 22. /api/data-workspace/preview-paste
    ok, st, data = call_api("POST", "/api/data-workspace/preview-paste", {
        "text": "CEUE203 / OOP | LECT | 14 / 15 | 93.3%"
    })
    valid = ok and data.get("valid") is True
    results.append(("/api/data-workspace/preview-paste", "POST", st, "PASS" if valid else "FAIL"))

    # 23. /api/data-workspace/commit-paste
    ok, st, data = call_api("POST", "/api/data-workspace/commit-paste", {
        "text": "CEUE203 / OOP | LECT | 14 / 15 | 93.3%"
    })
    valid = ok and data.get("success") is True
    results.append(("/api/data-workspace/commit-paste", "POST", st, "PASS" if valid else "FAIL"))

    # 24. /api/data-workspace/templates/{template_type}
    ok, st, data = call_api("GET", "/api/data-workspace/templates/attendance")
    valid = ok and "course_code" in str(data)
    results.append(("/api/data-workspace/templates/attendance", "GET", st, "PASS" if valid else "FAIL"))

    ok, st, data = call_api("GET", "/api/data-workspace/templates/marks")
    valid = ok and "course_code" in str(data)
    results.append(("/api/data-workspace/templates/marks", "GET", st, "PASS" if valid else "FAIL"))

    # 25. /api/data-workspace/reset
    ok, st, data = call_api("POST", "/api/data-workspace/reset", {"scenario": "student_synth_strong"})
    valid = ok and data.get("success") is True
    results.append(("/api/data-workspace/reset", "POST", st, "PASS" if valid else "FAIL"))

    # 26. /api/data-workspace/authorized-connector-stub
    ok, st, data = call_api("POST", "/api/data-workspace/authorized-connector-stub", {})
    valid = ok and data.get("status") == "security_boundary_verified"
    results.append(("/api/data-workspace/authorized-connector-stub", "POST", st, "PASS" if valid else "FAIL"))

    # Print summary
    print(f"{'ENDPOINT':<45} | {'METHOD':<6} | {'STATUS':<6} | {'RESULT':<6}")
    print("-" * 75)
    for path, method, status, res in results:
        print(f"{path:<45} | {method:<6} | {status:<6} | {res:<6}")

    all_passed = all(r[3] == "PASS" for r in results)
    print("\nOVERALL API RESULT:", "ALL PASS" if all_passed else "SOME FAILED")
    return all_passed

if __name__ == "__main__":
    run_audit()
