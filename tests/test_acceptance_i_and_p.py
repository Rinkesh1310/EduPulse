from edupulse.services.academic_service import AcademicService
from edupulse.storage.seed import seed_scenario_data


def test_acceptance_i_demo_merit_tri_state_paths():
    """Acceptance Test I:
    Verify tri-state evaluation paths (MET, NOT_MET, UNKNOWN) on Demo Merit Scheme.
    """
    seed_scenario_data("S3", reset=True)
    service = AcademicService()

    # Case 1: Attested income <= 8,00,000 and SGPA 7.63 (from S3 Sem 1)
    service.save_attested_fact("student_s3", "annualFamilyIncome", 500000.0, "2026-09-30")

    res = service.evaluate_scholarship(
        student_id="student_s3",
        scheme_id="demo_merit_fictional",
        selected_track="all",
        planned_remaining_classes=30,
    )
    assert res["schemeId"] == "demo_merit_fictional"
    criteria_map = {c["id"]: c for c in res["criteria"]}

    # Merit academic: Sem 1 SGPA is 7.63 >= 7.50 -> MET
    assert criteria_map["merit_academic"]["status"] == "MET"

    # Merit income: 500000 <= 800000 -> MET
    assert criteria_map["merit_income"]["status"] == "MET"

    # Merit attendance: Midterm S3 attendance is 76.5% vs required 80.0% -> UNKNOWN with trajectory hint
    assert criteria_map["merit_att"]["status"] == "UNKNOWN"
    assert criteria_map["merit_att"]["targetInfo"] is not None
    assert "Requires attending next" in criteria_map["merit_att"]["details"]

    # Case 2: High income > 8,00,000 -> NOT_MET
    service.save_attested_fact("student_s3", "annualFamilyIncome", 950000.0, "2026-09-30")
    res_high_inc = service.evaluate_scholarship(
        student_id="student_s3",
        scheme_id="demo_merit_fictional",
        selected_track="all",
    )
    c_high = {c["id"]: c for c in res_high_inc["criteria"]}
    assert c_high["merit_income"]["status"] == "NOT_MET"


def test_acceptance_p_mysy_secondary_only_unverified_banner():
    """Acceptance Test P:
    Verify MYSY scheme:
      - Has verificationLevel SECONDARY_ONLY
      - Generates visible unverified banner message
      - Generates tri-state summary counts (e.g. 'n met · n not met · n unknown')
      - Never includes the words 'eligible' or 'not eligible' in its summary verdict
      - Fresh track evaluation is withheld due to conflicting sources
    """
    seed_scenario_data("S3", reset=True)
    service = AcademicService()

    # Evaluate Renewal Track
    service.save_attested_fact("student_s3", "annualFamilyIncome", 450000.0, "2026-09-30")
    service.save_attested_fact("student_s3", "domicileGujarat", True, "2026-09-30")
    service.save_attested_fact("student_s3", "previousYearMarksPercent", 68.0, "2026-09-30")
    service.save_attested_fact("student_s3", "currentlyReceivingScheme", True, "2026-09-30")

    eval_ren = service.evaluate_scholarship(
        student_id="student_s3",
        scheme_id="mysy_2026_27",
        selected_track="renewal",
    )

    # 1. Unverified banner check
    assert eval_ren["isUnverified"] is True
    assert eval_ren["bannerMessage"] is not None
    assert "Not yet verified against an official source" in eval_ren["bannerMessage"]
    assert eval_ren["verificationLevel"] == "SECONDARY_ONLY"

    # 2. Summary format check
    summary_text = eval_ren["summaryCountsText"]
    assert "met" in summary_text and "unknown" in summary_text
    assert "eligible" not in summary_text.lower()
    assert "not eligible" not in summary_text.lower()

    # 3. Fresh track conflict check
    eval_fresh = service.evaluate_scholarship(
        student_id="student_s3",
        scheme_id="mysy_2026_27",
        selected_track="fresh",
    )
    fresh_crit = [c for c in eval_fresh["criteria"] if c["id"] == "mysy_fresh_unverified"]
    assert len(fresh_crit) == 1
    assert fresh_crit[0]["status"] == "UNKNOWN"
    assert "conflicting" in fresh_crit[0]["details"].lower() or "withheld" in fresh_crit[0]["details"].lower()
