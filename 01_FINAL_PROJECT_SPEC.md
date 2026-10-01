# EduPulse — Final Project Specification

## 1. Product title
EduPulse — Student Success & Scholarship Readiness Explorer

## 2. Problem being solved
Challenge 3 asks for a Student Success Risk Explorer that explores attendance, marks and engagement data to identify students who may benefit from additional academic support. The supplied challenge brief lists Education / ML as the theme, Data analysis + ML as the core skill, and Python/pandas/scikit-learn + Streamlit as the suggested stack.

## 3. Product thesis
CHARUSAT already contains academic information such as attendance and semester results. EduPulse adds an intelligence layer on top of the information that is legitimately available:

Official/authorized academic data
+ student-entered current assessment data
+ structured activity/engagement data
→ analytics + ML/pattern detection
→ explainable support signals
→ academic planning
→ scholarship-readiness planning

EduPulse must never pretend that missing raw marks, event participation or future SGPA values are known.

## 4. Data sources

### A. Academic source / CHARUSAT (authorized path only)
Potentially available:
- Student ID / basic profile
- Daily attendance
- Subject/course names
- Present/total counts
- Attendance percentages
- Semester number
- SGPA
- Course name
- Course type
- Credits
- Grades

The supplied screenshots demonstrate these fields.

### B. Runtime student input
Current assessment data:
- Assessment type (Midterm, Quiz, Internal, Assignment, etc.)
- Subject (auto-populated from discovered subjects where possible)
- Marks obtained
- Maximum marks
- Assessment date/term

Rules:
- If no assessment has happened yet, do not calculate marks-based signals.
- Do not create a fake marks value from SGPA or grade.
- Store obtained and maximum marks, not just a percentage.

### C. Engagement/activity input
Examples:
- Hackathons
- Technical competitions
- Workshops
- Seminars
- Academic activities
- Projects
- Club/student activities, when legitimately relevant

Use a predefined activity/event catalogue so students select events instead of remembering dates.

Rules:
- No participation entry does not automatically mean low engagement.
- Missing engagement data = insufficient data, not zero.
- Student can confirm participation from an event catalogue.
- Event participation contributes to engagement analytics.
- Do not add event participation as extra attendance if the same day is already reflected in official attendance.
- Official attendance remains the attendance source of truth.

## 5. Dynamic semester/data availability rules
The app must first determine what information exists.

### New Semester / pre-assessment
Available: attendance only.
Output: attendance analytics only.
Marks status: waiting for first assessment.

### First midterm completed
Available: attendance + current marks.
Output: attendance + academic performance signals.

### Semester result published
Available: attendance + semester result + current marks where entered.
Output: semester analysis, grade/course insights, SGPA history and trend.

### Only odd semester completed
Do not pretend even semester performance exists.
Allow target CGPA what-if planning for the next semester.

### Missing history
Show `Not available` / `Insufficient data` / `Not yet published` as appropriate.
Never convert missing values into zero.

## 6. Support-signal categories
Keep these as explainable, separate signals rather than one opaque score.

### Attendance signal
- Overall attendance
- Subject/course attendance
- Threshold proximity
- Attendance trend
- Future attendance recovery calculator

The supplied project discussions referenced a 75% overall / 70% per-subject examination-attendance threshold from CHARUSAT material. This threshold must be verified against the current official policy before being hard-coded in the live product.

### Academic performance signal
- Current assessment percentages
- Subject-level performance
- Assessment trend
- Previous SGPA / grades
- SGPA trend
- Course credit context

### Engagement signal
- Structured participation data
- Recent activity
- Activity frequency/diversity if supported by available data
- Never infer low engagement merely from no events.

### Data-quality / coverage signal
Show whether analysis is complete, partial or waiting for missing inputs.

## 7. Risk terminology
Use language such as:
- Support signal: Low / Moderate / High
- Attendance alert
- Academic attention area
- Engagement information
- Needs more data

Avoid definitive statements such as:
- `You will fail`
- `You are definitely at risk`
- `Scholarship eligible`

The product should say that signals indicate where additional support or review may be useful.

