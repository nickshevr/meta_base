# Personal LLM Execution Assistant — PRD (MVP)

## 1. Context

Цель: превратить текущие свободные текстовые заметки со встреч и целей в систему, которая помогает не забывать договоренности и еженедельно подсказывает приоритеты.

Ограничения и вводные:
- Ввод данных: вручную (основной режим).
- Языки: RU + EN.
- Использование: локальные файлы/Obsidian, без обязательных интеграций в MVP.
- LLM: внешний API допустим.
- Масштаб: до ~10 часов встреч в день.
- Статусы выполнения: пользователь отмечает вручную, система напоминает.
- Главная ценность через 1 месяц: текущие текстовые заметки преобразуются в реальные, отслеживаемые дела.

---

## 2. Product Vision

Продукт — это персональный «слой исполнения» поверх заметок:
1. Принимает сырые заметки/договоренности.
2. Извлекает action items и commitments.
3. Показывает, что забыто.
4. Формирует еженедельные приоритеты.
5. Напоминает о просроченных/подвисших задачах.

---

## 3. Primary User Flows

### Flow A — После встречи (ежедневный)
1. Пользователь добавляет заметку (RU/EN, свободный текст).
2. Система переводит заметку в нормализованный JSON-слой (через LLM) и предлагает извлеченные пункты:
   - задачи (что сделать),
   - владельца (кто делает),
   - срок (если найден),
   - контекст (из какой встречи).
3. Пользователь подтверждает/правит.
4. Пункты попадают в backlog со статусом `open`.

### Flow B — Еженедельный обзор
1. Пользователь запускает `weekly-review`.
2. Система анализирует:
   - незакрытые пункты,
   - пункты без апдейта,
   - дедлайны в ближайшие 7 дней,
   - потенциальные дубли/объединения.
3. Возвращает в одном markdown-файле:
   - «что, вероятно, забыто»,
   - список топ-приоритетов недели (3–7 пунктов),
   - предложенные объединения.

### Flow C — Напоминания
1. Digest формируется:
   - по команде пользователя,
   - и по расписанию (daily cron).
2. Пользователь получает:
   - просроченное,
   - скоро дедлайн,
   - long-open без прогресса.

---

## 4. Scope

### MVP (v0)
- Импорт заметок из локального markdown/txt файла в свободном формате.
- RU+EN extraction в action items.
- Нормализация сырого текста заметок в JSON через LLM.
- Ручное подтверждение extracted items.
- Статусы: `open / in_progress / done / dropped`.
- Weekly Review: forgotten + weekly priorities в одном markdown-файле.
- Напоминания и по запуску команды, и по расписанию.
- Экспорт результатов в markdown (удобно для Obsidian).

### Out of Scope (позже)
- Автоматические интеграции (Telegram/Calendar/Email).
- Совместная работа нескольких пользователей.
- Сложная аналитика производительности.

---

## 5. Functional Requirements

1. **Capture**
   - Принимать один или несколько markdown/txt файлов.
   - Поддерживать заметки смешанного языка RU/EN.
   - Поддерживать свободный формат заметок без обязательного шаблона.

2. **Normalization + Extraction**
   - Находить action items и commitments в свободном тексте.
   - Привязывать к дате/источнику заметки.
   - Строить JSON-структуру заметки (meeting metadata, commitments, tasks).
   - Отмечать confidence и требовать user confirmation при низкой уверенности.

3. **Task Store**
   - Хранить задачи в JSON с полями:
     - `id`, `title`, `description`, `source_note`, `created_at`,
     - `owner` (default: self),
     - `due_date` (optional),
     - `status`,
     - `last_updated_at`,
     - `tags`.

4. **Forgotten Detection**
   - Правила для «возможно забыто»:
     - `open` > N дней без обновления,
     - дедлайн близко или просрочен,
     - обещание зафиксировано, но task не создана.

