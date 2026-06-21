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

