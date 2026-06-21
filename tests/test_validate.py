import build


def good():
    return {
        "_name": "superpowers",
        "name": "superpowers",
        "source": "obra/superpowers",
        "pin": "896224c4b1879920ab573417e68fd51d2ccc9072",
        "why": "Методология разработки",
        "security": {"reviewed_by": "hahpiez4-source", "prompt_injection": "clean"},
    }


def test_valid_entry_has_no_errors():
    assert build.validate_entry(good(), set()) == []


def test_missing_required_field_reported():
    e = good(); del e["why"]
    errs = build.validate_entry(e, set())
    assert any("why" in x for x in errs)


def test_pin_must_be_commit_not_branch():
    e = good(); e["pin"] = "main"
    errs = build.validate_entry(e, set())
    assert any("pin" in x for x in errs)


def test_flagged_injection_is_error():
    e = good(); e["security"]["prompt_injection"] = "flagged"
    errs = build.validate_entry(e, set())
    assert any("prompt_injection" in x for x in errs)


def test_duplicate_name_reported():
    seen = set()
    build.validate_entry(good(), seen)
    errs = build.validate_entry(good(), seen)
    assert any("дубликат" in x.lower() or "duplicate" in x.lower() for x in errs)


def test_template_default_prompt_injection_fails_validation():
    """Дефолтное значение из _template.md должно НЕ проходить валидацию."""
    from pathlib import Path
    import yaml

    template_path = Path(__file__).parent.parent / "entries" / "_template.md"
    text = template_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1]) or {}

    # Убеждаемся, что дефолт содержит sentinel-строку
    sec = fm.get("security") or {}
    assert sec.get("prompt_injection") == "TODO-set-clean-only-after-review", (
        "Шаблон должен иметь sentinel-значение prompt_injection, "
        "а не 'clean', чтобы билд падал при копировании без правок"
    )

    # Убеждаемся, что такая запись НЕ проходит validate_entry
    fm["_name"] = "_template"
    errs = build.validate_entry(fm, set())
    assert any("prompt_injection" in e for e in errs), (
        "validate_entry должен вернуть ошибку для sentinel-значения prompt_injection"
    )
