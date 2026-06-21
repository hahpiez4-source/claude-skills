# Как добавить скилл

1. Скопируй `entries/_template.md` в `entries/<имя-скилла>.md` и заполни поля.
2. В `pin` укажи проверенный коммит оригинала:
   `git ls-remote https://github.com/<owner>/<repo>.git` (или sha тега/релиза).
3. Проверь скилл по `docs/security-checklist.md`.
4. Запусти сборку: `python build.py` — обновятся `README.md` и `.claude-plugin/marketplace.json`.
   НЕ редактируй эти два файла руками.
5. Открой Pull Request и пройди чек-лист в шаблоне.

Каталог принимает только записи с `security.prompt_injection: clean`.
