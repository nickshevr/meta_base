from __future__ import annotations

from personal_assistant.cli import build_parser


def test_cli_has_expected_commands() -> None:
    parser = build_parser()
    args = parser.parse_args(["import-notes", "./notes"])
    assert args.command == "import-notes"
    assert args.path == "./notes"


def test_cli_has_telegram_bot_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["telegram-bot", "--token", "123:abc"])
    assert args.command == "telegram-bot"
    assert args.token == "123:abc"
