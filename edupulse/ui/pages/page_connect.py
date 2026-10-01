# Security Notice: EduPulse never asks for passwords, credentials, tokens, or captchas.
import streamlit as st

from edupulse.domain.models import Student
from edupulse.providers.authorized_charusat import AuthorizedCharusatProvider, NotAuthorizedError
from edupulse.providers.file_import import FileImportProvider
from edupulse.providers.paste_import import PasteImportProvider
from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import (
    apply_custom_theme,
    render_html,
    render_page_header,
)


def render_page(service: AcademicService):
    apply_custom_theme()
    st_id = st.session_state.get("current_student_id", "student_synth_strong")
    student = service.get_student_profile(st_id)
    provenance = service.get_student_provenance(st_id)

    # 1. TOP HEADER
    render_page_header(
        title="Connect Academic Data",
        subtitle="Manage student records: select synthetic demo archetypes, upload local spreadsheets, or review institutional connectors.",
        student=student,
        provenance=provenance,
        as_of_date="2026-09-30",
        academic_status="Data Ingestion Gateway",
    )

    # Security & Integrity Banner
    st.info(
        "🔒 **Security Notice**: EduPulse never asks for, accepts, or stores university passwords, session tokens, or CAPTCHAs. "
        "All intelligence runs exclusively on self-supplied files, synthetic archetypes, or university-authorized sandboxes. "
        "Live unauthorized campus portal scraping is strictly prohibited."
    )

    tab_demo, tab_upload, tab_paste, tab_authorized = st.tabs(
        [
            "🎭 Use Demo Data",
            "📥 Import Academic Data (File Upload)",
            "📋 Paste Academic Data",
            "🔒 Authorized Academic Provider",
        ]
    )

    # -------------------------------------------------------------
    # TAB 1: Use Demo Data
    # -------------------------------------------------------------
    with tab_demo:
        st.subheader("Use Demo Data")
        st.caption("Select from 6 varied synthetic student personas to test analytics across different academic scenarios:")

        personas = service.get_available_personas()
        cur_id = st.session_state.get("current_student_id", "student_synth_strong")

        for p in personas:
            col_c1, col_c2 = st.columns([4, 1.2])
            is_active = (p["id"] == cur_id)
            prov = p.get("provenance", "Demo data")
            prov_badge = (
                "badge-low"
                if prov == "Demo data"
                else ("badge-moderate" if "Reference" in prov else "badge-info")
            )
            status_str = p.get("academic_status", "Active Term • Record Ready")

            with col_c1:
                render_html(
                    f"""
                    <div class="edu-card" style="margin-bottom: 8px; {'border-left: 4px solid #3b82f6;' if is_active else ''}">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:4px;">
                            <strong style="font-size:1.02rem; color:#0f172a;">{p['name']} ({p['external_id']})</strong>
                            <span class="{p.get('badge_class', 'badge-info')}">{p['archetype']}</span>
                        </div>
                        <p style="margin:4px 0 2px 0; color:#475569; font-size:0.88rem;">
                            <strong>Program:</strong> {p['program']} (Semester {p['semester']}, {p.get('academic_year', '2026-27')}) &nbsp;•&nbsp; 
                            <strong>Data Status:</strong> <code>{status_str}</code> &nbsp;•&nbsp; 
                            <strong>Source:</strong> <span class="{prov_badge}">{prov}</span>
                        </p>
                        <p style="margin:0; color:#64748b; font-size:0.84rem;">{p['description']}</p>
                    </div>
                    """
                )
            with col_c2:
                st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
                btn_label = "Active Profile ✓" if is_active else "Load Profile"
                btn_type = "primary" if is_active else "secondary"
                if st.button(btn_label, key=f"sel_persona_{p['id']}", type=btn_type, use_container_width=True):
                    st.session_state["current_student_id"] = p["id"]
                    st.success(f"Loaded student profile for {p['name']}.")
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 2: Import Academic Data (File Upload)
    # -------------------------------------------------------------
    with tab_upload:
        st.subheader("Import Academic Data (CSV / JSON)")
        st.write("Upload self-supplied academic records exported from your university student view:")

        st.markdown("**Download Standard CSV Templates:**")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.download_button(
                "📥 Attendance CSV Template",
                data=FileImportProvider.generate_attendance_csv_template(),
                file_name="attendance_template.csv",
                mime="text/csv",
                key="btn_download_att_template",
                use_container_width=True,
            )
        with col_t2:
            st.download_button(
                "📥 Marks CSV Template",
                data=FileImportProvider.generate_marks_csv_template(),
                file_name="marks_template.csv",
                mime="text/csv",
                key="btn_download_marks_template",
                use_container_width=True,
            )
        with col_t3:
            st.download_button(
                "📥 Daily Timetable CSV Template",
                data=FileImportProvider.generate_daily_csv_template(),
                file_name="daily_timetable_template.csv",
                mime="text/csv",
                key="btn_download_daily_template",
                use_container_width=True,
            )

        st.divider()

        col_up1, col_up2 = st.columns([2, 1])
        with col_up1:
            uploaded_file = st.file_uploader(
                "Step 1: Choose an Attendance CSV File", type=["csv"], key="file_upload_input"
            )
        with col_up2:
            import_student_name = st.text_input("Student Name (Optional)", value="Imported Student", key="txt_import_name")
            import_student_prog = st.text_input("Degree Program", value="B.Tech IT (Self-Supplied)", key="txt_import_prog")

        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            st.markdown("### Step 2 & 3: Preview & Validation")
            target_id = f"student_imported_{abs(hash(import_student_name)) % 10000}"
            preview = FileImportProvider.preview_attendance_csv(content, target_id)

            if preview["valid"]:
                st.success(f"✓ Validated {preview['rowCount']} rows cleanly (Batch checksum: `{preview['checksum']}`).")
                if st.button("Confirm and Commit Import", type="primary", key="btn_commit_file_import"):
                    imported_student = Student(
                        id=target_id,
                        externalStudentId=f"IMP-{abs(hash(import_student_name)) % 1000:03d}",
                        name=import_student_name,
                        program=import_student_prog,
                        semester=3,
                        academicYear="2026-27",
                    )
                    service.repo.save_student(imported_student)

                    for rec in preview["records"]:
                        service.repo.save_attendance_record(rec)

                    st.session_state["current_student_id"] = target_id
                    st.success(f"Batch imported successfully! Active student profile set to '{import_student_name}'.")
                    st.rerun()
            else:
                st.error("Validation errors detected in uploaded file:")
                for err in preview["errors"]:
                    st.markdown(f"- ❌ {err}")

    # -------------------------------------------------------------
    # TAB 3: Paste Academic Data
    # -------------------------------------------------------------
    with tab_paste:
        st.subheader("Paste Academic Data")
        st.caption("Copy table rows directly from your portal screen (e.g. `CEUE203 / OOP | LECT | 14 / 15 | 93.3%`):")

        paste_text = st.text_area(
            "Paste attendance table rows here",
            height=140,
            key="paste_import_input",
            placeholder="Course Code / Name | Component | Present / Total | Percentage\nCEUE203 / OOP | LECT | 14 / 15 | 93.3%\nCSUC201 / FDSA | LAB | 7 / 11 | 63.6%",
        )

        if st.button("Preview Pasted Data", key="btn_preview_paste"):
            if paste_text.strip():
                cur_id = st.session_state.get("current_student_id", "student_synth_strong")
                p_preview = PasteImportProvider.parse_attendance_paste(paste_text, cur_id)
                if p_preview["valid"]:
                    st.success(f"Parsed {p_preview['rowCount']} valid attendance records.")
                    for r in p_preview["records"]:
                        st.markdown(f"- **{r.courseId}** ({r.component.value}): {r.presentCount}/{r.totalCount} ({r.computed_percentage}%)")
                    if st.button("Commit Pasted Attendance", type="primary", key="btn_commit_paste"):
                        for r in p_preview["records"]:
                            service.repo.save_attendance_record(r)
                        st.success("Pasted records committed to active student profile!")
                        st.rerun()
                else:
                    st.error("Errors encountered while parsing pasted text:")
                    for err in p_preview["errors"]:
                        st.markdown(f"- ❌ {err}")
            else:
                st.warning("Please paste some table rows first.")

    # -------------------------------------------------------------
    # TAB 4: Authorized Institutional Connector
    # -------------------------------------------------------------
    with tab_authorized:
        st.subheader("Authorized Institutional Connector")
        st.warning("⚠️ **Live university synchronization requires an authorized institutional integration.**")

        render_html(
            """
            <div class="edu-card" style="border-left: 4px solid #f59e0b;">
                <h4>🔒 Enterprise Institutional Connector (Production Architecture)</h4>
                <p>Status: <span class="badge-moderate">Feature Flagged • Staged Offline</span></p>
                <p>
                    EduPulse does <strong>not</strong> claim live connection to CHARUSAT or any other institution.
                    Direct integration with a live university Student Information System (SIS) strictly requires:
                </p>
                <ol style="font-size: 0.92rem; color: #334155; line-height: 1.6;">
                    <li><strong>Institutional SSO / OAuth 2.0</strong>: SAML 2.0 or OIDC authentication sanctioned by university administration.</li>
                    <li><strong>Read-Only API Scopes</strong>: Secure REST/GraphQL token exchange restricted to evaluation and attendance endpoints.</li>
                    <li><strong>Zero Credential Retention</strong>: Direct user credentials (passwords, OTPs, CAPTCHAs) are strictly never handled or stored.</li>
                    <li><strong>No Scraping Compliance</strong>: Live campus portal scraping without official institution authorization is strictly prohibited.</li>
                </ol>
            </div>
            """
        )

        st.markdown("##### Test Authorized Institutional Connector Stub")
        st.caption("Verify that the production connector stub raises `NotAuthorizedError` when live sync is attempted without institutional credentials:")

        if st.button("Invoke AuthorizedCharusatProvider() Stub", key="btn_test_auth_provider"):
            try:
                provider = AuthorizedCharusatProvider()
                provider.get_profile()
            except NotAuthorizedError as e:
                st.info(f"🛡️ **Security Boundary Verified**: `{type(e).__name__}` caught successfully: {e}")
                st.caption("Confirmed: The system cleanly refuses live connections until an official university partnership is established.")
