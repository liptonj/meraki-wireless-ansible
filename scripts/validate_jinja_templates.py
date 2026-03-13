#!/usr/bin/env python3
"""
Validate Jinja2 template syntax used in this repository.

This performs a fast parse check on all *.j2 files under role and top-level
template directories so syntax errors are caught before playbook execution.
"""

from __future__ import annotations

from pathlib import Path
import sys

from jinja2 import Environment, TemplateSyntaxError


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_GLOBS = (
    "roles/*/templates/**/*.j2",
    "templates/**/*.j2",
)


def find_templates() -> list[Path]:
    files: set[Path] = set()
    for pattern in TEMPLATE_GLOBS:
        files.update(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(files)


def main() -> int:
    templates = find_templates()
    if not templates:
        print("No Jinja2 templates found.")
        return 0

    env = Environment(
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
    )

    failures: list[tuple[Path, TemplateSyntaxError]] = []
    for template_path in templates:
        source = template_path.read_text(encoding="utf-8")
        try:
            env.parse(source)
        except TemplateSyntaxError as exc:
            failures.append((template_path, exc))

    if failures:
        print("Jinja2 template validation failed:")
        for path, error in failures:
            rel = path.relative_to(ROOT)
            print(f"- {rel}:{error.lineno}: {error.message}")
        return 1

    print(f"Validated {len(templates)} Jinja2 template(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
