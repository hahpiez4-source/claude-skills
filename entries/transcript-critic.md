---
name: transcript-critic
source: jftuga/transcript-critic
pin: d34ec0d6f434e9a308df43a66fb6533332d12f64
category: video
tags: [transcription, whisper, local, analysis, content]
why: "Локальная транскрипция (whisper.cpp) видео/аудио + структурный разбор."
usecases:
  - "Транскрибировать свой вебинар/подкаст для контент-плана (кормить content-zavod)"
  - "Найти сильные цитаты и таймкоды для нарезки на клипы — без облака"
security:
  reviewed_by: hahpiez4-source
  reviewed_commit: d34ec0d6f434e9a308df43a66fb6533332d12f64
  date: 2026-06-23
  prompt_injection: clean
  notes: "Прочитаны все 8 файлов. Транскрипция полностью локальная (whisper.cpp), в облако ничего не уходит. Установщик прописывает себе только Read на свою папку. Caveat: текст чужого видео идёт в модель как данные (общий риск суммаризаторов); /transcribe запускает Bash — держи подтверждение Bash включённым."
---

# transcript-critic
Локально скачивает (yt-dlp по URL пользователя) или конвертирует (ffmpeg) аудио,
прогоняет через локальный whisper.cpp в .vtt/.txt, затем Claude по шаблону
ANALYSIS_PROMPT.md пишет структурный разбор: тезисы, термины, логические ошибки,
таймкоды. Транскрипция не требует сети — аудио не покидает машину.

Оригинал: https://github.com/jftuga/transcript-critic
Требуется локальный whisper.cpp + ffmpeg (+ yt-dlp для скачивания по ссылке).
⚠️ Транскрибируешь чужое видео — его содержимое попадает в модель как данные.
