from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_boot():
    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=15)
    at.run(timeout=15)
    assert not at.exception
    assert len(at.title) > 0
    assert any("Dashboard" in t.value or "EduPulse" in t.value for t in at.title)
