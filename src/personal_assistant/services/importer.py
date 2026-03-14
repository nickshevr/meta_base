from __future__ import annotations

import hashlib
from pathlib import Path

from personal_assistant.models import Note
from personal_assistant.repositories.base import NoteRepository
from personal_assistant.services.normalization import infer_language_hint, normalize_note_to_json


class NoteImporter:
    def __init__(self, note_repository: NoteRepository) -> None:
        self.note_repository = note_repository

    def import_path(self, source: Path) -> tuple[int, int]:
        existing_notes = self.note_repository.list_notes()
        known_hashes = {note.raw_text_hash for note in existing_notes}

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

        self.note_repository.save_notes(existing_notes)
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
