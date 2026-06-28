"""Capture file reader and decoder for offline analysis."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from ace_bridge.capture.writer import CapturedPacket


def read_capture(path: Path) -> Iterator[CapturedPacket]:
    """Read a JSONL capture file and yield CapturedPacket objects."""
    with path.open(encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                yield CapturedPacket(
                    interface=data["interface"],
                    direction=data["direction"],
                    raw=bytes.fromhex(data["raw_hex"].replace(" ", "")),
                    timestamp=data.get("timestamp", 0.0),
                    wall_time=datetime.fromisoformat(data.get("wall_time", "1970-01-01T00:00:00+00:00")),
                    decoded=data.get("decoded"),
                    crc_valid=data.get("crc_valid"),
                    notes=data.get("notes"),
                )
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                raise ValueError(f"Invalid capture record at line {line_num}: {e}") from e


def export_csv(path: Path, output_path: Optional[Path] = None) -> str:
    """Export a capture file to CSV format."""
    import csv
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "timestamp", "wall_time", "interface", "direction",
        "length", "raw_hex", "crc_valid", "notes",
    ])
    for packet in read_capture(path):
        writer.writerow([
            packet.timestamp,
            packet.wall_time.isoformat(),
            packet.interface,
            packet.direction,
            len(packet.raw),
            packet.raw.hex(" ").upper(),
            packet.crc_valid,
            packet.notes or "",
        ])

    csv_text = buf.getvalue()
    if output_path:
        output_path.write_text(csv_text)
    return csv_text
