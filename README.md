# claude-skills

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
| superpowers | development | Методология разработки: брейншторм → план → TDD → ревью. | Нужна дисциплина TDD и системная отладка; Нужен структурированный процесс от идеи до кода | ✅ clean | [obra/superpowers](https://github.com/obra/superpowers) |
| claude-ffmpeg-skill | video | Чистая обёртка ffmpeg: ресайз, склейка, субтитры, кадры — без облака. | Ручной монтаж: ресайз 16:9 → 9:16, конкатенация клипов, вшить субтитры; Извлечь кадры для превью, сжать под TikTok/Reels по готовым пресетам | ✅ clean | [ychoi-kr/claude-ffmpeg-skill](https://github.com/ychoi-kr/claude-ffmpeg-skill) |
| clipify | video | Длинное видео → клипы 9:16 с караоке-субтитрами, полностью локально. | Нарезать подкаст/стрим на короткие Reels/Shorts без ручного монтажа; Авто-переформат 16:9 → 9:16 с трекингом говорящего и субтитрами в стиле Opus.pro | ✅ clean | [louisedesadeleer/clipify](https://github.com/louisedesadeleer/clipify) |
| transcript-critic | video | Локальная транскрипция (whisper.cpp) видео/аудио + структурный разбор. | Транскрибировать свой вебинар/подкаст для контент-плана (кормить content-zavod); Найти сильные цитаты и таймкоды для нарезки на клипы — без облака | ✅ clean | [jftuga/transcript-critic](https://github.com/jftuga/transcript-critic) |
