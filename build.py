"""Сборщик каталога: entries/*.md -> README.md + .claude-plugin/marketplace.json."""
from __future__ import annotations

from pathlib import Path
import yaml


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
