import pandas as pd
import plotly.express as px
import streamlit as st

from edupulse.core.attendance import classify_attendance_band
from edupulse.domain.enums import AttendanceBand
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
    sem = student.semester if student else 3
    policy = service.get_policy()
    provenance = service.get_student_provenance(st_id)
    att_summary = service.get_attendance_summary(st_id, sem)
    records = att_summary["records"]
    as_of = att_summary.get("asOfDate", "2026-09-30")

    # 1. TOP HEADER
    render_page_header(
        title="Attendance Intelligence",
        subtitle="Component-level attendance tracking, threshold policies, and real-time recovery simulations.",
        student=student,
        provenance=provenance,
        as_of_date=as_of,
        academic_status="Attendance Baseline Active",
    )

    # 2. TOP METRICS
    computed_overall = att_summary["computedOverall"]
    comp_str = f"{computed_overall:.1f}%" if computed_overall is not None else "N/A"
    portal_val = att_summary["portalOverall"]
    portal_str = f"{portal_val:.1f}%" if portal_val is not None else "N/A"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card(
            title="Computed Overall",
            value=comp_str,
            subtext=f"{att_summary['totalPresent']}/{att_summary['totalClasses']} total sessions",
            status_level="Low" if (computed_overall or 0) >= policy.attendanceOverallPct else ("High" if (computed_overall or 0) < policy.attendancePerCoursePct else "Moderate"),
        )
    with m2:
        render_metric_card(
            title="Portal Reported",
            value=portal_str,
            subtext="Banner snapshot figure",
            status_level=None,
        )
    with m3:
        render_metric_card(
            title="Course Minimum",
            value=f"{policy.attendancePerCoursePct:.0f}%",
            subtext="Per-component target",
            status_level=None,
        )
    with m4:
        render_metric_card(
            title="Overall Minimum",
            value=f"{policy.attendanceOverallPct:.0f}%",
            subtext="Institutional standard",
            status_level=None,
        )

    if att_summary["mismatchNote"]:
        render_html(
            f"""
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:10px 14px; margin: 16px 0; font-size:0.88rem; color:#92400e;">
                ⚠️ <strong>Discrepancy Note:</strong> {att_summary['mismatchNote']}. Both figures are preserved without fabrication.
            </div>
            """
        )

    render_html("<div style='margin-bottom: 20px;'></div>")

    # 3. INTERACTIVE SUBJECT BREAKDOWN & FILTERS
    st.subheader("Subject-Level Attendance Breakdown")

    col_f1, col_f2, col_f3 = st.columns([1.5, 1.2, 1.2])
    with col_f1:
        courses_available = sorted(list({r.courseId for r in records}))
        sel_course_filter = st.selectbox(
            "Filter by Subject",
            options=["All Subjects"] + courses_available,
            key="att_sel_course_filter",
        )
    with col_f2:
        sel_comp_filter = st.selectbox(
            "Filter by Component",
            options=["All Components", "LECT", "LAB", "OTHER"],
            key="att_sel_comp_filter",
        )
    with col_f3:
        view_mode = st.radio(
            "Aggregation View",
            ["Component Breakdown", "Course Combined"],
            horizontal=True,
            key="att_view_mode",
        )

    # Apply filters
    filtered_records = records
    if sel_course_filter != "All Subjects":
        filtered_records = [r for r in filtered_records if r.courseId == sel_course_filter]
    if sel_comp_filter != "All Components":
        filtered_records = [r for r in filtered_records if r.component.value == sel_comp_filter]

    if view_mode == "Component Breakdown":
        if filtered_records:
            cols = st.columns(3)
            for idx, r in enumerate(filtered_records):
                band = classify_attendance_band(
                    r.computed_percentage,
                    threshold=policy.attendancePerCoursePct,
                    is_overall=False,
                    total_classes=r.totalCount,
                    small_sample_threshold=policy.smallSampleThreshold,
                )

                status_text = "Strong"
                badge_class = "badge-low"
                border_color = "#10b981"

                if band == AttendanceBand.EARLY_DATA:
                    status_text = "Early Data (<8 classes)"
                    badge_class = "badge-neutral"
                    border_color = "#cbd5e1"
                elif band == AttendanceBand.ATTENTION:
                    status_text = "Attention Area (<70%)"
                    badge_class = "badge-high"
                    border_color = "#ef4444"
                elif band == AttendanceBand.MONITOR:
                    status_text = "Monitor"
                    badge_class = "badge-moderate"
                    border_color = "#f59e0b"

                with cols[idx % 3]:
                    render_html(
                        f"""
                        <div class="edu-card" style="border-left: 4px solid {border_color}; margin-bottom: 14px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                                <strong style="font-size: 1.02rem; color: #0f172a;">{r.courseId}</strong>
                                <span class="{badge_class}" style="font-size: 0.76rem;">{status_text}</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 8px;">
                                Component: <strong>{r.component.value}</strong>
                            </div>
                            <div style="font-size: 1.6rem; font-weight: 800; color: #0f172a; margin-bottom: 4px;">
                                {r.computed_percentage}%
                            </div>
                            <div style="font-size: 0.85rem; color: #475569;">
                                Attended <strong>{r.presentCount}</strong> of <strong>{r.totalCount}</strong> sessions
                            </div>
                        </div>
                        """
                    )
        else:
            st.info("No attendance records match the selected filter criteria.")
    else:
        # Combined by course view
        combined = att_summary["combinedByCourse"]
        if sel_course_filter != "All Subjects":
            combined = {k: v for k, v in combined.items() if k == sel_course_filter}

        cols = st.columns(min(len(combined), 3) if combined else 1)
        for idx, (c_id, data) in enumerate(combined.items()):
            pct = data["percentage"]
            band = classify_attendance_band(pct, threshold=policy.attendancePerCoursePct, is_overall=False)
            status_text = "Strong" if band == AttendanceBand.STRONG else ("Attention Area" if band == AttendanceBand.ATTENTION else "Monitor")
            badge_class = "badge-low" if band == AttendanceBand.STRONG else ("badge-high" if band == AttendanceBand.ATTENTION else "badge-moderate")
            border_color = "#10b981" if band == AttendanceBand.STRONG else ("#ef4444" if band == AttendanceBand.ATTENTION else "#f59e0b")

            with cols[idx % len(cols)]:
                render_html(
                    f"""
                    <div class="edu-card" style="border-left: 4px solid {border_color};">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; font-size:1.05rem;">{c_id} (Combined)</h4>
                            <span class="{badge_class}">{status_text}</span>
                        </div>
                        <div style="font-size: 1.6rem; font-weight: 800; color: #0f172a; margin: 8px 0 4px 0;">
                            {pct}%
                        </div>
                        <p style="font-size:0.85rem; color:#475569; margin:0;">
                            {data['present']} attended / {data['total']} total sessions
                        </p>
                    </div>
                    """
                )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 4. INTERACTIVE ATTENDANCE TREND & DISTRIBUTION CHART
    st.subheader("📊 Component Attendance Overview Chart")
    if records:
        chart_records = [
            {
                "Component": f"{r.courseId} ({r.component.value})",
                "Attendance (%)": r.computed_percentage,
                "Present": r.presentCount,
                "Total": r.totalCount,
                "Status": "Attention Area" if (r.computed_percentage or 0) < 70 else ("Monitor" if (r.computed_percentage or 0) < 80 else "Strong"),
            }
            for r in records
            if r.computed_percentage is not None
        ]
        fig_att = px.bar(
            chart_records,
            x="Component",
            y="Attendance (%)",
            color="Status",
            color_discrete_map={
                "Strong": "#10b981",
                "Monitor": "#f59e0b",
                "Attention Area": "#ef4444",
            },
            range_y=[0, 100],
            title="Component Attendance Relative to Thresholds",
        )
        fig_att.add_hline(y=float(policy.attendancePerCoursePct), line_dash="dash", line_color="#ef4444", annotation_text=f"Course Threshold ({policy.attendancePerCoursePct:.0f}%)")
        fig_att.add_hline(y=float(policy.attendanceOverallPct), line_dash="dash", line_color="#2563eb", annotation_text=f"Overall Target ({policy.attendanceOverallPct:.0f}%)")
        fig_att.update_layout(height=280, margin=dict(l=20, r=20, t=35, b=20))
        st.plotly_chart(fig_att, use_container_width=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 5. RECOVERY CALCULATOR (Immediate execution)
    st.subheader("🎯 Attendance Recovery & Future Simulation")
    st.caption("Plan future attendance trajectory to achieve or maintain your required institutional standing:")

    rc_col1, rc_col2 = st.columns(2)
    with rc_col1:
        options = ["Overall"] + [f"{r.courseId} ({r.component.value})" for r in records]
        calc_target_item = st.selectbox("Target Scope", options, key="calc_target_scope")
        target_pct = st.slider("Target Percentage (%)", min_value=50.0, max_value=95.0, value=75.0, step=1.0, key="calc_target_pct")
        remaining_classes_input = st.number_input(
            "Estimated Remaining Classes (Planning Assumption)",
            min_value=1,
            max_value=150,
            value=35,
            step=5,
            key="calc_remaining_classes",
        )

    with rc_col2:
        if calc_target_item == "Overall":
            cur_p = att_summary["totalPresent"]
            cur_t = att_summary["totalClasses"]
        else:
            sel_idx = options.index(calc_target_item) - 1
            cur_p = records[sel_idx].presentCount
            cur_t = records[sel_idx].totalCount

        rec_res = service.calculate_recovery(
            present=cur_p,
            total=cur_t,
            target_pct=target_pct,
            remaining_classes=remaining_classes_input,
        )

        status_box = ""
        if not rec_res["isPossible"]:
            status_box = '<div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:10px 12px; color:#991b1b; font-size:0.9rem; margin-top:8px;">❌ Target is mathematically impossible given current class totals.</div>'
        elif rec_res["classesNeeded"] == 0:
            status_box = f'<div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:10px 12px; color:#166534; font-size:0.9rem; margin-top:8px;">✓ Target already achieved! Safe buffer: You can safely miss up to <strong>{rec_res["bufferClasses"]} class(es)</strong> before dropping below {target_pct:.0f}%.</div>'
        else:
            if rec_res["isRecoverableWithinRemaining"]:
                status_box = f'<div style="background:#fffbeb; border:1px solid #fde68a; border-radius:6px; padding:10px 12px; color:#92400e; font-size:0.9rem; margin-top:8px;">⚠️ Consecutive classes needed: <strong>{rec_res["classesNeeded"]}</strong> (will bring attendance to {rec_res["resultingPercentage"]}%).</div>'
            else:
                status_box = f'<div style="background:#fef2f2; border:1px solid #fecaca; border-radius:6px; padding:10px 12px; color:#991b1b; font-size:0.9rem; margin-top:8px;">❌ {rec_res["remainingMessage"]}. Requires {rec_res["classesNeeded"]} classes, exceeding planned remaining ({remaining_classes_input}).</div>'

        render_html(
            f"""
            <div class="edu-card" style="background:#f8fafc; border-left: 4px solid #0f766e; height: 100%;">
                <h5 style="margin-top:0; color:#0f766e;">Mathematical Simulation Result</h5>
                <p style="font-size:0.9rem; color:#475569; margin: 4px 0 8px 0;">
                    Current Standing: <strong>{cur_p}/{cur_t} ({(cur_p/cur_t*100.0) if cur_t > 0 else 0:.1f}%)</strong> &nbsp;|&nbsp; Target: <strong>{target_pct:.1f}%</strong>
                </p>
                {status_box}
                <div style="font-size:0.8rem; color:#64748b; margin-top:8px;">
                    <em>Note: {rec_res['notice']}</em>
                </div>
            </div>
            """
        )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 6. DAILY TIMETABLE AUDIT LOG
    st.subheader("📅 Daily Timetable Records")
    daily = service.get_daily_attendance(st_id)
    if daily:
        st.caption("Detailed chronological class sessions. Unmarked slots ('-') are excluded from counts pursuant to data governance rules.")
        daily_table = [
            {
                "Date": d.date,
                "Time Slot": d.timeSlot or "N/A",
                "Course Code": d.courseId,
                "Component": d.component or "THEORY",
                "Status": d.status.value,
                "Source": d.source,
            }
            for d in daily
        ]
        st.dataframe(pd.DataFrame(daily_table), use_container_width=True, hide_index=True)
    else:
        st.info("No daily timetable entries recorded.")
