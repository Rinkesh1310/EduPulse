import subprocess
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:8501"


def is_server_running(url: str = APP_URL) -> bool:
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except Exception:
        return False


def run_workspace_demo_capture():
    proc = None
    if not is_server_running():
        cmd = [
            str(Path(__file__).parent.parent / ".venv" / "Scripts" / "streamlit.exe"),
            "run",
            "app.py",
            "--server.headless", "true",
            "--server.port", "8501",
        ]
        proc = subprocess.Popen(cmd, cwd=str(Path(__file__).parent.parent))
        time.sleep(5)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # Viewports to capture
            viewports = [
                ("desktop", {"width": 1440, "height": 900}),
                ("mobile", {"width": 390, "height": 844}),
            ]

            for mode_name, vp in viewports:
                print(f"--- Capturing {mode_name.upper()} ({vp['width']}x{vp['height']}) ---")
                context = browser.new_context(viewport=vp)
                page = context.new_page()

                # 1. Onboarding / Academic Data Page
                page.goto(f"{APP_URL}/connect", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"01_onboarding_academic_data_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 01_onboarding_academic_data_{mode_name}.png")

                # 2. Student Workspace / Overview
                page.goto(f"{APP_URL}/dashboard", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"02_student_workspace_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 02_student_workspace_{mode_name}.png")

                # 3. Full Academic Record
                page.goto(f"{APP_URL}/record", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"03_academic_record_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 03_academic_record_{mode_name}.png")

                # 4. Assessment Entry (Marks Matrix)
                page.goto(f"{APP_URL}/academic", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"04_assessment_entry_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 04_assessment_entry_{mode_name}.png")

                # 5. Engagement Selection & History
                page.goto(f"{APP_URL}/engagement", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"05_engagement_selection_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 05_engagement_selection_{mode_name}.png")

                # 6. Student Success Explorer (Central Result)
                page.goto(f"{APP_URL}/explorer", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"06_success_explorer_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 06_success_explorer_{mode_name}.png")

                # 7. Modify marks on Academic page and capture changed result in Explorer
                page.goto(f"{APP_URL}/academic", wait_until="networkidle", timeout=20000)
                time.sleep(2)

                # Click "Analyze Academic Health" button or trigger recalculation
                try:
                    analyze_btn = page.locator("button:has-text('Analyze Academic Health')").first
                    if analyze_btn.is_visible():
                        analyze_btn.click()
                        time.sleep(2)
                except Exception as e:
                    print(f"Analyze click note: {e}")

                # Return to Success Explorer to capture changed result
                page.goto(f"{APP_URL}/explorer", wait_until="networkidle", timeout=20000)
                time.sleep(2)
                page.screenshot(
                    path=str(OUTPUT_DIR / f"07_changed_result_explorer_{mode_name}.png"),
                    full_page=True,
                )
                print(f"Saved 07_changed_result_explorer_{mode_name}.png")

                context.close()

            browser.close()
            print("All screenshots captured successfully!")
    finally:
        if proc:
            proc.terminate()
            proc.wait()


if __name__ == "__main__":
    run_workspace_demo_capture()
