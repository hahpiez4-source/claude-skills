# Плейбук: сторис/Reels из исходников видео (ВК + ТГ)

> Воспроизводимый процесс «папка с видео → готовая вертикальная сторис с подписями».
> Собран на реальном кейсе 2026-06-23 (ЭМИТ АвтоТехЦентр: 16 клипов → монтаж 23 сек).
> Инструменты: скиллы из каталога [[claude-skills]] — `ffmpeg-usage`, `clipify`, `transcribe`.

---

## 1. Цель и контекст
Автоматизировать видеоконтент для соцсетей: из набора снятых на телефон моментов собирать
готовые к публикации вертикальные сторис/клипы под ВК и Telegram, с подписями, локально и без облака.

## 2. Архитектура (как это устроено)

```
Исходники (.MOV, телефон)
   │
   ├─ [разведка] ffprobe: разрешение / длительность / звук / ориентация
   ├─ [контент]  кадр из середины (ffmpeg thumbnail) → Claude смотрит → понимает сюжет
   ├─ [речь?]    whisper.cpp (transcribe-скилл) → есть ли диалог (нужны ли субтитры)
   │
   ├─ ПОДПИСИ: Pillow рисует PNG-плашки с текстом (кириллица!)
   ├─ СЕГМЕНТЫ: ffmpeg на каждый клип → trim + scale/crop 9:16 + overlay подпись
   ├─ СКЛЕЙКА:  ffmpeg concat demuxer (-c copy)
   └─ ФИНАЛ:    + тихая аудиодорожка (anullsrc) + faststart → story.mp4 (1080×1920, H.264)
```

**Связка скиллов (вся локальная, ничего не утекает):**
- `transcribe` (whisper.cpp) / `clipify` (openai-whisper) — транскрипт, если в видео есть речь.
- `clipify` — автонарезка длинного видео по смешным/смысловым моментам + караоке-субтитры.
- `ffmpeg-usage` — монтаж, ресайз, наложение, склейка, кодирование под платформу.

## 3. Принятые решения (и почему)

| Решение | Почему |
|---|---|
| Сначала **разведка ffprobe + кадры**, потом монтаж | Не угадывать. Узнали: клипы уже 9:16, речи нет → субтитры не нужны, главное — монтаж |
| Подписи через **Pillow→PNG→overlay**, НЕ `drawtext` | brew-ffmpeg собран без libfreetype (нет `drawtext`/`subtitles`). overlay есть всегда |
| Шрифт **Arial Unicode** (`/System/Library/Fonts/Supplemental/`) | Полная кириллица. Скопировать в путь без пробелов перед использованием |
| **Без эмодзи** в подписях | ffmpeg/Pillow рендерят моно-глифы; цветные эмодзи → «тофу» (квадраты) |
| Финал **muted + тихая AAC-дорожка** | Музыку добавлять в редакторе ВК/ТГ (лицензионная библиотека, без копирайт-страйков). Тихая дорожка — чтобы файл не считался «немым» |
| Каждый сегмент кодируем **идентично**, потом concat `-c copy` | Быстро, без перекодирования при склейке. Требование: одинаковые codec/fps/SAR/timescale |
| `scale=...:force_original_aspect_ratio=increase,crop=1080:1920` | Заполняет кадр 9:16 без чёрных полос (обрезает лишнее) |
| Длина ~23 сек | TG сторис лимит 60с (ок одним куском); ВК История 15с/сегмент → ВК разобьёт, либо постить как VK Клип |

## 4. ⚠️ Ошибки, которые БЫЛИ — и как не повторять

1. **`ffmpeg` съедает stdin в цикле `while read … done < file`.**
   Симптом: цикл обрабатывает только ПЕРВУЮ строку, дальше молча обрывается (собрался 1 сегмент из 11).
   Причина: ffmpeg читает stdin, выпивает остаток файла-манифеста.
   **Фикс: всегда `ffmpeg -nostdin …`** в циклах/скриптах (или `</dev/null` на команду/скрипт целиком).

2. **brew-ffmpeg без `drawtext`** (`No such filter: 'drawtext'`).
   Причина: сборка без libfreetype/libass.
   **Фикс:** проверять `ffmpeg -filters | grep drawtext` заранее; если нет — путь Pillow→PNG→`overlay`.
   (Альтернатива: поставить полноценный ffmpeg из tap `homebrew-ffmpeg/ffmpeg`.)

3. **Зависший ffmpeg ждёт stdin на финальном шаге** (anullsrc/concat без `-nostdin`).
   Симптом: процесс жив, ffmpeg-потомка нет, ничего не двигается.
   **Фикс:** `-nostdin` везде; запускать сборку как скрипт `bash build.sh </dev/null`.

