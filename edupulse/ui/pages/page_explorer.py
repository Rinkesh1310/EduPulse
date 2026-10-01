import streamlit as st

from edupulse.domain.enums import SupportLevel
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
    sem = student.semester if student else 3
    signals = service.get_support_signals(st_id)
    policy = signals["policy"]
    provenance = service.get_student_provenance(st_id)
    narrative = service.get_diagnostic_narrative(st_id)
    att_summary = service.get_attendance_summary(st_id, sem)
    coverage = service.get_coverage(st_id)
    as_of = att_summary.get("asOfDate", "2026-09-30")

    # 1. TOP HEADER: Clean SaaS Hierarchy
    render_page_header(
        title="Student Success Explorer",
        subtitle="Evidence-based academic intelligence and diagnostic reasoning engine.",
        student=student,
        provenance=provenance,
        as_of_date=as_of,
        academic_status=f"Data Confidence: {coverage.overall.value}",
    )

    # 2. EXECUTIVE DIAGNOSTIC CENTERPIECE
    support_sig = signals["overallSupportSignal"]
    border_accent = (
        "#10b981"
        if support_sig == SupportLevel.LOW
        else ("#ef4444" if support_sig == SupportLevel.HIGH else "#f59e0b")
    )
    sig_badge = (
        "badge-low"
        if support_sig == SupportLevel.LOW
        else ("badge-high" if support_sig == SupportLevel.HIGH else "badge-moderate")
    )

    render_html(
        f"""
        <div class="edu-card" style="border-left: 6px solid {border_accent}; background: #ffffff; padding: 26px 28px; margin-bottom: 24px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:0.85rem; font-weight:800; text-transform:uppercase; letter-spacing:0.08em; color:#64748b;">
                        Overall Support Signal
                    </span>
                    <span class="{sig_badge}" style="font-size:0.95rem; font-weight:700; padding:5px 14px;">
                        {support_sig.value.upper()}
                    </span>
                </div>
                <div style="display:flex; gap:8px; align-items:center;">
                    <span class="badge-neutral" style="font-size:0.8rem;">Data Coverage: <strong>{coverage.overall.value}</strong></span>
                    <span class="badge-neutral" style="font-size:0.8rem;">As of {as_of}</span>
                </div>
            </div>
            
            <div style="margin-top: 14px; margin-bottom: 16px;">
                <span style="font-size:0.82rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#0369a1;">
                    What was detected?
                </span>
                <p style="font-size: 1.12rem; font-weight: 600; color: #0f172a; margin: 4px 0 0 0; line-height: 1.45;">
                    {narrative['what_detected']}
                </p>
            </div>

            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; font-size: 0.88rem; color: #475569;">
                <strong>Governance Principle:</strong> Support signals exist to alert mentors and students to supportive opportunities early in the semester. 
                They are non-punitive, evidence-based checkpoints and do not predict final course grades or exam outcomes.
            </div>
        </div>
        """
    )

    # 3. THREE-PILLAR BREAKDOWN
    p1, p2, p3 = st.columns(3)
    with p1:
        att_pct = att_summary["computedOverall"]
        att_str = f"{att_pct:.1f}%" if att_pct is not None else "N/A"
        att_sig = signals["attendanceSignal"]
        att_badge = "badge-low" if att_sig == SupportLevel.LOW else ("badge-high" if att_sig == SupportLevel.HIGH else "badge-moderate")
        render_html(
            f"""
            <div class="edu-card" style="height: 100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase;">Attendance Pillar</span>
                    <span class="{att_badge}">{att_sig.value}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight:800; color:#0f172a; margin: 8px 0 2px 0;">{att_str}</div>
                <p style="font-size: 0.84rem; color: #475569; margin: 0;">
                    {att_summary['totalPresent']}/{att_summary['totalClasses']} sessions recorded &nbsp;•&nbsp; 
                    {signals['attendanceMeta'].get('belowCount', 0)} component(s) &lt; {policy.attendancePerCoursePct:.0f}%
                </p>
            </div>
            """
        )

    with p2:
        acad_sig = signals["academicSignal"]
        acad_badge = "badge-low" if acad_sig == SupportLevel.LOW else ("badge-high" if acad_sig == SupportLevel.HIGH else ("badge-info" if acad_sig == SupportLevel.NEEDS_MORE_DATA else "badge-moderate"))
        render_html(
            f"""
            <div class="edu-card" style="height: 100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase;">Academic Pillar</span>
                    <span class="{acad_badge}">{acad_sig.value}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight:800; color:#0f172a; margin: 8px 0 2px 0;">
                    {signals['academicMeta'].get('evaluatedCount', 0)} Evaluated
                </div>
                <p style="font-size: 0.84rem; color: #475569; margin: 0;">
                    Coverage: <strong>{signals['academicMeta'].get('coverage', 'N/A')}</strong> &nbsp;•&nbsp; 
                    {signals['academicMeta'].get('belowCount', 0)} subject(s) &lt; 50% benchmark
                </p>
            </div>
            """
        )

    with p3:
        eng = signals["engagementSummary"]
        render_html(
            f"""
            <div class="edu-card" style="height: 100%;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase;">Engagement Portfolio</span>
                    <span class="badge-info">{eng['level']}</span>
                </div>
                <div style="font-size: 1.5rem; font-weight:800; color:#0f172a; margin: 8px 0 2px 0;">
                    {eng['points']:.1f} pts
                </div>
                <p style="font-size: 0.84rem; color: #475569; margin: 0;">
                    {eng['eventCount']} confirmed events ({eng['diversityCount']} categories) &nbsp;•&nbsp; <em>Independent Indicator</em>
                </p>
            </div>
            """
        )

    render_html("<div style='margin-bottom: 24px;'></div>")

    # 4. "WHY?" — SCANNABLE EVIDENCE CARDS
    st.subheader("🔍 Why was this detected? (Signal Evidence & Traceability)")
    st.caption("Detailed audit trail of contributing indicators with active thresholds, observed values, and provenance:")

    reasons = signals["reasons"]
    if reasons:
        cols_ev = st.columns(2)
        for idx, r in enumerate(reasons):
            with cols_ev[idx % 2]:
                direction_badge = (
                    "badge-high"
                    if r.direction == "concern"
                    else ("badge-low" if r.direction == "positive" else "badge-neutral")
                )
                dir_label = "Attention Area" if r.direction == "concern" else ("Healthy Marker" if r.direction == "positive" else "Contextual Note")
                border_color = "#ef4444" if r.direction == "concern" else ("#10b981" if r.direction == "positive" else "#cbd5e1")

                threshold_note = ""
                if "attendance" in r.indicator.lower():
                    threshold_note = f"Policy Threshold: ≥ {policy.attendancePerCoursePct:.0f}% course / {policy.attendanceOverallPct:.0f}% overall"
                elif "marks" in r.indicator.lower() or "score" in r.indicator.lower():
                    threshold_note = "Benchmark: ≥ 50% passing threshold / ≥ 65% strong"
                else:
                    threshold_note = "Evaluation Standard: Institutional Academic Policy"

                render_html(
                    f"""
                    <div class="edu-card" style="border-left: 4px solid {border_color}; padding: 16px 18px; margin-bottom: 12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                            <strong style="font-size: 0.95rem; color: #0f172a;">{r.indicator}</strong>
                            <span class="{direction_badge}" style="font-size:0.75rem;">{dir_label}</span>
                        </div>
                        <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b; margin: 4px 0;">
                            {r.value}
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b; margin-top: 6px;">
                            {threshold_note} &nbsp;•&nbsp; <strong>Source:</strong> <em>{r.source} ({provenance})</em>
                        </div>
                    </div>
                    """
                )
    else:
        st.info("✓ All active indicators meet or exceed baseline expectations. No alerts triggered.")

    render_html("<div style='margin-bottom: 24px;'></div>")

    # 5. "WHAT SHOULD I DO NEXT?" — ACTION RECOMMENDATIONS
    st.subheader("💡 What should I do next? (Action Recommendations)")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        render_html(
            f"""
            <div class="edu-card" style="border-left: 4px solid #3b82f6; height: 100%;">
                <h5 style="color:#1e3a8a; margin-top:0;">🎯 Prioritized Focus Areas</h5>
                <ul style="margin: 8px 0 0 0; padding-left: 18px; line-height: 1.6; color:#334155; font-size:0.92rem;">
                    {''.join(f'<li style="margin-bottom:6px;">{a}</li>' for a in narrative['what_to_do_next'])}
                </ul>
            </div>
            """
        )

    with col_a2:
        render_html(
            """
            <div class="edu-card" style="border-left: 4px solid #0f766e; height: 100%;">
                <h5 style="color:#0f766e; margin-top:0;">📖 Campus Support & Mentorship Resources</h5>
                <ul style="margin: 8px 0 0 0; padding-left: 18px; line-height: 1.6; color:#334155; font-size:0.92rem;">
                    <li style="margin-bottom:6px;"><strong>Faculty Consultation</strong>: Visit subject professors during designated office hours to review difficult exam questions.</li>
                    <li style="margin-bottom:6px;"><strong>Peer Tutoring Circles</strong>: Join department study circles in the central library to reinforce core problem-solving competencies.</li>
                    <li style="margin-bottom:6px;"><strong>Skills Acceleration</strong>: Explore technical hackathons and practical workshops in the <strong>Engagement Catalogue</strong>.</li>
                    <li style="margin-bottom:6px;"><strong>Scholarship Safeguards</strong>: Check the <strong>Scholarship Readiness Planner</strong> to maintain your academic renewal buffer.</li>
                </ul>
            </div>
            """
        )

    render_html("<div style='margin-bottom: 24px;'></div>")

    # 6. ATTENDANCE RECOVERY & BUFFER CALCULATOR
    st.subheader("📈 Attendance Recovery & Buffer Calculator")
    st.caption("Interactive recovery simulator to calculate exact class attendance needed to reach or maintain institutional thresholds:")

    tot_p = att_summary["totalPresent"]
    tot_c = att_summary["totalClasses"]

    col_rec1, col_rec2 = st.columns([1, 1.2])
    with col_rec1:
        target_threshold = st.slider(
            "Target Attendance Threshold (%)",
            min_value=60.0,
            max_value=90.0,
            value=float(policy.attendanceOverallPct),
            step=1.0,
            key="slider_explorer_recovery_target",
        )
        planned_future = st.number_input(
            "Estimated Remaining Classes in Semester",
            min_value=1,
            max_value=150,
            value=35,
            step=5,
            key="num_explorer_remaining_classes",
        )

    with col_rec2:
        recovery_res = service.calculate_recovery(
            present=tot_p,
            total=tot_c,
            target_pct=target_threshold,
            remaining_classes=planned_future,
        )

        render_html(
            f"""
            <div class="edu-card" style="border-left: 4px solid #0f766e; height: 100%;">
                <h5 style="margin-top:0; color:#0f766e;">Recovery Simulation Result</h5>
                <p style="font-size:0.95rem; font-weight:600; color:#0f172a; margin:4px 0;">{recovery_res['message']}</p>
                <div style="font-size:0.88rem; color:#475569; margin-top:8px;">
                    Current Standing: <strong>{recovery_res['currentPct']:.1f}%</strong> ({tot_p}/{tot_c}) &nbsp;|&nbsp; 
                    Classes Needed: <strong>{recovery_res['neededConsecutive']}</strong>
                </div>
            </div>
            """
        )

    render_html("<div style='margin-bottom: 24px;'></div>")

    # 7. "HOW IS THIS CALCULATED?" — TRANSPARENT ENGINE PANEL
    st.subheader("⚙️ How is this calculated? (Policy & Decision Logic)")
    with st.expander("ℹ️ Inspect Calculation Engine & Mathematical Formulations", expanded=False):
        c_ver1, c_ver2 = st.columns([3, 1])
        with c_ver1:
            st.markdown(
                rf"""
                #### 1. Combined Support Signal Decision Matrix
                EduPulse computes support signals hierarchically:
                $$\text{{Overall Support Signal}} = \max\left(\text{{Attendance Signal}}, \text{{Academic Signal}}\right)$$
                *Priority Order: High &gt; Moderate &gt; Low &gt; Needs more data.*

                #### 2. Attendance Signal Engine
                - **High Alert**: Overall attendance $&lt; {policy.attendanceOverallPct:.0f}\%$ OR $\ge 2$ subject components $&lt; {policy.attendancePerCoursePct:.0f}\%$ (minimum {policy.smallSampleThreshold} classes to guard against small-sample skew).
                - **Moderate Alert**: Overall attendance between ${policy.attendancePerCoursePct:.0f}\%$ and ${policy.attendanceOverallPct - 0.1:.0f}\%$, OR exactly $1$ subject component $&lt; {policy.attendancePerCoursePct:.0f}\%$.
                - **Low (Stable)**: Overall attendance $\ge {policy.attendanceOverallPct:.0f}\%$ and all courses $\ge {policy.attendancePerCoursePct:.0f}\%$.

                #### 3. Academic Signal Engine
                - **High Alert**: Overall subject marks average $&lt; 50\%$ OR $\ge 2$ subjects $&lt; 50\%$.
                - **Moderate Alert**: Marks average between $50\%$ and $64.9\%$, OR exactly $1$ subject $&lt; 50\%$, OR declining SGPA trend.
                - **Low (Stable)**: Marks average $\ge 65\%$ across evaluated subjects with no subject below benchmark.
                - **Needs More Data**: No evaluations returned yet; zero fabricated scores.

                #### 4. Engagement Independence Principle
                - Co-curricular engagement points are calculated as $\text{{Points}} = \sum (\text{{Weight}} \times \text{{Duration Factor}})$.
                - **Independence Guarantee**: Engagement does **NOT** increase or decrease the Academic Support Signal. It remains a distinct, positive indicator of student growth.
                """
            )
        with c_ver2:
            render_verification_badge(policy.verified, "Policy Verified" if policy.verified else "Unverified for your institute")
            st.caption(f"Rule Engine Version: **v{policy.version}**")
            st.caption(f"Course Minimum: **{policy.attendancePerCoursePct:.0f}%**")
            st.caption(f"Overall Minimum: **{policy.attendanceOverallPct:.0f}%**")
