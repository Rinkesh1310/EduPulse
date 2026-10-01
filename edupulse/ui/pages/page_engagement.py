from datetime import datetime

import pandas as pd
import streamlit as st

from edupulse.domain.enums import EngagementStatus
from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import (
    apply_custom_theme,
    render_html,
    render_metric_card,
    render_page_header,
)


def render_page(service: AcademicService):
    apply_custom_theme()
    st_id = st.session_state.get("current_student_id", "student_synth_strong")
    student = service.get_student_profile(st_id)
    provenance = service.get_student_provenance(st_id)
    summary = service.get_engagement_summary(st_id)

    # 1. TOP HEADER
    render_page_header(
        title="Engagement & Co-Curricular",
        subtitle="Co-curricular portfolio tracking, competitive achievements, and skill-building activities.",
        student=student,
        provenance=provenance,
        as_of_date="2026-09-30",
        academic_status=f"Portfolio Status: {summary['level']}",
    )

    # 2. TOP METRIC TILES
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card(
            title="Engagement Level",
            value=summary["level"],
            subtext=summary["description"],
            status_level="Low" if summary["points"] >= 4.0 else "Moderate",
        )
    with m2:
        render_metric_card(
            title="Engagement Points",
            value=f"{summary['points']:.1f}",
            subtext="Activity weight × duration factor",
            status_level=None,
        )
    with m3:
        render_metric_card(
            title="Confirmed Events",
            value=str(summary["eventCount"]),
            subtext="Current academic term",
            status_level=None,
        )
    with m4:
        render_metric_card(
            title="Activity Diversity",
            value=str(summary["diversityCount"]),
            subtext="Distinct category types",
            status_level=None,
        )

    # Academic Fairness & Independence Guarantee
    st.info(
        "⚖️ **Academic Fairness & Independence Principle**: Co-curricular activities celebrate student initiative and holistic growth. "
        "Engagement metrics **never directly increase or decrease the academic support signal**, nor do they excuse required class attendance."
    )

    if summary.get("overlaps"):
        for ov in summary["overlaps"]:
            st.warning(
                f"ℹ️ **Attendance Overlap**: Event '{ov['name']}' on {ov['date']} matches an official Present (P) session. *{ov['note']}*"
            )

    tab_cat, tab_hist, tab_calc = st.tabs(
        ["📋 Activity Catalogue & Selection", "📜 Confirmed Participation History", "ℹ️ How Calculated?"]
    )

    all_events = service.get_events()
    participations = {p.eventId: p for p in service.get_participations(st_id)}

    # -------------------------------------------------------------
    # TAB 1: Catalogue & Selection
    # -------------------------------------------------------------
    with tab_cat:
        st.subheader("Campus Activity Catalogue")
        st.caption("Browse sanctioned university competitions, hackathons, and technical workshops:")

        col_d1, col_d2 = st.columns([3, 1.2])
        with col_d1:
            st.markdown(f"Term Declaration: **{summary['status']}**")
        with col_d2:
            if st.button("Declare No Events This Term", key="btn_decl_none", use_container_width=True):
                service.set_engagement_declaration(st_id, "2026-27-ODD", EngagementStatus.DECLARED_NONE)
                st.success("Declared no events for the current term (Informational).")
                st.rerun()

        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 Search catalogue by event name or organizer", value="", key="search_events")
        with col_s2:
            types = ["All Categories"] + sorted(list({e.activityType.title() for e in all_events}))
            sel_type = st.selectbox("Category Filter", types, key="filter_cat")

        filtered_events = all_events
        if search_query.strip():
            q = search_query.lower()
            filtered_events = [
                e for e in filtered_events
                if q in e.name.lower() or q in e.organizer.lower()
            ]
        if sel_type != "All Categories":
            filtered_events = [e for e in filtered_events if e.activityType.lower() == sel_type.lower()]

        st.caption(f"Displaying **{len(filtered_events)}** of **{len(all_events)}** campus activities:")

        for evt in filtered_events:
            is_participated = evt.eventId in participations and participations[evt.eventId].confirmed
            duration_desc = "Full Day" if evt.durationType == "full-day" else f"{evt.hours or 1.0}h"

            with st.container():
                col_c1, col_c2 = st.columns([4, 1.5])
                with col_c1:
                    status_badge = '<span class="badge-low" style="font-size:0.75rem;">✓ Participated</span>' if is_participated else '<span class="badge-neutral" style="font-size:0.75rem;">Not Logged</span>'
                    render_html(
                        f"""
                        <div class="edu-card" style="margin-bottom: 8px; {'border-left: 4px solid #10b981;' if is_participated else ''}">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <strong style="font-size: 1.02rem; color: #0f172a;">{evt.name}</strong>
                                <div style="display:flex; gap:6px;">
                                    <span class="badge-info" style="font-size: 0.75rem;">{evt.activityType.title()}</span>
                                    {status_badge}
                                </div>
                            </div>
                            <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">
                                📅 <strong>{evt.date}</strong> &nbsp;|&nbsp; ⏱️ Duration: <strong>{duration_desc}</strong> &nbsp;|&nbsp; 🏛️ Organizer: <strong>{evt.organizer}</strong>
                            </div>
                        </div>
                        """
                    )
                with col_c2:
                    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
                    btn_label = "Remove Participation" if is_participated else "I Participated ✓"
                    btn_type = "secondary" if is_participated else "primary"
                    if st.button(btn_label, type=btn_type, key=f"btn_part_{evt.eventId}", use_container_width=True):
                        new_state = not is_participated
                        service.toggle_event_participation(
                            student_id=st_id,
                            event_id=evt.eventId,
                            confirmed=new_state,
                            confirmation_date=datetime.now().strftime("%Y-%m-%d"),
                        )
                        service.set_engagement_declaration(st_id, "2026-27-ODD", EngagementStatus.HAS_EVENTS)
                        st.rerun()

    # -------------------------------------------------------------
    # TAB 2: Participation History
    # -------------------------------------------------------------
    with tab_hist:
        st.subheader("Confirmed Participation History")
        confirmed_parts = [p for p in service.get_participations(st_id) if p.confirmed]

        if confirmed_parts:
            events_map = {e.eventId: e for e in all_events}
            hist_records = []
            for p in confirmed_parts:
                evt = events_map.get(p.eventId)
                if evt:
                    hist_records.append({
                        "Activity Name": evt.name,
                        "Category": evt.activityType.title(),
                        "Date": evt.date,
                        "Duration": "Full Day" if evt.durationType == "full-day" else f"{evt.hours or 1.0}h",
                        "Organizer": evt.organizer,
                        "Confirmed Timestamp": p.confirmationDate or "N/A",
                    })

            df_hist = pd.DataFrame(hist_records)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)
            st.caption("You can toggle participation on or off from the catalogue tab at any time.")
        else:
            st.info("ℹ️ **No participation records confirmed yet**. Select events from the catalogue above to add to your history.")

    # -------------------------------------------------------------
    # TAB 3: How Calculated
    # -------------------------------------------------------------
    with tab_calc:
        st.subheader("Engagement Calculation Formulation")
        st.markdown(
            r"""
            **Points Formulation**:
            $$\text{Points} = \sum (\text{Activity Weight} \times \text{Duration Factor})$$
            - **Activity Weights**: Hackathon (3.0), Competition (3.0), Project (3.0), Workshop (2.0), Academic Activity (2.0), Seminar (1.0), Club (1.0).
            - **Duration Factor**: Full-Day event = 1.0; Hourly event = $\min(\text{hours}/4.0, 1.0)$ with floor 0.25.
            - **Tiers**:
              - *Getting started*: 1–2 events or <4 points.
              - *Active*: $\ge 4$ points or $\ge 3$ events.
              - *Highly active*: $\ge 10$ points across $\ge 3$ distinct activity types.
            - **Zero Negative Impact**: Low participation never creates an academic penalty or alters the core support signal.
            """
        )