4. **Сам себе мешал: `pkill`-ил собственные сборки.**
   Симптом: каждая фоновая сборка падала со статусом killed/failed.
   **Фикс:** не запускать новые сборки/`pkill`, пока идёт текущая. Дожидаться уведомления о завершении, не дёргать процесс.

5. **macOS Python (Framework) — `CERTIFICATE_VERIFY_FAILED`** при авто-загрузке моделей whisper.
   **Фикс:** один раз запустить `/Applications/Python 3.11/Install Certificates.command`.
   Обходной путь: качать модель через `curl` (берёт системные сертификаты) в нужную папку кэша.

6. **Скиллы зашивают пути/модели (англ.) хардкодом.**
   `transcript-critic` ждёт `~/github.com/ggerganov/whisper.cpp/build/bin/whisper-cli` + `ggml-medium.en.bin`;
   `clipify` зовёт `whisper --model tiny.en --language en`.
   **Фикс:** симлинк бинаря/модели по ожидаемому пути; для РУССКОГО запускать с мультиязычной моделью и `-l ru` / `--language ru` (мелкие модели врут с таймкодами — для живого видео брать `medium`/`large`).

7. **SKILL.md в КОРНЕ репо, а не в `skills/`.**
   Эти видео-скиллы как «скилл» в списке могут не появиться. Используются через чтение их SKILL.md + прямой запуск команд/скриптов.

## 5. Воспроизводимый RUNBOOK (по шагам)

```bash
SRC="путь/к/папке/с/видео"          # исходники
OUT="$SRC/сторис"; B=/tmp/story_build
rm -rf "$B"; mkdir -p "$B" "$OUT"

# 0) ПРОВЕРКА окружения
ffmpeg -filters | grep -q drawtext && echo "drawtext есть" || echo "drawtext НЕТ → путь Pillow"

# 1) РАЗВЕДКА: техданные всех клипов
for f in "$SRC"/*.MOV; do
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$f"
  ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"
done

# 2) КОНТЕНТ: кадр из середины каждого клипа → Claude смотрит, придумывает порядок и подписи
ffmpeg -nostdin -v error -y -ss <середина> -i "$f" -vf scale=320:-1 -frames:v 1 "$B/thumb.jpg"

# 3) ПОДПИСИ: Pillow рисует PNG-плашки (шрифт Arial Unicode, БЕЗ эмодзи)
#    canvas 1080×240 прозрачный → rounded_rectangle(чёрный @150 alpha) → белый текст по центру

# 4) СЕГМЕНТЫ: на каждый клип (ОБЯЗАТЕЛЬНО -nostdin!)
ffmpeg -nostdin -v error -y -ss "$SS" -i "$FILE" -i "$PNG" -t "$DUR" \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v];[v][1:v]overlay=0:1480[o]" \
  -map "[o]" -an -r 30 -c:v libx264 -preset ultrafast -crf 22 -pix_fmt yuv420p -video_track_timescale 30000 "$B/segNN.mp4"

# 5) СКЛЕЙКА (list.txt: file 'seg00.mp4' …)
ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$B/list.txt" -c copy "$B/montage.mp4"

# 6) ФИНАЛ: тихая дорожка + faststart
ffmpeg -nostdin -v error -y -i "$B/montage.mp4" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
  -c:v copy -c:a aac -shortest -movflags +faststart "$OUT/story.mp4"
```
**Запускать сборку как скрипт:** `bash build.sh </dev/null` (защита от зависаний на stdin).

## 6. Чек-лист «не забыть»
- [ ] `ffmpeg -filters | grep drawtext` — есть? если нет → Pillow→PNG→overlay.
- [ ] Все ffmpeg в циклах/скриптах с **`-nostdin`**.
- [ ] Шрифт с кириллицей скопирован в путь без пробелов; без эмодзи.
- [ ] Подписи в нижней трети (y≈1480) — не перекрыть зоной интерфейса сторис.
- [ ] Все сегменты кодируются ИДЕНТИЧНО (fps/SAR/pix_fmt/timescale) → concat `-c copy`.
- [ ] Финал: 1080×1920, H.264, yuv420p, +faststart, тихая AAC.
- [ ] Не `pkill`-ить и не запускать параллельные сборки; дождаться завершения.
- [ ] Длина: TG ≤60с; ВК История ≤15с/сегмент (иначе VK Клип).
- [ ] Музыку добавляет пользователь в редакторе ВК/ТГ (копирайт).

## 7. Идеи на развитие
- Свой скилл «нарезка → постинг в VK/Telegram + русские субтитры» (пустая ниша, см. [[claude-skills]] CLAUDE.md).
- Параметризовать этот рунбук в один скрипт-генератор (папка → сторис) с конфигом подписей.
