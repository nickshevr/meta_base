from __future__ import annotations

import re
from typing import Any


def infer_language_hint(text: str) -> str:
    cyr = len(re.findall(r"[А-Яа-я]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    if cyr > 0 and lat > 0:
        return "ru+en"
    if cyr > 0:
        return "ru"
    return "en"


def normalize_note_to_json(raw_text: str) -> dict:
    """Local fallback normalizer.

    MVP placeholder until external LLM integration is added.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    action_candidates = [
        line
        for line in lines
        if line.lower().startswith(("todo", "action", "действие", "сделать", "- [ ]"))
    ]
    return {
        "summary": lines[0] if lines else "",
        "action_candidates": action_candidates,
        "line_count": len(lines),
    }


def extract_tasks(raw_text: str) -> list[dict[str, Any]]:
    """Rule-based fallback extractor until LLM extraction is wired in."""
    tasks: list[dict[str, Any]] = []
    for line in raw_text.splitlines():
        normalized = line.strip()
        if not normalized:
            continue

        lowered = normalized.lower()
        if lowered.startswith(("todo:", "action:", "действие:", "сделать:")):
            title = normalized.split(":", maxsplit=1)[1].strip()
            if title:
                tasks.append(
                    {
                        "title": title,
                        "description": normalized,
                        "owner": "self",
                        "due_date": None,
                        "tags": [],
                        "confidence": 0.9,
                    }
                )
            continue

        if normalized.startswith("- [ ]"):
            title = normalized.removeprefix("- [ ]").strip()
            if title:
                tasks.append(
                    {
                        "title": title,
                        "description": normalized,
                        "owner": "self",
                        "due_date": None,
                        "tags": [],
                        "confidence": 0.8,
                    }
                )

    return tasks
