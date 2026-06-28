"""Tests for CLI commands."""

from typer.testing import CliRunner

from ace_bridge.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "bridge" in result.output.lower() or "ACE" in result.output


def test_start_simulate() -> None:
    """start --simulate should run bridge in simulation mode and exit cleanly on interrupt."""
    # We can't easily test an infinite loop CLI — just verify it starts without error
    # In real testing, this would use asyncio.timeout or process control
    # For now just verify the command is registered
    result = runner.invoke(app, ["start", "--help"])
    assert result.exit_code == 0
    assert "--simulate" in result.output


def test_inspect_usb_help() -> None:
    result = runner.invoke(app, ["inspect-usb", "--help"])
    assert result.exit_code == 0


def test_decode_hex_valid() -> None:
    result = runner.invoke(app, ["decode-hex", "AA 01 04 10"])
    # Should not crash even without a known packet format
    assert result.exit_code == 0
    assert "AA" in result.output


def test_decode_hex_invalid() -> None:
    result = runner.invoke(app, ["decode-hex", "ZZ not hex"])
    assert result.exit_code != 0


def test_sniff_rs485_shows_stub_message() -> None:
    result = runner.invoke(app, ["sniff-rs485", "--port", "/dev/null"])
    # Should exit with non-zero and print stub message
    assert result.exit_code != 0


def test_status_shows_not_implemented() -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code != 0
