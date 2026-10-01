import pandas as pd
import streamlit as st

from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import (
    apply_custom_theme,
    render_html,
    render_page_header,
)


def render_page(service: AcademicService):
    apply_custom_theme()
    st_id = st.session_state.get("current_student_id", "student_synth_strong")
    record = service.get_student_academic_record(st_id)
    student = record["student"]
    provenance = record["provenance"]
    academic_status = record["academicStatus"]
    courses = record["courses"]
    att_summary = record["attendanceSummary"]
    results = record["results"]
    eng_summary = record["engagementSummary"]
    as_of = att_summary.get("asOfDate", "2026-09-30")

    # 1. TOP HEADER
    render_page_header(
        title="Full Academic Record",
        subtitle="Comprehensive transcript records, component attendance, published results, and evaluation availability.",
        student=student,
        provenance=provenance,
        as_of_date=as_of,
        academic_status=academic_status,
    )

    # Academic Data Summary Bar
    render_html(
        f"""
        <div class="edu-card" style="margin-top: 10px; margin-bottom: 20px; border-left: 4px solid #3b82f6;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <span style="font-size:0.8rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; font-weight:700;">Academic Data Status</span>
                    <div style="font-size:1.02rem; font-weight:700; color:#1e293b; margin-top:2px;">{academic_status}</div>
                </div>
                <div>
                    <span style="font-size:0.8rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; font-weight:700;">Data Source</span>
                    <div style="font-size:0.95rem; font-weight:600; color:#475569; margin-top:2px;">
                        <span class="{'badge-low' if provenance=='Demo data' else ('badge-moderate' if 'Reference' in provenance else 'badge-info')}">{provenance}</span>
                    </div>
                </div>
                <div>
                    <span style="font-size:0.8rem; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; font-weight:700;">Overall Attendance</span>
                    <div style="font-size:1.05rem; font-weight:700; color:#0f766e; margin-top:2px;">
                        {att_summary['computedOverall'] or 'N/A'}% ({att_summary['totalPresent']}/{att_summary['totalClasses']} sessions)
                    </div>
                </div>
            </div>
        </div>
        """
    )

    tab_courses, tab_history, tab_assessments, tab_engagement = st.tabs(
        [
            "📚 Enrolled Courses & Attendance",
            "📜 Semester History & SGPA",
            "📝 Current Assessment Availability",
            "🌟 Engagement & Activity State",
        ]
    )

    # ------------------------------------------------------------------
    # TAB 1: Enrolled Courses & Attendance
    # ------------------------------------------------------------------
    with tab_courses:
        st.subheader("Current Semester Enrolled Subjects")
        st.caption(
            f"Official course catalogue for Semester {student.semester if student else 3} with component-level attendance records and thresholds:"
        )

        rows = []
        for c in courses:
            c_name = f"{c['code']} — {c['shortName']}"
            if c["components"]:
                for comp in c["components"]:
                    status_badge = "Healthy"
                    if comp["band"] == "Attention area":
                        status_badge = "Attention (<70%)"
                    elif comp["band"] == "Monitor":
                        status_badge = "Monitor"
                    elif comp["band"] == "Small sample":
                        status_badge = "Small Sample"

                    pct_str = f"{comp['percentage']:.1f}%" if comp["percentage"] is not None else "UNMARKED (-)"
                    rows.append({
                        "Subject Code & Name": c_name,
                        "Component": comp["component"],
                        "Present / Total": f"{comp['present']} / {comp['total']}",
                        "Attendance %": pct_str,
                        "Threshold Status": status_badge,
                        "Credits": f"{c['credits']:.1f}",
                        "Assessment Availability": "Available (Logged)" if c["hasAssessment"] else "Awaiting Assessment",
                    })
            else:
                rows.append({
                    "Subject Code & Name": c_name,
                    "Component": "COMBINED",
                    "Present / Total": "UNMARKED (-)",
                    "Attendance %": "UNMARKED (-)",
                    "Threshold Status": "Discovery Course (Unmarked)",
                    "Credits": f"{c['credits']:.1f}",
                    "Assessment Availability": "Awaiting Assessment",
                })

        if rows:
            df_courses = pd.DataFrame(rows)
            st.dataframe(df_courses, use_container_width=True, hide_index=True)

        if att_summary.get("mismatchNote"):
            st.warning(f"⚠️ **Portal Truncation Flag**: {att_summary['mismatchNote']}")

    # ------------------------------------------------------------------
    # TAB 2: Semester History & SGPA
    # ------------------------------------------------------------------
    with tab_history:
        st.subheader("Published Semester History & Credits")
        st.caption("Historical performance across completed examination terms:")

        if results:
            hist_rows = []
            for r in results:
                status_txt = "Complete" if r.creditsComplete else "Incomplete / Missing Term"
                hist_rows.append({
                    "Semester": f"Semester {r.semester}",
                    "Exam Term": r.monthYear or r.examDate or "N/A",
                    "SGPA": f"{r.sgpa:.2f}" if r.sgpa is not None else "N/A",
                    "Credits Earned": f"{getattr(r, 'creditsEarned', getattr(r, 'totalCreditsDeclared', 0.0)):.1f}" if getattr(r, "creditsEarned", getattr(r, "totalCreditsDeclared", None)) is not None else "N/A",
                    "Credits Total": f"{getattr(r, 'creditsTotal', getattr(r, 'totalCreditsDeclared', 0.0)):.1f}" if getattr(r, "creditsTotal", getattr(r, "totalCreditsDeclared", None)) is not None else "N/A",
                    "Credit Status": status_txt,
                    "Course Grades Available": len(getattr(r, "courses", [])) if getattr(r, "courses", None) else (len(getattr(r, "courseResults", [])) if getattr(r, "courseResults", None) else 0),
                })
            df_hist = pd.DataFrame(hist_rows)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)

            # Detailed course grades where supplied
            for r in results:
                grade_items = r.courses or r.courseResults
                if grade_items:
                    with st.expander(f"📋 Course-Level Published Grades — Semester {r.semester} ({r.monthYear or r.examDate or ''})"):
                        grade_rows = [
                            {
                                "Course": getattr(cr, "courseName", None) or getattr(cr, "courseCode", "N/A"),
                                "Grade": getattr(cr, "grade", "N/A"),
                                "Credits": getattr(cr, "credits", 0.0),
                                "Type": getattr(cr, "courseType", None) or "COURSE",
                            }
                            for cr in grade_items
                        ]
                        st.dataframe(pd.DataFrame(grade_rows), use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ **No published semester results on record** (e.g. newly enrolled Semester 1 student).")

    # ------------------------------------------------------------------
    # TAB 3: Current Assessment Availability
    # ------------------------------------------------------------------
    with tab_assessments:
        st.subheader("Current Term Assessment Inventory")
        st.caption("Active internal evaluations, midterms, and practicals recorded for the ongoing term:")

        all_assessments = []
        for c in courses:
            for a in c["assessments"]:
                all_assessments.append({
                    "Subject": f"{c['code']} ({c['shortName']})",
                    "Assessment Type": a["type"],
                    "Term": a["term"] or "N/A",
                    "Date": a["date"] or "N/A",
                    "Marks Obtained": a["obtained"],
                    "Total Marks": a["total"],
                    "Percentage": f"{a['percentage']:.1f}%",
                    "Status": "Evaluated",
                })

        if all_assessments:
            st.dataframe(pd.DataFrame(all_assessments), use_container_width=True, hide_index=True)
        else:
            st.info("⏳ **No assessments logged yet for the current term**.")

    # ------------------------------------------------------------------
    # TAB 4: Engagement Data State
    # ------------------------------------------------------------------
    with tab_engagement:
        st.subheader("Engagement & Activity Portfolio State")
        st.caption("Co-curricular participations, verified events, and current declaration status:")

        col_e1, col_e2, col_e3, col_e4 = st.columns(4)
        with col_e1:
            st.metric("Engagement Level", eng_summary["level"])
        with col_e2:
            st.metric("Engagement Points", f"{eng_summary['points']:.1f}")
        with col_e3:
            st.metric("Confirmed Events", str(eng_summary["eventCount"]))
        with col_e4:
            st.metric("Declaration Status", eng_summary["status"])

        render_html(
            """
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; margin-top:16px; font-size:0.88rem; color:#475569;">
                <strong>Governance & Independence Note:</strong> Co-curricular engagement metrics serve as an independent portfolio indicator.
                Pursuant to institutional academic fairness standards, high engagement never offsets or diminishes academic attendance requirements,
                nor does lack of engagement trigger punitive academic alerts.
            </div>
            """
        )