## 8. Explainability
Every support signal should include the main contributing indicators.
Example:
- CPI attendance = 57%
- FDSA Lab attendance = 63%
- Current CPI assessment = 45%
- Academic trend is declining

Also show positive indicators where appropriate.

## 9. Subject-level intelligence
Example data:
- OOP Lecture: 93%
- OOP Lab: 88%
- FDSA Lecture: 77%
- FDSA Lab: 63%
- CPI Lecture: 57%

Possible UI:
- Strong
- Monitor
- Attention area

The exact labels/thresholds must be configurable and justified, not silently invented.

## 10. Attendance recovery calculator
Given present/total attendance and a target percentage, calculate the number of consecutive future classes that would need attendance to reach the target if the student attends all future classes.

Formula for current present `P`, total `T`, target `r`:
(P + x) / (T + x) >= r
Solve for the minimum non-negative integer x.

Also show that any future absence will change the calculation.

## 11. Academic what-if planner
If prior semester/cumulative information and credit totals are available, calculate what SGPA is required in a future semester to reach a target CGPA.

Use credit-weighted calculations when credit data is available.

Do not simply average semester SGPA values unless credits are equal and that assumption is explicitly stated.

Example concept:
Current CGPA: 7.63
Target: 8.00
Required next-semester SGPA: calculated from actual completed/future credits.

## 12. Scholarship Readiness Planner
This is separate from academic support risk.

Features:
- Select a scholarship scheme.
- Load the scheme's official/published criteria.
- Show each criterion as `Met`, `Not Met`, `Unknown / Needs Verification`.
- Calculate academic/attendance targets when the scheme's rules make such a calculation valid.
- Show which inputs/documents remain unverified.
- Never present the result as a guaranteed scholarship decision.

Criteria must be versioned by scheme/year and linked to the official source used during implementation.

The supplied discussions used MYSY as an example; verify current official rules before implementation.

## 13. Suggested pages
1. Landing / Connect Academic Data
2. Student Dashboard
3. Attendance Intelligence
4. Academic Performance
5. Engagement & Activities
6. Student Success Explorer
7. Scholarship Readiness Planner
8. Settings / Data & Privacy

## 14. Dashboard content
- Overall attendance
- Academic performance indicator
- Engagement indicator / coverage
- Support signal
- Main reasons
- Weak/attention subjects
- Trend charts
- Data freshness / coverage
- Scholarship readiness snapshot

## 15. Cohort/mentor mode (optional if time permits)
A mentor/admin can upload a de-identified class dataset and explore students with concerning patterns.
Do not expose private student data unnecessarily.

## 16. Privacy/security expectations
- Do not store university passwords.
- Do not log passwords or session cookies.
- Do not bypass CAPTCHA or access controls.
- Use the minimum required academic data.
- Encrypt data in transit.
- Prefer ephemeral/demo data for hackathon mode.
- Provide a clear data-source and privacy explanation.

## 17. Implementation philosophy
Build a clean adapter boundary:

`AcademicDataProvider`
→ `MockAcademicProvider` for demo
→ `AuthorizedCharusatProvider` only when legitimate API/SSO/export access exists.

Keep analytics independent from the data source so the project can work today with demo/import data and later with an approved integration.

## 18. MVP priority
Must-have:
- Responsive polished UI
- Attendance import/mock connector
- Subject detection
- Runtime marks entry with assessment availability logic
- Engagement event catalogue + participation selection
- Attendance analytics
- Marks analytics
- Engagement analytics
- Explainable support signals
- Attendance recovery calculator
- Semester/SGPA trend where available
- Scholarship readiness rules engine with at least one demonstrable scheme using official, current criteria

Nice-to-have:
- Cohort explorer
- ML model with a defensible labelled dataset
- Personalized what-if simulation
- Exportable report
- Mentor dashboard

## 19. Judge-facing message
EduPulse is not another college ERP. It is an intelligence and planning layer that answers:
- What does my academic data currently say?
- Where are my support/attention areas?
- What data is missing?
- What do I need to improve next?
- Based on a selected scholarship's published rules, what requirements are currently met and what future target should I plan for?
