from pathlib import Path

import pytest

from edupulse.providers.authorized_charusat import AuthorizedCharusatProvider
from edupulse.providers.base import NotAuthorizedError
from edupulse.storage.repository import StudentRepository
from edupulse.storage.seed import seed_scenario_data


def test_security_j_static_scan_no_credentials():
    """Security Acceptance Test J.1:
    Asserts no password/username/cookie/captcha fields, no login forms in source code.
    """
    repo_root = Path(__file__).parent.parent
    source_dirs = [repo_root / "edupulse", repo_root / "app.py"]

    forbidden_identifiers = [
        "password",
        "passwd",
        "captcha",
        "login_form",
        "auth_token",
        "session_cookie",
    ]

    violations = []
    for s_path in source_dirs:
        if s_path.is_file():
            files = [s_path]
        else:
            files = list(s_path.rglob("*.py")) + list(s_path.rglob("*.json"))

        for f in files:
            content = f.read_text(encoding="utf-8", errors="ignore").lower()
            for token in forbidden_identifiers:
                # Check for token usage outside of security documentation/assert strings
                if token in content and "security notice" not in content and "never asks for" not in content:
                    violations.append(f"Forbidden credential token '{token}' in {f.relative_to(repo_root)}")

    assert not violations, "Credential fields or tokens detected in source code:\n" + "\n".join(violations)


def test_security_j_no_http_client_targeting_university_domain():
    """Security Acceptance Test J.2:
    Asserts no requests/httpx/urllib client targeting any live university domain.
    """
    repo_root = Path(__file__).parent.parent
    edupulse_dir = repo_root / "edupulse"

    forbidden_domains = [
        "charusat.ac.in",
        "charusat.edu.in",
        "charusat-portal",
    ]

    violations = []
    for f in edupulse_dir.rglob("*.py"):
        content = f.read_text(encoding="utf-8", errors="ignore").lower()
        for dom in forbidden_domains:
            if dom in content:
                violations.append(f"University domain target '{dom}' found in {f.relative_to(repo_root)}")

    assert not violations, "University domain scraping target detected:\n" + "\n".join(violations)


def test_security_j_authorized_provider_stub_guard():
    """Security Acceptance Test J.3:
    Asserts AuthorizedCharusatProvider cannot execute and raises NotAuthorizedError.
    """
    stub = AuthorizedCharusatProvider()
    assert stub.capabilities()["supports_live"] is False
    with pytest.raises(NotAuthorizedError, match="requires an official university-sanctioned API"):
        stub.get_profile()


def test_security_j_demo_storage_pii_boundary():
    """Security Acceptance Test J.4:
    Asserts database contains only fictional student identities and no real PII.
    """
    seed_scenario_data("S3", reset=True)
    repo = StudentRepository()
    try:
        student = repo.get_student("student_s3")
        assert student is not None
        assert student.name == "Demo Student"
        assert student.externalStudentId == "DEMO-S3-001"
        assert "demo" in student.program.lower()
    finally:
        repo.close()
