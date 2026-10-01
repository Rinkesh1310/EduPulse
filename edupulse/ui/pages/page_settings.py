import json

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
    policy = service.get_policy()
    provenance = service.get_student_provenance(st_id)

    # 1. TOP HEADER
    render_page_header(
        title="Settings & Data Privacy",
        subtitle="Manage academic datasets, scenario benchmarks, privacy configurations, and summary exports.",
        student=student,
        provenance=provenance,
        as_of_date="2026-09-30",
        academic_status="Platform Settings Active",
    )

    # 1. Privacy & Security Boundary Card
    render_html(
        """
        <div class="edu-card" style="border-left: 4px solid #10b981;">
            <h4 style="margin-top:0; color:#166534;">🔒 Security & Privacy Guarantees</h4>
            <ul style="margin:8px 0 0 0; padding-left:18px; line-height:1.6; color:#334155; font-size:0.9rem;">
                <li><strong>No Credential Ingestion</strong>: EduPulse never asks for, accepts, or stores university usernames, passwords, or CAPTCHAs.</li>
                <li><strong>No Live Scraping</strong>: Live campus portal scraping without institutional API authorization is strictly prohibited.</li>
                <li><strong>Synthetic Identity Defaults</strong>: All demo profiles use completely synthetic identifiers (e.g. <code>Priya Sharma</code>, <code>SYNTH-2026-001</code>).</li>
                <li><strong>Local-Only Storage</strong>: Student records and runtime marks reside entirely in your local session and ephemeral SQLite database.</li>
            </ul>
        </div>
        """
    )

    render_html("<div style='margin-bottom: 24px;'></div>")

    # 2. Reference Scenarios -> Screenshot Reference
    st.subheader("🔬 Reference Scenarios")
    st.markdown("##### Screenshot Reference")
    st.caption("Settings → Reference Scenarios → Screenshot Reference")
    render_html(
        """
        <div class="edu-card" style="border-left: 4px solid #6366f1; background: #faf5ff;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <strong style="color:#4338ca; font-size:1.02rem;">📸 Screenshot Reference (CHARUSAT Validation Benchmark)</strong>
                <span class="badge-moderate">Reference / Validation Data</span>
            </div>
            <p style="margin: 6px 0 4px 0; font-size: 0.88rem; color: #475569;">
                <strong>Data Classification:</strong> <code>Reference / Validation Data</code> &nbsp;•&nbsp; 
                <strong>Benchmark Purpose:</strong> Preserved strictly for automated regression testing and validation against authentic portal screenshots.
                This persona is not the default demo student.
            </p>
            <ul style="margin: 4px 0 8px 0; font-size: 0.84rem; color: #334155; line-height:1.5;">
                <li><strong>Portal Truncation Mismatch:</strong> Banner displays 80.0% while exact computed attendance from visible rows is 76.5%.</li>
                <li><strong>Component Alerts:</strong> Critical Professional Identity (CPI) LECT at 57.1% and FDSA LAB at 63.6% (both below 70%).</li>
                <li><strong>Discovered Courses:</strong> Timetable discovery finds DM and FCN with attendance marked as UNMARKED ('-').</li>
                <li><strong>Semester 1 Incomplete Credits:</strong> December 2025 SGPA 7.63 with creditsComplete = false (Semester 2 not in supplied data).</li>
            </ul>
        </div>
        """
    )
    col_ref1, col_ref2 = st.columns([2, 2])
    with col_ref1:
        if st.button("Load Screenshot Reference (S3)", type="primary", key="btn_load_screenshot_ref", use_container_width=True):
            if not service.get_student_profile("student_s3"):
                service.reset_to_scenario("S3")
            st.session_state["current_student_id"] = "student_s3"
            st.success("Loaded Screenshot Reference Persona (S3)! Redirecting...")
            st.rerun()
    with col_ref2:
        st.markdown(f"<div style='margin-top:8px; font-size:0.88rem; color:#475569;'>Active Student: <strong>{student.name if student else 'None'} ({st_id})</strong></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 3. Synthetic Personas Dataset Selector
    st.subheader("🎭 Synthetic Student Personas")
    st.caption("Switch between our 6 varied synthetic student personas to test calculations and UI responsiveness:")

    personas = service.get_available_personas()
    synth_personas = [p for p in personas if p["id"] != "student_s3"]

    cols_p = st.columns(3)
    for idx, p in enumerate(synth_personas):
        with cols_p[idx % 3]:
            is_active = (p["id"] == st_id)
            btn_label = f"✓ Active: {p['name']}" if is_active else f"Select {p['name']}"
            btn_type = "primary" if is_active else "secondary"
            render_html(
                f"""
                <div class="edu-card" style="height: 140px; margin-bottom: 8px; {'border-left: 4px solid #3b82f6;' if is_active else ''}">
                    <strong style="font-size:0.95rem; color:#0f172a;">{p['icon']} {p['name']}</strong><br/>
                    <span class="{p.get('badge_class', 'badge-info')}" style="font-size: 0.72rem;">{p['archetype']}</span>
                    <p style="font-size: 0.8rem; color: #64748b; margin-top: 6px; line-height:1.35;">{p['description']}</p>
                </div>
                """
            )
            if st.button(btn_label, key=f"btn_p_{p['id']}", type=btn_type, use_container_width=True):
                st.session_state["current_student_id"] = p["id"]
                st.rerun()

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 4. Workspace Reset & Lifecycle Controls
    st.subheader("🛠️ Workspace State & Reset Controls")
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        render_html(
            """
            <div class="edu-card">
                <h5 style="margin-top:0;">Reset Demo Data</h5>
                <p style="font-size:0.85rem; color:#64748b;">
                    Restores all synthetic demo personas and reference scenarios back to pristine initial defaults.
                </p>
            </div>
            """
        )
        if st.button("Reset All Demo Personas", key="btn_reset_all_demo", use_container_width=True):
            service.seed_all_personas(reset=True)
            st.session_state["current_student_id"] = "student_synth_strong"
            st.success("All demo records reset to baseline defaults!")
            st.rerun()

    with col_act2:
        render_html(
            """
            <div class="edu-card">
                <h5 style="margin-top:0;">Clear Local Database</h5>
                <p style="font-size:0.85rem; color:#64748b;">
                    Purges ephemeral local database entries and clears imported files.
                </p>
            </div>
            """
        )
        if st.button("Delete All Local Data", key="btn_delete_all_data", use_container_width=True):
            service.delete_all_data()
            service.seed_all_personas(reset=True)
            st.session_state["current_student_id"] = "student_synth_strong"
            st.success("Cleared local database and restored initial baseline!")
            st.rerun()

    render_html("<div style='margin-bottom: 24px;'></div>")

    # 5. Policy Configuration Inspector
    st.subheader("📋 Academic Policy Configuration")
    col_p1, col_p2 = st.columns([3, 1])
    with col_p1:
        render_html(
            f"""
            <div class="edu-card">
                <p style="margin:0 0 6px 0; font-size:0.92rem;">
                    Policy Version: <strong>v{policy.version}</strong> &nbsp;|&nbsp; 
                    Overall Threshold: <strong>{policy.attendanceOverallPct:.0f}%</strong> &nbsp;|&nbsp; 
                    Course Threshold: <strong>{policy.attendancePerCoursePct:.0f}%</strong> &nbsp;|&nbsp; 
                    Small Sample Guard: <strong>{policy.smallSampleThreshold} classes</strong>
                </p>
                <div style="font-size:0.82rem; color:#64748b;">
                    Source Note: {policy.sourceNote}
                </div>
            </div>
            """
        )
    with col_p2:
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        render_verification_badge(policy.verified, "Policy Verified" if policy.verified else "Unverified for your institute")

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 6. De-identified Summary Export
    st.subheader("📤 Export De-Identified Academic Summary")
    st.caption("Export your analytics, signals, and course metrics without personal identifiers (PII-free JSON):")

    sem = student.semester if student else 3
    signals = service.get_support_signals(st_id)
    att_summary = service.get_attendance_summary(st_id, sem)

    deidentified_payload = {
        "program": student.program if student else "B.Tech IT (demo)",
        "semester": sem,
        "academicYear": student.academicYear if student else "2026-27",
        "provenance": provenance,
        "computedOverallAttendance": att_summary["computedOverall"],
        "attendanceSignal": signals["attendanceSignal"].value,
        "academicSignal": signals["academicSignal"].value,
        "overallSupportSignal": signals["overallSupportSignal"].value,
        "engagementLevel": signals["engagementSummary"]["level"],
        "engagementPoints": signals["engagementSummary"]["points"],
        "componentAttendance": [
            {
                "courseCode": r.courseId,
                "component": r.component.value,
                "percentage": r.computed_percentage,
                "present": r.presentCount,
                "total": r.totalCount,
            }
            for r in att_summary["records"]
        ],
    }

    json_str = json.dumps(deidentified_payload, indent=2)
    st.download_button(
        "📥 Download De-Identified Summary (JSON)",
        data=json_str,
        file_name=f"edupulse_summary_{st_id}.json",
        mime="application/json",
        key="btn_download_deidentified_json",
        use_container_width=True,
    )
