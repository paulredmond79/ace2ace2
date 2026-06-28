"""ACE 2 Pro RS485 protocol — packet encoding and decoding.

Protocol confirmed by community reverse engineering:
- Source: hakimio IDA Pro MCU firmware analysis (gist 4916ff69add458fdc51aeea76f21efb9)
- Confidence: High for frame format; Medium for payload schemas (proto3 schema not public)

Frame format:
    [0xFF][0xAA][FLAGS][SEQ_LO][SEQ_HI][CMD][LEN][...payload...][CRC_LO][CRC_HI][0xFE]

Payload is Protocol Buffers proto3. Complete .proto schema is not yet publicly available.
See docs/Protocol.md for full specification and docs/Unknowns.md RS-2 for remaining gaps.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import IntEnum

from ace_bridge.utils.crc import crc16_kermit

FRAME_HEADER = b"\xff\xaa"
FRAME_FOOTER = b"\xfe"
HEADER_SIZE = 7  # 0xFF 0xAA FLAGS SEQ_LO SEQ_HI CMD LEN
FOOTER_SIZE = 3  # CRC_LO CRC_HI 0xFE
MIN_FRAME_SIZE = HEADER_SIZE + FOOTER_SIZE
MAX_PAYLOAD_SIZE = 100  # confirmed from MCU firmware

FLAGS_REQUEST = 0x00  # host → ACE
FLAGS_RESPONSE = 0x80  # ACE → host


class ACE2Command(IntEnum):
    """ACE 2 Pro command bytes.

    Source: hakimio IDA Pro MCU firmware analysis.
    Confidence: High — 78 commands enumerated from MCU dispatch table.
    """

    DISCOVER_DEVICE = 0x00
    ASSIGN_DEVICE_ID = 0x01
    IAP_UPGRADE = 0x02
    IAP_FIRMWARE = 0x03
    IAP_UPGRADE_FINISH = 0x04
    IAP_VERSION = 0x05
    GET_STATUS = 0x06
    GET_INFO = 0x07
    FEED_OR_ROLLBACK = 0x08
    STOP_FEED_OR_ROLLBACK = 0x09
    UPDATE_SPEED = 0x0A
    DRYING = 0x0B
    SET_DRY_TEMP = 0x0C
    GET_RFID_CACHE = 0x0D
    SET_RFID_ENABLE = 0x0E
    LINEAR_KEY_CALIBRATE = 0x0F
    GET_MATERIAL_INFO = 0x10
    SET_SLOT_STATUS = 0x11
    SET_MATERIAL_NAME = 0x12
    SET_FEED_CHECK = 0x13
    SET_PRINTER_STATUS = 0x14
    GET_TEMP = 0x40
    SET_DRY_POWER = 0x41
    SET_VALVE = 0x42
    GET_FILAMENT_INFO = 0x44
    FLASH_LED = 0x46
    SET_FAN = 0x47
    MOTOR_MOVE = 0x48
    GET_SENSOR_STATE = 0x49
    DRY_CMD = 0x4B
    GET_FEED_INFO = 0x4C
    MOTOR_TEST = 0x4D
    GET_MOTOR_STATUS = 0x4E

    UNKNOWN = 0xFF  # Catch-all for unrecognised commands


class ACE2SlotState(IntEnum):
    """ACE 2 Pro slot state codes.

    Source: hakimio IDA Pro firmware analysis.
    Confidence: High.
    """

    READY = 0x00
    FEEDING = 0x01
    ROLLBACK = 0x02
    ASSISTING = 0x03
    FEED_ERROR = 0x81
    ROLLBACK_ERROR = 0x82
    ASSIST_ERROR = 0x83
    PRELOAD_ERROR = 0x84
    STUCK_ERROR = 0x85
    TANGLED_ERROR = 0x86
    MOTOR_ERROR = 0x87

    UNKNOWN = 0xFF


@dataclass
class ACE2Packet:
    """Decoded ACE 2 Pro RS485 packet."""

    flags: int  # FLAGS byte (0x00 = request, 0x80 = response)
    seq: int  # 2-byte sequence counter (little-endian)
    command: ACE2Command
    payload: bytes  # Raw protobuf bytes (not yet decoded)
    raw: bytes  # Complete original frame bytes
    crc_valid: bool
    crc_expected: int
    crc_computed: int

    @property
    def is_response(self) -> bool:
        return bool(self.flags & FLAGS_RESPONSE)

    @property
    def is_request(self) -> bool:
        return not self.is_response


class FrameError(Exception):
    """Error parsing an ACE 2 Pro frame."""


def decode_frame(data: bytes) -> ACE2Packet:
    """Decode a complete ACE 2 Pro frame from raw bytes.

    Args:
        data: Complete frame bytes

    Raises:
        FrameError: If the frame is malformed
    """
    if len(data) < MIN_FRAME_SIZE:
        raise FrameError(f"Frame too short: {len(data)} bytes (minimum {MIN_FRAME_SIZE})")

    if data[:2] != FRAME_HEADER:
        raise FrameError(f"Invalid header: expected FF AA, got {data[:2].hex().upper()}")

    if data[-1:] != FRAME_FOOTER:
        raise FrameError(f"Invalid footer: expected FE, got {data[-1]:02X}")

    flags = data[2]
    seq = struct.unpack_from("<H", data, 3)[0]
    cmd_byte = data[5]
    payload_len = data[6]

    if 7 + payload_len + 3 > len(data):
        raise FrameError(
            f"Frame truncated: header says payload={payload_len} but frame has {len(data)} bytes"
        )

    payload = data[7 : 7 + payload_len]

    # CRC covers FLAGS through end of PAYLOAD
    crc_data = data[2 : 7 + payload_len]
    crc_computed = crc16_kermit(crc_data)
    crc_expected = struct.unpack_from("<H", data, 7 + payload_len)[0]

    try:
        command = ACE2Command(cmd_byte)
    except ValueError:
        command = ACE2Command.UNKNOWN

    return ACE2Packet(
        flags=flags,
        seq=seq,
        command=command,
        payload=payload,
        raw=data,
        crc_valid=(crc_computed == crc_expected),
        crc_expected=crc_expected,
        crc_computed=crc_computed,
    )


def encode_frame(
    command: ACE2Command,
    seq: int,
    payload: bytes = b"",
    flags: int = FLAGS_REQUEST,
) -> bytes:
    """Encode an ACE 2 Pro frame for transmission.

    Args:
        command: Command byte
        seq: Sequence counter (2 bytes, little-endian)
        payload: Protobuf-encoded payload (max 100 bytes)
        flags: FLAGS_REQUEST (0x00) or FLAGS_RESPONSE (0x80)

    Returns:
        Complete frame bytes ready for RS485 transmission

    Raises:
        ValueError: If payload exceeds MAX_PAYLOAD_SIZE
    """
    if len(payload) > MAX_PAYLOAD_SIZE:
        raise ValueError(f"Payload is {len(payload)} bytes, exceeds maximum {MAX_PAYLOAD_SIZE}")

    seq_bytes = struct.pack("<H", seq)
    header_fields = bytes([flags]) + seq_bytes + bytes([int(command), len(payload)])
    crc_data = header_fields + payload
    crc = crc16_kermit(crc_data)
    crc_bytes = struct.pack("<H", crc)

    return FRAME_HEADER + header_fields + payload + crc_bytes + FRAME_FOOTER


def encode_discover_request(seq: int = 0) -> bytes:
    """Build a DISCOVER_DEVICE broadcast frame.

    Sent by the host to discover all ACE 2 Pro units on the RS485 bus.
    Each unit responds with its 96-bit STM32 unique ID.
    """
    return encode_frame(ACE2Command.DISCOVER_DEVICE, seq=seq, payload=b"")


def encode_assign_device_id(uid: tuple[int, int, int], seq: int, initial_seq: int) -> bytes:
    """Build an ASSIGN_DEVICE_ID frame for a specific ACE 2 Pro.

    Args:
        uid: 3-tuple of 32-bit STM32 unique ID words (from DISCOVER response)
        seq: Current sequence counter
        initial_seq: Initial SEQ value to assign to this device

    ⚠️ Unknown: Exact protobuf encoding of UID + initial_seq.
    See docs/Unknowns.md RS-2. Placeholder implementation.
    """
    # TODO: Encode UID and initial_seq as protobuf once .proto schema is available
    # For now, use raw bytes as best guess
    payload = struct.pack("<IIIB", uid[0], uid[1], uid[2], initial_seq)
    return encode_frame(ACE2Command.ASSIGN_DEVICE_ID, seq=seq, payload=payload)


def find_frames(buf: bytes) -> list[tuple[int, int]]:
    """Scan a byte buffer for complete ACE 2 Pro frames.

    Returns list of (start_index, end_index) pairs.
    """
    frames: list[tuple[int, int]] = []
    i = 0
    while i < len(buf) - 1:
        if buf[i] == 0xFF and buf[i + 1] == 0xAA:
            if i + 7 <= len(buf):
                payload_len = buf[i + 6]
                end = i + 7 + payload_len + 3  # header(7) + payload + crc(2) + footer(1)
                if end <= len(buf) and buf[end - 1] == 0xFE:
                    frames.append((i, end))
                    i = end
                    continue
        i += 1
    return frames
