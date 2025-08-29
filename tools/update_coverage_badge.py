#!/usr/bin/env python3
"""
Update README coverage badge, **always** regenerating coverage.xml by running pytest first.
Requires: pytest + pytest-cov.
"""

from __future__ import annotations

import re
import sys
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import os

DEFAULT_PAGES_BASE = "https://hidekihokuto.github.io/algolib"

def _guess_pages_base_url() -> str:
    """Best-effort to derive GitHub Pages base URL.

    Priority:
    1) GHPAGES_BASE_URL env var (if set)
    2) Parse `git config --get remote.origin.url`
    3) DEFAULT_PAGES_BASE fallback
    """
    base = os.environ.get("GHPAGES_BASE_URL", "").strip()
    if base:
        return base.rstrip("/")
    try:
        out = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], cwd=ROOT, text=True
        ).strip()
        owner_repo = ""
        if out.startswith("git@") and ":" in out:
            # e.g. git@github.com:Owner/Repo.git
            owner_repo = out.split(":", 1)[1]
        elif out.startswith("http://") or out.startswith("https://"):
            # e.g. https://github.com/Owner/Repo.git
            parts = out.split("/")
            owner_repo = "/".join(parts[-2:])
        if owner_repo.endswith(".git"):
            owner_repo = owner_repo[:-4]
        if "/" in owner_repo:
            owner, repo = owner_repo.split("/", 1)
            return f"https://{owner.lower()}.github.io/{repo}"
    except Exception:
        pass
    return DEFAULT_PAGES_BASE

ROOT = Path(__file__).resolve().parents[1]
COV_XML = ROOT / "coverage.xml"
README = ROOT / "README.md"
SITE_COV_DIR = ROOT / "docs" / "build" / "html" / "coverage"


def run_pytest_cov() -> int:
    """Run pytest to (re)create coverage.xml.

    Returns
    -------
    int
        The pytest return code (0 if tests passed). We don't bail on failures;
        we still attempt to update the README with whatever coverage was
        produced (if any).
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src/algolib",
        "--cov-report=xml:coverage.xml",
        f"--cov-report=html:{SITE_COV_DIR.as_posix()}",
        "-q",
    ]
    print("🧪 Running pytest to refresh coverage.xml...", flush=True)
    try:
        proc = subprocess.run(cmd, cwd=ROOT)
        return proc.returncode
    except FileNotFoundError:
        print("[warn] pytest not found. Please install pytest and pytest-cov.", file=sys.stderr)
        return 127



def run_pytest_cov() -> int:
    """Run pytest to (re)create coverage.xml.

    Returns
    -------
    int
        The pytest return code (0 if tests passed). We don't bail on failures;
        we still attempt to update the README with whatever coverage was
        produced (if any).
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src/algolib",
        "--cov-report=xml:coverage.xml",
        "-q",
    ]
    print("🧪 Running pytest to refresh coverage.xml...", flush=True)
    try:
        proc = subprocess.run(cmd, cwd=ROOT)
        return proc.returncode
    except FileNotFoundError:
        print("[warn] pytest not found. Please install pytest and pytest-cov.", file=sys.stderr)
        return 127


def read_coverage_percent(xml_path: Path) -> float:
    if not xml_path.exists():
        print(f"[warn] {xml_path} not found. Run pytest with --cov-report=xml first.", file=sys.stderr)
        sys.exit(2)
    root = ET.parse(xml_path).getroot()
    # coverage.xml (coverage.py) has 'line-rate' at root
    line_rate = root.get("line-rate")
    if line_rate is None:
        raise RuntimeError("line-rate not found in coverage.xml")
    pct = round(float(line_rate) * 100.0, 2)
    return pct


def update_readme(pct: float) -> None:
    if not README.exists():
        print("[warn] README.md not found.", file=sys.stderr)
        sys.exit(3)

    base = _guess_pages_base_url()
    link = f"{base}/coverage/"

    # Always link to the published site; do not embed local absolute paths into README
    badge = f"[![coverage](https://img.shields.io/badge/coverage-{pct:.2f}%25-brightgreen)]({link})"
    
    block = (
        "<!-- coverage-badge:start -->\n"
        f"{badge}\n"
        f"Coverage: {pct:.2f}%\n"
        "<!-- coverage-badge:end -->"
    )

    txt = README.read_text(encoding="utf-8")
    pattern = r"<!-- coverage-badge:start -->.*?<!-- coverage-badge:end -->"
    if re.search(pattern, txt, flags=re.S):
        new = re.sub(pattern, block, txt, flags=re.S)
    else:
        # If no block exists, append at the end of first heading section
        new = txt.strip() + "\n\n" + block + "\n"

    if new != txt:
        README.write_text(new, encoding="utf-8")
        print(f"[ok] README updated to {pct:.2f}%")
    else:
        print("[ok] README already up-to-date")


def main() -> None:
    rc = run_pytest_cov()
    if rc != 0:
        print(f"[warn] pytest exited with code {rc}; attempting to update README from existing coverage.xml.", file=sys.stderr)
    pct = read_coverage_percent(COV_XML)
    print(f"📈 Current coverage: {pct:.2f}%")
    update_readme(pct)


if __name__ == "__main__":
    main()