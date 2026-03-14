from __future__ import annotations

from datetime import datetime, timezone, timedelta

from personal_assistant.models import Task, TaskStatus


def build_weekly_report(tasks: list[Task], stale_days: int = 7) -> str:
    now = datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(days=stale_days)

    overdue: list[Task] = []
    upcoming: list[Task] = []
    stale: list[Task] = []

    for task in tasks:
        if task.status in {TaskStatus.DONE, TaskStatus.DROPPED}:
            continue

        if task.due_date:
            due = datetime.fromisoformat(task.due_date)
            if due < now:
                overdue.append(task)
            elif due < now + timedelta(days=7):
                upcoming.append(task)

        updated_at = datetime.fromisoformat(task.updated_at)
        if updated_at < stale_cutoff:
            stale.append(task)

    lines = ["# Weekly Review", "", "## Forgotten / Stale", *format_tasks(stale), "", "## Overdue", *format_tasks(overdue), "", "## Due this week", *format_tasks(upcoming)]
    return "\n".join(lines).strip() + "\n"


def format_tasks(tasks: list[Task]) -> list[str]:
    if not tasks:
        return ["- None"]
    return [f"- [{task.status.value}] {task.title} (id: {task.id})" for task in tasks]
