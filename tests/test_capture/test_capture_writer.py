"""Tests for capture writer and reader."""

import json
import tempfile
from pathlib import Path

import pytest

from ace_bridge.capture.reader import read_capture
from ace_bridge.capture.writer import CapturedPacket, CaptureWriter


@pytest.mark.asyncio
async def test_capture_writer_creates_file() -> None:
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = Path(f.name)

    try:
        async with CaptureWriter(path) as writer:
            packet = CapturedPacket(
                interface="rs485",
                direction="rx",
                raw=b"\xaa\x01\x04",
            )
            await writer.write(packet)

        assert path.exists()
        lines = path.read_text().strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["interface"] == "rs485"
        assert data["direction"] == "rx"
        assert data["raw_hex"] == "AA 01 04"
        assert data["length"] == 3
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_capture_writer_multiple_packets() -> None:
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = Path(f.name)

    try:
        async with CaptureWriter(path) as writer:
            for i in range(10):
                packet = CapturedPacket(
                    interface="usb",
                    direction="tx",
                    raw=bytes([i]),
                )
                await writer.write(packet)

        lines = path.read_text().strip().splitlines()
        assert len(lines) == 10
    finally:
        path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_capture_roundtrip() -> None:
    """Write then read back; verify data is preserved."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        path = Path(f.name)

    try:
        original = CapturedPacket(
            interface="rs485",
            direction="rx",
            raw=b"\xaa\xbb\xcc",
            notes="test packet",
        )
        async with CaptureWriter(path) as writer:
            await writer.write(original)

        packets = list(read_capture(path))
        assert len(packets) == 1
        assert packets[0].interface == "rs485"
        assert packets[0].direction == "rx"
        assert packets[0].raw == b"\xaa\xbb\xcc"
        assert packets[0].notes == "test packet"
    finally:
        path.unlink(missing_ok=True)
