from __future__ import annotations

import re


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
