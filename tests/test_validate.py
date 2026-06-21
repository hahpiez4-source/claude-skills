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
