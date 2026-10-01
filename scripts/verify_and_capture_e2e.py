import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:8501"

PAGES_TO_TEST = [
    ("01_desktop_dashboard", f"{APP_URL}/"),
    ("02_desktop_attendance", f"{APP_URL}/attendance"),
    ("03_desktop_academic", f"{APP_URL}/academic"),
    ("04_desktop_engagement", f"{APP_URL}/engagement"),
    ("05_desktop_success_explorer", f"{APP_URL}/explorer"),
    ("06_desktop_scholarship", f"{APP_URL}/scholarship"),
    ("07_desktop_record", f"{APP_URL}/record"),
    ("08_desktop_connect", f"{APP_URL}/connect"),
    ("09_desktop_cohort", f"{APP_URL}/cohort"),
    ("10_desktop_privacy", f"{APP_URL}/settings"),
]

def run_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # ----------------------------------------------------
        # 1. DESKTOP AUDIT (1440 x 900)
        # ----------------------------------------------------
        print("=== RUNNING DESKTOP (1440x900) AUDIT ===")
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        for name, url in PAGES_TO_TEST:
            print(f"Visiting {name}: {url}...")
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(2.5)

            # Specific page interactions
            if "attendance" in name:
                # Test attendance component filter
                try:
                    lab_option = page.locator("label:has-text('LAB')").first
                    if lab_option.is_visible():
                        lab_option.click()
                        time.sleep(1)
                except Exception as e:
                    print(f"Attendance filter note: {e}")
            elif "academic" in name:
                # Enter marks and click analyze
                try:
                    num_input = page.locator("input[type='number']").first
                    if num_input.is_visible():
                        num_input.fill("22.5")
                    btn = page.locator("button:has-text('Analyze Academic Health')").first
                    if btn.is_visible():
                        btn.click()
                        time.sleep(1.5)
                except Exception as e:
                    print(f"Academic analyze note: {e}")
            elif "engagement" in name:
                # Toggle activity participation
                try:
                    chk = page.locator("input[type='checkbox']").first
                    if chk.is_visible():
                        chk.click()
                        time.sleep(1.5)
                except Exception as e:
                    print(f"Engagement toggle note: {e}")

            out_path = OUTPUT_DIR / f"{name}.png"
            page.screenshot(path=str(out_path), full_page=True)
            print(f"[OK] Saved {out_path.name}")

        context.close()

        # ----------------------------------------------------
        # 2. MOBILE AUDIT (390 x 844)
        # ----------------------------------------------------
        print("=== RUNNING MOBILE (390x844) AUDIT ===")
        m_context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        m_page = m_context.new_page()

        mobile_pages = [
            ("11_mobile_dashboard", f"{APP_URL}/"),
            ("12_mobile_success_explorer", f"{APP_URL}/explorer"),
            ("13_mobile_attendance", f"{APP_URL}/attendance"),
            ("14_mobile_academic", f"{APP_URL}/academic"),
        ]

        for m_name, m_url in mobile_pages:
            print(f"Visiting mobile {m_name}: {m_url}...")
            m_page.goto(m_url, wait_until="networkidle", timeout=30000)
            time.sleep(2.5)
            m_out = OUTPUT_DIR / f"{m_name}.png"
            m_page.screenshot(path=str(m_out), full_page=True)
            print(f"[OK] Saved {m_out.name}")

        m_context.close()
        browser.close()
        print("=== COMPLETE AUDIT & VISUAL CAPTURE SUCCESSFUL ===")

if __name__ == "__main__":
    run_e2e()
