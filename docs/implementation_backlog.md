# Implementation Backlog

Этот backlog описывает старт работ после утверждения PRD.
Подход: **быстрый MVP на JSON**, но архитектурно закладываем миграцию на **SQLite**, деплой в **Yandex Cloud** и управление инфраструктурой через **Terraform**.

## Оперативный план действий (что делать первым)

1. Поднять каркас CLI-проекта на Python 3 с type hints и базовыми командами (`import-notes`, `review-extraction`, `weekly-review`, `remind`).
2. Реализовать JSON-хранилище (`notes.json`, `tasks.json`, `task_events.json`) с атомарной записью.
3. Подключить импорт markdown/txt и идемпотентность через хеш сырого текста.
4. Добавить LLM-конвейер: `normalize_note_to_json` + `extract_tasks` с schema validation и retry.
5. Ввести ручной confirm/edit этап для extracted задач (особенно при low confidence).
6. Реализовать weekly value-цикл: forgotten detection, weekly priorities, единый markdown-report.
7. Включить reminders в двух режимах: on-demand и scheduled (cron/systemd).
8. После стабилизации MVP — подготовить repository abstraction и миграцию JSON → SQLite.

## 1) Эпик: Core CLI (Python 3 + type hints)

### 1.1 Bootstrap проекта
- [ ] Создать структуру Python-проекта (`src/`, `tests/`, `pyproject.toml`).
- [ ] Подключить линтер/форматтер и проверку типов.
- [ ] Завести базовый CLI (`app --help`).

### 1.2 Доменные модели
- [ ] Описать typed-модели: `Note`, `Task`, `TaskEvent`, `WeeklyReport`.
- [ ] Добавить enum-статусы задач: `open`, `in_progress`, `done`, `dropped`.
- [ ] Описать JSON-схемы/валидаторы на вход и на персист.

### 1.3 Команды CLI (минимум)
- [ ] `import-notes <path>`
- [ ] `review-extraction <batch-id>`
- [ ] `weekly-review`
- [ ] `remind --mode on-demand`

**DoD:** CLI запускается, команды доступны, валидация аргументов работает.

---

## 2) Эпик: Ingestion и LLM-нормализация

### 2.1 Импорт заметок
- [ ] Поддержка свободных markdown/txt файлов.
- [ ] Хеширование сырого текста для идемпотентности.
- [ ] Сохранение metadata заметки.

### 2.2 Нормализация в JSON через LLM
- [ ] Prompt job `normalize_note_to_json`.
- [ ] JSON schema validation + retry при невалидном ответе.
- [ ] Логирование сырого ответа LLM для дебага.

### 2.3 Извлечение задач
- [ ] Prompt job `extract_tasks`.
- [ ] confidence score + очередь ручной верификации.
- [ ] Извлечение дедлайнов, владельцев, тегов.

**DoD:** из свободной заметки стабильно получаем нормализованный JSON и список задач на подтверждение.

---

## 3) Эпик: Хранилище JSON (MVP)

### 3.1 JSON-репозитории
- [ ] Реализовать `notes.json`, `tasks.json`, `task_events.json`.
- [ ] Добавить атомарную запись (temp file + rename).
- [ ] Добавить индексы в памяти (по id, статусу, due_date).

### 3.2 Слой абстракции для будущей SQLite миграции
- [ ] Ввести интерфейсы `NoteRepository`, `TaskRepository`, `TaskEventRepository`.
- [ ] Сделать текущую реализацию `Json*Repository`.
- [ ] Подготовить контракт-тесты репозиториев (чтобы потом подставить SQLite без ломки бизнес-логики).

**DoD:** данные надежно пишутся/читаются из JSON, бизнес-логика не зависит от конкретного storage backend.

---

## 4) Эпик: Weekly review и reminders

### 4.1 Forgotten detection
- [ ] Rule engine: stale/open > N days.
- [ ] Rule engine: upcoming/overdue deadlines.
- [ ] Rule engine: commitment без task.

### 4.2 Weekly priorities
- [ ] Скоинг приоритетов (urgency + importance + blockers).
- [ ] Prompt job `weekly_review` для краткого объяснения приоритетов.
- [ ] Дедупликация/merge suggestions.

### 4.3 Единый weekly report
- [ ] Генерировать один markdown-файл отчета.
- [ ] Секции: forgotten / priorities / duplicates / due this week.
- [ ] Включать ссылки на source notes/task ids.

### 4.4 Reminders
- [ ] On-demand режим (`remind --mode on-demand`).
- [ ] Scheduled режим (через cron/systemd locally).
- [ ] Шаблон reminder digest в markdown.

**DoD:** weekly report и reminders стабильно генерируются и полезны в ежедневном/еженедельном цикле.

---

## 5) Эпик: Подготовка к SQLite (следующий шаг после MVP)

### 5.1 План миграции
- [ ] Описать целевую схему SQLite (`notes`, `tasks`, `task_events`).
- [ ] Подготовить миграционный скрипт `json_to_sqlite`.
- [ ] Добавить dry-run и отчет о миграции.

### 5.2 Реализация SQLite-репозиториев
- [ ] `SqliteNoteRepository`, `SqliteTaskRepository`, `SqliteTaskEventRepository`.
- [ ] Повторно прогнать контракт-тесты репозиториев.
- [ ] Feature flag `STORAGE_BACKEND=json|sqlite`.

**DoD:** можно переключиться на SQLite без изменений в core business logic.

---

## 6) Эпик: Yandex Cloud + Terraform (production-ready этап)

### 6.1 Terraform foundation
- [ ] Создать `infra/terraform` с окружениями `dev/prod`.
- [ ] Описать backend для state (удаленный, с lock).
- [ ] Провайдер `yandex` + базовые переменные.

### 6.2 Инфраструктура
- [ ] Сервис для запуска CLI/worker (VM или container runtime).
- [ ] Secret management для LLM API keys.
- [ ] Хранилище для артефактов (reports/logs/backups).

### 6.3 Деплой и операции
- [ ] Make targets: `infra-plan`, `infra-apply`, `infra-destroy`.
- [ ] CI job для `terraform fmt/validate/plan`.
- [ ] Backup/restore стратегия для SQLite и репортов.

**DoD:** инфраструктура поднимается через Terraform, окружение воспроизводимо, секреты и бэкапы настроены.

---

## 7) Рекомендуемый порядок спринтов

### Sprint 1 (MVP skeleton)
- Эпики 1 + 2.1 + 3.1

### Sprint 2 (MVP intelligence)
- Эпики 2.2 + 2.3 + 4.1

### Sprint 3 (MVP value delivery)
- Эпики 4.2 + 4.3 + 4.4

### Sprint 4 (future-proofing)
- Эпик 3.2 + 5.1

### Sprint 5+ (platform)
- Эпики 5.2 + 6.*

---

## 8) Критические риски и меры
- **Нестабильный JSON от LLM** → strict schema validation + retries + fallback parsing.
- **Потеря данных в JSON storage** → атомарная запись + регулярные snapshots.
- **Сложная миграция на SQLite** → контракт-тесты репозиториев с первого дня.
- **Сложность инфраструктуры** → Terraform-модули и разделение dev/prod с самого начала.
