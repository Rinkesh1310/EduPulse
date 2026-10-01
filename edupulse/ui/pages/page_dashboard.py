import plotly.express as px
import streamlit as st

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
    if not student:
        service.seed_all_personas(reset=False)
        student = service.get_student_profile(st_id)

    sem = student.semester if student else 3
    signals_data = service.get_support_signals(st_id)
    att_summary = service.get_attendance_summary(st_id, sem)
    coverage = service.get_coverage(st_id)
    provenance = service.get_student_provenance(st_id)
    narrative = service.get_diagnostic_narrative(st_id)
    courses = service.list_courses(st_id, sem)
    courses_map = {c.id: c for c in courses}
    assessments = service.get_assessments(st_id)
    results = service.get_semester_results(st_id)
    policy = service.get_policy()

    # 1. TOP HEADER: EduPulse Student Identity & Academic Period
    render_page_header(
        title="EduPulse — Student Success Dashboard",
        subtitle="Holistic academic intelligence, attendance analytics, and proactive pathway support.",
        student=student,
        provenance=provenance,
        as_of_date=att_summary.get("asOfDate", "2026-09-30"),
        academic_status=f"Active Term • Coverage: {coverage.overall.value}",
    )

    # 2. HERO: Your Academic Snapshot
    support_sig = signals_data["overallSupportSignal"]
    render_html(
        f"""
        <div class="edu-card" style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-left: 5px solid {'#10b981' if support_sig.value=='Low' else ('#ef4444' if support_sig.value=='High' else '#f59e0b')};">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <span style="font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#64748b;">
                    Executive Intelligence Summary
                </span>
                <span class="{'badge-low' if support_sig.value=='Low' else ('badge-high' if support_sig.value=='High' else 'badge-moderate')}">
                    Support Status: {support_sig.value}
                </span>
            </div>
            <h3 style="margin: 8px 0 6px 0; font-size: 1.25rem; color: #0f172a;">
                Your Academic Snapshot
            </h3>
            <p style="font-size: 1.02rem; color: #1e293b; margin: 0 0 12px 0; font-weight: 500; line-height: 1.45;">
                {narrative['what_detected']}
            </p>
            <div style="font-size: 0.88rem; color: #475569; display: flex; gap: 16px; flex-wrap: wrap;">
                <span>🎯 Attendance: <strong>{att_summary['computedOverall'] or 'N/A'}%</strong></span>
                <span>📚 Evaluated Subjects: <strong>{signals_data['academicMeta'].get('evaluatedCount', 0)} of {len(courses)}</strong></span>
                <span>🌟 Co-Curricular: <strong>{signals_data['engagementSummary']['level']}</strong></span>
            </div>
        </div>
        """
    )

    # 3. PRIMARY METRICS (4 clean, consistent tiles)
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        computed_att = att_summary["computedOverall"]
        att_display = f"{computed_att:.1f}%" if computed_att is not None else "N/A"
        render_metric_card(
            title="Attendance Rate",
            value=att_display,
            subtext=f"{att_summary['totalPresent']}/{att_summary['totalClasses']} total sessions recorded",
            status_level=signals_data["attendanceSignal"],
        )
    with col_m2:
        acad_sig = signals_data["academicSignal"]
        render_metric_card(
            title="Academic Standing",
            value=acad_sig.value,
            subtext=f"Coverage: {signals_data['academicMeta'].get('coverage', 'N/A')}",
            status_level=acad_sig,
        )
    with col_m3:
        eng = signals_data["engagementSummary"]
        render_metric_card(
            title="Engagement Level",
            value=eng["level"],
            subtext=f"{eng['points']:.1f} pts across {eng['eventCount']} confirmed event(s)",
            status_level=None,
        )
    with col_m4:
        render_metric_card(
            title="Support Signal",
            value=support_sig.value,
            subtext=signals_data["overallDisplayText"],
            status_level=support_sig,
        )

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    # 4. ACADEMIC ATTENTION AREAS
    col_attn, col_diag = st.columns([1.5, 1])

    with col_attn:
        st.subheader("⚠️ Academic Attention Areas")
        # Identify subjects below benchmark (<50%) or components below 70%
        att_alerts = [
            r for r in att_summary["records"]
            if r.computed_percentage is not None
            and r.computed_percentage < policy.attendancePerCoursePct
            and r.totalCount >= policy.smallSampleThreshold
        ]

        by_course_ass = {}
        for a in assessments:
            by_course_ass.setdefault(a.courseId, []).append(a)

        acad_alerts = []
        for cid, a_list in by_course_ass.items():
            tot_obt = sum(x.obtainedMarks for x in a_list)
            tot_max = sum(x.totalMarks for x in a_list)
            pct = round((tot_obt / tot_max) * 100.0, 1) if tot_max > 0 else 0.0
            if pct < 50.0:
                c_obj = courses_map.get(cid)
                c_name = c_obj.shortName if c_obj else cid
                acad_alerts.append({"course": c_name, "pct": pct, "count": len(a_list)})

        if acad_alerts or att_alerts:
            if acad_alerts:
                for al in acad_alerts:
                    render_html(
                        f"""
                        <div class="edu-card" style="border-left: 4px solid #ef4444; padding: 12px 16px; margin-bottom: 8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="color:#991b1b; font-size:0.95rem;">Subject Performance Alert: {al['course']}</strong>
                                <span class="badge-high">{al['pct']}% Average</span>
                            </div>
                            <p style="margin:4px 0 0 0; font-size:0.85rem; color:#475569;">
                                Scored below institutional 50% benchmark across {al['count']} evaluation(s). Consider consulting faculty mentorship.
                            </p>
                        </div>
                        """
                    )
            if att_alerts:
                for ar in att_alerts:
                    render_html(
                        f"""
                        <div class="edu-card" style="border-left: 4px solid #f59e0b; padding: 12px 16px; margin-bottom: 8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="color:#92400e; font-size:0.95rem;">Attendance Alert: {ar.courseId} ({ar.component.value})</strong>
                                <span class="badge-moderate">{ar.computed_percentage}% Attendance</span>
                            </div>
                            <p style="margin:4px 0 0 0; font-size:0.85rem; color:#475569;">
                                Currently below the {policy.attendancePerCoursePct:.0f}% minimum threshold ({ar.presentCount}/{ar.totalCount} classes).
                            </p>
                        </div>
                        """
                    )
        else:
            render_html(
                """
                <div class="edu-card" style="border-left: 4px solid #10b981; padding: 14px 18px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="badge-low">All Baselines Healthy</span>
                    </div>
                    <p style="margin:6px 0 0 0; font-size:0.9rem; color:#334155;">
                        No academic attention areas detected. All evaluated subject marks and attendance components meet or exceed institutional standards.
                    </p>
                </div>
                """
            )

        # 5. PERFORMANCE & SGPA TREND
        st.subheader("📈 Performance Trajectory")
        if results:
            sgpa_data = [
                {
                    "Semester": f"Sem {r.semester}",
                    "SGPA": r.sgpa,
                    "Credits": getattr(r, "totalCreditsDeclared", 25.0) or 25.0,
                }
                for r in results
            ]
            fig_sgpa = px.line(
                sgpa_data,
                x="Semester",
                y="SGPA",
                markers=True,
                range_y=[5.0, 10.0],
                title="Historical Published SGPA Trajectory",
            )
            fig_sgpa.update_traces(line_color="#2563eb", marker=dict(size=8, color="#1e40af"))
            fig_sgpa.update_layout(height=220, margin=dict(l=20, r=20, t=35, b=20))
            st.plotly_chart(fig_sgpa, use_container_width=True)
        elif assessments:
            ass_chart = [
                {"Subject": courses_map[a.courseId].shortName if a.courseId in courses_map else a.courseId, "Marks (%)": a.percentage}
                for a in assessments
            ]
            fig_ass = px.bar(
                ass_chart,
                x="Subject",
                y="Marks (%)",
                range_y=[0, 100],
                title="Current Assessment Scores (%)",
                color="Marks (%)",
                color_continuous_scale="Blues",
            )
            fig_ass.add_hline(y=50, line_dash="dash", line_color="#ef4444", annotation_text="Benchmark (50%)")
            fig_ass.update_layout(height=220, margin=dict(l=20, r=20, t=35, b=20))
            st.plotly_chart(fig_ass, use_container_width=True)
        else:
            st.info("ℹ️ Performance trajectory graph activates upon first published SGPA or midterm score.")

    with col_diag:
        # 6. ATTENDANCE INTELLIGENCE
        st.subheader("📊 Attendance Intelligence")
        render_html(
            f"""
            <div class="edu-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; font-size:0.92rem; color:#0f172a;">Overall Sessions</span>
                    <span style="font-size:1.1rem; font-weight:700; color:#1e293b;">{att_summary['totalPresent']} / {att_summary['totalClasses']}</span>
                </div>
                <div style="background:#f1f5f9; border-radius:9999px; height:8px; width:100%; margin:10px 0; overflow:hidden;">
                    <div style="background:{'#10b981' if (computed_att or 0)>=75 else ('#ef4444' if (computed_att or 0)<70 else '#f59e0b')}; height:100%; width:{min(computed_att or 0, 100)}%;"></div>
                </div>
                <p style="font-size:0.82rem; color:#64748b; margin:0;">
                    Target: &ge; {policy.attendanceOverallPct:.0f}% institutional standard.
                </p>
                {f'<p style="font-size:0.8rem; color:#d97706; margin-top:6px;">⚠️ {att_summary["mismatchNote"]}</p>' if att_summary.get("mismatchNote") else ''}
            </div>
            """
        )

        # 7. RECOMMENDED NEXT ACTIONS
        st.subheader("💡 Recommended Next Actions")
        render_html(
            f"""
            <div class="edu-card" style="border-left: 4px solid #3b82f6;">
                <ul style="margin: 0; padding-left: 18px; line-height: 1.55; font-size: 0.88rem; color: #334155;">
                    {''.join(f'<li style="margin-bottom:6px;">{a}</li>' for a in narrative['what_to_do_next'][:3])}
                </ul>
            </div>
            """
        )

        # 8. SCHOLARSHIP PLANNING SNAPSHOT
        st.subheader("🎖️ Scholarship Readiness")
        render_html(
            """
            <div class="edu-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.9rem; font-weight:600;">Renewal Criterion Track</span>
                    <span class="badge-info">Active Plan</span>
                </div>
                <p style="font-size:0.85rem; color:#64748b; margin:8px 0 0 0;">
                    Track attendance buffer and target CGPA requirements in the dedicated <strong>Scholarship Readiness Planner</strong>.
                </p>
            </div>
            """
        )
