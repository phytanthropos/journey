from __future__ import annotations

import argparse
import glob
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Issue:
    path: Path
    line: int
    column: int
    code: str
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}:{self.column}: {self.code} {self.message}"


def _is_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def _iter_files(patterns: Iterable[str]) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()

    for raw in patterns:
        matches = glob.glob(raw, recursive=True)
        if matches:
            candidates = [Path(match) for match in matches]
        else:
            candidates = [Path(raw)]

        for candidate in candidates:
            if not candidate.exists():
                continue
            if candidate.is_dir():
                for root, dirs, files in os.walk(candidate):
                    root_path = Path(root)
                    dirs[:] = [d for d in dirs if not d.startswith(".")]
                    for filename in files:
                        file_path = root_path / filename
                        if _is_hidden(file_path):
                            continue
                        if file_path.suffix != ".py":
                            continue
                        if file_path not in seen:
                            seen.add(file_path)
                            found.append(file_path)
            else:
                if _is_hidden(candidate):
                    continue
                if candidate.suffix != ".py":
                    continue
                if candidate not in seen:
                    seen.add(candidate)
                    found.append(candidate)

    return found


def scan_path(path: Path, max_line_length: int = 88) -> list[Issue]:
    issues: list[Issue] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Issue(path, 0, 0, "E900", f"cannot read file: {exc.strerror or exc}")]

    lines = text.splitlines(keepends=True)
    for line_no, line in enumerate(lines, start=1):
        stripped_newline = line.rstrip("\n")
        if stripped_newline.rstrip("\r").endswith((" ", "\t")):
            column = len(stripped_newline.rstrip("\r"))
            issues.append(Issue(path, line_no, column, "E101", "trailing whitespace"))
        if len(stripped_newline.rstrip("\r")) > max_line_length:
            issues.append(
                Issue(
                    path,
                    line_no,
                    max_line_length + 1,
                    "E501",
                    f"line too long ({len(stripped_newline.rstrip(chr(13)))} > {max_line_length} characters)",
                )
            )
        leading = stripped_newline.lstrip(" \t\r")
        prefix = stripped_newline[: len(stripped_newline) - len(leading)]
        if "\t" in prefix:
            issues.append(Issue(path, line_no, 1, "E102", "tab indentation"))

    if text and not text.endswith(("\n", "\r\n")):
        issues.append(Issue(path, len(lines), len(lines[-1]) + 1 if lines else 1, "E104", "missing final newline"))

    return issues


def fix_path(path: Path) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except OSError:
        return False

    lines = original.splitlines()
    fixed_lines: list[str] = []
    for line in lines:
        leading_len = len(line) - len(line.lstrip(" \t"))
        leading = line[:leading_len].replace("\t", "    ")
        body = line[leading_len:].rstrip(" \t")
        fixed_lines.append(leading + body)

    fixed = "\n".join(fixed_lines)
    if original.endswith("\n") or original.endswith("\r\n"):
        fixed += "\n"
    else:
        fixed += "\n"

    if fixed != original:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pyquality", description="Scan and fix simple Python code-quality issues.")
    parser.add_argument("command", nargs="?", choices=["scan", "fix"], default="scan")
    parser.add_argument("paths", nargs="*", help="Files, directories, or glob patterns to inspect")
    parser.add_argument("--max-line-length", type=int, default=88)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    paths = args.paths or ["."]
    files = _iter_files(paths)

    if not files:
        print("No matching Python files found.", file=sys.stderr)
        return 2

    if args.command == "fix":
        changed = False
        for path in files:
            changed = fix_path(path) or changed
        return 0 if changed else 0

    issues: list[Issue] = []
    for path in files:
        issues.extend(scan_path(path, max_line_length=args.max_line_length))

    if issues:
        for issue in issues:
            print(issue.format())
        return 1

    print("No issues found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
