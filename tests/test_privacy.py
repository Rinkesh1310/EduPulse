from pathlib import Path

import pytest

from edupulse.domain import Student


def test_fictional_identity_defaults():
    student = Student(id="demo", externalStudentId="DEMO-S3-001")
    assert student.name == "Demo Student"
    assert student.externalStudentId == "DEMO-S3-001"
    assert student.program == "B.Tech IT (demo)"


def test_forbidden_strings_scan():
    forbidden_file = Path(__file__).parent / "local_forbidden_strings.txt"
    if not forbidden_file.exists():
        pytest.skip("tests/local_forbidden_strings.txt absent; skipping local forbidden strings scan.")

    forbidden_patterns = [
        line.strip() for line in forbidden_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if not forbidden_patterns:
        pytest.skip("No forbidden patterns specified in tests/local_forbidden_strings.txt.")

    repo_root = Path(__file__).parent.parent
    text_extensions = {".py", ".json", ".md", ".txt", ".csv", ".toml", ".yaml", ".yml"}

    violations = []
    for file_path in repo_root.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in text_extensions:
            # Skip git, venv, and the forbidden file itself
            rel_str = str(file_path.relative_to(repo_root))
            if any(part in rel_str for part in [".venv", ".git", "__pycache__", "local_forbidden_strings.txt"]):
                continue

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for pat in forbidden_patterns:
                    if pat.lower() in content.lower():
                        violations.append(f"Forbidden string '{pat}' detected in {rel_str}")
            except Exception:
                pass

    assert not violations, "Forbidden strings found in repository:\n" + "\n".join(violations)
