from __future__ import annotations

from pathlib import Path

from personal_assistant.repositories.json_repo import JsonNoteRepository, JsonTaskEventRepository, JsonTaskRepository
from personal_assistant.services.importer import NoteImporter


def test_importer_is_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "notes"
    source.mkdir()
    (source / "meeting.md").write_text("TODO: send recap", encoding="utf-8")

    repo = JsonNoteRepository(tmp_path / "notes.json")
    importer = NoteImporter(repo)

    first = importer.import_path(source)
    second = importer.import_path(source)

    assert first == (1, 0)
    assert second == (0, 1)
    assert len(repo.list_notes()) == 1


def test_importer_creates_tasks_and_events(tmp_path: Path) -> None:
    source = tmp_path / "notes"
    source.mkdir()
    (source / "meeting.md").write_text("TODO: send recap\n- [ ] prepare status update", encoding="utf-8")

    note_repo = JsonNoteRepository(tmp_path / "notes.json")
    task_repo = JsonTaskRepository(tmp_path / "tasks.json")
    event_repo = JsonTaskEventRepository(tmp_path / "task_events.json")

    importer = NoteImporter(note_repo, task_repo, event_repo)
    imported, skipped = importer.import_path(source)

    assert (imported, skipped) == (1, 0)

    tasks = task_repo.list_tasks()
    assert len(tasks) == 2
    assert {task.title for task in tasks} == {"send recap", "prepare status update"}

    events = event_repo.list_events()
    assert len(events) == 2
    assert all(event.event_type == "created" for event in events)
