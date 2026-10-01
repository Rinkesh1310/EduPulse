from typing import Any

import streamlit as st

from edupulse.domain.enums import SupportLevel


def apply_custom_theme():
    """Applies a unified, premium SaaS analytics design system across EduPulse."""
    st.markdown(
        """
        <style>
        /* Import clean modern typography */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --font-display: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            
            --bg-canvas: #f8fafc;
            --surface-card: #ffffff;
            --surface-muted: #f1f5f9;
            --border-subtle: #e2e8f0;
            --border-focus: #3b82f6;

            --text-heading: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --text-faint: #94a3b8;

            --color-primary: #1e3a8a;
            --color-primary-accent: #2563eb;
            --color-primary-light: #eff6ff;

            --color-success: #166534;
            --color-success-bg: #f0fdf4;
            --color-success-border: #bbf7d0;

            --color-warning: #92400e;
            --color-warning-bg: #fffbeb;
            --color-warning-border: #fde68a;

            --color-danger: #991b1b;
            --color-danger-bg: #fef2f2;
            --color-danger-border: #fecaca;

            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            --radius-full: 9999px;

            --shadow-subtle: 0 1px 2px 0 rgba(15, 23, 42, 0.04), 0 1px 1px 0 rgba(15, 23, 42, 0.02);
            --shadow-card: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
            --shadow-card-hover: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
        }

        /* Global application typography & layout */
        html, body, [class*="css"] {
            font-family: var(--font-body);
            color: var(--text-body);
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display) !important;
            color: var(--text-heading) !important;
            letter-spacing: -0.015em;
            font-weight: 700;
        }

        /* Streamlit main block container padding */
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3.5rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
            max-width: 1380px;
        }

        /* Refined Card Component */
        .edu-card {
            background: var(--surface-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 22px 24px;
            margin-bottom: 18px;
            box-shadow: var(--shadow-card);
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .edu-card:hover {
            box-shadow: var(--shadow-card-hover);
            border-color: #cbd5e1;
        }

        /* Clean SaaS Metric Tile */
        .edu-metric-tile {
            background: var(--surface-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 16px 18px;
            box-shadow: var(--shadow-subtle);
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .edu-metric-tile .metric-label {
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-bottom: 6px;
        }
        .edu-metric-tile .metric-value {
            font-family: var(--font-display);
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--text-heading);
            letter-spacing: -0.02em;
            line-height: 1.2;
        }
        .edu-metric-tile .metric-subtext {
            font-size: 0.82rem;
            color: var(--text-muted);
            margin-top: 6px;
        }

        /* Standardized Status Badges */
        .badge-high {
            background-color: var(--color-danger-bg);
            color: var(--color-danger);
            border: 1px solid var(--color-danger-border);
            padding: 4px 10px;
            border-radius: var(--radius-full);
            font-weight: 600;
            font-size: 0.82rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }
        .badge-high::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #ef4444;
        }

        .badge-moderate {
            background-color: var(--color-warning-bg);
            color: var(--color-warning);
            border: 1px solid var(--color-warning-border);
            padding: 4px 10px;
            border-radius: var(--radius-full);
            font-weight: 600;
            font-size: 0.82rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }
        .badge-moderate::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #f59e0b;
        }

        .badge-low {
            background-color: var(--color-success-bg);
            color: var(--color-success);
            border: 1px solid var(--color-success-border);
            padding: 4px 10px;
            border-radius: var(--radius-full);
            font-weight: 600;
            font-size: 0.82rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }
        .badge-low::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #10b981;
        }

        .badge-info {
            background-color: var(--color-primary-light);
            color: var(--color-primary-accent);
            border: 1px solid #bfdbfe;
            padding: 4px 10px;
            border-radius: var(--radius-full);
            font-weight: 600;
            font-size: 0.82rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }
        .badge-info::before {
            content: '';
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #3b82f6;
        }

        .badge-neutral {
            background-color: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            padding: 4px 10px;
            border-radius: var(--radius-full);
            font-weight: 600;
            font-size: 0.82rem;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }

        /* Evidence Scannable Rows */
        .evidence-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1.5fr;
            gap: 12px;
            padding: 10px 14px;
            border-bottom: 1px solid #f1f5f9;
            font-size: 0.88rem;
            align-items: center;
        }
        .evidence-row:last-child {
            border-bottom: none;
        }

        /* Streamlit Tab Overrides */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: var(--radius-md) var(--radius-md) 0 0;
            padding: 8px 16px;
            font-family: var(--font-body);
            font-weight: 500;
            font-size: 0.92rem;
            color: var(--text-muted);
            border: none;
        }
        .stTabs [aria-selected="true"] {
            color: var(--color-primary-accent) !important;
            font-weight: 600 !important;
            border-bottom: 2px solid var(--color-primary-accent) !important;
            background-color: transparent !important;
        }

        /* Streamlit Button Styling */
        .stButton button {
            border-radius: var(--radius-md);
            font-family: var(--font-body);
            font-weight: 600;
            font-size: 0.88rem;
            padding: 0.5rem 1rem;
            transition: all 0.15s ease;
        }

        /* Responsive Layout Utilities */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }
            .evidence-row {
                grid-template-columns: 1fr;
                gap: 6px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_html(html: str):
    """Renders HTML safely without triggering CommonMark indented code blocks."""
    cleaned = "\n".join(line.strip() for line in html.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def render_page_header(
    title: str,
    subtitle: str,
    student: Any,
    provenance: str,
    as_of_date: str | None = None,
    academic_status: str | None = None,
):
    """Renders a standard, high-hierarchy SaaS page header."""
    name_str = student.name if student else "Demo Student"
    ext_id = student.externalStudentId if student else "SYNTH-2026-001"
    prog = student.program if student else "B.Tech Computer Science"
    sem = student.semester if student else 3
    ay = student.academicYear if student else "2026-27"
    as_of = as_of_date or "2026-09-30"

    prov_badge_class = (
        "badge-low"
        if provenance == "Demo data"
        else ("badge-moderate" if "Reference" in provenance else "badge-info")
    )

    st.title(title)
    render_html(
        f"""
        <div style="margin-top: -12px; margin-bottom: 22px; padding-bottom: 14px; border-bottom: 1px solid #e2e8f0;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div>
                    <p style="margin: 0; color: #475569; font-size: 0.96rem; font-weight: 400;">
                        {subtitle}
                    </p>
                </div>
                <div style="text-align: right; display: flex; flex-direction: column; align-items: flex-end; gap: 6px;">
                    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                        <span class="{prov_badge_class}">Data Source: {provenance}</span>
                        <span class="badge-neutral" style="font-size: 0.78rem;">As of {as_of}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: #334155; font-weight: 500;">
                        <strong>{name_str}</strong> &nbsp;•&nbsp; <code>{ext_id}</code> &nbsp;•&nbsp; {prog} (Sem {sem}, {ay})
                    </div>
                </div>
            </div>
            {f'<div style="margin-top: 8px; font-size: 0.8rem; color: #64748b;"><strong>Status:</strong> <code>{academic_status}</code></div>' if academic_status else ''}
        </div>
        """
    )


def render_metric_card(title: str, value: str, subtext: str, status_level: SupportLevel | str | None = None):
    """Renders a clean SaaS metric card."""
    badge_html = ""
    if status_level:
        badge_class = "badge-info"
        val_str = status_level.value if hasattr(status_level, "value") else str(status_level)
        if val_str == "High":
            badge_class = "badge-high"
        elif val_str == "Moderate":
            badge_class = "badge-moderate"
        elif val_str == "Low":
            badge_class = "badge-low"
        badge_html = f'<span class="{badge_class}" style="font-size:0.75rem; padding:2px 8px;">{val_str}</span>'

    render_html(
        f"""
        <div class="edu-metric-tile">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="metric-label">{title}</div>
                {badge_html}
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
        """
    )


def render_support_signal_card(signal: SupportLevel, title: str, reasons: list[Any]):
    """Renders the executive Overall Support Signal Hero Card."""
    badge_class = "badge-info"
    badge_label = signal.value
    border_accent = "#3b82f6"

    if signal == SupportLevel.HIGH:
        badge_class = "badge-high"
        border_accent = "#ef4444"
    elif signal == SupportLevel.MODERATE:
        badge_class = "badge-moderate"
        border_accent = "#f59e0b"
    elif signal == SupportLevel.LOW:
        badge_class = "badge-low"
        border_accent = "#10b981"

    render_html(
        f"""
        <div class="edu-card" style="border-left: 5px solid {border_accent}; background: #ffffff; padding: 22px 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#64748b;">Executive Support Signal</span>
                    <span class="{badge_class}" style="font-size:0.9rem; padding:4px 12px;">{badge_label}</span>
                </div>
                <span class="badge-neutral" style="font-size:0.75rem;">Non-Punitive Academic Guidance</span>
            </div>
            <p style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 4px 0 8px 0; letter-spacing: -0.01em;">
                {title}
            </p>
            <p style="font-size: 0.88rem; color: #475569; margin: 0; line-height: 1.45;">
                Signals identify key focus areas for targeted mentorship, concept review, and buffer management. 
                They represent supportive institutional checkpoints, never academic penalties or outcome forecasts.
            </p>
        </div>
        """
    )


def render_verification_badge(verified: bool, label: str | None = None):
    """Renders policy and authority verification status."""
    if verified:
        badge_html = f'<span class="badge-low" style="font-size:0.8rem;">{label or "Policy Verified"}</span>'
    else:
        badge_html = f'<span class="badge-moderate" style="font-size:0.8rem;">{label or "Unverified for your institute"}</span>'
    render_html(badge_html)
