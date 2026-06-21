# Claude Skills Catalog — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Публичный репозиторий-каталог скиллов Claude Code, где карточки в `entries/*.md` автоматически собираются в читаемый `README.md` и устанавливаемый `.claude-plugin/marketplace.json` (ссылки на внешние репо, не копии).

**Architecture:** Источник правды — markdown-карточки с YAML-frontmatter в `entries/`. Скрипт `build.py` парсит карточки, валидирует обязательные поля, генерирует `marketplace.json` и `README.md`. Генерируемые файлы руками не правятся; `build.py --check` подтверждает их актуальность.

**Tech Stack:** Python 3.9+, PyYAML (парсинг frontmatter), pytest (тесты). Без других зависимостей.

## Global Constraints

- Единица каталога — внешний плагин/репозиторий; в репо хранятся только карточки-ссылки, НЕ копии кода.
- Пин обязателен: `source` в marketplace.json содержит `sha` проверенного коммита. Формат source: `{"source": "url", "url": "https://github.com/<owner>/<repo>.git", "sha": "<40-hex>"}`.
- `README.md` и `.claude-plugin/marketplace.json` — ТОЛЬКО генерируемые. Не редактировать руками.
- Обязательные поля карточки: `name`, `source` (вид `owner/repo`), `pin` (7–40 hex), `why`, `security.reviewed_by`, `security.prompt_injection` (= `clean`, иначе сборка падает).
- Файлы в `entries/`, начинающиеся с `_` (напр. `_template.md`), сборкой игнорируются.
- Маркетплейс: `name: "claude-skills"`, `owner.name: "hahpiez4-source"`.
- Каждая запись плагина в marketplace.json: `name`, `description` (= `why`), `source`, `category`, `homepage`.

---

### Task 1: Каркас проекта

**Files:**
- Create: `/Users/macbook/Desktop/claude-skills/.gitignore`
- Create: `/Users/macbook/Desktop/claude-skills/requirements.txt`
- Create: `/Users/macbook/Desktop/claude-skills/tests/__init__.py` (пустой)
- Create: `/Users/macbook/Desktop/claude-skills/build.py` (заготовка-заглушка)

**Interfaces:**
- Consumes: ничего
- Produces: рабочее окружение, импортируемый модуль `build`

- [ ] **Step 1: git init + структура папок**

```bash
cd /Users/macbook/Desktop/claude-skills
git init
mkdir -p entries tests .claude-plugin .github docs/superpowers/specs docs/superpowers/plans
```
(Спека и этот план уже лежат в `docs/superpowers/`.)

- [ ] **Step 2: requirements.txt**

```
PyYAML>=6.0
pytest>=7.0
```

- [ ] **Step 3: .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
```

- [ ] **Step 4: build.py-заглушка (чтобы тесты могли импортировать модуль)**

```python
"""Сборщик каталога: entries/*.md -> README.md + .claude-plugin/marketplace.json."""
from __future__ import annotations
```

- [ ] **Step 5: установить зависимости и проверить импорт**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pip install -r requirements.txt && python3 -c "import build; print('ok')"`
Expected: печатает `ok`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: scaffold claude-skills catalog project"
```

---

### Task 2: Парсинг карточки (frontmatter)

**Files:**
- Modify: `build.py`
- Test: `tests/test_parse.py`

**Interfaces:**
- Consumes: ничего
- Produces: `parse_entry(path: str | Path) -> dict` — возвращает словарь полей frontmatter, плюс ключ `_name` = имя файла без расширения. Бросает `ValueError` если frontmatter отсутствует/битый.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_parse.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_parse.py -v`
Expected: FAIL — `AttributeError: module 'build' has no attribute 'parse_entry'`

- [ ] **Step 3: Write minimal implementation**

В `build.py` добавить:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_parse.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_parse.py
git commit -m "feat: parse entry frontmatter"
```

---

### Task 3: Валидация карточки

**Files:**
- Modify: `build.py`
- Test: `tests/test_validate.py`

**Interfaces:**
- Consumes: `parse_entry`
- Produces: `validate_entry(entry: dict, seen_names: set[str]) -> list[str]` — возвращает список ошибок (пустой = валидно). Мутирует `seen_names`, добавляя `entry["name"]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_validate.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_validate.py -v`
Expected: FAIL — `module 'build' has no attribute 'validate_entry'`

- [ ] **Step 3: Write minimal implementation**

В `build.py` добавить:
```python
import re

_SOURCE_RE = re.compile(r"^[\w.-]+/[\w.-]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")


def validate_entry(entry: dict, seen_names: set) -> list:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_validate.py -v`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_validate.py
git commit -m "feat: validate entry required fields, pin, uniqueness"
```

---

### Task 4: Генерация marketplace.json

**Files:**
- Modify: `build.py`
- Test: `tests/test_marketplace.py`

