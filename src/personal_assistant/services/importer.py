from __future__ import annotations

import hashlib
from pathlib import Path

from personal_assistant.models import Note, Task, TaskEvent
from personal_assistant.repositories.base import NoteRepository, TaskEventRepository, TaskRepository
from personal_assistant.services.normalization import extract_tasks, infer_language_hint, normalize_note_to_json


class NoteImporter:
    def __init__(
        self,
        note_repository: NoteRepository,
        task_repository: TaskRepository | None = None,
        event_repository: TaskEventRepository | None = None,
    ) -> None:
        self.note_repository = note_repository
        self.task_repository = task_repository
        self.event_repository = event_repository

    def import_path(self, source: Path) -> tuple[int, int]:
        existing_notes = self.note_repository.list_notes()
        known_hashes = {note.raw_text_hash for note in existing_notes}

        existing_tasks = self.task_repository.list_tasks() if self.task_repository else []
        known_task_keys = {(task.source_note_id, task.title.lower().strip()) for task in existing_tasks}

        existing_events = self.event_repository.list_events() if self.event_repository else []

        imported = 0
        skipped = 0
        for file_path in self._iter_supported_files(source):
            raw_text = file_path.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            if content_hash in known_hashes:
                skipped += 1
                continue

            note = Note.create(
                title=file_path.stem,
                path=str(file_path),
                language_hint=infer_language_hint(raw_text),
                raw_text_hash=content_hash,
                raw_text=raw_text,
                normalized_json=normalize_note_to_json(raw_text),
            )
            existing_notes.append(note)
            known_hashes.add(content_hash)
            imported += 1

            extracted = extract_tasks(raw_text)
            for item in extracted:
                key = (note.id, item["title"].lower().strip())
                if key in known_task_keys:
                    continue
                task = Task.create(
                    title=item["title"],
                    description=item["description"],
                    source_note_id=note.id,
                    owner=item["owner"],
                    due_date=item["due_date"],
                    tags=item["tags"],
                )
                existing_tasks.append(task)
                known_task_keys.add(key)

                if self.event_repository:
                    existing_events.append(
                        TaskEvent.create(
                            task_id=task.id,
                            event_type="created",
                            payload={"source_note_id": note.id, "confidence": item["confidence"]},
                        )
                    )

        self.note_repository.save_notes(existing_notes)
        if self.task_repository:
            self.task_repository.save_tasks(existing_tasks)
        if self.event_repository:
            self.event_repository.save_events(existing_events)

        return imported, skipped

    @staticmethod
    def _iter_supported_files(source: Path) -> list[Path]:
        if source.is_file() and source.suffix.lower() in {".md", ".txt"}:
            return [source]

        if source.is_dir():
            collected: list[Path] = []
            for ext in ("*.md", "*.txt"):
                collected.extend(source.glob(ext))
            return sorted(collected)

        return []
