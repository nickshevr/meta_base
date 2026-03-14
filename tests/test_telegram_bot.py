from __future__ import annotations

from pathlib import Path

from personal_assistant.services.telegram_bot import TelegramBotApp, split_long_message


class FakeTelegramApiClient:
    def __init__(self) -> None:
        self.sent: list[tuple[int, str]] = []

    def send_message(self, chat_id: int, text: str) -> None:
        self.sent.append((chat_id, text))


def test_plain_text_message_imports_note_and_creates_task(tmp_path: Path) -> None:
    api = FakeTelegramApiClient()
    app = TelegramBotApp(data_dir=tmp_path, api_client=api)  # type: ignore[arg-type]

    responses = app.handle_text("TODO: send recap")

    assert len(responses) == 1
    assert responses[0].startswith("Imported: 1, skipped: 0")
    assert len(app.note_repo.list_notes()) == 1
    assert len(app.task_repo.list_tasks()) == 1


def test_weekly_command_returns_report_sections(tmp_path: Path) -> None:
    api = FakeTelegramApiClient()
    app = TelegramBotApp(data_dir=tmp_path, api_client=api)  # type: ignore[arg-type]
    app.handle_text("TODO: ship draft")

    responses = app.handle_text("/weekly")
    report = "\n".join(responses)

    assert "# Weekly Review" in report
    assert "## Weekly Priorities" in report


def test_process_update_sends_reply(tmp_path: Path) -> None:
    api = FakeTelegramApiClient()
    app = TelegramBotApp(data_dir=tmp_path, api_client=api)  # type: ignore[arg-type]

    app.process_update({"update_id": 1, "message": {"chat": {"id": 123}, "text": "/help"}})

    assert len(api.sent) == 1
    chat_id, text = api.sent[0]
    assert chat_id == 123
    assert "/weekly" in text


def test_split_long_message_chunks() -> None:
    chunks = split_long_message("a" * 8000, chunk_size=3500)
    assert len(chunks) == 3
    assert sum(len(chunk) for chunk in chunks) == 8000
