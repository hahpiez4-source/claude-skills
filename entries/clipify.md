---
name: clipify
source: louisedesadeleer/clipify
pin: 621855bdc0ea67c40d872ffb8f216f5f10c7bc73
category: video
tags: [video, reels, shorts, subtitles, whisper, ffmpeg]
why: "Длинное видео → клипы 9:16 с караоке-субтитрами, полностью локально."
usecases:
  - "Нарезать подкаст/стрим на короткие Reels/Shorts без ручного монтажа"
  - "Авто-переформат 16:9 → 9:16 с трекингом говорящего и субтитрами в стиле Opus.pro"
security:
  reviewed_by: hahpiez4-source
  reviewed_commit: 621855bdc0ea67c40d872ffb8f216f5f10c7bc73
  date: 2026-06-23
  prompt_injection: clean
  notes: "Прочитаны SKILL.md + все 4 скрипта. Сетевых вызовов в коде нет, всё локально (whisper+ffmpeg+numpy). Обфускации/деструктива/эксфильтрации нет. Минор: зависимости не зафиксированы в requirements.txt — ставятся руками по README."
---

# clipify
Автонарезка длинного видео на соцклипы 9:16. Локальный Whisper транскрибирует,
скрипт ищет смешные моменты/панчлайны, режет ffmpeg-ом, при 16:9→9:16 определяет
говорящего по motion-energy и панорамирует, затем выжигает ASS-субтитры
(слово-за-словом, как Opus.pro). Без облака — всё на твоей машине.

Оригинал: https://github.com/louisedesadeleer/clipify
Установка (по README): `brew install ffmpeg` + `pip install openai-whisper numpy`.
⚠️ Русский язык: модель `tiny.en` — английская; для RU бери whisper `medium`/`large`.
