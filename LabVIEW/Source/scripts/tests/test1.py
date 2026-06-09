import subprocess
import sys
from pathlib import Path

import pytest

from scripts import validate_paths as vp


def test_test_segment_cases():
    assert vp.test_segment(".hidden")
    assert vp.test_segment(".git")
    assert vp.test_segment("Node1")
    assert not vp.test_segment("node")
    assert not vp.test_segment("123Start")
    assert vp.test_segment("A123")


def test_load_paths_file(tmp_path):
    p = tmp_path / "files.txt"
    p.write_text("src/MyFile.cs\n\nTests/TestA.cs\n")
    got = vp.load_paths_file(str(p))
    assert got == ["src/MyFile.cs", "Tests/TestA.cs"]


def test_load_paths_file_missing():
    with pytest.raises(SystemExit) as exc:
        vp.load_paths_file("no-such-file.txt")
    assert exc.value.code == 2


def test_parse_path_config_sections(tmp_path):
    cfg = tmp_path / "PathConfigs.ini"
    cfg.write_text(
        """
[GlobalIncludePaths]
Src
Tests

[GlobalExcludePaths]
node_modules
"""
    )
    inc, exc = vp.parse_path_config(str(cfg))
    assert "Src" in inc
    assert "Tests" in inc
    assert "node_modules" in exc


def test_in_scope_include_exclude():
    inc = ["Src/Lib"]
    exc = ["Src/Lib/Generated"]
    assert vp.in_scope("Src/Lib/File.cs", inc, exc)
    assert not vp.in_scope("Src/Other/File.cs", inc, exc)
    assert not vp.in_scope("Src/Lib/Generated/Gen.cs", inc, exc)


def test_scan_repo_files(tmp_path):
    (tmp_path / "A").mkdir()
    (tmp_path / "A" / "One.txt").write_text("x")
    (tmp_path / "B").mkdir()
    (tmp_path / "B" / "Two.txt").write_text("y")
    files = vp.scan_repo_files(str(tmp_path))
    rels = {Path(f).as_posix() for f in files}
    assert "A/One.txt" in rels
    assert "B/Two.txt" in rels


def run_script(script_path, cwd, paths_file, expect_code=0):
    proc = subprocess.run(
        [sys.executable, str(script_path), "--paths-file", str(paths_file)],
        cwd=str(cwd),
    )
    assert proc.returncode == expect_code


def test_end_to_end_valid_and_invalid(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    scripts_dir = Path(__file__).resolve().parents[1] / "src" / "scripts"
    script = scripts_dir / "validate_paths.py"

    # valid file
    (repo / "Src").mkdir()
    (repo / "Src" / "GoodFile.cs").write_text("x")
    pf = repo / "changed-files.txt"
    pf.write_text("Src/GoodFile.cs\n")
    run_script(script, repo, pf, expect_code=0)

    # invalid file (lowercase start)
    (repo / "Src" / "badfile.cs").write_text("x")
    pf.write_text("Src/badfile.cs\n")
    run_script(script, repo, pf, expect_code=1)