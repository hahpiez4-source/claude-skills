"""Сборщик каталога: entries/*.md -> README.md + .claude-plugin/marketplace.json."""
from __future__ import annotations

from pathlib import Path
import re
import yaml

_SOURCE_RE = re.compile(r"^[\w.-]+/[\w.-]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def parse_entry(path) -> dict:
    """Прочитать карточку: вернуть dict frontmatter + ключ _name (имя файла)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path.name}: нет YAML-frontmatter (файл должен начинаться с '---')")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: frontmatter не закрыт вторым '---'")
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: frontmatter должен быть набором полей")
    data["_name"] = path.stem
    return data


def validate_entry(entry: dict, seen_names: set) -> list:
    """Валидировать карточку, мутировать seen_names, вернуть список ошибок."""
    name = entry.get("_name", "?")
    errs = []

    def need(field):
        if not entry.get(field):
            errs.append(f"{name}: отсутствует обязательное поле '{field}'")

    for f in ("name", "source", "pin", "why"):
        need(f)

    src = entry.get("source", "")
    if src and not _SOURCE_RE.match(str(src)):
        errs.append(f"{name}: source должен быть вида 'owner/repo', получено '{src}'")

    pin = str(entry.get("pin", ""))
    if pin and not _SHA_RE.match(pin):
        errs.append(f"{name}: pin должен быть коммитом (7–40 hex), а не веткой: '{pin}'")

    sec = entry.get("security") or {}
    if not isinstance(sec, dict) or not sec.get("reviewed_by"):
        errs.append(f"{name}: отсутствует security.reviewed_by")
    if (sec.get("prompt_injection") if isinstance(sec, dict) else None) != "clean":
        errs.append(f"{name}: security.prompt_injection должен быть 'clean' для попадания в каталог")

    nm = entry.get("name")
    if nm:
        if nm in seen_names:
            errs.append(f"{name}: дубликат имени '{nm}'")
        seen_names.add(nm)

    return errs


def _plugin_obj(entry: dict) -> dict:
    """Преобразовать entry в объект плагина для marketplace.json."""
    owner_repo = entry["source"]
    return {
        "name": entry["name"],
        "description": entry["why"],
        "source": {
            "source": "url",
            "url": f"https://github.com/{owner_repo}.git",
            "sha": str(entry["pin"]),
        },
        "category": entry.get("category", "other"),
        "homepage": f"https://github.com/{owner_repo}",
    }


def build_marketplace(entries: list) -> dict:
    """Собрать полный объект marketplace.json из списка карточек."""
    plugins = [_plugin_obj(e) for e in sorted(entries, key=lambda e: e["name"])]
    return {
        "name": "claude-skills",
        "description": "Каталог проверенных скиллов Claude Code (ссылки, не копии).",
        "owner": {"name": "hahpiez4-source"},
        "plugins": plugins,
    }
