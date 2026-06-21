"""Сборщик каталога: entries/*.md -> README.md + .claude-plugin/marketplace.json."""
from __future__ import annotations

from pathlib import Path
import re
import yaml
import json
import sys
import argparse

_SOURCE_RE = re.compile(r"^[\w.-]+/[\w.-]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def _esc(text: str) -> str:
    """Экранировать символ | для безопасного использования в ячейках Markdown-таблицы."""
    return str(text).replace("|", "\\|")


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
    if sec.get("prompt_injection") != "clean":
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


README_HEADER = """# claude-skills

Каталог проверенных скиллов/плагинов для Claude Code. Здесь только **ссылки на оригиналы**, не копии кода.

## Установка

```bash
claude plugin marketplace add hahpiez4-source/claude-skills
claude plugin install <имя-скилла>@claude-skills
```

## Каталог

<!-- Таблица сгенерирована build.py. Руками не редактировать. -->

| Скилл | Категория | Зачем | Юзкейсы | Проверка | Источник |
|---|---|---|---|---|---|
"""


def _readme_row(e: dict) -> str:
    use = "; ".join(e.get("usecases", []) or [])
    sec = "✅ clean" if (e.get("security") or {}).get("prompt_injection") == "clean" else "⚠️"
    src = e["source"]
    link = f"[{_esc(src)}](https://github.com/{_esc(src)})"
    return f"| {_esc(e['name'])} | {_esc(e.get('category', 'other'))} | {_esc(e['why'])} | {_esc(use)} | {sec} | {link} |"


def build_readme(entries: list) -> str:
    rows = [
        _readme_row(e)
        for e in sorted(entries, key=lambda e: (e.get("category", "other"), e["name"]))
    ]
    return README_HEADER + "\n".join(rows) + "\n"


def load_entries(entries_dir: Path) -> list:
    """Парсит и валидирует все entries/*.md (кроме _*); бросает SystemExit с ошибками."""
    entries, errors, seen = [], [], set()
    for p in sorted(Path(entries_dir).glob("*.md")):
        if p.name.startswith("_"):
            continue
        e = parse_entry(p)
        errs = validate_entry(e, seen)
        if errs:
            errors.extend(errs)
        else:
            entries.append(e)
    if errors:
        raise SystemExit("Ошибки валидации карточек:\n  - " + "\n  - ".join(errors))
    return entries


def run(root, check: bool = False) -> int:
    """Генерирует контент; при check=False пишет файлы (returns 0); при check=True сравнивает с диском."""
    root = Path(root)
    entries = load_entries(root / "entries")
    mp_text = json.dumps(build_marketplace(entries), ensure_ascii=False, indent=2) + "\n"
    readme_text = build_readme(entries)
    targets = {
        root / ".claude-plugin" / "marketplace.json": mp_text,
        root / "README.md": readme_text,
    }
    if check:
        drift = [str(path) for path, text in targets.items()
                 if not path.exists() or path.read_text("utf-8") != text]
        if drift:
            print("Рассинхрон (запусти build.py без --check):\n  " + "\n  ".join(drift))
            return 1
        return 0
    for path, text in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"Записал {path}")
    return 0


def main(argv=None) -> int:
    """CLI-обёртка с поддержкой --check."""
    ap = argparse.ArgumentParser(description="Сборщик каталога claude-skills")
    ap.add_argument("--check", action="store_true",
                    help="проверить актуальность сгенерированных файлов без записи")
    args = ap.parse_args(argv)
    return run(Path(__file__).parent, check=args.check)


if __name__ == "__main__":
    sys.exit(main())
