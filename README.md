# EduPulse — Student Success & Scholarship Readiness Explorer

[![Tests](https://img.shields.io/badge/pytest-52%20passed%2C%201%20skipped-brightgreen.svg)]()
[![Lint](https://img.shields.io/badge/ruff-all%20checks%20passed-blue.svg)]()
[![Privacy](https://img.shields.io/badge/security-no%20credentials%20%7C%20zero%20scraping-success.svg)]()
[![Platform](https://img.shields.io/badge/architecture-reusable%20multi--student%20analytics-6366f1.svg)]()

EduPulse is an intelligence and academic planning application built for **College Hackathon Challenge 3: Student Success Risk Explorer**. It explores attendance, assessment marks, and co-curricular engagement data across diverse student profiles to identify where academic support may be beneficial, calculate actionable recovery plans, and evaluate scholarship readiness against published criteria with total explainability.

---

## 🎭 Synthetic Demo Personas & Reusable Analytics

EduPulse is designed as a reusable analytics product supporting multiple student profiles, self-supplied file imports, and institutional benchmarking. 

The default demo experience uses completely synthetic data with zero personal student identity:

| Persona | Name | Program | Archetype | Key Characteristics |
|---|---|---|---|---|
| **Default** | **Priya Sharma** (`SYNTH-2026-001`) | B.Tech CS (Sem 3) | **Strong Academics & Attendance** | 92.7% attendance, high marks (>90%), active hackathon leadership, Low support signal. |
| **Alert** | **Rohan Verma** (`SYNTH-2026-002`) | B.Tech IT (Sem 3) | **Attendance Concern & Recovery** | 68.4% attendance (<75% threshold, 4 components <70%), solid marks (80%), High support signal. |
| **Alert** | **Kabir Mehta** (`SYNTH-2026-003`) | B.Tech EC (Sem 3) | **Academic Performance Concern** | 85.4% attendance, low assessment scores (<50%), declining SGPA (-1.20 points), High support signal. |
| **Early** | **Ananya Iyer** (`SYNTH-2026-004`) | B.Tech AI (Sem 1) | **Insufficient Current Marks** | 91.9% attendance, zero marks yet ("Waiting for first assessment"), no fabricated marks or SGPA. |
| **Growth** | **Devansh Joshi** (`SYNTH-2026-005`) | B.Tech ME (Sem 3) | **Improving Trajectory** | 84.8% attendance, SGPA rising from 6.50 to 7.80 (+1.30) across unequal credits (22 and 26). |
| **Active** | **Zara Mansuri** (`SYNTH-2026-006`) | B.Tech CE (Sem 3) | **Engagement-Rich Leadership** | 85.2% attendance, 8.1 engagement points across 4 events and 4 distinct activity types. |
| **Benchmark** | **Demo Student** (`DEMO-S3-001`) | B.Tech IT (Sem 3) | **Screenshot Reference (Validation)** | Preserved regression validation benchmark for portal truncation (80% vs 76.5%) and CPI/FDSA lab alerts. |

### Accessing the Screenshot Reference Scenario:
The original screenshot-derived validation scenario is preserved for regression testing and edge-case verification:
- Navigate to **Settings & Data Privacy → Reference Scenarios → Screenshot Reference (CHARUSAT Validation)**.
- Click **"Load Screenshot Reference (S3)"** or select it directly from the Demo Workspace sidebar dropdown.

---

## ⚡ Demo Workspace & Dynamic Recalculation

EduPulse features a prominent **Demo Workspace / Student Selector**:
1. **Sidebar Dropdown**: Instantly switch between any of the 6 synthetic personas, the screenshot reference benchmark, or custom imported profiles.
2. **Top Banner Quick-Switcher**: 1-click persona chips on the Overview dashboard.
3. **Dynamic Reactive Recalculation**: Switching a persona immediately recalculates all 7 application pages:
   - **Overview**: Diagnostic narrative (WHAT was detected, WHY, and WHAT the student can do next), KPIs, and scholarship snapshot.
   - **Attendance Intelligence**: Course components, recovery calculator, and daily timetable log.
   - **Academic Performance**: Current assessments, published results, and CGPA what-if planner.
   - **Engagement & Activities**: Verified co-curricular points and diversity levels.
   - **Student Success Explorer**: Transparent multi-pillar support signals and evidence traceability.
   - **Scholarship Readiness Planner**: Dynamic eligibility tracking based on active student results and attendance.
   - **Mentor Cohort Explorer**: Highlights where the active student sits in the wider unsupervised cohort pattern space.

---

## 📥 Import Academic Data (Self-Supplied Files & Paste)

Located at **Connect & Import Data**, users can supply their own academic records with clear **Data Provenance** tracking:
- **Spreadsheet Upload (CSV/JSON)**: Upload attendance, marks, or timetable records with pre-validation and row-level error reporting. Official downloadable templates are provided.
- **Paste Copied Table Rows**: Copy table rows directly from university portal screens (e.g. `CEUE203 / OOP | LECT | 14 / 15 | 93.3%`). Unmarked dates (`-`) are mapped to `UNMARKED` rather than absent.
- **Authorized Academic Provider**: Offline enterprise architecture reference with strict zero-credential and zero-scraping guarantees.

Every screen features visible **Data Provenance Labels**:
- `[🏷️ Demo data]` for synthetic personas
- `[🔬 Reference scenario]` for the screenshot validation benchmark
- `[📥 Imported data]` for self-supplied uploads
- `[Insufficient data]` when records have not yet been recorded
- `[Needs verification]` for unverified policy and scholarship criteria

---

## 🚀 Quickstart & Setup

### 1. Environment Requirements
- Python 3.11+ (Tested on Python 3.14.3)
- Windows / macOS / Linux

### 2. Setup Virtual Environment & Dependencies
```bash
# Clone or navigate to the repository
cd d:/EduPulse

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install project dependencies
pip install -r requirements.txt

# Install Playwright browser binaries for screenshot testing (optional)
playwright install chromium
```

### 3. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Testing & Verification

Run the complete automated test suite (including unit tests, Hypothesis property tests, persona switching tests, and security scans):
```bash
# Run all tests (52 passed, 1 skipped)
pytest -v

# Run with ruff linting
ruff check edupulse tests app.py

# Capture fresh full-page desktop & mobile screenshots
python scripts/capture_screenshots.py
```

---

## 🔒 Security & Privacy Guarantees

- **No Credential Ingestion**: Never asks for, stores, or transmits university passwords, session tokens, or CAPTCHA answers.
- **No Live Scraping**: Live portal scraping is strictly prohibited. `AuthorizedCharusatProvider` is a stub raising `NotAuthorizedError`.
- **Fictional Synthetic Identity**: Default identity is `Priya Sharma` (`SYNTH-2026-001`). No personal academic data is used.
- **Calm, Constructive Language**: Prohibits terms like "fail", "at risk", or "scholarship eligible".
