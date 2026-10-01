import plotly.express as px
import streamlit as st

from edupulse.ml.cohort_generator import generate_synthetic_cohort
from edupulse.ml.unsupervised import run_unsupervised_cohort_analysis
from edupulse.services.academic_service import AcademicService
from edupulse.ui.components.theme import (
    apply_custom_theme,
    render_html,
    render_metric_card,
    render_page_header,
)


@st.cache_data
def get_analyzed_cohort():
    df = generate_synthetic_cohort(n=300, seed=42)
    return run_unsupervised_cohort_analysis(df, min_k=3, max_k=6)


def render_page(service: AcademicService):
    apply_custom_theme()
    st_id = st.session_state.get("current_student_id", "student_synth_strong")
    student = service.get_student_profile(st_id)
    provenance = service.get_student_provenance(st_id)

    # 1. TOP HEADER
    render_page_header(
        title="Mentor Cohort Explorer",
        subtitle="Unsupervised multi-dimensional pattern analysis and exploratory cohort archetypes.",
        student=student,
        provenance=provenance,
        as_of_date="2026-09-30",
        academic_status="Advisory / Mentor Intelligence Mode",
    )

    # MANDATORY ML HONESTY BANNER
    st.info(
        "🔬 **Machine Learning Methodology & Privacy Notice**: Synthetic data · exploratory patterns · not a validated predictor. "
        "Unsupervised clustering identifies emergent behavior groups without circular pseudo-labels. "
        "Any pattern group with fewer than 5 members is automatically suppressed under k-anonymity rules. "
        "[Read ML Honesty Statement](docs/ML_HONESTY.md)"
    )

    analysis = get_analyzed_cohort()
    df_analyzed = analysis["analyzedData"]

    # 2. TOP METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card(
            title="Cohort Size",
            value=f"{len(df_analyzed)} students",
            subtext="De-identified synthetic cohort",
            status_level=None,
        )
    with m2:
        render_metric_card(
            title="Pattern Clusters",
            value=f"k = {analysis['bestK']}",
            subtext=f"Optimal silhouette: {analysis['bestSilhouette']}",
            status_level="Low",
        )
    with m3:
        render_metric_card(
            title="Unusual Cases",
            value=f"{analysis['anomalyCount']}",
            subtext="IsolationForest (5% contamination)",
            status_level="Moderate",
        )
    with m4:
        render_metric_card(
            title="Privacy Guard",
            value="< 5 Suppressed",
            subtext="k-anonymity privacy guarantee",
            status_level="Low",
        )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 3. CLUSTER VISUALIZATION & ARCHETYPES
    col_chart, col_groups = st.columns([3, 2])

    with col_chart:
        st.subheader("Multidimensional Pattern Space")
        fig = px.scatter(
            df_analyzed,
            x="attendance_overall",
            y="mean_marks",
            color="cluster_id",
            symbol="is_anomaly",
            hover_data=["student_id", "lowest_component_att", "engagement_points", "rule_based_signal"],
            labels={
                "attendance_overall": "Overall Attendance (%)",
                "mean_marks": "Average Assessment Marks (%)",
                "cluster_id": "Cluster Group",
            },
            title="Attendance vs Assessment Performance (Exploratory Clusters)",
        )
        fig.add_hline(y=50, line_dash="dot", line_color="#ef4444", annotation_text="Benchmark (50%)")
        fig.add_vline(x=75, line_dash="dot", line_color="#f59e0b", annotation_text="Attendance Minimum (75%)")
        fig.update_layout(height=420, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col_groups:
        st.subheader("Identified Cluster Archetypes")
        for p in analysis["clusterProfiles"]:
            if p["isSuppressed"]:
                st.warning(f"🔒 **{p['label']}** ({p['memberCount']} students) — {p['description']}")
            else:
                render_html(
                    f"""
                    <div class="edu-card" style="margin-bottom: 10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#0f172a; font-size:0.95rem;">Group {p['clusterId'] + 1}: {p['label']}</strong>
                            <span class="badge-info" style="font-size:0.75rem;">{p['memberCount']} students</span>
                        </div>
                        <p style="margin: 4px 0 6px 0; font-size: 0.88rem; color: #334155;">{p['description']}</p>
                        <div style="font-size: 0.8rem; color: #64748b;">
                            Avg Attendance: <strong>{p['meanAttendance']}%</strong> | 
                            Avg Marks: <strong>{p['meanMarks']}</strong> | 
                            Avg Engagement: <strong>{p['meanEngagement']} pts</strong>
                        </div>
                    </div>
                    """
                )

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 4. FILTERABLE COHORT TABLE
    st.subheader("Filterable Cohort Records")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sel_cluster = st.selectbox(
            "Filter by Cluster Group",
            options=["All Clusters"] + [f"Group {i+1}" for i in range(analysis["bestK"])],
            key="cohort_cluster_filter",
        )
    with col_f2:
        only_anomalies = st.checkbox("Show only unusual pattern cases (IsolationForest anomalies)", value=False, key="chk_only_anom")

    display_df = df_analyzed.copy()
    if sel_cluster != "All Clusters":
        c_idx = int(sel_cluster.split()[1]) - 1
        display_df = display_df[display_df["cluster_id"] == c_idx]
    if only_anomalies:
        display_df = display_df[display_df["is_anomaly"] == -1]

    cols_to_show = [
        "student_id",
        "attendance_overall",
        "lowest_component_att",
        "mean_marks",
        "engagement_points",
        "cluster_id",
        "rule_based_signal",
    ]
    renamed = {
        "student_id": "De-Identified ID",
        "attendance_overall": "Overall Attendance (%)",
        "lowest_component_att": "Lowest Component (%)",
        "mean_marks": "Average Marks (%)",
        "engagement_points": "Engagement (pts)",
        "cluster_id": "Cluster",
        "rule_based_signal": "Rule Signal",
    }
    st.dataframe(
        display_df[cols_to_show].rename(columns=renamed),
        use_container_width=True,
        hide_index=True,
    )
