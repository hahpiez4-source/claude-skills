# claude-skills — каталог проверенных скиллов Claude Code

> Личный мета-проект (НЕ привязан к бизнесу). Полка карточек-ссылок на полезные скиллы с проверкой безопасности.
> Репо: https://github.com/hahpiez4-source/claude-skills (публичный, аккаунт `hahpiez4-source`).

## Главная идея
Храним **карточки-ссылки**, не копии чужого кода. Каждая карточка пинится на конкретный коммит (автор не подменит задним числом) и проходит ревью безопасности. Из карточек `build.py` автоматически собирает `README.md` (витрина) и `.claude-plugin/marketplace.json` (установка одной командой).

## Структура (правишь ТОЛЬКО `entries/*.md`)
- `entries/*.md` — ★ источник правды, одна карточка = один скилл (`_template.md` — шаблон).
- `build.py` — генератор: `entries/*.md` → `README.md` + `marketplace.json`. **README и marketplace руками НЕ редактировать.**
- `docs/security-checklist.md` — на что смотреть при ревью (prompt injection и пр.).
- `docs/video-candidates.md` — шортлист видео-скиллов из разведки GitHub.
- `tests/` — pytest (17 тестов), проверяют парсинг/валидацию/генерацию.

## Как добавить скилл
1. Скопировать `entries/_template.md` → `entries/<имя>.md`, заполнить frontmatter.
2. Узнать pin (последний коммит): `gh api repos/<owner>/<repo>/commits/<branch> --jq .sha`.
3. **Ревью по `docs/security-checklist.md`** — прочитать исходник НА КОММИТЕ pin. `prompt_injection: clean` ставить только после реальной проверки.
4. `python3 build.py` → пересобрать. `python3 build.py --check` (rc=0) → согласовано. `python3 -m pytest -q` → зелёные.
5. `git commit` + `git push`.

## Установка скилла из каталога (на любой машине)
```bash
claude plugin marketplace add hahpiez4-source/claude-skills
claude plugin install <имя>@claude-skills   # склонирует репо на проверенный pin
```
⚠️ Эти видео-репо кладут `SKILL.md` в КОРЕНЬ (не в `skills/`), поэтому как «скилл» в списке могут не появиться — используются через чтение их SKILL.md + запуск команд напрямую.

## Содержимое каталога (на 2026-06-23)
- **superpowers** (obra) — методология: брейншторм → план → TDD → ревью.
- **clipify** (louisedesadeleer) — нарезка длинного → клипы 9:16 + караоке-субтитры, локально.
- **claude-ffmpeg-skill** (ychoi-kr) — обёртка ffmpeg (ресайз/склейка/субтитры), локально.
- **transcript-critic** (jftuga) — транскрипция whisper.cpp + разбор, локально.

## Видео-стек (проверен вживую 2026-06-23, всё работает на РУССКОМ)
Локальные зависимости на Маке: `ffmpeg`/`ffprobe`/`yt-dlp` (brew), `openai-whisper`+torch (pip), `whisper-cli` (brew whisper.cpp).
- transcript-critic зашит на путь `~/github.com/ggerganov/whisper.cpp/build/bin/whisper-cli` + модель `models/ggml-medium.en.bin` → сделан симлинк на brew-бинарь и на скачанную `ggml-base.bin` (мультиязычная).
- clipify зашит на `--model tiny.en` (англ.); для РУССКОГО запускать `whisper ... --model base --language ru` (или `medium` — точнее).
- ⚠️ Русский: мелкие модели врут с таймкодами — для живого/шумного видео брать `medium`/`large`.
- Починены SSL-сертификаты Python.framework (Install Certificates.command) — whisper сам качает модели.

## Цепочка под задачу (автоматизация контента в соцсетях)
Длинное видео → транскрипт (clipify/transcript-critic) → нарезка 9:16 + субтитры (clipify) → доводка (ffmpeg-skill) → посты/треды через скилл `content-zavod`. Всё локально.

## Открытые идеи (пустые ниши = свой скилл через skill-creator)
- [ ] Скилл «нарезка → постинг в VK/Telegram/Reels» (никто не закрывает — все стопаются на экспорте файла).
- [ ] Русские субтитры из коробки (кириллица-шрифты, переносы, русские стоп-слова для нарезки).
