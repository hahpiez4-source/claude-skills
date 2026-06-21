from pathlib import Path
import pytest
import build


def write(tmp_path, text):
    p = tmp_path / "superpowers.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_parse_reads_frontmatter_fields(tmp_path):
    p = write(tmp_path, """---
name: superpowers
source: obra/superpowers
pin: 896224c4b1879920ab573417e68fd51d2ccc9072
why: "Методология разработки"
security:
  reviewed_by: hahpiez4-source
  prompt_injection: clean
---

# Superpowers
тело
""")
    entry = build.parse_entry(p)
    assert entry["name"] == "superpowers"
    assert entry["source"] == "obra/superpowers"
    assert entry["security"]["prompt_injection"] == "clean"
    assert entry["_name"] == "superpowers"


def test_parse_raises_without_frontmatter(tmp_path):
    p = write(tmp_path, "просто текст без frontmatter")
    with pytest.raises(ValueError):
        build.parse_entry(p)
