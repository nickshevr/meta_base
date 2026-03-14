from __future__ import annotations

from typing import Protocol

from personal_assistant.models import Note, Task, TaskEvent


class NoteRepository(Protocol):
    def list_notes(self) -> list[Note]: ...

    def save_notes(self, notes: list[Note]) -> None: ...


class TaskRepository(Protocol):
    def list_tasks(self) -> list[Task]: ...

    def save_tasks(self, tasks: list[Task]) -> None: ...


class TaskEventRepository(Protocol):
    def list_events(self) -> list[TaskEvent]: ...

    def save_events(self, events: list[TaskEvent]) -> None: ...
