from __future__ import annotations

import argparse
from pathlib import Path

from personal_assistant.repositories.json_repo import (
    JsonNoteRepository,
    JsonTaskEventRepository,
    JsonTaskRepository,
)
from personal_assistant.services.importer import NoteImporter
from personal_assistant.services.reporting import build_weekly_report
from personal_assistant.services.telegram_bot import run_telegram_bot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="assistant", description="Personal LLM Execution Assistant")
    parser.add_argument("--data-dir", default=".assistant_data", help="Directory for JSON storage")

    sub = parser.add_subparsers(dest="command", required=True)

    import_notes = sub.add_parser("import-notes", help="Import markdown/txt notes")
    import_notes.add_argument("path", help="Path to file or directory")

    sub.add_parser("review-extraction", help="List normalized notes for manual review")

    weekly = sub.add_parser("weekly-review", help="Generate weekly report markdown")
    weekly.add_argument("--output", default="weekly_review.md", help="Output markdown file")

    remind = sub.add_parser("remind", help="Generate reminder digest")
    remind.add_argument("--mode", choices=["on-demand", "scheduled"], default="on-demand")

    tg = sub.add_parser("telegram-bot", help="Run Telegram bot in long-polling mode")
    tg.add_argument("--token", default=None, help="Telegram bot token (fallback: TELEGRAM_BOT_TOKEN)")

    return parser


def run() -> int:
    parser = build_parser()
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    note_repo = JsonNoteRepository(data_dir / "notes.json")
    task_repo = JsonTaskRepository(data_dir / "tasks.json")
    event_repo = JsonTaskEventRepository(data_dir / "task_events.json")
    _ = event_repo

    if args.command == "import-notes":
        importer = NoteImporter(note_repo, task_repo, event_repo)
        imported, skipped = importer.import_path(Path(args.path))
        created_tasks = len(task_repo.list_tasks())
        print(f"Imported: {imported}, skipped: {skipped}, total tasks: {created_tasks}")
        return 0

    if args.command == "review-extraction":
        notes = note_repo.list_notes()
        if not notes:
            print("No notes available.")
            return 0
        for note in notes:
            print(f"- {note.title} ({note.id})")
            print(f"  language={note.language_hint} path={note.path}")
            print(f"  normalized={note.normalized_json}")
        return 0

    if args.command == "weekly-review":
        report = build_weekly_report(task_repo.list_tasks())
        out_path = Path(args.output)
        out_path.write_text(report, encoding="utf-8")
        print(f"Weekly review written to {out_path}")
        return 0

    if args.command == "remind":
        report = build_weekly_report(task_repo.list_tasks())
        print(f"Reminder mode: {args.mode}")
        print(report)
        return 0

    if args.command == "telegram-bot":
        run_telegram_bot(data_dir=data_dir, token=args.token)
        return 0

    parser.print_help()
    return 1
