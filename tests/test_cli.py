import json
from pathlib import Path
import build

ENTRY = """---
name: superpowers
source: obra/superpowers
pin: 896224c4b1879920ab573417e68fd51d2ccc9072
category: development
why: "Методология разработки"
usecases:
  - "Нужна дисциплина TDD"
security:
  reviewed_by: hahpiez4-source
  prompt_injection: clean
---
# Superpowers
"""


def setup_repo(tmp_path):
    (tmp_path / "entries").mkdir()
    (tmp_path / "entries" / "superpowers.md").write_text(ENTRY, encoding="utf-8")
    (tmp_path / "entries" / "_template.md").write_text("---\nname: _t\n---\n", encoding="utf-8")
    (tmp_path / ".claude-plugin").mkdir()
    return tmp_path


def test_run_writes_files(tmp_path):
    root = setup_repo(tmp_path)
    rc = build.run(root, check=False)
    assert rc == 0
    mp = json.loads((root / ".claude-plugin" / "marketplace.json").read_text("utf-8"))
    assert mp["plugins"][0]["name"] == "superpowers"
    assert "claude plugin marketplace add" in (root / "README.md").read_text("utf-8")


def test_template_file_skipped(tmp_path):
    root = setup_repo(tmp_path)
    build.run(root, check=False)
    mp = json.loads((root / ".claude-plugin" / "marketplace.json").read_text("utf-8"))
    assert [p["name"] for p in mp["plugins"]] == ["superpowers"]


def test_check_passes_after_build_then_detects_drift(tmp_path):
    root = setup_repo(tmp_path)
    build.run(root, check=False)
    assert build.run(root, check=True) == 0          # совпадает
    (root / "README.md").write_text("изменено руками\n", encoding="utf-8")
    assert build.run(root, check=True) == 1          # рассинхрон пойман
