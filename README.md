# pyquality

`pyquality` is a small Python CLI that scans source files for a few common code-quality issues and can fix the simple ones automatically.

## Features

- Scan files and directories recursively
- Accept glob patterns like `src/**/*.py`
- Detect:
  - trailing whitespace
  - tab-based indentation
  - lines longer than a configurable limit
  - missing final newline
- Optionally fix trailing whitespace, tab indentation, and missing final newline

## Usage

```bash
pyquality scan path/to/file.py
pyquality scan src/ --max-line-length 100
pyquality fix path/to/file.py
pyquality fix src/**/*.py
```

If you omit the subcommand, `scan` is used by default.

## Exit codes

- `0` — no issues found
- `1` — issues were found
- `2` — command-line or file handling error

## Development

```bash
python -m pytest
```
