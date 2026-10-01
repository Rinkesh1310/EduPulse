
import numpy as np
import pandas as pd


def generate_synthetic_cohort(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Generates a synthetic, de-identified student cohort with realistic distributions
    and realistic missingness for unsupervised mentor exploration.
    
    Columns:
      - student_id: pseudonymous identifier ('STU-001', ...)
      - attendance_overall: overall attendance percentage (0-100)
      - lowest_component_att: lowest single course/lab attendance percentage
      - mean_marks: average assessment percentage (with missingness)
      - marks_trend: delta percentage points between assessments
      - sgpa_trend: change in SGPA from previous semester
      - engagement_points: points derived from co-curricular participation
      - data_coverage: Complete | Partial | Waiting
      - rule_based_signal: rule-based support signal (High, Moderate, Low, Needs more data)
    """
    rng = np.random.default_rng(seed)

    student_ids = [f"STU-{i+1:03d}" for i in range(n)]

    # 1. Attendance: Mixture distribution (majority healthy 75-92%, minority attention 45-72%)
    is_attention_cohort = rng.random(n) < 0.22
    healthy_att = rng.normal(loc=82.0, scale=6.0, size=n)
    low_att = rng.normal(loc=61.0, scale=8.0, size=n)
    attendance_overall = np.where(is_attention_cohort, low_att, healthy_att)
    attendance_overall = np.clip(attendance_overall, 35.0, 98.0)

    # Lowest component attendance: usually 5-15% lower than overall
    comp_drop = rng.exponential(scale=7.0, size=n)
    lowest_component_att = np.clip(attendance_overall - comp_drop, 25.0, attendance_overall)

    # 2. Marks: Realistic missingness (20% have no marks yet, 15% partial)
    marks_missingness_mask = rng.random(n) < 0.20
    raw_marks = rng.normal(loc=66.0, scale=14.0, size=n)
    raw_marks = np.clip(raw_marks, 30.0, 95.0)
    mean_marks = np.where(marks_missingness_mask, np.nan, raw_marks)

    # Marks trend: delta (-25 to +25) with missingness where marks are missing
    raw_marks_trend = rng.normal(loc=1.5, scale=8.0, size=n)
    marks_trend = np.where(np.isnan(mean_marks), np.nan, raw_marks_trend)

    # 3. SGPA Trend: -1.2 to +1.2
    sgpa_trend_missing = rng.random(n) < 0.25  # Sem 1 or transfer students without prior trend
    raw_sgpa_trend = rng.normal(loc=0.05, scale=0.45, size=n)
    sgpa_trend = np.where(sgpa_trend_missing, np.nan, np.clip(raw_sgpa_trend, -1.8, 1.8))

    # 4. Engagement Points: Exponential distribution (many 0-4, few highly active 10+)
    engagement_points = rng.exponential(scale=3.5, size=n)
    engagement_points = np.round(np.clip(engagement_points, 0.0, 22.0), 1)

    # 5. Coverage flags
    coverage_list = []
    for i in range(n):
        if np.isnan(mean_marks[i]) and np.isnan(sgpa_trend[i]):
            coverage_list.append("Waiting")
        elif np.isnan(mean_marks[i]) or np.isnan(sgpa_trend[i]):
            coverage_list.append("Partial")
        else:
            coverage_list.append("Complete")

    # 6. Apply standard rule-based signal engine for direct comparability
    signals = []
    for i in range(n):
        att = attendance_overall[i]
        lowest = lowest_component_att[i]
        marks = mean_marks[i]

        att_sev = 1  # Low
        if att < 75.0 or lowest < 70.0:
            att_sev = 3  # High
        elif att < 80.0:
            att_sev = 2  # Moderate

        acad_sev = 0  # Needs more data
        if not np.isnan(marks):
            if marks < 50.0:
                acad_sev = 3
            elif marks < 65.0:
                acad_sev = 2
            else:
                acad_sev = 1

        # Combine
        if acad_sev == 0:
            final_sev = att_sev
        else:
            final_sev = max(att_sev, acad_sev)
            if att_sev >= 2 and acad_sev >= 2:
                final_sev = min(3, final_sev + 1)

        sig_map = {1: "Low", 2: "Moderate", 3: "High"}
        signals.append(sig_map.get(final_sev, "Low"))

    df = pd.DataFrame({
        "student_id": student_ids,
        "attendance_overall": np.round(attendance_overall, 1),
        "lowest_component_att": np.round(lowest_component_att, 1),
        "mean_marks": np.round(mean_marks, 1),
        "marks_trend": np.round(marks_trend, 1),
        "sgpa_trend": np.round(sgpa_trend, 2),
        "engagement_points": engagement_points,
        "data_coverage": coverage_list,
        "rule_based_signal": signals,
    })

    return df
