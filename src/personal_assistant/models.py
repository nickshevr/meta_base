from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DROPPED = "dropped"


@dataclass(slots=True)
class Note:
    id: str
    title: str
    path: str
    captured_at: str
    language_hint: str
    raw_text_hash: str
    raw_text: str
    normalized_json: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        title: str,
        path: str,
        language_hint: str,
        raw_text_hash: str,
        raw_text: str,
        normalized_json: dict[str, Any] | None = None,
    ) -> "Note":
        return cls(
            id=str(uuid4()),
            title=title,
            path=path,
            captured_at=datetime.now(timezone.utc).isoformat(),
            language_hint=language_hint,
            raw_text_hash=raw_text_hash,
            raw_text=raw_text,
            normalized_json=normalized_json or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Note":
        return cls(**payload)


@dataclass(slots=True)
class Task:
    id: str
    title: str
    description: str
    source_note_id: str
    owner: str
    status: TaskStatus
    priority_score: float
    due_date: str | None
    created_at: str
    updated_at: str
    tags: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        source_note_id: str,
        owner: str = "self",
        due_date: str | None = None,
        tags: list[str] | None = None,
    ) -> "Task":
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            id=str(uuid4()),
            title=title,
            description=description,
            source_note_id=source_note_id,
            owner=owner,
            status=TaskStatus.OPEN,
            priority_score=0.0,
            due_date=due_date,
            created_at=now,
            updated_at=now,
            tags=tags or [],
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Task":
        payload = payload.copy()
        payload["status"] = TaskStatus(payload["status"])
        return cls(**payload)


@dataclass(slots=True)
class TaskEvent:
    id: str
    task_id: str
    event_type: str
    payload: dict[str, Any]
    created_at: str

    @classmethod
    def create(cls, task_id: str, event_type: str, payload: dict[str, Any]) -> "TaskEvent":
        return cls(
            id=str(uuid4()),
            task_id=task_id,
            event_type=event_type,
            payload=payload,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskEvent":
        return cls(**payload)
