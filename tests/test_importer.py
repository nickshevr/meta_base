from __future__ import annotations

from pathlib import Path

from personal_assistant.repositories.json_repo import JsonNoteRepository
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
