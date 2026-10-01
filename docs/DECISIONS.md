# Architecture & Design Decisions Log

This document records key defensible engineering decisions made during the development of EduPulse.

---

### DEC-001: Data Persistence with SQLite and SQLAlchemy 2
- **Context**: The app needs lightweight local persistence for student profiles, imported data batches, assessment records, engagement participation, and attested facts.
- **Decision**: Use SQLite with SQLAlchemy 2 (ORM + typed Core mappings) stored at `edupulse.db` (git-ignored).
- **Rationale**: Zero external server dependencies; rapid startup in Streamlit; transaction isolation; seamless reset/wipe capabilities.

### DEC-002: Streamlit `st.navigation` Multi-Page Pattern
- **Context**: Streamlit supports both legacy multi-page directory structures (`pages/*.py`) and modern programmatic `st.navigation` (available since v1.36+).
- **Decision**: Use `st.navigation` in `app.py` referencing page modules in `edupulse/ui/pages/`.
- **Rationale**: Allows centralized state initialization, session management, dynamic badges/section grouping, and consistent page-level error handling.

### DEC-003: Pure Domain & Core Separation (Import Boundary Rule)
- **Context**: Core mathematical and logic calculations must remain independent of Streamlit UI and between discrete domains.
- **Decision**: Keep `edupulse/core/` completely free of `streamlit` imports. Furthermore, enforce an architectural boundary: `edupulse/core/attendance*` must never import `edupulse/core/engagement*`.
- **Rationale**: Enables deterministic unit and property-based testing (Hypothesis) without Streamlit runtime context, and ensures separation of concerns.

### DEC-004: Exact Arithmetic and Attendance Recovery Formula
- **Context**: Attendance ratios and recovery calculations must handle fractional percentages and prevent floating point errors.
- **Decision**: Use `Fraction` and exact integer division/ceil arithmetic for recovery steps:
  $$x = \max\left(0, \left\lceil \frac{p \cdot T - 100 \cdot P}{100 - p} \right\rceil\right)$$
  Buffer calculation:
  $$m = \left\lfloor \frac{100 \cdot P - p \cdot T}{p} \right\rfloor$$
- **Rationale**: Meets property tests where $(P+x)/(T+x) \ge p$ and $(P+x-1)/(T+x-1) < p$ strictly hold for $x > 0$.

### DEC-005: Multi-Semester CGPA Calculation
- **Context**: CGPA calculation from historical semesters where credit totals might be missing or unverified.
- **Decision**: Only compute credit-weighted CGPA when credits are complete. If credits are missing or equal, block automatic averaging unless explicitly attested by the student with "assume equal credits" noted.
- **Rationale**: Prevents misleading CGPAs caused by differing semester credit loads.

### DEC-006: Scholarship Evaluation Met / Not Met / Unknown Taxonomy
- **Context**: Secondary sources like MYSY have conflicting or unverified fresh-applicant rules, and mid-term evaluations cannot know final certified figures.
- **Decision**: Return tri-state results (`MET`, `NOT_MET`, `UNKNOWN`) alongside evidence basis (`official_import`, `app_estimate`, `self_declared`) and list required unverified items.
- **Rationale**: Complies with Rule 0.3 ("criteria currently met / not met / unknown") and ensures students are never misled with false eligibility promises.

### DEC-007: Multi-Student Synthetic Seeding & Zero-Wipe Persona Switching
- **Context**: Single-student hardcoded defaults make the application appear as a dashboard built for one student rather than an institutional student-success platform.
- **Decision**: Seed all 6 synthetic personas and the screenshot reference validation benchmark simultaneously into SQLite with student-scoped IDs. Switching personas updates `st.session_state["current_student_id"]` and triggers an immediate recalculation of all modules without database wipes or loss of user-added assessments.
- **Rationale**: Provides instant, zero-latency switching between student archetypes; preserves historical validation tests; and proves genuine platform reusability.
