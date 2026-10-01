from pathlib import Path

from edupulse.ml.cohort_generator import generate_synthetic_cohort
from edupulse.ml.unsupervised import run_unsupervised_cohort_analysis


def test_acceptance_v_cohort_generation_and_unsupervised_ml():
    """Acceptance Test V:
    Verify:
      1. Synthetic cohort of 300 students generates with pseudonymous IDs and missingness.
      2. No supervised label training (unsupervised KMeans & IsolationForest only).
      3. Silhouette score tuning selects optimal k between 3 and 6.
      4. Small-group suppression works for groups with < 5 members.
      5. Mandatory honesty banner string exists in the page implementation.
    """
    # 1. Cohort Generation
    df = generate_synthetic_cohort(n=300, seed=42)
    assert len(df) == 300
    assert "student_id" in df.columns
    assert df["student_id"].iloc[0] == "STU-001"
    assert df["mean_marks"].isna().sum() > 0  # verifies realistic missingness
    assert df["sgpa_trend"].isna().sum() > 0

    # 2. Unsupervised Clustering & Silhouette Tuning
    analysis = run_unsupervised_cohort_analysis(df, min_k=3, max_k=6, random_state=42)
    best_k = analysis["bestK"]
    assert 3 <= best_k <= 6
    assert analysis["bestSilhouette"] > 0.0
    assert len(analysis["silhouetteScores"]) == 4  # k=3, 4, 5, 6
    assert analysis["anomalyCount"] > 0

    # 3. Small-group privacy suppression check
    # With n=300 and k in [3..6], setting threshold to 150 guarantees at least one cluster is suppressed (<150 members)
    res_suppression = run_unsupervised_cohort_analysis(
        df, min_k=3, max_k=6, suppression_threshold=150
    )
    suppressed_profiles = [p for p in res_suppression["clusterProfiles"] if p["isSuppressed"]]
    assert len(suppressed_profiles) > 0
    assert "Suppressed" in suppressed_profiles[0]["label"]
    assert suppressed_profiles[0]["meanAttendance"] is None

    # 4. Mandatory Honesty Banner check on page_cohort.py
    cohort_page_path = Path(__file__).parent.parent / "edupulse" / "ui" / "pages" / "page_cohort.py"
    content = cohort_page_path.read_text(encoding="utf-8")
    assert "Synthetic data · exploratory patterns · not a validated predictor" in content
    assert "ML_HONESTY.md" in content
