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

ROOT = Path(__file__).resolve().parents[1]
COV_XML = ROOT / "coverage.xml"
README = ROOT / "README.md"


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

    # You can customize the badge style/alt text here
    badge = f"[![coverage](https://img.shields.io/badge/coverage-{pct:.2f}%25-brightgreen)](./docs/coverage/index.html)"

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