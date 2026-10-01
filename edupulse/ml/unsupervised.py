from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.impute import MissingIndicator, SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def run_unsupervised_cohort_analysis(
    df: pd.DataFrame,
    min_k: int = 3,
    max_k: int = 6,
    random_state: int = 42,
    suppression_threshold: int = 5,
) -> dict[str, Any]:
    """Runs unsupervised clustering and anomaly detection on cohort data.
    
    Adheres strictly to Master Spec Section 8:
      - Uses median imputation WITH missing-indicator features (never imputes 0 as 'no participation').
      - Selects KMeans k by silhouette score across k in [3..6].
      - Runs IsolationForest for anomalous or unusual combinations.
      - Generates human-readable cluster descriptions.
      - Enforces privacy suppression: any cluster with < suppression_threshold members is suppressed.
    """
    feature_cols = [
        "attendance_overall",
        "lowest_component_att",
        "mean_marks",
        "marks_trend",
        "sgpa_trend",
        "engagement_points",
    ]

    X_raw = df[feature_cols].copy()

    # 1. Missing indicators
    indicator = MissingIndicator()
    missing_flags = indicator.fit_transform(X_raw)

    # 2. Median imputation for numerical features
    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X_raw)

    # Combine imputed features and missing indicators
    if missing_flags.shape[1] > 0:
        X_combined = np.hstack([X_imputed, missing_flags])
    else:
        X_combined = X_imputed

    # 3. Standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_combined)

    # 4. KMeans Silhouette Tuning (k in 3..6)
    best_k = min_k
    best_score = -1.0
    silhouette_scores = {}

    for k in range(min_k, max_k + 1):
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X_scaled)
        score = float(silhouette_score(X_scaled, labels))
        silhouette_scores[k] = round(score, 3)
        if score > best_score:
            best_score = score
            best_k = k

    # Fit best KMeans
    kmeans_model = KMeans(n_clusters=best_k, random_state=random_state, n_init=10)
    cluster_labels = kmeans_model.fit_predict(X_scaled)

    # 5. Isolation Forest for unusual combinations (contamination = 5%)
    iso = IsolationForest(contamination=0.05, random_state=random_state)
    anomaly_preds = iso.fit_predict(X_scaled)  # -1 is anomaly, 1 is normal
    is_anomaly = anomaly_preds == -1

    # Attach results to dataframe
    df_analyzed = df.copy()
    df_analyzed["cluster_id"] = cluster_labels
    df_analyzed["is_anomaly"] = is_anomaly

    # 6. Cluster Profiling & Privacy Suppression (< 5 members)
    cluster_profiles = []
    for c_id in range(best_k):
        sub_df = df_analyzed[df_analyzed["cluster_id"] == c_id]
        member_count = len(sub_df)

        if member_count < suppression_threshold:
            cluster_profiles.append({
                "clusterId": c_id,
                "label": f"Pattern Group {c_id + 1} (Suppressed)",
                "memberCount": member_count,
                "isSuppressed": True,
                "description": f"Group suppressed (< {suppression_threshold} members) to preserve student privacy.",
                "meanAttendance": None,
                "meanMarks": None,
                "meanEngagement": None,
            })
            continue

        mean_att = float(sub_df["attendance_overall"].mean())
        mean_marks = float(sub_df["mean_marks"].dropna().mean()) if sub_df["mean_marks"].count() > 0 else None
        mean_eng = float(sub_df["engagement_points"].mean())

        # Generate human-readable profile
        if mean_att >= 80.0 and (mean_marks is None or mean_marks >= 65.0):
            desc = "Strong overall attendance with high assessment scores and healthy trajectory."
            label_text = "Strong Engagement & Consistent Academics"
        elif mean_att < 72.0:
            desc = "Attendance attention area with component risks; benefit from attendance recovery."
            label_text = "Attendance Review & Intervention Needed"
        elif mean_marks is not None and mean_marks < 55.0:
            desc = "Steady attendance but assessment performance indicates subject mastery gaps."
            label_text = "Academic & Tutoring Support Focus"
        elif sub_df["mean_marks"].isna().sum() / member_count > 0.5:
            desc = "Early semester or missing assessment entries; awaiting first midterm results."
            label_text = "Early Data / Pre-Assessment Cohort"
        else:
            desc = "Balanced profile across attendance and coursework with moderate engagement."
            label_text = "Moderate & Steady Trajectory"

        cluster_profiles.append({
            "clusterId": c_id,
            "label": label_text,
            "memberCount": member_count,
            "isSuppressed": False,
            "description": desc,
            "meanAttendance": round(mean_att, 1),
            "meanMarks": round(mean_marks, 1) if mean_marks is not None else "Awaiting data",
            "meanEngagement": round(mean_eng, 1),
        })

    return {
        "bestK": best_k,
        "silhouetteScores": silhouette_scores,
        "bestSilhouette": round(best_score, 3),
        "clusterProfiles": cluster_profiles,
        "anomalyCount": int(is_anomaly.sum()),
        "analyzedData": df_analyzed,
    }
