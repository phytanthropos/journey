from pathlib import Path

from pyquality.cli import fix_path, main, scan_path


def test_scan_reports_trailing_whitespace_and_long_line(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("value = 1    \n" + "x = '" + ("a" * 20) + "'\n", encoding="utf-8")

    issues = scan_path(file_path, max_line_length=10)

    codes = [issue.code for issue in issues]
    assert "E101" in codes
    assert "E501" in codes


def test_fix_removes_trailing_whitespace_and_adds_newline(tmp_path):
    file_path = tmp_path / "sample.py"
    file_path.write_text("def demo():\n\treturn 1   ", encoding="utf-8")

    changed = fix_path(file_path)

    assert changed is True
    assert file_path.read_text(encoding="utf-8") == "def demo():\n    return 1\n"


def test_main_fix_and_scan_roundtrip(tmp_path, capsys):
    file_path = tmp_path / "sample.py"
    file_path.write_text("x = 1\t\n", encoding="utf-8")

    assert main(["scan", str(file_path)]) == 1
    assert main(["fix", str(file_path)]) == 0
    assert main(["scan", str(file_path)]) == 0

    out = capsys.readouterr().out
    assert "No issues found." in out
