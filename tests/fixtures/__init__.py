"""Test fixture loader utilities."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent


def load_fixture(relative_path: str) -> bytes:
    """Load a binary fixture file for use in protocol tests.

    Example:
        raw = load_fixture("ace2_pro/startup_sequence.bin")
        packet = decode_ace2_packet(raw)
    """
    path = FIXTURES_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(
            f"Fixture not found: {path}\n"
            "Capture real packets and save them to tests/fixtures/ "
            "before writing protocol decode tests."
        )
    return path.read_bytes()
