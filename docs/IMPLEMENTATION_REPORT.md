# EduPulse Implementation Report

**Project Title**: EduPulse — Student Success & Scholarship Readiness Explorer  
**Challenge**: Challenge 3 — Student Success Risk Explorer  
**Lead Engineer / Implementation Agent**: Antigravity  
**Status**: In Progress  

---

## Executive Summary
This document tracks the phased construction, verification gates, test outcomes, screenshots, and compliance guarantees for EduPulse.

---

## Phase 0: Inspection, Environment & Scaffolding
- **Status**: Completed (Gate passed: App boots, tests run)
- **Work Completed**:
  - Inspected repository workspace, existing reference screenshots, and challenge brief.
  - Documented findings in [REPO_INSPECTION.md](file:///d:/EduPulse/docs/REPO_INSPECTION.md).
  - Initialized [DECISIONS.md](file:///d:/EduPulse/docs/DECISIONS.md).
  - Initialized virtual environment `.venv` with Python 3.14.
  - Installed dependencies: `streamlit`, `pandas`, `numpy`, `scikit-learn`, `plotly`, `pydantic`, `sqlalchemy`, `pytest`, `hypothesis`, `ruff`, `playwright`.
  - Installed Playwright Chromium browser binaries for automated screenshots.
  - Created `.gitignore` enforcing non-negotiable security boundaries (no screenshots committed, no local forbidden strings).
  - Structured config files: `policy.json`, `engagement_model.json`, `signal_rules.json`, `scholarship/mysy_2026_27.json`, `scholarship/demo_merit_fictional.json`, `events_demo.json`.
  - Defined domain models and enums with Pydantic v2.
  - Configured `pyproject.toml` with pytest pythonpath and ruff.
- **Verification Gate**:
  - `pytest -v`: 4 passed/skipped (Domain model creation, Assessment validation, Fictional identity, AppTest boot).
  - Streamlit AppTest booted and executed cleanly.

---

## Phase 1: Core Calculations & Formula Tests
- **Status**: Completed (Gate passed: All formula tests green)
- **Work Completed**:
  - Implemented pure arithmetic attendance engine in [edupulse/core/attendance.py](file:///d:/EduPulse/edupulse/core/attendance.py):
    - Exact ratio with 1-decimal rounding (8/9 -> 88.9%, not 88%).
    - Attendance headline mismatch note (|portalReported - computed| > 1 pt) without overwriting either.
    - Attendance recovery formula using `Fraction` and integer ceil arithmetic.
    - Buffer calculation when current attendance >= target.
    - Remaining classes feasibility check and max allowable misses within planning horizon.
    - Component and overall attendance bands with small-sample guard (<8 classes labeled "Early data").
    - Component-to-course combined aggregation.
    - Daily attendance status handling: P and A counted; NT and UNMARKED ('-') strictly excluded.
  - Implemented academic performance engine in [edupulse/core/academic.py](file:///d:/EduPulse/edupulse/core/academic.py):
    - Subject percentage = sum(obtained)/sum(total), strictly avoiding averages of percentages.
    - Academic bands (Attention <50, Monitor 50-<65, Strong >=65).
    - Assessment trend with n=2 "early indication" flag.
    - SGPA trend (+-0.3 threshold; "Not enough history" for <2 semesters).
    - Credit-weighted CGPA with strict missing-credits block unless explicitly assumed equal.
    - Future required SGPA planner, max achievable CGPA, and already-secured detection.
  - Implemented engagement scoring engine in [edupulse/core/engagement.py](file:///d:/EduPulse/edupulse/core/engagement.py):
    - Type weights, duration factors (full-day 1.0, hours/4 with floor 0.25).
    - Levels: Getting started, Active, Highly active.
    - Overlap detection with official attendance ("Counted in official attendance; adds to engagement only").
    - Verified engagement never increases support signal.
  - Enforced architectural import boundary: `edupulse/core/attendance.py` does not import `engagement`.
- **Verification Gate**:
  - `pytest -v`: 22 passed, 1 skipped.
  - Hypothesis property test passed (100 random examples verifying $(P+x)/(T+x) \ge p$ and $(P+x-1)/(T+x-1) < p$).
  - Reference calculation checks verified (70/100 @ 75 -> 20; 8/14 @ 70 -> 6; 7/11 @ 70 -> 3; 65/85 @ 75 -> 0 with R=30 max misses 8; 26 credits @ 7.63, F=24, target 8.00 -> 8.40).

---

## Phase 2: Providers, Domain Models, Storage & Seeds
- **Status**: Completed (Gate passed: All fixtures load, bad files give row-level errors)
- **Work Completed**:
  - Implemented SQLite persistence layer using SQLAlchemy 2 in [edupulse/storage/database.py](file:///d:/EduPulse/edupulse/storage/database.py) and [edupulse/storage/models.py](file:///d:/EduPulse/edupulse/storage/models.py).
  - Built typed repositories with CRUD and reset capabilities in [edupulse/storage/repository.py](file:///d:/EduPulse/edupulse/storage/repository.py).
  - Built [AuthorizedCharusatProvider](file:///d:/EduPulse/edupulse/providers/authorized_charusat.py) raising `NotAuthorizedError` on every access per Security Boundary Rule 0.1.
  - Implemented [MockAcademicProvider](file:///d:/EduPulse/edupulse/providers/mock.py) covering all scenarios (S1 to S8), accurately encoding the default S3 persona (headline 80.0% vs computed 76.5%, attention rows, extra timetable courses, Sem 1 result with incomplete credits).
  - Built [FileImportProvider](file:///d:/EduPulse/edupulse/providers/file_import.py) with CSV template generation, schema validation, preview->commit batch tracking, and row-level error reporting.
  - Built [PasteImportProvider](file:///d:/EduPulse/edupulse/providers/paste_import.py) supporting student clipboard table imports and daily timetable parsing with `-` correctly treated as `UNMARKED`.
  - Built seed loader in [edupulse/storage/seed.py](file:///d:/EduPulse/edupulse/storage/seed.py) populating events catalogue and scenario data.
- **Verification Gate**:
  - `pytest -v tests/test_providers_and_storage.py`: 5 passed.
  - Total test suite: 27 passed, 1 skipped.

---

## Phase 3: Data Availability State Machine & Explainable Support Signals
- **Status**: Completed (Gate passed: S3 expected signals match Section 6; Acceptance Tests A, B, E, F, G, H green)
- **Work Completed**:
  - Implemented data availability state machine in [edupulse/core/availability.py](file:///d:/EduPulse/edupulse/core/availability.py):
    - Resolves 7 discrete domains: attendance, marks, results, credits, engagement, policy, scholarship.
    - Yields structured `Coverage` object with chips, status tags, and missing-semester detection.
  - Implemented support signals and explainability engine in [edupulse/core/signals.py](file:///d:/EduPulse/edupulse/core/signals.py):
    - Attendance signal: High / Moderate / Low / Needs more data. Correctly identifies component alerts while excluding early data (<8 classes).
    - Academic signal: High / Moderate / Low / Needs more data based on subject marks percentages and SGPA trends.
    - Overall support signal: Combines signals with converging-evidence escalation rule; never uses the word 'risk'.
    - Explainability: Produces itemized `SignalReason` list detailing concern, positive, and informational factors.
  - Verified Acceptance Test A on Persona S3:
    - Attendance = High (CPI 57.1% and FDSA Lab 63.6% both < 70%).
    - Computed overall = 76.5% (Monitor band).
    - Academic = Needs more data.
    - Overall support signal = "High — based on attendance only; academic data incomplete".
  - Verified Acceptance Test B (recovery cases), E (midterm marks entered), F (CGPA planning), G (engagement overlap note & non-escalation), H (language and tone boundary).
- **Verification Gate**:
  - `pytest -v tests/test_acceptance_a_to_h.py`: 6 passed.
  - Full test suite: 33 passed, 1 skipped.

---

## Phase 4: Streamlit UI Implementation & Responsive Design
- **Status**: Completed (Gate passed: AppTest flows pass; Desktop 1440x900 and Mobile 390x844 screenshots captured and reviewed)
- **Work Completed**:
  - Implemented application service in [edupulse/services/academic_service.py](file:///d:/EduPulse/edupulse/services/academic_service.py) fulfilling all typed UI contracts.
  - Implemented custom styling and theme utilities in [edupulse/ui/components/theme.py](file:///d:/EduPulse/ui/components/theme.py):
    - CSS tokens, accessible contrast-safe badges (no color-alone meaning, icon + text), card hover micro-animations, responsive containers.
  - Built core user interface pages:
    - [page_dashboard.py](file:///d:/EduPulse/edupulse/ui/pages/page_dashboard.py): Profile header, attendance computed vs reported discrepancy note, academic & engagement KPIs, overall support signal card, attention subjects, interactive component attendance chart, scholarship snapshot.
    - [page_attendance.py](file:///d:/EduPulse/edupulse/ui/pages/page_attendance.py): Component vs Course-combined toggle, Strong/Monitor/Attention area cards, interactive Attendance Recovery Calculator with remaining classes assumption and buffer calculation, daily timetable with P/A/NT/UNMARKED handling.
    - [page_academic.py](file:///d:/EduPulse/edupulse/ui/pages/page_academic.py): Live-validated assessment entry form, subject performance summary chart, chronological assessment trend indicators, published results and SGPA history, credit-weighted CGPA what-if target planner.
    - [page_engagement.py](file:///d:/EduPulse/edupulse/ui/pages/page_engagement.py): Filterable and searchable activity catalogue, interactive participation toggles, official attendance date overlap alerts, explicit "I have no events" declaration, points breakdown.
    - [page_explorer.py](file:///d:/EduPulse/edupulse/ui/pages/page_explorer.py): Student Success Explorer with full reason traceability, "Why?" & "How calculated?" policy rules, and "What can I do next?" support checklist.
    - [page_connect.py](file:///d:/EduPulse/edupulse/ui/pages/page_connect.py): Demo scenario selector (S1-S8), CSV/JSON file upload with downloadable templates and preview/commit flow, paste table parser, and clear Authorized University Connector boundary.
  - Integrated modern `st.navigation` multipage routing in [app.py](file:///d:/EduPulse/app.py) with unique URL paths and persistent session state.
- **Verification Gate**:
  - `pytest -v tests/test_ui_flows.py`: 2 passed cleanly.
  - Playwright visual capture executed via [scripts/capture_screenshots.py](file:///d:/EduPulse/scripts/capture_screenshots.py):
    - Captured 12 desktop (1440x900) and mobile (390x844) full-page screenshots into `docs/screenshots/`:
      - `01_dashboard_desktop_1440x900.png` / `01_dashboard_mobile_390x844.png`
      - `02_attendance_desktop_1440x900.png` / `02_attendance_mobile_390x844.png`
      - `03_academic_desktop_1440x900.png` / `03_academic_mobile_390x844.png`
      - `04_engagement_desktop_1440x900.png` / `04_engagement_mobile_390x844.png`
      - `05_explorer_desktop_1440x900.png` / `05_explorer_mobile_390x844.png`
      - `06_connect_desktop_1440x900.png` / `06_connect_mobile_390x844.png`
    - Inspected mobile layout: single-column reflow, zero horizontal clipping, responsive scroll containers.

---

## Phase 5: Scholarship Readiness Engine & Verification Docs
- **Status**: Completed (Gate passed: Tests I, P pass; unverified banners and tri-state criteria display correctly)
- **Work Completed**:
  - Implemented pure scholarship readiness evaluation engine in [edupulse/core/scholarship.py](file:///d:/EduPulse/edupulse/core/scholarship.py):
    - Evaluates each scheme criterion to tri-state statuses: `MET`, `NOT_MET`, `UNKNOWN`.
    - Distinguishes evidence basis: `official_import`, `app_estimate`, `self_declared`.
    - Evaluates midterm attendance as `UNKNOWN` with trajectory hint ("On track" with allowable buffer vs "Needs attention" with consecutive classes needed); marks `NOT_MET` only when mathematically unreachable within remaining classes.
    - Strictly forbids deriving percentage from SGPA; requires explicit attested marksheet percentage.
    - Suppresses eligibility verdicts on unverified, conflicting, or secondary schemes, returning summary counts only ("n met · n not met · n unknown").
  - Formulated seed scholarship schemes in `edupulse/config/scholarship/`:
    - `mysy_2026_27.json`: Mukhyamantri Yuva Swavalamban Yojana with `SECONDARY_ONLY` verification level and conflicting fresh-track criterion.
    - `demo_merit_fictional.json`: Verified demo scheme exercising all tri-state code paths.
  - Authored comprehensive verification protocol in [docs/VERIFY_SCHOLARSHIP.md](file:///d:/EduPulse/docs/VERIFY_SCHOLARSHIP.md) detailing exact official portal verification steps and the JSON schema for adding new schemes without code changes.
  - Built complete interactive UI in [page_scholarship.py](file:///d:/EduPulse/edupulse/ui/pages/page_scholarship.py) with student attestation inputs, criteria cards, and missing documentation checklist.
- **Verification Gate**:
  - `pytest -v tests/test_acceptance_i_and_p.py`: 2 passed (Test I on Demo Merit Scheme, Test P on MYSY secondary unverified banner & fresh track conflict).
  - Playwright visual capture verified `07_scholarship_desktop_1440x900.png` and `07_scholarship_mobile_390x844.png`.

---

## Phase 6: Mentor Cohort Explorer & Unsupervised ML
- **Status**: Completed (Gate passed: Test V passes; ML honesty documentation complete; small-group suppression active)
- **Work Completed**:
  - Implemented synthetic student cohort generator in [edupulse/ml/cohort_generator.py](file:///d:/EduPulse/edupulse/ml/cohort_generator.py):
    - Generates $n=300$ de-identified students with seeded RNG (`random_state=42`).
    - Encodes realistic distributions (attendance, lowest component, mean marks, trends, engagement points) and realistic missingness.
    - Uses pseudonymous identifiers (`STU-001` through `STU-300`).
    - Applies the standard rule-based signal engine to every row for direct comparability with unsupervised clusters.
  - Implemented unsupervised ML engine in [edupulse/ml/unsupervised.py](file:///d:/EduPulse/edupulse/ml/unsupervised.py):
    - Preprocessing with median imputation and `MissingIndicator` flags (never imputes 0 as 'no participation').
    - KMeans clustering with automatic silhouette score tuning over $k \in [3, 6]$.
    - IsolationForest anomaly detection to flag unusual combinations.
    - Generates human-readable cluster archetype labels and descriptions.
    - Enforces small-group privacy suppression rule: any pattern group with $< 5$ members is automatically suppressed.
  - Authored scientific statement against circular supervised pseudo-labeling in [docs/ML_HONESTY.md](file:///d:/EduPulse/docs/ML_HONESTY.md).
  - Built interactive UI in [page_cohort.py](file:///d:/EduPulse/edupulse/ui/pages/page_cohort.py) featuring mandatory honesty banner, multidimensional scatter plot, cluster archetype cards, and filterable table.
- **Verification Gate**:
  - `pytest -v tests/test_acceptance_v_cohort_ml.py`: 1 passed.
  - Verified mandatory banner string `Synthetic data · exploratory patterns · not a validated predictor` is present.
  - Captured `08_cohort_desktop_1440x900.png` and `08_cohort_mobile_390x844.png`.

---

## Phase 7: Settings, Data & Privacy, Security Audits & Final Hardening
- **Status**: Completed (Gate passed: Security Acceptance Tests J green; no overflow at 390px; clean ruff linting)
- **Work Completed**:
  - Implemented comprehensive Settings & Data Privacy page in [page_settings.py](file:///d:/EduPulse/edupulse/ui/pages/page_settings.py):
    - Sandbox scenario switcher (S1 to S8).
    - Academic policy configuration and verification badge.
    - De-identified academic summary export in both JSON and CSV formats.
    - Local data reset and complete database wiping.
  - Implemented Security Acceptance Tests in [tests/test_security_j.py](file:///d:/EduPulse/tests/test_security_j.py):
    - Static scan verifying zero credential tokens (`password`, `captcha`, `login_form`, `session_cookie`) in application code.
    - Static scan verifying no HTTP clients targeting any university domains.
    - Verified `AuthorizedCharusatProvider` raises `NotAuthorizedError`.
    - Verified demo storage contains only synthetic identities.
  - Verified mobile responsive layouts at 390px (Playwright mobile context: zero horizontal clipping).
  - Cleaned all linting issues with Ruff (`ruff check edupulse tests app.py` exits 0 with zero errors).
- **Verification Gate**:
  - `pytest -v tests/test_security_j.py`: 4 passed.
  - `ruff check`: All checks passed!
  - Captured `09_settings_desktop_1440x900.png` and `09_settings_mobile_390x844.png`.

---

## Phase 8: Deliverables, Checklist & Polish
- **Status**: Completed (Gate passed: Full end-to-end test pass; human verification checklist compiled)
- **Work Completed**:
  - Compiled user guide and setup documentation in [README.md](file:///d:/EduPulse/README.md).
  - Maintained architecture decisions in [docs/DECISIONS.md](file:///d:/EduPulse/docs/DECISIONS.md).
  - Maintained scholarship verification guide in [docs/VERIFY_SCHOLARSHIP.md](file:///d:/EduPulse/docs/VERIFY_SCHOLARSHIP.md).
  - Maintained machine learning honesty paper in [docs/ML_HONESTY.md](file:///d:/EduPulse/docs/ML_HONESTY.md).
- **Verification Gate**:
  - Full test suite: **42 passed, 1 skipped** in 8.75s.
  - Total test files: 10 test modules covering calculations, availability, signals, providers, storage, UI flows, security, and acceptance criteria A through V.

---

## Complete Verification & Test Execution Summary

| Command | Real Output / Exit Code | Pass / Fail Count | Notes |
| :--- | :--- | :--- | :--- |
| `pytest -v` | Exit code 0 | **42 passed, 1 skipped** | All unit, property, security, and acceptance tests green |
| `ruff check edupulse tests app.py` | Exit code 0 | **All checks passed!** | Clean Python codebase adhering to pyproject.toml standards |
| `python scripts/capture_screenshots.py` | Exit code 0 | **18 screenshots captured** | Full-page desktop (1440x900) & mobile (390x844) captures |

---

## Visual Capture Artifacts List (`docs/screenshots/`)

1. `01_dashboard_desktop_1440x900.png` — Desktop Student Dashboard with KPI cards, support signal, and attendance bar chart.
2. `01_dashboard_mobile_390x844.png` — Mobile Student Dashboard with single-column responsive reflow.
3. `02_attendance_desktop_1440x900.png` — Desktop Attendance Intelligence with subject cards, recovery calculator, and daily timetable.
4. `02_attendance_mobile_390x844.png` — Mobile Attendance Intelligence with responsive recovery controls.
5. `03_academic_desktop_1440x900.png` — Desktop Academic Performance with assessment entry, subject mastery chart, and CGPA planner.
6. `03_academic_mobile_390x844.png` — Mobile Academic Performance with full form validation.
7. `04_engagement_desktop_1440x900.png` — Desktop Engagement & Activities with catalogue filters and participation toggles.
8. `04_engagement_mobile_390x844.png` — Mobile Engagement & Activities with compact activity cards.
9. `05_explorer_desktop_1440x900.png` — Desktop Student Success Explorer with explainability reasons and action steps.
10. `05_explorer_mobile_390x844.png` — Mobile Student Success Explorer with responsive action cards.
11. `06_connect_desktop_1440x900.png` — Desktop Connect Academic Data with scenario sandbox, CSV downloaders, and connector boundary.
12. `06_connect_mobile_390x844.png` — Mobile Connect Academic Data.
13. `07_scholarship_desktop_1440x900.png` — Desktop Scholarship Readiness Planner with MYSY unverified banner and tri-state criteria.
14. `07_scholarship_mobile_390x844.png` — Mobile Scholarship Readiness Planner.
15. `08_cohort_desktop_1440x900.png` — Desktop Mentor Cohort Explorer with scatter plot, archetypes, and privacy suppression.
16. `08_cohort_mobile_390x844.png` — Mobile Mentor Cohort Explorer.
17. `09_settings_desktop_1440x900.png` — Desktop Settings & Data Privacy with export options and data wiping controls.
18. `09_settings_mobile_390x844.png` — Mobile Settings & Data Privacy.

---

## Configuration Defaults & Provenance Table

| Configuration Item | Default Value | Source / Origin | Verification Status | UI Display Note |
| :--- | :--- | :--- | :--- | :--- |
| **Attendance Overall Threshold** | `75.0%` | CHARUSAT CMPICA student handbook | Unverified for specific institute | "Unverified for your institute" badge |
| **Attendance Per-Course Threshold** | `70.0%` | CHARUSAT CMPICA student handbook | Unverified for specific institute | "Unverified for your institute" badge |
| **Attendance Aggregation Level** | `component` | Master spec requirement | Configurable default | Shows component + course combined |
| **Small-Sample Guard** | `8 classes` | Master spec requirement | Demo default guard | Excluded from signal escalation (<8 classes labelled "Early data") |
| **Attendance Monitor Band** | `75.0% to <80.0%` | Master spec requirement | Demo default | "Monitor" |
| **Marks Attention Band** | `< 50.0%` | Master spec requirement | Demo default | "Attention area" |
| **Marks Monitor Band** | `50.0% to < 65.0%` | Master spec requirement | Demo default | "Monitor" |
| **Marks Strong Band** | `>= 65.0%` | Master spec requirement | Demo default | "Strong" |
| **Assessment Trend Threshold** | `10.0 percentage points`| Master spec requirement | Demo default | Requires $\ge 2$ entries; $n=2$ labelled "early indication" |
| **SGPA Trend Threshold** | `0.30 grade points` | Master spec requirement | Demo default | $\ge +0.3$ Improving, $\le -0.3$ Declining |
| **CGPA Scale Maximum** | `10.0` | University 10-point scale | Standard scale | Max achievable CGPA calculation |
| **Future Planned Credits** | `24.0` | S3 semester load assumption | Editable planning assumption | Labelled "planning assumption" |
| **Hackathon / Competition Weight**| `3.0 points` | Master spec engagement model | Demo default | "How is this calculated?" panel |
| **Workshop / Academic Act Weight**| `2.0 points` | Master spec engagement model | Demo default | "How is this calculated?" panel |
| **Seminar / Club Activity Weight**| `1.0 points` | Master spec engagement model | Demo default | "How is this calculated?" panel |
| **Duration Factor (Full-Day)** | `1.0` | Master spec engagement model | Demo default | Scaled by hours for hourly events |
| **Duration Factor (Hourly)** | `min(hours/4, 1.0) >= 0.25`| Master spec engagement model | Demo default | Capped at 1.0, floored at 0.25 |
| **MYSY Renewal Criteria** | Att $\ge 75\%$, Marks $\ge 50\%$, Inc $\le 6\text{L}$ | Secondary educational portals | `SECONDARY_ONLY` | Banner: "Not yet verified against an official source" |
| **MYSY Fresh Criteria** | 80th percentile vs 80% marks | Conflicting secondary sources | `CONFLICTING` | Evaluation withheld until confirmed |
| **Demo Merit Scheme** | Att $\ge 80\%$, SGPA $\ge 7.50$, Inc $\le 8\text{L}$ | Fictional demonstration scheme | `OFFICIAL_VERIFIED` | Full tri-state demonstration |

---

## Needs Human Verification Checklist

Before deploying EduPulse into a live production university environment, a human administrator or faculty advisor must confirm the following items:

- [ ] **1. Official MYSY Criteria & URL**:
  - Verify official guidelines at [https://mysy.guj.nic.in](https://mysy.guj.nic.in).
  - Resolve whether fresh applicants require 80th percentile or 80% aggregate board marks.
  - Update `edupulse/config/scholarship/mysy_2026_27.json` with official URL, title, and timestamp.
- [ ] **2. CHARUSAT Institute Attendance Policy**:
  - Confirm whether the student's specific institute enforces 75% overall / 70% per-course, or a uniform 80%.
  - Verify whether "each course" requires separate theory and laboratory thresholds or course-combined totals.
  - Set `"verified": true` in `edupulse/config/policy.json` once confirmed.
- [ ] **3. Official Grade-Point Conversion Scale**:
  - Obtain the institute's official letter-grade to grade-point scale (e.g. A+ = 10, A = 9, B+ = 8).
  - Do NOT convert SGPA to percentage until an official conversion formula (e.g. $(SGPA - 0.5) \times 10$) is verified.
- [ ] **4. Semester 1 Course Roster & Semester 2 Publication Status**:
  - Confirm whether the 3 courses listed in Semester 1 represent the complete curriculum or a partial marksheet.
  - Confirm whether Semester 2 results have been published or remain unannounced.
- [ ] **5. Official Event & Co-Curricular Catalogue Source**:
  - Connect with the university student activities cell to ingest verified hackathons, clubs, and sports events via the admin CSV import feature.

---

---

## Phase 9: Demo Quality & Data Generalization Pass
- **Status**: Completed & Verified
- **Motivation**:
  - The previous default demo experience was based on screenshot-derived academic data, giving the impression of a single-student prototype rather than a reusable analytics platform.
  - This pass generalized EduPulse into an institutional platform with multiple diverse student archetypes, completely synthetic default data, prominent persona switching, and clear data provenance labels.
- **Key Enhancements**:
  1. **Synthetic Default Experience**:
     - Default persona changed to **Priya Sharma** (`SYNTH-2026-001`, B.Tech Computer Science, Semester 3).
     - Exemplary baseline: 92.7% attendance, >90% assessment marks, Sem 1 & 2 published records (SGPA 8.75 & 8.90), hackathon leadership, and Low support signal.
     - Zero personal student identity used as default.
  2. **6 Varied Synthetic Student Personas**:
     - `student_synth_strong` (Priya Sharma): Strong attendance & academics (Low signal).
     - `student_synth_att_concern` (Rohan Verma): Attendance concern (68.4% attendance, 4 course components <70%, solid 80% marks, recovery calculator active).
     - `student_synth_acad_concern` (Kabir Mehta): Academic attention areas (<50% marks in core subjects, declining SGPA -1.20, strong 85.4% attendance).
     - `student_synth_early` (Ananya Iyer): Insufficient assessment data (91.9% attendance, waiting for first assessments, zero fabricated marks/SGPA).
     - `student_synth_improving` (Devansh Joshi): Improving multi-semester trajectory (SGPA 6.50 -> 7.80 with unequal credits: 22 and 26, rising marks 70% -> 87.5%).
     - `student_synth_eng` (Zara Mansuri): Engagement-rich leadership (8.1 points across 4 events, 4 distinct categories, active timetable overlap check).
  3. **Screenshot Reference (Validation Scenario)**:
     - Preserved intact as `student_s3` (`DEMO-S3-001`, Demo Student, B.Tech IT).
     - Permanently accessible via **Settings & Data Privacy → Reference Scenarios → Screenshot Reference (CHARUSAT Validation)**.
     - Preserves portal truncation benchmark (80.0% reported vs 76.5% computed), CPI (57.1%), and FDSA Lab (63.6%).
  4. **Prominent Demo Workspace / Student Selector**:
     - Sidebar dropdown with rich archetype descriptions and live data provenance indicators.
     - 1-click Quick-Switcher buttons across the top of the Overview dashboard.
     - Dynamic reactive recalculation: switching students immediately updates all 7 modules without database wipes or state crosstalk.
  5. **Student Success Diagnostic Narrative (WHAT, WHY, WHAT NEXT)**:
     - Top of Overview dashboard immediately explains:
       - **WHAT was detected**: Concise plain-English diagnostic.
       - **WHY it was detected**: Itemized evidence and specific policy/marks triggers.
       - **WHAT the student can do next**: Constructive, non-shaming action steps.
  6. **Data Provenance Labels**:
     - Explicit badges across all pages: `[🏷️ Demo data]`, `[🔬 Reference scenario]`, `[📥 Imported data]`, `[Insufficient data]`, `[Needs verification]`.
  7. **Import Academic Data Flow**:
     - Available at **Connect & Import Data** with CSV/JSON upload (downloadable templates), paste table view, and clear distinction from offline enterprise connectors.
- **Verification Gate**:
  - `pytest -v`: **52 passed, 1 skipped** in 17.87s.
  - `ruff check edupulse tests app.py`: **All checks passed!**
  - `python scripts/capture_screenshots.py`: **30 screenshots captured** across desktop (1440x900) and mobile (390x844).

---

## Known Gaps & Design Boundaries
1. **Live Portal Automation**: Deliberately disabled and feature-flagged off via `AuthorizedCharusatProvider` raising `NotAuthorizedError` in accordance with Security Boundary Rule 0.1.
2. **Missing History**: Historical gaps (e.g. Semester 2 in S3) are not fabricated. They display as "Semester 2 not in supplied data".
3. **No Supervised Risk Predictions**: Predictive classifier intentionally omitted in accordance with scientific ethics and [ML_HONESTY.md](file:///d:/EduPulse/docs/ML_HONESTY.md). Unsupervised clustering and rule-based explainability are provided instead.
