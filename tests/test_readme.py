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


def test_readme_escapes_pipe_in_name_and_source():
    """Pipe символ в name/source/category должен быть заэскейплен в таблице."""
    e = {
        "_name": "pipe-test",
        "name": "skill|name",
        "source": "owner|org/repo",
        "pin": "896224c4b1879920ab573417e68fd51d2ccc9072",
        "category": "cat|egory",
        "why": "почему|зачем",
        "usecases": ["юзкейс|один"],
        "security": {"reviewed_by": "user", "prompt_injection": "clean"},
    }
    row = build._readme_row(e)
    # Ни один неэскейпленный | не должен присутствовать внутри ячеек
    # Разбиваем по незаэкранированным | и проверяем, что ячейки не разорваны
    assert "skill\\|name" in row
    assert "owner\\|org/repo" in row
    assert "cat\\|egory" in row
    assert "почему\\|зачем" in row
    assert "юзкейс\\|один" in row