5. **Weekly Prioritization**
   - Возвращать список приоритетов на неделю на основе:
     - срочности,
     - важности (по ключевым словам/тегам/весу цели),
     - блокеров/зависимостей.

6. **Reminder Output**
   - Генерировать markdown digest:
     - overdue,
     - upcoming,
     - stale,
     - suggested focus for week.

---

## 6. Non-Functional Requirements

- Язык реализации: Python 3.
- Кодовая база с type hints во всех основных модулях.
- Локальное хранение данных: JSON (MVP).
- Внешний LLM используется только для аналитики/извлечения.
- Конфиг модели и API-ключа через `.env`.
- Идемпотентность импорта (повторный импорт не должен плодить дубли).
- Прозрачность: хранить исходный текст и normalized JSON результат.

---

## 7. Suggested MVP Architecture

- **Interface layer**: CLI-first (минимальный барьер).
- **Input parser**: markdown/txt reader.
- **Normalization service**: LLM pipeline, перевод свободной заметки в JSON-схему.
- **Extraction service**: LLM+rules для извлечения структурированных задач.
- **Storage**: JSON files.
- **Review engine**: rule-based + LLM summary.
- **Output renderer**: markdown reports для Obsidian (один файл на weekly review).

### Why CLI-first
- Быстрый запуск без UI.
- Прямо подходит под сценарий «локальный файл / Obsidian».
- Позволяет отложить фронтенд до подтверждения ценности.

---

## 8. Data Model (draft)

### `notes.json`
- `id`
- `title`
- `path`
- `captured_at`
- `language_hint`
- `raw_text_hash`
- `normalized_json`

### `tasks.json`
- `id`
- `title`
- `description`
- `source_note_id`
- `owner`
- `status`
- `priority_score`
- `due_date`
- `created_at`
- `updated_at`

### `task_events.json`
- `id`
- `task_id`
- `event_type` (`created`, `status_changed`, `commented`, `reminded`)
- `payload`
- `created_at`

---

## 9. LLM Strategy (non-local)

### Prompt jobs
1. `normalize_note_to_json` — перевести свободный текст заметки в JSON по схеме.
2. `extract_tasks` — выделить список action items из normalized JSON / raw note.
3. `normalize_tasks` — убрать дубли, нормализовать названия.
4. `weekly_review` — сформировать forgotten list + weekly priorities.

### Guardrails
- Всегда просить структурированный JSON-ответ.
- Валидация схемы перед записью.
- При невалидном ответе — retry с указанием ошибки схемы.
- Не удалять задачи автоматически по выводу LLM.

---

## 10. Success Metrics (MVP)

Через 4 недели:
- ≥70% встреч имеют извлеченные и подтвержденные action items.
- Снижение доли «забытых» задач (самооценка пользователя).
- Еженедельный обзор экономит время планирования (субъективно).
- Пользователь продолжает использовать систему 4+ недель.

---

## 11. Implementation Plan (before coding)

### Phase 0 — Design freeze
- Утвердить этот документ.
- Зафиксировать MVP-команды CLI и формат JSON-схем.

### Phase 1 — Foundation
- Инициализация Python 3 проекта.
- Базовые доменные модели с type hints.
- JSON storage и импорт заметок.

### Phase 2 — Intelligence
- LLM normalizer `note -> JSON`.
- LLM extraction pipeline.
- Confirm/edit flow.

### Phase 3 — Weekly value
- Forgotten detection rules.
- Weekly priorities + единый markdown report.
- Два режима напоминаний: on-demand + scheduled.

### Phase 4 — UX polish
- Улучшения prompt’ов.
- Снижение дублей.
- Опциональная подготовка к Telegram integration.

---

## 12. Decisions Locked (approved)

1. CLI backend: **Python 3 + type hints**.
2. Хранилище MVP: **JSON**.
3. Формат входных заметок: **свободный**, с переводом в JSON через LLM.
4. Формат weekly report: **один файл**.
5. Напоминания: **и по команде, и по расписанию**.
