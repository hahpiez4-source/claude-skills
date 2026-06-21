import build


def entry():
    return {
        "_name": "superpowers", "name": "superpowers", "source": "obra/superpowers",
        "pin": "896224c4b1879920ab573417e68fd51d2ccc9072",
        "category": "development", "why": "Методология разработки",
        "usecases": ["Нужна дисциплина TDD"],
        "security": {"reviewed_by": "hahpiez4-source", "prompt_injection": "clean"},
    }


def test_readme_has_install_command():
    md = build.build_readme([entry()])
    assert "claude plugin marketplace add hahpiez4-source/claude-skills" in md


def test_readme_lists_entry_with_link():
    md = build.build_readme([entry()])
    assert "superpowers" in md
    assert "https://github.com/obra/superpowers" in md
    assert "Методология разработки" in md
