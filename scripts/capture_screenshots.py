import subprocess
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:8501"

PAGES = [
    ("dashboard", "01_dashboard", "dashboard"),
    ("attendance", "02_attendance", "attendance"),
    ("academic", "03_academic", "academic"),
    ("engagement", "04_engagement", "engagement"),
    ("explorer", "05_explorer", "signals"),
    ("scholarship", "07_scholarship", "scholarship"),
    ("cohort", "08_cohort", "cohort"),
    ("settings", "09_settings", "settings"),
    ("connect", "06_connect", "connect"),
]


def is_server_running(url: str = APP_URL) -> bool:
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except Exception:
        return False


def capture():
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

            # Desktop (1440x900)
            desktop_context = browser.new_context(viewport={"width": 1440, "height": 900})
            desktop_page = desktop_context.new_page()

            # Mobile (390x844)
            mobile_context = browser.new_context(viewport={"width": 390, "height": 844})
            mobile_page = mobile_context.new_page()

            for url_slug, prefix, short_name in PAGES:
                target_url = f"{APP_URL}/{url_slug}" if url_slug != "dashboard" else APP_URL

                # Capture desktop
                try:
                    desktop_page.goto(target_url, wait_until="networkidle", timeout=15000)
                    time.sleep(2)
                    desktop_page.screenshot(path=str(OUTPUT_DIR / f"{prefix}_desktop_1440x900.png"), full_page=True)
                    desktop_page.screenshot(path=str(OUTPUT_DIR / f"{short_name}_desktop.png"), full_page=True)
                    print(f"Captured {prefix}_desktop")
                except Exception as e:
                    print(f"Error capturing desktop {prefix}: {e}")

                # Capture mobile
                try:
                    mobile_page.goto(target_url, wait_until="networkidle", timeout=15000)
                    time.sleep(2)
                    mobile_page.screenshot(path=str(OUTPUT_DIR / f"{prefix}_mobile_390x844.png"), full_page=True)
                    mobile_page.screenshot(path=str(OUTPUT_DIR / f"{short_name}_mobile.png"), full_page=True)
                    print(f"Captured {prefix}_mobile")
                except Exception as e:
                    print(f"Error capturing mobile {prefix}: {e}")

            browser.close()
    finally:
        if proc:
            proc.terminate()
            proc.wait()


if __name__ == "__main__":
    capture()
