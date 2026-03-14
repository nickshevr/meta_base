from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from personal_assistant.models import Note, Task, TaskEvent


class JsonRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._atomic_write([])

    def _read(self) -> list[dict]:
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
            if not isinstance(payload, list):
                raise ValueError(f"Expected list payload in {self.path}")
            return payload

    def _atomic_write(self, payload: list[dict]) -> None:
        with NamedTemporaryFile("w", delete=False, dir=self.path.parent, encoding="utf-8") as temp:
            json.dump(payload, temp, ensure_ascii=False, indent=2)
            temp_path = Path(temp.name)
        temp_path.replace(self.path)


class JsonNoteRepository(JsonRepository):
    def list_notes(self) -> list[Note]:
        return [Note.from_dict(item) for item in self._read()]

    def save_notes(self, notes: list[Note]) -> None:
        self._atomic_write([note.to_dict() for note in notes])


class JsonTaskRepository(JsonRepository):
    def list_tasks(self) -> list[Task]:
        return [Task.from_dict(item) for item in self._read()]

    def save_tasks(self, tasks: list[Task]) -> None:
        self._atomic_write([task.to_dict() for task in tasks])


class JsonTaskEventRepository(JsonRepository):
    def list_events(self) -> list[TaskEvent]:
        return [TaskEvent.from_dict(item) for item in self._read()]

    def save_events(self, events: list[TaskEvent]) -> None:
        self._atomic_write([event.to_dict() for event in events])
