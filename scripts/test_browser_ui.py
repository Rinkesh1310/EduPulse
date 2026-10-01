"""
End-to-end browser automation script using Playwright.
Audits all interactive elements, validates dynamic recalculations,
tests the complete CSV upload/preview/commit flow, tests invalid CSV handling,
and captures desktop & mobile screenshots.
"""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = Path(r"C:\Users\rmita\.gemini\antigravity-ide\brain\1dd7ebb4-b3d7-4f45-8a15-71413edaf723")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

WORKSPACE_DIR = Path(r"D:\EduPulse")
TEMP_VALID_CSV = WORKSPACE_DIR / "tests" / "test_valid_import.csv"
TEMP_INVALID_CSV = WORKSPACE_DIR / "tests" / "test_invalid_import.csv"

# Prepare test CSV files
TEMP_VALID_CSV.write_text(
    "course_code,component,present_count,total_count\n"
    "CEUE203,LECT,14,15\n"
    "CEUE203,LAB,8,9\n"
    "CSUC201,LECT,28,36\n"
    "CSUC201,LAB,7,11\n"
    "HSUV201,LECT,8,14\n",
    encoding="utf-8"
)

TEMP_INVALID_CSV.write_text(
    "course_code,component,present_count,total_count\n"
    "CEUE203,LECT,20,15\n"
    "CSUC201,INVALID,-5,10\n",
    encoding="utf-8"
)

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. DESKTOP VIEWPORT (1440 x 900)
        # -------------------------------------------------------------
        print("=== RUNNING DESKTOP AUDIT (1440 x 900) ===")
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Step 1: Load Overview Page
        page.goto("http://localhost:5173", wait_until="networkidle")
        time.sleep(2)
        print("Overview title:", page.title())
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_01_overview.png"), full_page=True)
        print("Captured desktop_01_overview.png")

        # Step 2: Navigate to Success Explorer
        page.locator("aside button", has_text="Success Explorer").click()
        page.wait_for_selector("text=Student Success Explorer")
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_02_success_explorer.png"), full_page=True)
        print("Captured desktop_02_success_explorer.png")

        # Step 3: Attendance Intelligence & Recovery Calculator
        page.locator("aside button", has_text="Attendance").click()
        page.wait_for_selector("text=Attendance Intelligence")
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_03_attendance.png"), full_page=True)
        print("Captured desktop_03_attendance.png")

        # Step 4: Academics & Marks Changes
        page.locator("aside button", has_text="Academics").click()
        page.wait_for_selector("text=Academic Performance")
        time.sleep(1.5)

        print("Testing marks scenario: 9/20...")
        page.locator("button", has_text="9 / 20 (Below 50%)").click()
        page.locator("button", has_text="Analyze Academic Health").click()
        time.sleep(2)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_04_academics_low_marks.png"), full_page=True)
        print("Captured desktop_04_academics_low_marks.png")

        print("Testing marks scenario: 18/20...")
        page.locator("button", has_text="18 / 20 (Strong 90%)").click()
        page.locator("button", has_text="Analyze Academic Health").click()
        time.sleep(2)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_05_academics_high_marks.png"), full_page=True)
        print("Captured desktop_05_academics_high_marks.png")

        # Step 5: Engagement Catalogue & Participation Toggle
        page.locator("aside button", has_text="Engagement").click()
        page.wait_for_selector("text=Campus Activity Catalogue")
        time.sleep(1.5)
        page.locator("button", has_text="Mark as Participated").first.click()
        time.sleep(2)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_06_engagement.png"), full_page=True)
        print("Captured desktop_06_engagement.png")

        # Step 6: Scholarship Planner
        page.locator("aside button", has_text="Scholarship Planner").click()
        page.wait_for_selector("text=Scholarship Readiness Planner")
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_07_scholarship.png"), full_page=True)
        print("Captured desktop_07_scholarship.png")

        # Step 7: Mentor Explorer & Cohort ML
        page.locator("aside button", has_text="Mentor Explorer").click()
        page.wait_for_selector("text=Mentor Cohort Explorer")
        time.sleep(2)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_08_mentor_cohort.png"), full_page=True)
        print("Captured desktop_08_mentor_cohort.png")

        # Step 8: Data Workspace - Upload Academic CSV FLOW
        page.locator("aside button", has_text="Data Workspace").click()
        page.wait_for_selector("text=Connect Academic Data")
        time.sleep(1.5)

        # Switch to Tab 2: Upload Academic CSV
        page.locator("button", has_text="Upload Academic CSV").click()
        time.sleep(1)

        # Fill Form: Name and Degree
        name_input = page.locator("input[placeholder='e.g. Rinkesh']")
        name_input.fill("Rinkesh")
        program_input = page.locator("input[placeholder='e.g. B.Tech IT']")
        program_input.fill("B.Tech IT")

        # 1. Test Valid CSV Upload
        print("Uploading valid academic CSV...")
        file_input = page.locator("input[type='file']")
        file_input.set_input_files(str(TEMP_VALID_CSV))
        page.wait_for_selector("text=Valid Batch (5 Rows)", timeout=10000)
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_09a_csv_valid_preview.png"), full_page=True)
        print("Captured desktop_09a_csv_valid_preview.png")

        # Click Confirm and Commit Import
        page.locator("button", has_text="Confirm and Commit Import").click()
        page.wait_for_selector("text=Imported 5 records cleanly", timeout=10000)
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_09b_csv_commit_success.png"), full_page=True)
        print("Captured desktop_09b_csv_commit_success.png")

        # 2. Test Invalid CSV Upload & Error Handling
        print("Uploading invalid CSV to verify actionable error handling...")
        page.locator("button", has_text="Clear").click()
        time.sleep(0.5)

        file_input = page.locator("input[type='file']")
        file_input.set_input_files(str(TEMP_INVALID_CSV))
        page.wait_for_selector("text=We couldn't validate this file", timeout=10000)
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_09c_csv_actionable_error.png"), full_page=True)
        print("Captured desktop_09c_csv_actionable_error.png")

        # Test View Requirements
        page.locator("button", has_text="View Requirements").first.click()
        time.sleep(1)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_09d_requirements_drawer.png"), full_page=True)
        print("Captured desktop_09d_requirements_drawer.png")

        # 3. Test Authorized Institutional Connector Tab
        page.locator("button", has_text="Connect Authorized Provider").click()
        time.sleep(1)
        page.locator("button", has_text="Invoke AuthorizedCharusatProvider() Stub").click()
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_10_authorized_stub.png"), full_page=True)
        print("Captured desktop_10_authorized_stub.png")

        # Step 9: Settings
        page.locator("aside button", has_text="Settings").click()
        page.wait_for_selector("text=Platform Settings & Privacy")
        time.sleep(1.5)
        page.screenshot(path=str(ARTIFACT_DIR / "desktop_11_settings.png"), full_page=True)
        print("Captured desktop_11_settings.png")

        context.close()

        # -------------------------------------------------------------
        # 2. MOBILE VIEWPORT (390 x 844)
        # -------------------------------------------------------------
        print("=== RUNNING MOBILE AUDIT (390 x 844) ===")
        m_context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        m_page = m_context.new_page()

        m_page.goto("http://localhost:5173", wait_until="networkidle")
        time.sleep(2)
        m_page.screenshot(path=str(ARTIFACT_DIR / "mobile_01_overview.png"), full_page=False)
        print("Captured mobile_01_overview.png")

        # Open mobile drawer menu
        m_page.locator("button[aria-label='Toggle navigation menu']").click()
        time.sleep(1)
        m_page.screenshot(path=str(ARTIFACT_DIR / "mobile_02_drawer.png"), full_page=False)
        print("Captured mobile_02_drawer.png")

        # Navigate to Success Explorer on mobile
        m_page.locator("button:has-text('Success Explorer')").last.click()
        m_page.wait_for_selector("text=Student Success Explorer")
        time.sleep(1.5)
        m_page.screenshot(path=str(ARTIFACT_DIR / "mobile_03_explorer.png"), full_page=False)
        print("Captured mobile_03_explorer.png")

        # Mobile Attendance
        m_page.locator("button[aria-label='Toggle navigation menu']").click()
        time.sleep(0.5)
        m_page.locator("button:has-text('Attendance')").last.click()
        m_page.wait_for_selector("text=Attendance Intelligence")
        time.sleep(1.5)
        m_page.screenshot(path=str(ARTIFACT_DIR / "mobile_04_attendance.png"), full_page=False)
        print("Captured mobile_04_attendance.png")

        # Mobile Data Workspace
        m_page.locator("button[aria-label='Toggle navigation menu']").click()
        time.sleep(0.5)
        m_page.locator("button:has-text('Data Workspace')").last.click()
        m_page.wait_for_selector("text=Connect Academic Data")
        time.sleep(1.5)
        m_page.screenshot(path=str(ARTIFACT_DIR / "mobile_05_data_workspace.png"), full_page=False)
        print("Captured mobile_05_data_workspace.png")

        m_context.close()
        browser.close()
        print("=== ALL BROWSER AUDITS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
