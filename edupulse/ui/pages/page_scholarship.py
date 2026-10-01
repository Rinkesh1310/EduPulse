from datetime import datetime

import streamlit as st

from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import (
    apply_custom_theme,
    render_html,
    render_page_header,
    render_verification_badge,
)


def render_page(service: AcademicService):
    apply_custom_theme()
    st_id = st.session_state.get("current_student_id", "student_synth_strong")
    student = service.get_student_profile(st_id)
    provenance = service.get_student_provenance(st_id)
    schemes = service.get_scholarships()

    # 1. TOP HEADER
    render_page_header(
        title="Scholarship Readiness Planner",
        subtitle="Eligibility audit checklists, criteria verification, and future target planning.",
        student=student,
        provenance=provenance,
        as_of_date="2026-09-30",
        academic_status="Scholarship Planning Mode",
    )

    if not schemes:
        st.info("No scholarship scheme definitions configured.")
        return

    # Scheme Selector & Verification Bar
    col_sc1, col_sc2 = st.columns([2, 1])
    with col_sc1:
        scheme_options = {s.schemeId: f"{s.name} ({s.academicYear})" for s in schemes}
        selected_scheme_id = st.selectbox(
            "Selected Scholarship Scheme",
            options=list(scheme_options.keys()),
            format_func=lambda sid: scheme_options[sid],
            key="sch_select_scheme",
        )
    with col_sc2:
        scheme = next(s for s in schemes if s.schemeId == selected_scheme_id)
        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        render_verification_badge(
            scheme.verificationLevel.value == "OFFICIAL_VERIFIED",
            f"Scheme Status: {scheme.verificationLevel.value.replace('_', ' ').title()}",
        )

    if scheme.verificationLevel.value in ("SECONDARY_ONLY", "CONFLICTING", "UNVERIFIED") or not scheme.officialSourceUrl:
        st.warning(
            f"⚠️ **Scheme Verification Notice**: {scheme.notes or 'Criteria synthesized from institutional guidelines. Official verification required prior to application submission.'}"
        )

    # Track Selection & Planning Settings
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        track = st.radio(
            "Application Track",
            ["renewal", "fresh"],
            format_func=lambda t: "Renewal Track (Continuing Enrolled Students)" if t == "renewal" else "Fresh Applicant Track (New Entrants)",
            horizontal=True,
            key="sch_track_select",
        )
    with col_t2:
        rem_classes = st.number_input(
            "Estimated Remaining Classes",
            min_value=5,
            max_value=120,
            value=35,
            step=5,
            key="sch_rem_classes",
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # Student Self-Attested Facts Form
    attested_facts = service.get_attested_facts(st_id)
    with st.expander("📝 Enter / Update Self-Attested Criteria (Income, Domicile, Prior Marksheet)", expanded=not bool(attested_facts)):
        st.caption("Attest candidate facts required by official schemes (stored locally in session, never transmitted externally):")
        with st.form("sch_attestation_form"):
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                cur_income = float(attested_facts.get("annualFamilyIncome", 450000.0))
                income_val = st.number_input("Annual Family Income (INR)", min_value=0.0, max_value=5000000.0, value=cur_income, step=25000.0)
                cur_domicile = bool(attested_facts.get("domicileGujarat", True))
                domicile_val = st.checkbox("State Domicile Confirmed", value=cur_domicile)
            with col_a2:
                cur_marks = float(attested_facts.get("previousYearMarksPercent", 68.5))
                marks_val = st.number_input("Previous Qualifying Marksheet Percentage (0-100%)", min_value=0.0, max_value=100.0, value=cur_marks, step=0.5)
                st.caption("Must be entered directly from official marksheet. Never estimated or derived from SGPA.")
                cur_rec = bool(attested_facts.get("currentlyReceivingScheme", True))
                rec_val = st.checkbox("Currently an Approved Scheme Beneficiary", value=cur_rec)

            save_attestation = st.form_submit_button("Save Attested Facts", type="primary")
            if save_attestation:
                now_str = datetime.now().isoformat()
                service.save_attested_fact(st_id, "annualFamilyIncome", income_val, now_str)
                service.save_attested_fact(st_id, "domicileGujarat", domicile_val, now_str)
                service.save_attested_fact(st_id, "previousYearMarksPercent", marks_val, now_str)
                service.save_attested_fact(st_id, "currentlyReceivingScheme", rec_val, now_str)
                st.success("Attested information saved successfully!")
                st.rerun()

    # Evaluation Output
    eval_result = service.evaluate_scholarship(
        student_id=st_id,
        scheme_id=selected_scheme_id,
        selected_track=track,
        planned_remaining_classes=rem_classes,
    )

    st.subheader(f"Readiness Audit: {eval_result['schemeName']}")
    render_html(
        f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; margin-bottom:16px; font-size:0.92rem;">
            Readiness Summary: <strong>{eval_result['summaryCountsText']}</strong> &nbsp;•&nbsp; 
            <em>Criteria classification: MET / NOT MET / UNKNOWN based on verifiable local evidence.</em>
        </div>
        """
    )

    for crit in eval_result["criteria"]:
        status = crit["status"]
        badge_class = "badge-low" if status == "MET" else ("badge-high" if status == "NOT_MET" else "badge-moderate")
        border_color = "#10b981" if status == "MET" else ("#ef4444" if status == "NOT_MET" else "#f59e0b")

        render_html(
            f"""
            <div class="edu-card" style="border-left: 4px solid {border_color}; margin-bottom: 12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <strong style="font-size:0.98rem; color:#0f172a;">{crit['label']}</strong>
                    <span class="{badge_class}">{status}</span>
                </div>
                <p style="margin: 4px 0 6px 0; font-size: 0.92rem; color: #1e293b;">{crit['details']}</p>
                <div style="font-size: 0.82rem; color: #64748b;">
                    Evidence Basis: <code>{crit['basis']}</code> &nbsp;|&nbsp; Verification: {crit['verification']}
                </div>
            </div>
            """
        )

    # Missing Documents Checklist
    if eval_result["missingDocuments"]:
        st.subheader("📋 Verifiable Documents Required for Submission")
        for doc in eval_result["missingDocuments"]:
            st.markdown(f"- 📄 **{doc['name']}**: *{doc['note']}*")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # Future What-If Target Calculator
    st.subheader("🎯 Future Target & Buffer Simulator")
    st.caption("Simulate academic and attendance requirements to ensure scholarship renewal criteria remain fully satisfied:")

    c_w1, c_w2 = st.columns(2)
    with c_w1:
        target_cgpa = st.slider("Target Cumulative CGPA", min_value=6.0, max_value=9.5, value=7.5, step=0.1, key="sch_target_cgpa")
        future_credits = st.number_input("Future Planned Semester Credits", min_value=12.0, max_value=40.0, value=24.0, step=1.0, key="sch_future_credits")

    with c_w2:
        plan_res = service.calculate_cgpa_plan(st_id, target_cgpa=target_cgpa, future_credits=future_credits)
        render_html(
            f"""
            <div class="edu-card" style="border-left: 4px solid #2563eb; background:#f8fafc; height: 100%;">
                <h5 style="margin-top:0; color:#1e40af;">Academic Renewal Target</h5>
                <p style="margin:4px 0 8px 0; font-size:0.9rem; color:#334155;">
                    Current CGPA: <strong>{plan_res['cgpaInfo']['cgpa'] or 'N/A'}</strong> &nbsp;|&nbsp; Target: <strong>{target_cgpa:.2f}</strong>
                </p>
                <div style="font-size:0.88rem; color:#0f172a; font-weight:600;">
                    {plan_res['futurePlan']['message'] if plan_res.get('futurePlan') else plan_res['cgpaInfo'].get('message', '')}
                </div>
            </div>
            """
        )

    st.info("ℹ️ **Educational Disclaimer**: This module provides academic planning and threshold tracking. It does not disburse funds or guarantee institutional scholarship sanction.")
