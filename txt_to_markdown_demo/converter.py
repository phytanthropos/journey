#!/usr/bin/env python3
"""txt_to_markdown_demo/converter.py

A compact demo converter that turns a plain-text note into a Markdown file
using predictable, heuristic-based transformations.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List

BOLD_CUES = {
    "IMPORTANT",
    "BOLD",
    "NOTE",
    "WARNING",
    "TIP",
    "TODO",
}

LIST_BULLET_RE = re.compile(r"^(\s*)([-*•])\s+(.*)$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
ALL_CAPS_RE = re.compile(r"^[A-Z0-9][A-Z0-9 _/&'\-]{2,}$")
TITLE_CANDIDATE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ,:'\-/()]{2,}$")
INDENTED_CODE_RE = re.compile(r"^(?:\t| {4,})\S")


def collapse_blank_lines(lines: Iterable[str]) -> List[str]:
    out: List[str] = []
    previous_blank = False
    for line in lines:
        if line.strip():
            out.append(line.rstrip())
            previous_blank = False
        else:
            if not previous_blank:
                out.append("")
                previous_blank = True
    while out and out[0] == "":
        out.pop(0)
    while out and out[-1] == "":
        out.pop()
    return out


def is_title_candidate(line: str) -> bool:
    text = line.strip()
    if not text:
        return False
    if len(text) > 70:
        return False
    if text.endswith((".", "!", "?", ";")):
        return False
    if text.startswith(("-", "*", "•", ">")):
        return False
    if re.match(r"^\d+[.)]\s+", text):
        return False
    return bool(TITLE_CANDIDATE_RE.match(text) or ALL_CAPS_RE.match(text))


def format_heading(text: str, level: int) -> str:
    cleaned = text.strip().rstrip(":").strip()
    return f"{'#' * level} {cleaned}"


def emphasize_cue(line: str) -> str:
    match = re.match(r"^([A-Z][A-Z0-9 _/-]{1,24}):\s*(.*)$", line)
    if not match:
        return line
    cue, rest = match.groups()
    cue = cue.strip()
    if cue in BOLD_CUES:
        return f"**{cue}:** {rest}".rstrip()
    return line


def convert_lines(lines: List[str]) -> List[str]:
    result: List[str] = []
    in_code_block = False
    used_title = False

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if in_code_block:
            if stripped == "```":
                result.append("```")
                in_code_block = False
            elif INDENTED_CODE_RE.match(line):
                result.append(line[4:] if line.startswith("    ") else line.lstrip("\t"))
            elif not stripped:
                result.append("")
            else:
                result.append("```")
                in_code_block = False
        if in_code_block:
            continue

        if not stripped:
            result.append("")
            continue

        if stripped == "```":
            result.append("```")
            in_code_block = not in_code_block
            continue

        if INDENTED_CODE_RE.match(line):
            result.append("```")
            result.append(line[4:] if line.startswith("    ") else line.lstrip("\t"))
            in_code_block = True
            continue

        if stripped.startswith(">"):
            result.append(stripped)
            continue

        bullet_match = LIST_BULLET_RE.match(line)
        if bullet_match:
            indent, _bullet, content = bullet_match.groups()
            result.append(f"{indent}- {content.strip()}")
            continue

        ordered_match = ORDERED_RE.match(line)
        if ordered_match:
            indent, number, content = ordered_match.groups()
            result.append(f"{indent}{number}. {content.strip()}")
            continue

        if not used_title and is_title_candidate(stripped):
            result.append(format_heading(stripped, 1))
            used_title = True
            continue

        if stripped.endswith(":") and len(stripped) <= 80:
            result.append(format_heading(stripped, 2))
            continue

        if ALL_CAPS_RE.match(stripped) and len(stripped) <= 80:
            result.append(format_heading(stripped, 2))
            continue

        result.append(emphasize_cue(line.rstrip()))

    if in_code_block:
        result.append("```")

    return collapse_blank_lines(result)


def convert_text(text: str) -> str:
    lines = text.splitlines()
    converted = convert_lines(lines)
    return "\n".join(converted).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a plain-text file into a lightly formatted Markdown file."
    )
    parser.add_argument("input", help="Path to the source .txt file")
    parser.add_argument(
        "output",
        nargs="?",
        help="Optional path to the output .md file (defaults to same basename)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_path = Path(args.output) if args.output else input_path.with_suffix(".md")

    source = input_path.read_text(encoding="utf-8")
    markdown = convert_text(source)
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Wrote Markdown to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
