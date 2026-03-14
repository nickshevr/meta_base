from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from personal_assistant.repositories.json_repo import JsonNoteRepository, JsonTaskEventRepository, JsonTaskRepository
from personal_assistant.services.importer import NoteImporter
from personal_assistant.services.reporting import build_weekly_report


class TelegramApiClient:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"

    def get_updates(self, offset: int | None = None, timeout: int = 30) -> list[dict[str, Any]]:
        params = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        payload = self._post("getUpdates", params)
        return payload.get("result", [])

    def send_message(self, chat_id: int, text: str) -> None:
        self._post("sendMessage", {"chat_id": chat_id, "text": text})

    def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = urllib.parse.urlencode(payload).encode("utf-8")
        request = urllib.request.Request(
            url=f"{self.base_url}/{method}",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            raw = response.read().decode("utf-8")
        parsed = json.loads(raw)
        if not parsed.get("ok"):
            raise RuntimeError(f"Telegram API error for {method}: {parsed}")
        return parsed


class TelegramBotApp:
    def __init__(self, data_dir: Path, api_client: TelegramApiClient) -> None:
        self.data_dir = data_dir
        self.api_client = api_client

        self.note_repo = JsonNoteRepository(data_dir / "notes.json")
        self.task_repo = JsonTaskRepository(data_dir / "tasks.json")
        self.event_repo = JsonTaskEventRepository(data_dir / "task_events.json")
        self.importer = NoteImporter(self.note_repo, self.task_repo, self.event_repo)

    def run_forever(self, poll_interval_s: float = 1.0) -> None:
        offset: int | None = None
        while True:
            updates = self.api_client.get_updates(offset=offset, timeout=30)
            for update in updates:
                offset = update["update_id"] + 1
                self.process_update(update)
            time.sleep(poll_interval_s)

    def process_update(self, update: dict[str, Any]) -> None:
        message = update.get("message", {})
        chat = message.get("chat", {})
        chat_id = chat.get("id")
        text = (message.get("text") or "").strip()

        if not chat_id:
            return

        for reply in self.handle_text(text):
            self.api_client.send_message(chat_id=chat_id, text=reply)

    def handle_text(self, text: str) -> list[str]:
        if not text:
            return ["Пришлите текст заметки или команду /help"]

        if text.startswith("/start") or text.startswith("/help"):
            return [
                "Команды:\n"
                "/import <текст заметки> — импорт заметки\n"
                "/weekly — weekly review\n"
                "/remind — reminder digest\n"
                "Или отправьте обычный текст, он будет импортирован как заметка."
            ]

        if text.startswith("/weekly"):
            report = build_weekly_report(self.task_repo.list_tasks())
            return split_long_message(report)

        if text.startswith("/remind"):
            report = build_weekly_report(self.task_repo.list_tasks())
            return ["Reminder mode: on-demand", *split_long_message(report)]

        if text.startswith("/import"):
            payload = text.removeprefix("/import").strip()
            if not payload:
                return ["После /import добавьте текст заметки."]
            return [self._import_note_text(payload)]

        return [self._import_note_text(text)]

    def _import_note_text(self, payload: str) -> str:
        inbox_dir = self.data_dir / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        note_path = inbox_dir / f"telegram_{int(time.time() * 1000)}.txt"
        note_path.write_text(payload, encoding="utf-8")
        imported, skipped = self.importer.import_path(note_path)
        total_tasks = len(self.task_repo.list_tasks())
        return f"Imported: {imported}, skipped: {skipped}, total tasks: {total_tasks}"


def split_long_message(text: str, chunk_size: int = 3500) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks


def run_telegram_bot(data_dir: Path, token: str | None = None) -> None:
    resolved_token = token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not resolved_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set")

    app = TelegramBotApp(data_dir=data_dir, api_client=TelegramApiClient(resolved_token))
    app.run_forever()