**Interfaces:**
- Consumes: карточки-словари
- Produces: `build_marketplace(entries: list[dict]) -> dict` — возвращает полный объект marketplace.json. Плагины отсортированы по `name`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_marketplace.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_marketplace.py -v`
Expected: FAIL — `module 'build' has no attribute 'build_marketplace'`

- [ ] **Step 3: Write minimal implementation**

В `build.py` добавить:
```python
def _plugin_obj(entry: dict) -> dict:
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
    plugins = [_plugin_obj(e) for e in sorted(entries, key=lambda e: e["name"])]
    return {
        "name": "claude-skills",
        "description": "Каталог проверенных скиллов Claude Code (ссылки, не копии).",
        "owner": {"name": "hahpiez4-source"},
        "plugins": plugins,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_marketplace.py -v`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_marketplace.py
git commit -m "feat: generate marketplace.json object"
```

---

### Task 5: Генерация README

**Files:**
- Modify: `build.py`
- Test: `tests/test_readme.py`

**Interfaces:**
- Consumes: карточки-словари
- Produces: `build_readme(entries: list[dict]) -> str` — markdown-строка: шапка с инструкцией установки + таблица записей, отсортированных по `(category, name)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_readme.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_readme.py -v`
Expected: FAIL — `module 'build' has no attribute 'build_readme'`

- [ ] **Step 3: Write minimal implementation**

В `build.py` добавить:
```python
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
    link = f"[{e['source']}](https://github.com/{e['source']})"
    why = str(e["why"]).replace("|", "\\|")
    use = use.replace("|", "\\|")
    return f"| {e['name']} | {e.get('category', 'other')} | {why} | {use} | {sec} | {link} |"


def build_readme(entries: list) -> str:
    rows = [
        _readme_row(e)
        for e in sorted(entries, key=lambda e: (e.get("category", "other"), e["name"]))
    ]
    return README_HEADER + "\n".join(rows) + "\n"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_readme.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_readme.py
git commit -m "feat: generate README catalog table"
```

---

### Task 6: CLI `build.py` — запись файлов и режим `--check`

**Files:**
- Modify: `build.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `parse_entry`, `validate_entry`, `build_marketplace`, `build_readme`
- Produces:
  - `load_entries(entries_dir, root) -> list[dict]` — парсит и валидирует все `entries/*.md` (кроме `_*`); при ошибках валидации бросает `SystemExit` с текстом ошибок.
  - `run(root: Path, check: bool) -> int` — генерирует контент; при `check=False` пишет `README.md` и `.claude-plugin/marketplace.json`, возвращает 0; при `check=True` сравнивает с диском, возвращает 0 если совпадает, иначе 1.
  - `main(argv=None)` — CLI-обёртка (`--check`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest tests/test_cli.py -v`
Expected: FAIL — `module 'build' has no attribute 'run'`

- [ ] **Step 3: Write minimal implementation**

В `build.py` добавить:
```python
import json
import sys
import argparse


def load_entries(entries_dir: Path, root: Path) -> list:
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
    root = Path(root)
    entries = load_entries(root / "entries", root)
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
    ap = argparse.ArgumentParser(description="Сборщик каталога claude-skills")
    ap.add_argument("--check", action="store_true",
                    help="проверить актуальность сгенерированных файлов без записи")
    args = ap.parse_args(argv)
    return run(Path(__file__).parent, check=args.check)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run all tests**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 -m pytest -v`
Expected: PASS (все тесты зелёные)

- [ ] **Step 5: Commit**

```bash
git add build.py tests/test_cli.py
git commit -m "feat: build.py CLI with write and --check modes"
```

---

### Task 7: Контент репозитория + первая сборка

**Files:**
- Create: `entries/_template.md`
- Create: `entries/superpowers.md`
- Create: `CONTRIBUTING.md`
- Create: `docs/security-checklist.md`
- Create: `.github/PULL_REQUEST_TEMPLATE.md`
- Generated: `README.md`, `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: `build.py`
- Produces: готовый к публикации репозиторий

- [ ] **Step 1: `entries/_template.md`**

```markdown
---
name: имя-скилла
source: owner/repo
pin: <40-символьный sha проверенного коммита>
category: development
tags: [тег1, тег2]
why: "Одно предложение: чем полезен."
usecases:
  - "Когда пригодится — пример 1"
  - "Когда пригодится — пример 2"
security:
  reviewed_by: твой-github-логин
  reviewed_commit: <тот же sha, что pin>
  date: 2026-06-21
  prompt_injection: clean
  notes: "Что проверил."
---

# Название
Свободное описание, заметки, ссылки.
```

- [ ] **Step 2: `entries/superpowers.md` (первая реальная запись, dogfood)**

```markdown
---
name: superpowers
source: obra/superpowers
pin: 896224c4b1879920ab573417e68fd51d2ccc9072
category: development
tags: [tdd, debugging, planning, code-review]
why: "Методология разработки: брейншторм → план → TDD → ревью."
usecases:
  - "Нужна дисциплина TDD и системная отладка"
  - "Нужен структурированный процесс от идеи до кода"
security:
  reviewed_by: hahpiez4-source
  reviewed_commit: 896224c4b1879920ab573417e68fd51d2ccc9072
  date: 2026-06-21
  prompt_injection: clean
  notes: "Прочитаны SKILL.md скиллов; вредных инструкций не найдено."
---

# Superpowers
Набор из 14 скиллов: brainstorming, writing-plans, test-driven-development,
systematic-debugging, using-git-worktrees и др. Оригинал: https://github.com/obra/superpowers
```

- [ ] **Step 3: `docs/security-checklist.md`**

```markdown
# Чек-лист безопасности скилла (prompt injection)

Перед мерджем открой оригинал скилла НА КОММИТЕ `pin` и проверь:

- [ ] Нет скрытых инструкций «игнорируй прежние указания / ignore previous instructions».
- [ ] Нет команд на выкачивание данных (curl/wget на чужие хосты, отправка токенов/ключей).
- [ ] Нет деструктивных команд (`rm -rf`, массовое удаление, форк-бомбы).
- [ ] Нет обфускации (base64/hex-полезная нагрузка, которую исполняют).
- [ ] Не запрашивает лишних прав/инструментов без причины.
- [ ] Описание (`why`, `usecases`) честное и соответствует содержимому.

Любой пункт под сомнением → `prompt_injection: flagged`, PR не принимать.
```

- [ ] **Step 4: `.github/PULL_REQUEST_TEMPLATE.md`**

```markdown
## Новый скилл в каталог

- [ ] Заполнил карточку `entries/<имя>.md` по шаблону `_template.md`
- [ ] Указал конкретный коммит в `pin` (sha, не ветку)
- [ ] Прочитал содержимое скилла на этом коммите — prompt injection не найдено
- [ ] Запустил `python build.py` и закоммитил обновлённые README.md и marketplace.json
- [ ] `python build.py --check` проходит без ошибок

Источник скилла: <ссылка на оригинальный репозиторий>
```

- [ ] **Step 5: `CONTRIBUTING.md`**

```markdown
# Как добавить скилл

1. Скопируй `entries/_template.md` в `entries/<имя-скилла>.md` и заполни поля.
2. В `pin` укажи проверенный коммит оригинала:
   `git ls-remote https://github.com/<owner>/<repo>.git` (или sha тега/релиза).
3. Проверь скилл по `docs/security-checklist.md`.
4. Запусти сборку: `python build.py` — обновятся `README.md` и `.claude-plugin/marketplace.json`.
   НЕ редактируй эти два файла руками.
5. Открой Pull Request и пройди чек-лист в шаблоне.

Каталог принимает только записи с `security.prompt_injection: clean`.
```

- [ ] **Step 6: Собрать и прогнать проверку**

Run: `cd /Users/macbook/Desktop/claude-skills && python3 build.py && python3 build.py --check && python3 -m pytest -q`
Expected: файлы записаны; `--check` возвращает 0; все тесты зелёные

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat: initial catalog content + first entry (superpowers)"
```

---

### Task 8: Публикация на GitHub (по согласованию с владельцем)

**Files:** —

**Interfaces:**
- Consumes: готовый локальный репозиторий
- Produces: публичный репозиторий `hahpiez4-source/claude-skills`

> ⚠️ Необратимое/внешнее действие — выполнять ТОЛЬКО после явного «да» владельца.

- [ ] **Step 1: Создать публичный репозиторий и запушить**

```bash
cd /Users/macbook/Desktop/claude-skills
gh repo create hahpiez4-source/claude-skills --public --source=. --remote=origin --push
```

- [ ] **Step 2: Проверить установку из свежего маркетплейса**

```bash
claude plugin marketplace add hahpiez4-source/claude-skills
claude plugin marketplace list | grep claude-skills
```
Expected: маркетплейс добавлен, в нём виден плагин `superpowers`.

---

## Self-Review

**1. Spec coverage:**
- Гибрид (каталог + установка) → Task 5 (README) + Task 4 (marketplace.json). ✓
- Ссылки не копии → `source.url` + `homepage`, кода в репо нет. ✓
- Карточки как источник правды → Task 2/3, `entries/`. ✓
- build.py генерит оба файла → Task 4/5/6. ✓
- Ручная проверка + чек-лист + пин → Task 7 (checklist, PR template), валидация pin Task 3, `sha` в Task 4. ✓
- Личный масштаб, минимум автоматики → без обязательного CI; `--check` опционален. ✓
- Открытый вопрос про формат marketplace.json → закрыт: пин через `source.sha`. ✓

**2. Placeholder scan:** плейсхолдеров нет; весь код приведён полностью. `_template.md` содержит намеренные placeholder-значения — это контент шаблона, не пропуск в плане.

**3. Type consistency:** имена функций (`parse_entry`, `validate_entry`, `build_marketplace`, `build_readme`, `load_entries`, `run`, `main`) согласованы между задачами и тестами; структура `source` (`{source,url,sha}`) одинакова в Task 4 и спеке.
