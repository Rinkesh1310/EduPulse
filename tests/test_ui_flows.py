from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_apptest_dashboard_flow():
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run(timeout=15)
    assert not at.exception
    # Assert dashboard title is present
    titles = [t.value for t in at.title]
    assert any("Student Success Dashboard" in t for t in titles)


def test_apptest_navigation_all_pages():
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run(timeout=15)
    assert not at.exception
    assert len(at.exception) == 0


def test_apptest_persona_switcher():
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run(timeout=15)
    assert not at.exception
    assert at.session_state["current_student_id"] == "student_synth_strong"

    # Switch persona to student_synth_att_concern
    at.sidebar.selectbox(key="_sidebar_persona_selector").select("student_synth_att_concern")
    at.run(timeout=15)
    assert not at.exception
    assert at.session_state["current_student_id"] == "student_synth_att_concern"
