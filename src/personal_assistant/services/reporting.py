from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from personal_assistant.models import Task, TaskStatus


IMPORTANT_TAGS = {"p0", "critical", "important", "vip", "goal"}
BLOCKER_TAGS = {"blocker", "blocked", "dependency"}


def build_weekly_report(tasks: list[Task], stale_days: int = 7) -> str:
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=stale_days)

    overdue: list[Task] = []
    upcoming: list[Task] = []
    stale: list[Task] = []

    active_tasks = [task for task in tasks if task.status not in {TaskStatus.DONE, TaskStatus.DROPPED}]

    for task in active_tasks:
        if task.due_date:
            due = datetime.fromisoformat(task.due_date)
            if due < now:
                overdue.append(task)
            elif due <= now + timedelta(days=7):
                upcoming.append(task)

        updated_at = datetime.fromisoformat(task.updated_at)
        if updated_at < stale_cutoff:
            stale.append(task)

    priorities = rank_weekly_priorities(active_tasks, now=now)
    duplicates = find_duplicate_task_titles(active_tasks)

    lines = [
        "# Weekly Review",
        "",
        "## Forgotten / Stale",
        *format_tasks(stale),
        "",
        "## Weekly Priorities",
        *format_priorities(priorities),
        "",
        "## Duplicate Candidates",
        *format_duplicates(duplicates),
        "",
        "## Overdue",
        *format_tasks(overdue),
        "",
        "## Due this week",
        *format_tasks(upcoming),
    ]
    return "\n".join(lines).strip() + "\n"


def rank_weekly_priorities(tasks: list[Task], now: datetime, limit: int = 5) -> list[tuple[Task, float]]:
    scored = [(task, calculate_priority_score(task, now=now)) for task in tasks]
    return sorted(scored, key=lambda item: item[1], reverse=True)[:limit]


def calculate_priority_score(task: Task, now: datetime) -> float:
    score = 0.0

    if task.due_date:
        due = datetime.fromisoformat(task.due_date)
        days_to_due = (due - now).total_seconds() / 86400
        if days_to_due < 0:
            score += 100
        elif days_to_due <= 2:
            score += 40
        elif days_to_due <= 7:
            score += 20

    lower_tags = {tag.lower() for tag in task.tags}
    if lower_tags & IMPORTANT_TAGS:
        score += 20
    if lower_tags & BLOCKER_TAGS:
        score += 15

    if task.priority_score > 0:
        score += min(task.priority_score, 25)

    if task.status == TaskStatus.IN_PROGRESS:
        score += 5

    return round(score, 2)


def find_duplicate_task_titles(tasks: list[Task]) -> list[tuple[str, int]]:
    normalized_titles = [normalize_title(task.title) for task in tasks if normalize_title(task.title)]
    counts = Counter(normalized_titles)
    duplicates = [(title, count) for title, count in counts.items() if count > 1]
    return sorted(duplicates, key=lambda item: (-item[1], item[0]))


def normalize_title(title: str) -> str:
    return " ".join(title.lower().split())


def format_tasks(tasks: list[Task]) -> list[str]:
    if not tasks:
        return ["- None"]
    return [f"- [{task.status.value}] {task.title} (id: {task.id})" for task in tasks]


def format_priorities(priorities: list[tuple[Task, float]]) -> list[str]:
    if not priorities:
        return ["- None"]
    return [f"- ({score:.1f}) [{task.status.value}] {task.title} (id: {task.id})" for task, score in priorities]


def format_duplicates(duplicates: list[tuple[str, int]]) -> list[str]:
    if not duplicates:
        return ["- None"]
    return [f"- {title} (x{count})" for title, count in duplicates]
