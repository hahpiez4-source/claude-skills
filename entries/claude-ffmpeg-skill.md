---
name: claude-ffmpeg-skill
source: ychoi-kr/claude-ffmpeg-skill
pin: b88cb5ce08337ab55c66c67674100b8de29cf232
category: video
tags: [video, ffmpeg, subtitles, convert, social-presets]
why: "Чистая обёртка ffmpeg: ресайз, склейка, субтитры, кадры — без облака."
usecases:
  - "Ручной монтаж: ресайз 16:9 → 9:16, конкатенация клипов, вшить субтитры"
  - "Извлечь кадры для превью, сжать под TikTok/Reels по готовым пресетам"
security:
  reviewed_by: hahpiez4-source
  reviewed_commit: b88cb5ce08337ab55c66c67674100b8de29cf232
  date: 2026-06-23
  prompt_injection: clean
  notes: "Прочитаны все 8 файлов. Вредоносного нет, всё локально; в сеть ходит только git clone себя самого. validate.py — стандартная библиотека, без сети. Рекомендация: ставить через git clone, а не curl|bash (про сам паттерн, не про репо)."
---

# claude-ffmpeg-skill
Cookbook-скилл: даёт Claude набор готовых команд ffmpeg — конвертация форматов,
ресайз/смена соотношения сторон, GIF, аудио, обрезка/склейка, скорость, субтитры
(вшить/мягкие/извлечь), извлечение кадров, сжатие, веб-оптимизация. Есть пресеты
под YouTube/Instagram/TikTok/Twitter. Данные никуда не уходят — всё локально.

Оригинал: https://github.com/ychoi-kr/claude-ffmpeg-skill
Установка: предпочитай `git clone` + копирование в `~/.claude/skills/`
(а не `curl -sSL ... | bash`). Требуется локальный ffmpeg/ffprobe.
