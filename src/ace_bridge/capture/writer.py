"""Capture file writer.

Records every packet observed on RS485 and USB to a JSONL file for offline analysis.

Each line is a JSON object with:
- timestamp (monotonic, float seconds)
- wall_time (ISO8601)
- interface ("rs485" | "usb")
- direction ("rx" | "tx")
- raw_hex (space-separated uppercase hex)
- length (byte count)
- decoded (dict of decoded fields, if available)
- crc_valid (bool | null if CRC unknown)
- notes (optional free-text for annotations)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Literal

logger = logging.getLogger(__name__)

Interface = Literal["rs485", "usb"]
Direction = Literal["rx", "tx"]


@dataclass
class CapturedPacket:
    """A single captured packet."""

    interface: Interface
    direction: Direction
    raw: bytes
    timestamp: float = field(default_factory=time.monotonic)
    wall_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    decoded: dict[str, object] | None = None
    crc_valid: bool | None = None
    notes: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "timestamp": self.timestamp,
            "wall_time": self.wall_time.isoformat(),
            "interface": self.interface,
            "direction": self.direction,
            "raw_hex": self.raw.hex(" ").upper(),
            "length": len(self.raw),
            "decoded": self.decoded,
            "crc_valid": self.crc_valid,
            "notes": self.notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


class CaptureWriter:
    """Async JSONL capture writer.

    Buffers packets in a queue and flushes to disk asynchronously.
    Never blocks the main bridge loop.

    Usage:
        async with CaptureWriter(Path("captures/session.jsonl")) as writer:
            await writer.write(packet)
    """

    def __init__(self, path: Path, buffer_size: int = 1000) -> None:
        self._path = path
        self._queue: asyncio.Queue[CapturedPacket | None] = asyncio.Queue(maxsize=buffer_size)
        self._file: IO[str] | None = None
        self._task: asyncio.Task[None] | None = None
        self._written = 0

    async def __aenter__(self) -> CaptureWriter:
        await self.start()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.stop()

    async def start(self) -> None:
        """Open capture file and start background writer task."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self._path.open("a", encoding="utf-8")
        self._task = asyncio.create_task(self._writer_loop(), name="capture_writer")
        logger.info("Capture writer started: %s", self._path)

    async def stop(self) -> None:
        """Drain queue and close file."""
        await self._queue.put(None)  # sentinel
        if self._task:
            await self._task
        if self._file:
            self._file.close()
        logger.info("Capture writer stopped. %d packets written to %s", self._written, self._path)

    async def write(self, packet: CapturedPacket) -> None:
        """Enqueue a packet for writing. Non-blocking."""
        try:
            self._queue.put_nowait(packet)
        except asyncio.QueueFull:
            logger.warning("Capture queue full — dropping packet")

    async def _writer_loop(self) -> None:
        """Background task: drain queue and write to file."""
        while True:
            packet = await self._queue.get()
            if packet is None:  # sentinel
                break
            assert self._file is not None
            self._file.write(packet.to_json() + "\n")
            self._written += 1
            self._queue.task_done()
