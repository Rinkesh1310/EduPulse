# Machine Learning Methodology & Honesty Statement

**Document Version**: 1.0.0  
**Project**: EduPulse — Student Success & Scholarship Readiness Explorer  

---

## 1. Why EduPulse Rejects Pseudo-Supervised Classification

In educational data mining hackathons and prototypes, a common anti-pattern is:
1. Define a rule-based heuristic to assign student risk labels (`High`, `Moderate`, `Low`).
2. Train a supervised classifier (e.g. Random Forest, XGBoost, MLP) to predict those very labels.
3. Report high accuracy (e.g. 98%) as evidence of "Machine Learning for Student Risk".

### Why This is Scientifically Fraudulent & Circular:
- **Tautology**: The model is merely approximating the software engineer's deterministic rules, not discovering real-world educational failure dynamics.
- **Illusion of Predictiveness**: If the underlying rule is biased or unverified (e.g. penalizing students with legitimate medical leaves or missing odd-semester credits), the supervised model bakes in and codifies that bias while masking the explicit explainability of the rules.
- **Ground Truth Absence**: No ground-truth outcome label (e.g. end-of-degree graduation, course failure, university dropout, academic probation) exists in current midterm portal views.

Therefore, **EduPulse does NOT train any supervised classifier on synthetic or rule-derived labels**.

---

## 2. What Would Be Required for a Legitimate Supervised Predictor?

To build an academically valid and legally defensible predictive ML model in a production university setting, an institution would need:

1. **Checkpoint-Time Feature Availability**:
   - The training set must strictly consist of features known *at the specific decision checkpoint* (e.g. Week 6 of Semester 3).
   - Zero future data leakage (no semester-end total credits, no final exam marks, no future attendance records).
2. **True Longitudinal Later Outcomes**:
   - Explicit binary or continuous outcomes recorded *after* the checkpoint:
     - End-of-semester course failure ($\ge 1$ F grade).
     - Formal academic probation status.
     - Degree withdrawal / dropout after 12 months.
3. **Time-Based Train/Validation/Test Splits**:
   - Random k-fold cross-validation suffers from temporal leakage.
   - Models must be trained on past academic cohorts (e.g. 2021–2023) and validated on subsequent out-of-time cohorts (e.g. 2024–2025).
4. **Probability Calibration**:
   - Raw classifier probabilities must be calibrated using Platt scaling or Isotonic regression (evaluated via Brier score and reliability curves).
   - High support interventions must not be triggered by poorly calibrated risk scores.
5. **Subgroup Fairness & Disparate Impact Auditing**:
   - Auditing error rates (False Positive Rate, False Negative Rate) across student demographics (admission categories, domicile, socio-economic cohorts) to prevent systemic bias.
6. **The Rules Baseline to Beat**:
   - Any machine learning model must statistically outperform a simple, explainable baseline:
     $$\text{Baseline: } \text{Flag if } \text{Overall Attendance} < 75\% \text{ OR } \text{Assessments} < 50\%$$
   - If complex models provide negligible gain over transparent heuristics, the simpler explainable rule must be chosen.

---

## 3. Legitimate Role of Unsupervised Pattern Analysis

In the absence of historical outcome labels, machine learning serves an **exploratory and descriptive role**:
- **K-Means Clustering** with silhouette optimization identifies emergent behavior archetypes (e.g. high attendance with exam anxiety; strong lab engagement with theory gaps).
- **Isolation Forest** detects multidimensional anomalies and edge cases (e.g. 98% attendance with 0% submissions, or top marks with unrecorded attendance).
- **Privacy Preservation**: Small subgroups ($< 5$ students) are systematically suppressed to prevent re-identification.
