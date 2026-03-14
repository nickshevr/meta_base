from __future__ import annotations

from personal_assistant.cli import build_parser


def test_cli_has_expected_commands() -> None:
    parser = build_parser()
    args = parser.parse_args(["import-notes", "./notes"])
    assert args.command == "import-notes"
    assert args.path == "./notes"
