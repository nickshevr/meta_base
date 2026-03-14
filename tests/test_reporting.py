from __future__ import annotations

from datetime import datetime, timedelta, timezone

from personal_assistant.models import Task, TaskStatus
from personal_assistant.services.reporting import build_weekly_report, calculate_priority_score, find_duplicate_task_titles


def make_task(
    task_id: str,
    title: str,
    *,
    status: TaskStatus = TaskStatus.OPEN,
    due_in_days: int | None = None,
    updated_days_ago: int = 0,
    tags: list[str] | None = None,
    priority_score: float = 0.0,
) -> Task:
    now = datetime.now(timezone.utc)
    due_date = (now + timedelta(days=due_in_days)).isoformat() if due_in_days is not None else None
    return Task(
        id=task_id,
        title=title,
        description="",
        source_note_id="n1",
        owner="self",
        status=status,
        priority_score=priority_score,
        due_date=due_date,
        created_at=now.isoformat(),
        updated_at=(now - timedelta(days=updated_days_ago)).isoformat(),
        tags=tags or [],
    )


def test_weekly_report_contains_new_sections() -> None:
    task = make_task("t1", "Ship draft", due_in_days=1)

    report = build_weekly_report([task])
    assert "# Weekly Review" in report
    assert "## Weekly Priorities" in report
    assert "## Duplicate Candidates" in report
    assert "## Due this week" in report
    assert "Ship draft" in report


def test_priority_score_prefers_overdue_and_important_tasks() -> None:
    now = datetime.now(timezone.utc)
    overdue = make_task("t1", "Overdue task", due_in_days=-1)
    low = make_task("t2", "Backlog cleanup", due_in_days=14)
    important = make_task("t3", "Critical bug", due_in_days=3, tags=["critical", "blocker"])

    overdue_score = calculate_priority_score(overdue, now=now)
    low_score = calculate_priority_score(low, now=now)
    important_score = calculate_priority_score(important, now=now)

    assert overdue_score > important_score > low_score


def test_duplicate_detection_normalizes_case_and_spaces() -> None:
    tasks = [
        make_task("t1", "Prepare weekly report"),
        make_task("t2", "prepare   weekly   report"),
        make_task("t3", "Another item"),
    ]

    duplicates = find_duplicate_task_titles(tasks)
    assert duplicates == [("prepare weekly report", 2)]


def test_stale_task_is_marked_in_forgotten_section() -> None:
    stale = make_task("t1", "Follow up", updated_days_ago=10)
    report = build_weekly_report([stale], stale_days=7)

    assert "## Forgotten / Stale" in report
    assert "Follow up" in report
