import streamlit as st

from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import apply_custom_theme
from edupulse.ui.pages import (
    page_academic,
    page_attendance,
    page_cohort,
    page_connect,
    page_dashboard,
    page_engagement,
    page_explorer,
    page_record,
    page_scholarship,
    page_settings,
)

st.set_page_config(
    page_title="EduPulse — Student Success & Academic Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_theme()


# Initialize academic service
def get_service() -> AcademicService:
    srv = AcademicService()
    if not srv.get_student_profile("student_synth_strong"):
        srv.seed_all_personas(reset=True)
    return srv


service = get_service()

# Default to synthetic persona (Priya Sharma - Strong Academics & Attendance)
if "current_student_id" not in st.session_state:
    st.session_state["current_student_id"] = "student_synth_strong"

# Sidebar: Compact Student Profile Context
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 4px 0 10px 0;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.4rem;">🎓</span>
                <span style="font-family:'Plus Jakarta Sans',sans-serif; font-size:1.15rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em;">
                    EduPulse
                </span>
            </div>
            <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Student Academic Intelligence Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    personas = service.get_available_personas()
    cur_id = st.session_state.get("current_student_id", "student_synth_strong")
    ids = [p["id"] for p in personas]
    cur_idx = ids.index(cur_id) if cur_id in ids else 0

    def on_persona_change():
        st.session_state["current_student_id"] = st.session_state["_sidebar_persona_selector"]

    selected_pid = st.selectbox(
        "Active Student Profile",
        options=ids,
        index=cur_idx,
        format_func=lambda pid: next((f"{p['name']} ({p['archetype']})" for p in personas if p["id"] == pid), pid),
        key="_sidebar_persona_selector",
        on_change=on_persona_change,
        help="Select demo persona to observe dynamic analytics across all intelligence modules.",
    )
    st.session_state["current_student_id"] = selected_pid

    active_persona = next((p for p in personas if p["id"] == selected_pid), None)
    if active_persona:
        prov = active_persona.get("provenance", "Demo data")
        badge_style = "badge-low" if prov == "Demo data" else ("badge-moderate" if "Reference" in prov else "badge-info")
        status_info = active_persona.get("academic_status", "Active Term")
        st.markdown(
            f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; margin-top: 6px; font-size: 0.8rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 4px;">
                    <span style="color:#475569; font-weight:600;">Data Source:</span>
                    <span class="{badge_style}" style="font-size:0.72rem; padding:2px 8px;">{prov}</span>
                </div>
                <div style="color: #64748b; font-size: 0.76rem; line-height: 1.35; margin-top:4px;">
                    {active_persona.get('description', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# Page callbacks
def show_dashboard():
    page_dashboard.render_page(service)


def show_attendance():
    page_attendance.render_page(service)


def show_academic():
    page_academic.render_page(service)


def show_engagement():
    page_engagement.render_page(service)


def show_explorer():
    page_explorer.render_page(service)


def show_scholarship():
    page_scholarship.render_page(service)


def show_record():
    page_record.render_page(service)


def show_connect():
    page_connect.render_page(service)


def show_cohort():
    page_cohort.render_page(service)


def show_settings():
    page_settings.render_page(service)


# Standardized Multipage Navigation
pages = {
    "Student Workspace": [
        st.Page(show_dashboard, title="Overview", icon="🏠", default=True, url_path="dashboard"),
        st.Page(show_attendance, title="Attendance", icon="📊", url_path="attendance"),
        st.Page(show_academic, title="Academics", icon="📚", url_path="academic"),
        st.Page(show_engagement, title="Engagement", icon="🌟", url_path="engagement"),
        st.Page(show_explorer, title="Success Explorer", icon="🧭", url_path="explorer"),
        st.Page(show_scholarship, title="Scholarship", icon="🎖️", url_path="scholarship"),
        st.Page(show_record, title="Full Academic Record", icon="📑", url_path="record"),
    ],
    "Data & Administration": [
        st.Page(show_connect, title="Academic Data", icon="📂", url_path="connect"),
        st.Page(show_cohort, title="Mentor Explorer", icon="👥", url_path="cohort"),
        st.Page(show_settings, title="Data & Privacy", icon="⚙️", url_path="settings"),
    ],
}

nav = st.navigation(pages)
nav.run()
