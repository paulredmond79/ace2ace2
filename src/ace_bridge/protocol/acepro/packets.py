"""ACE Pro (ACE1) USB protocol — packet encoding and decoding.

Protocol confirmed by community reverse engineering:
- Source: printers-for-people/ACEResearch, Kobra-S1/ACEPRO, multiple Klipper drivers
- Confidence: High

Frame format:
    [0xFF][0xAA][LEN_LO][LEN_HI][...JSON payload...][CRC_LO][CRC_HI][0xFE]

Payload is UTF-8 JSON (JSON-RPC style):
    Request:  {"id": 1, "method": "get_status", "params": {}}
    Response: {"id": 1, "result": {...}, "code": 0, "msg": "success"}

CRC: CRC-16/MCRF4XX over JSON payload bytes only (not header/footer/length).

See docs/Protocol.md for full specification.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from ace_bridge.utils.crc import crc16_mcrf4xx

FRAME_HEADER = b"\xff\xaa"
FRAME_FOOTER = b"\xfe"
MAX_FRAME_SIZE = 1024  # Device freezes if frame exceeds this


class ACEProMethod(StrEnum):
    """Known ACE Pro JSON-RPC method names.

    Source: printers-for-people/ACEResearch strace captures + Klipper driver code.
    """

    GET_STATUS = "get_status"
    GET_INFO = "get_info"
    GET_FILAMENT_INFO = "get_filament_info"
    DRYING = "drying"
    DRYING_STOP = "drying_stop"
    FEED_FILAMENT = "feed_filament"
    STOP_FEED_FILAMENT = "stop_feed_filament"
    UNWIND_FILAMENT = "unwind_filament"
    UPDATE_UNWINDING_SPEED = "update_unwinding_speed"
    STOP_UNWIND_FILAMENT = "stop_unwind_filament"
    START_FEED_ASSIST = "start_feed_assist"
    STOP_FEED_ASSIST = "stop_feed_assist"
    ENABLE_RFID = "enable_rfid"
    DISABLE_RFID = "disable_rfid"


@dataclass
class ACEProPacket:
    """Decoded ACE Pro USB packet."""

    payload_json: dict[str, Any]  # Decoded JSON payload
    raw: bytes  # Complete original frame bytes
    crc_valid: bool
    crc_expected: int
    crc_computed: int

    @property
    def method(self) -> str | None:
        """JSON-RPC method name (for requests)."""
        return self.payload_json.get("method")

    @property
    def request_id(self) -> int | None:
        return self.payload_json.get("id")

    @property
    def result(self) -> dict[str, Any] | None:
        return self.payload_json.get("result")

    @property
    def error_code(self) -> int | None:
        return self.payload_json.get("code")


class FrameError(Exception):
    """Error parsing an ACE Pro frame."""


def decode_frame(data: bytes) -> ACEProPacket:
    """Decode a complete ACE Pro frame from raw bytes.

    Args:
        data: Complete frame bytes including header, length, payload, CRC, footer

    Raises:
        FrameError: If the frame is malformed or too short
    """
    if len(data) < 7:  # min: 0xFF 0xAA + len(2) + payload(0) + crc(2) + 0xFE = 7
        raise FrameError(f"Frame too short: {len(data)} bytes (minimum 7)")

    if data[:2] != FRAME_HEADER:
        raise FrameError(f"Invalid header: expected FF AA, got {data[:2].hex().upper()}")

    if data[-1:] != FRAME_FOOTER:
        raise FrameError(f"Invalid footer: expected FE, got {data[-1]:02X}")

    payload_len = struct.unpack_from("<H", data, 2)[0]
    payload_end = 4 + payload_len

    if payload_end + 2 + 1 > len(data):
        raise FrameError(
            f"Frame truncated: header says payload={payload_len} bytes "
            f"but frame is only {len(data)} bytes"
        )

    payload_bytes = data[4:payload_end]
    crc_expected = struct.unpack_from("<H", data, payload_end)[0]
    crc_computed = crc16_mcrf4xx(payload_bytes)

    try:
        payload_json = json.loads(payload_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise FrameError(f"JSON decode failed: {e}") from e

    return ACEProPacket(
        payload_json=payload_json,
        raw=data,
        crc_valid=(crc_computed == crc_expected),
        crc_expected=crc_expected,
        crc_computed=crc_computed,
    )


def encode_frame(payload: dict[str, Any]) -> bytes:
    """Encode a JSON payload into an ACE Pro frame.

    Computes CRC-16/MCRF4XX over the JSON bytes and builds the complete frame.

    Args:
        payload: JSON-serialisable dict (request or response)

    Returns:
        Complete frame bytes ready for USB transmission

    Raises:
        ValueError: If encoded frame would exceed MAX_FRAME_SIZE
    """
    payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    _check_header_collision(payload_bytes)

    crc = crc16_mcrf4xx(payload_bytes)
    length = struct.pack("<H", len(payload_bytes))
    crc_bytes = struct.pack("<H", crc)

    frame = FRAME_HEADER + length + payload_bytes + crc_bytes + FRAME_FOOTER

    if len(frame) > MAX_FRAME_SIZE:
        raise ValueError(
            f"Encoded frame is {len(frame)} bytes, exceeds maximum {MAX_FRAME_SIZE}. "
            "Reduce payload size."
        )
    return frame


def build_request(method: str, request_id: int, params: dict[str, Any] | None = None) -> bytes:
    """Build a JSON-RPC request frame."""
    payload: dict[str, Any] = {"id": request_id, "method": method}
    if params:
        payload["params"] = params
    return encode_frame(payload)


def build_response(request_id: int, result: dict[str, Any], code: int = 0) -> bytes:
    """Build a JSON-RPC response frame."""
    payload: dict[str, Any] = {
        "id": request_id,
        "result": result,
        "code": code,
        "msg": "success" if code == 0 else "error",
    }
    return encode_frame(payload)


def find_frames(buf: bytes) -> list[tuple[int, int]]:
    """Scan a byte buffer for complete ACE Pro frames.

    Returns list of (start_index, end_index) pairs for each found frame.
    Caller should call decode_frame() on each slice.
    """
    frames: list[tuple[int, int]] = []
    i = 0
    while i < len(buf) - 1:
        if buf[i] == 0xFF and buf[i + 1] == 0xAA:
            if i + 4 <= len(buf):
                payload_len = struct.unpack_from("<H", buf, i + 2)[0]
                end = i + 4 + payload_len + 2 + 1  # header + len_field + payload + crc + footer
                if end <= len(buf) and buf[end - 1] == 0xFE:
                    frames.append((i, end))
                    i = end
                    continue
        i += 1
    return frames


def _check_header_collision(payload_bytes: bytes) -> None:
    """Warn if payload contains the frame header bytes.

    Source: printers-for-people/ACEResearch PROTOCOL.md safety note.
    If 0xFF 0xAA appears in the JSON payload, the device may freeze on next frame.
    """
    if FRAME_HEADER in payload_bytes:
        import warnings

        warnings.warn(
            "ACE Pro frame payload contains the header sequence 0xFF 0xAA. "
            "This may cause the device to freeze. Consider restructuring the payload.",
            stacklevel=3,
        )
