import build


def entry():
    return {
        "_name": "superpowers", "name": "superpowers", "source": "obra/superpowers",
        "pin": "896224c4b1879920ab573417e68fd51d2ccc9072",
        "category": "development", "why": "Методология разработки",
        "security": {"reviewed_by": "hahpiez4-source", "prompt_injection": "clean"},
    }


def test_marketplace_top_level():
    mp = build.build_marketplace([entry()])
    assert mp["name"] == "claude-skills"
    assert mp["owner"]["name"] == "hahpiez4-source"
    assert len(mp["plugins"]) == 1


def test_plugin_entry_shape():
    p = build.build_marketplace([entry()])["plugins"][0]
    assert p["name"] == "superpowers"
    assert p["description"] == "Методология разработки"
    assert p["category"] == "development"
    assert p["homepage"] == "https://github.com/obra/superpowers"
    assert p["source"] == {
        "source": "url",
        "url": "https://github.com/obra/superpowers.git",
        "sha": "896224c4b1879920ab573417e68fd51d2ccc9072",
    }


def test_plugins_sorted_by_name():
    a = entry(); a["name"] = "zzz"; a["source"] = "x/zzz"
    b = entry(); b["name"] = "aaa"; b["source"] = "x/aaa"
    names = [p["name"] for p in build.build_marketplace([a, b])["plugins"]]
    assert names == ["aaa", "zzz"]
