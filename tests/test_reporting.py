from __future__ import annotations

from datetime import datetime, timezone, timedelta

from personal_assistant.models import Task, TaskStatus
from personal_assistant.services.reporting import build_weekly_report


def test_weekly_report_contains_sections() -> None:
    now = datetime.now(timezone.utc)
    task = Task(
        id="t1",
        title="Ship draft",
        description="",
        source_note_id="n1",
        owner="self",
        status=TaskStatus.OPEN,
        priority_score=0.0,
        due_date=(now + timedelta(days=1)).isoformat(),
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
        tags=[],
    )

    report = build_weekly_report([task])
    assert "# Weekly Review" in report
    assert "## Due this week" in report
    assert "Ship draft" in report
