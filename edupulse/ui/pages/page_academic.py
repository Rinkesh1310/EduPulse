from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from edupulse.core.academic import (
    calculate_assessment_trend,
    calculate_sgpa_trend,
    calculate_subject_marks_percentage,
    classify_academic_band,
)
from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import (
    apply_custom_theme,
    render_page_header,
    render_support_signal_card,
)


def render_page(service: AcademicService):
    apply_custom_theme()
    st_id = st.session_state.get("current_student_id", "student_synth_strong")
    student = service.get_student_profile(st_id)
    sem = student.semester if student else 3
    courses = service.list_courses(st_id, sem)
    courses_map = {c.id: c for c in courses}
    assessments = service.get_assessments(st_id)
    results = service.get_semester_results(st_id)
    provenance = service.get_student_provenance(st_id)

    # 1. TOP HEADER
    render_page_header(
        title="Academic Performance",
        subtitle="Evaluation analytics, runtime marks entry, and multi-semester SGPA progression.",
        student=student,
        provenance=provenance,
        as_of_date="2026-09-30",
        academic_status="Term Evaluation In Progress",
    )

    tab_eval, tab_history, tab_cgpa = st.tabs(
        ["Current Assessments & Entry", "Published Results & SGPA", "CGPA What-If Planner"]
    )

    # =============================================================
    # TAB 1: Current Assessments & Interactive Matrix
    # =============================================================
    with tab_eval:
        st.subheader("Current Semester Assessments")
        st.caption(
            "Subjects automatically populate from your enrolled academic record. "
            "Enter current marks, then click **Analyze Academic Health** to immediately recompute signals."
        )

        existing_by_course = {}
        for a in assessments:
            existing_by_course.setdefault(a.courseId, []).append(a)

        # Interactive Subject Assessment Matrix
        st.markdown("#### 📝 Runtime Assessment Marks Matrix")
        st.caption("Adjust scores and toggle availability. Changes immediately recalculate your academic standing upon clicking Analyze.")

        if courses:
            input_states = {}
            for c in courses:
                c_ass = existing_by_course.get(c.id, [])
                default_avail = len(c_ass) > 0
                first_ass = c_ass[0] if c_ass else None
                default_obtained = float(first_ass.obtainedMarks) if first_ass else 15.0
                default_total = float(first_ass.totalMarks) if first_ass else 20.0

                col_sub, col_avail, col_obt, col_tot = st.columns([2, 1.2, 1.2, 1.2])
                with col_sub:
                    st.markdown(f"**{c.shortName}** <span style='font-size:0.82rem; color:#64748b;'>({c.code})</span>", unsafe_allow_html=True)
                    if c.fullName and c.fullName != c.shortName:
                        st.caption(c.fullName)
                with col_avail:
                    avail = st.checkbox(
                        "Available",
                        value=default_avail,
                        key=f"mat_avail_{c.id}",
                        help=f"Toggle whether an assessment has been returned for {c.shortName}",
                    )
                with col_obt:
                    obt = st.number_input(
                        f"Obtained ({c.shortName})",
                        min_value=0.0,
                        max_value=100.0,
                        value=default_obtained,
                        step=0.5,
                        disabled=not avail,
                        key=f"mat_obt_{c.id}",
                        label_visibility="collapsed",
                    )
                with col_tot:
                    tot = st.number_input(
                        f"Max ({c.shortName})",
                        min_value=1.0,
                        max_value=100.0,
                        value=default_total,
                        step=1.0,
                        disabled=not avail,
                        key=f"mat_tot_{c.id}",
                        label_visibility="collapsed",
                    )

                input_states[c.id] = {
                    "course": c,
                    "available": avail,
                    "obtained": obt,
                    "total": tot,
                }

            col_btn1, col_btn2 = st.columns([2, 3])
            with col_btn1:
                analyze_clicked = st.button(
                    "🚀 Analyze Academic Health",
                    type="primary",
                    key="btn_analyze_matrix",
                    use_container_width=True,
                )

            if analyze_clicked:
                updated_count = 0
                for cid, state in input_states.items():
                    if state["available"]:
                        if state["obtained"] > state["total"]:
                            st.error(f"Error in {state['course'].shortName}: Obtained marks ({state['obtained']}) cannot exceed total ({state['total']}).")
                            st.stop()
                        service.save_or_update_course_assessment(
                            student_id=st_id,
                            course_id=cid,
                            ass_type="Midterm",
                            obtained_marks=state["obtained"],
                            total_marks=state["total"],
                            date="2026-09-20",
                            term="T1",
                        )
                        updated_count += 1
                    else:
                        for existing_a in existing_by_course.get(cid, []):
                            service.delete_assessment(existing_a.id)

                st.success(f"✓ Recomputed academic analytics for {updated_count} active course assessments!")
                st.rerun()
        else:
            st.info("No enrolled courses registered for the current semester.")

        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        # Signal Impact Cards
        assessments = service.get_assessments(st_id)
        signals = service.get_support_signals(st_id)

        col_sig1, col_sig2 = st.columns([1, 1.5])
        with col_sig1:
            render_support_signal_card(
                signals["overallSupportSignal"],
                f"Overall Signal: {signals['overallSupportSignal'].value}",
                signals["reasons"],
            )
        with col_sig2:
            st.markdown(
                f"""
                <div class="edu-card" style="height: 100%;">
                    <h5 style="margin-top:0; color:#1e3a8a;">Academic Diagnostics Summary</h5>
                    <p style="margin:4px 0 6px 0; font-size:0.92rem;">Academic Signal: <strong>{signals['academicSignal'].value}</strong></p>
                    <p style="font-size:0.85rem; color:#475569; margin:0 0 8px 0;">
                        Coverage: <strong>{signals['academicMeta'].get('coverage', 'N/A')}</strong> &nbsp;|&nbsp; 
                        Subjects Below Benchmark (50%): <strong>{signals['academicMeta'].get('belowCount', 0)}</strong>
                    </p>
                    <div style="font-size:0.85rem; color:#334155;">
                        <strong>Audit Explanations:</strong>
                        <ul style="margin:4px 0 0 0; padding-left:18px;">
                            {''.join(f'<li>{r.indicator}: {r.value}</li>' for r in signals['academicReasons'][:3]) or '<li>No academic alerts detected.</li>'}
                        </ul>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

        # Interactive Performance Chart
        if assessments:
            st.markdown("### 📊 Subject Performance Chart")
            by_course = {}
            for a in assessments:
                by_course.setdefault(a.courseId, []).append(a)

            chart_data = []
            for c_id, a_list in by_course.items():
                c_name = courses_map[c_id].shortName if c_id in courses_map else c_id
                pct = calculate_subject_marks_percentage(a_list)
                band = classify_academic_band(pct)
                trend_dir, delta, is_early = calculate_assessment_trend(a_list)
                early_flag = " (Early)" if is_early else ""

                chart_data.append({
                    "Subject": c_name,
                    "Percentage": pct,
                    "Count": f"{len(a_list)} assessment(s)",
                    "Band": band.value if band else "N/A",
                    "Trend": f"{trend_dir.value}{early_flag}",
                })

            fig = px.bar(
                chart_data,
                x="Subject",
                y="Percentage",
                color="Band",
                color_discrete_map={
                    "Strong": "#10b981",
                    "Monitor": "#f59e0b",
                    "Attention area": "#ef4444",
                },
                range_y=[0, 100],
                title="Marks Percentage by Subject (Aggregated: sum(obtained) / sum(total))",
            )
            fig.add_hline(y=50, line_dash="dash", line_color="#ef4444", annotation_text="Benchmark (50%)")
            fig.add_hline(y=65, line_dash="dash", line_color="#10b981", annotation_text="Strong Standard (65%)")
            fig.update_layout(height=280, margin=dict(l=20, r=20, t=35, b=20))
            st.plotly_chart(fig, use_container_width=True)

            # Saved Assessments list with Delete
            st.markdown("### 📋 Saved Assessment Items")
            for a in assessments:
                c_name = courses_map[a.courseId].shortName if a.courseId in courses_map else a.courseId
                col_i1, col_i2, col_i3, col_i4 = st.columns([3, 2, 2, 1])
                with col_i1:
                    st.write(f"**{c_name}** — {a.type} ({a.term or ''})")
                with col_i2:
                    st.write(f"Score: **{a.obtainedMarks}/{a.totalMarks}** ({a.percentage:.1f}%)")
                with col_i3:
                    st.caption(f"Date: {a.date}")
                with col_i4:
                    if st.button("Delete", key=f"del_{a.id}"):
                        service.delete_assessment(a.id)
                        st.rerun()
        else:
            st.info("ℹ️ **Marks analysis waiting for first assessment**. No current assessments logged yet.")

        # Additional Assessment Log Form (with robust course validation)
        with st.expander("➕ Log Custom Assessment (Quiz, Practical, Assignment)"):
            with st.form("add_custom_assessment_form", clear_on_submit=True):
                col_f1, col_f2 = st.columns(2)
                course_options = [c.id for c in courses]
                with col_f1:
                    if course_options:
                        selected_course_id = st.selectbox(
                            "Subject / Course",
                            options=course_options,
                            format_func=lambda cid: f"{courses_map[cid].code} — {courses_map[cid].shortName}" if cid in courses_map else cid,
                            key="ass_custom_course_select",
                        )
                    else:
                        st.warning("No enrolled courses available to add an assessment.")
                        selected_course_id = None

                    ass_type = st.selectbox(
                        "Assessment Type",
                        ["Quiz", "Internal Exam", "Lab Assessment", "Assignment", "Project"],
                        key="ass_custom_type_select",
                    )
                    ass_term = st.text_input("Term / Unit (Optional)", value="T2", key="ass_custom_term_input")
                with col_f2:
                    ass_date = st.date_input("Date", value=datetime.now(), key="ass_custom_date_input")
                    obtained_marks = st.number_input("Obtained Marks", min_value=0.0, max_value=100.0, value=18.0, step=0.5, key="ass_custom_obtained_input")
                    total_marks = st.number_input("Maximum Marks", min_value=1.0, max_value=100.0, value=20.0, step=1.0, key="ass_custom_total_input")

                submit_btn = st.form_submit_button("Save Assessment Record", type="primary")
                if submit_btn:
                    if not selected_course_id:
                        st.error("Please select a valid course before saving.")
                    elif obtained_marks > total_marks:
                        st.error(f"Validation Error: Obtained marks ({obtained_marks}) cannot exceed total ({total_marks}).")
                    else:
                        service.add_assessment(
                            student_id=st_id,
                            course_id=selected_course_id,
                            ass_type=ass_type,
                            date=str(ass_date),
                            obtained_marks=obtained_marks,
                            total_marks=total_marks,
                            term=ass_term,
                        )
                        st.success("Assessment saved successfully!")
                        st.rerun()

    # =============================================================
    # TAB 2: Published Results & SGPA History
    # =============================================================
    with tab_history:
        st.subheader("Published Semester History")
        if results:
            trend_dir, sgpa_delta = calculate_sgpa_trend(results)
            delta_str = f" ({'+' if sgpa_delta and sgpa_delta > 0 else ''}{sgpa_delta:.2f})" if sgpa_delta else ""
            st.write(f"Historical Semesters Recorded: **{len(results)}** | Trend: **{trend_dir.value}**{delta_str}")

            for r in results:
                st.markdown(
                    f"""
                    <div class="edu-card">
                        <h4>Semester {r.semester} ({r.monthYear}) — SGPA: {r.sgpa:.2f}</h4>
                        <p style="font-size: 0.85rem; color: #64748b;">
                            Credits Complete: <strong>{r.creditsComplete}</strong> | Declared Credits: <strong>{r.totalCreditsDeclared or 'Unconfirmed'}</strong>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if r.courses:
                    course_data = [
                        {
                            "Course Name": c.courseName,
                            "Type": c.courseType,
                            "Credits": c.credits,
                            "Grade": c.grade,
                        }
                        for c in r.courses
                    ]
                    st.dataframe(pd.DataFrame(course_data), use_container_width=True, hide_index=True)

            if student and student.semester > 1:
                known_sems = [r.semester for r in results]
                for s in range(1, student.semester):
                    if s not in known_sems:
                        st.warning(f"ℹ️ Semester {s} not in supplied data. Never fabricated or guessed.")
        else:
            st.info("No prior published semester results recorded.")

    # =============================================================
    # TAB 3: CGPA What-If Planner
    # =============================================================
    with tab_cgpa:
        st.subheader("🎯 Target CGPA What-If Planner")
        st.write("Plan the exact SGPA needed in future credits to achieve your target cumulative grade point average.")

        assume_equal = st.checkbox("Assume equal credits if semester credits are incomplete", value=False, key="chk_assume_equal")
        target_g = st.slider("Target CGPA", min_value=6.0, max_value=9.5, value=8.0, step=0.05, key="slider_target_cgpa")
        future_c = st.number_input("Future Planned Credits", min_value=1.0, max_value=60.0, value=24.0, step=1.0, key="num_future_credits")

        plan_res = service.calculate_cgpa_plan(st_id, target_cgpa=target_g, future_credits=future_c, assume_equal_credits=assume_equal)

        if plan_res["isBlocked"]:
            st.error(f"❌ {plan_res['cgpaInfo']['message']}")
        else:
            plan = plan_res["futurePlan"]
            cgpa_info = plan_res["cgpaInfo"]
            st.markdown(
                f"""
                <div class="edu-card">
                    <h4>Current CGPA: {cgpa_info['cgpa']:.2f}</h4>
                    <p style="font-size:0.9rem; color:#64748b;">{cgpa_info.get('label', '')}</p>
                    <hr/>
                    <p>Target CGPA: <strong>{target_g:.2f}</strong> over next <strong>{future_c:.0f} credits</strong></p>
                """,
                unsafe_allow_html=True,
            )
            if plan["status"] == "already_secured":
                st.success(f"✓ {plan['message']}")
            elif plan["status"] == "reachable":
                st.warning(f"Required Next-Term SGPA: **{plan['requiredSgpa']:.2f}**.")
                st.write(plan["message"])
            else:
                st.error(f"⚠️ {plan['message']}")

            st.caption(f"Maximum achievable CGPA in this term: **{plan['maxAchievable']:.2f}** (at 10.0 scale max).")
            st.markdown("</div>", unsafe_allow_html=True)
