from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def python_sources() -> list[Path]:
    return [ROOT / "Home.py", *sorted((ROOT / "pages").glob("*.py"))]


def test_application_python_files_parse() -> None:
    for path in python_sources():
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_requirements_are_deduplicated() -> None:
    lines = [
        line.strip().lower()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    names = [line.split(";", 1)[0].split("[", 1)[0].split("=")[0].strip() for line in lines]
    assert len(names) == len(set(names)), "requirements.txt contains duplicate packages"
    assert not any(name == "fpdf" for name in names), "Use fpdf2, not conflicting legacy fpdf"


def test_background_removal_uses_external_secret_and_bounded_timeout() -> None:
    source = (ROOT / "pages" / "BgForge.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert "REMOVE_BG_API_KEY" in source
    assert "StreamlitSecretNotFoundError" in source, (
        "Missing local Streamlit secrets must fall back to the environment safely"
    )
    assert "timeout=REQUEST_TIMEOUT_SECONDS" in source
    assert "AkeMEkvNP" not in source
    # Catch literal API-key assignments in the background remover module.
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"API_KEY", "REMOVE_BG_API_KEY"}:
                    assert not isinstance(node.value, ast.Constant), (
                        f"{target.id} must not be assigned a hard-coded literal"
                    )


def test_keep_awake_empty_commit_workflow_is_removed() -> None:
    assert not (ROOT / ".github" / "workflows" / "keep_awake.yml").exists()
