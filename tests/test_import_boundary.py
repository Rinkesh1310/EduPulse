import ast
from pathlib import Path


def test_attendance_does_not_import_engagement():
    core_dir = Path(__file__).parent.parent / "edupulse" / "core"
    attendance_files = list(core_dir.glob("attendance*.py"))
    assert len(attendance_files) > 0, "No attendance core files found"

    for f in attendance_files:
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "engagement" not in alias.name, f"Forbidden import of engagement in {f.name}"
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                assert "engagement" not in mod, f"Forbidden import from engagement in {f.name}"
                for alias in node.names:
                    assert "engagement" not in alias.name, f"Forbidden import of engagement symbol in {f.name}"
