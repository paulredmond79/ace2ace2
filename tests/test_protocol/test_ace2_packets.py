"""Tests for ACE 2 Pro RS485 packet encoding and decoding.

Protocol confirmed from: hakimio IDA Pro MCU firmware analysis.
Frame format: 0xFF 0xAA + FLAGS + SEQ(2) + CMD(1) + LEN(1) + proto_payload + CRC16(2) + 0xFE
"""

import struct
import pytest

from ace_bridge.protocol.ace2.packets import (
    FRAME_HEADER,
    FRAME_FOOTER,
    FLAGS_REQUEST,
    FLAGS_RESPONSE,
    ACE2Command,
    ACE2SlotState,
    ACE2Packet,
    FrameError,
    decode_frame,
    encode_frame,
    encode_discover_request,
    find_frames,
)
from ace_bridge.utils.crc import crc16_kermit


def _build_raw_frame(
    flags: int,
    seq: int,
    cmd: ACE2Command,
    payload: bytes = b"",
) -> bytes:
    """Build a valid ACE 2 Pro frame."""
    seq_bytes = struct.pack("<H", seq)
    header_fields = bytes([flags]) + seq_bytes + bytes([int(cmd), len(payload)])
    crc_data = header_fields + payload
    crc = crc16_kermit(crc_data)
    return FRAME_HEADER + header_fields + payload + struct.pack("<H", crc) + FRAME_FOOTER


class TestEncodeFrame:
    def test_encode_produces_correct_header_footer(self) -> None:
        frame = encode_frame(ACE2Command.GET_STATUS, seq=1)
        assert frame[:2] == FRAME_HEADER
        assert frame[-1:] == FRAME_FOOTER

    def test_encode_flags_byte(self) -> None:
        frame = encode_frame(ACE2Command.GET_STATUS, seq=1, flags=FLAGS_REQUEST)
        assert frame[2] == FLAGS_REQUEST

    def test_encode_seq_little_endian(self) -> None:
        frame = encode_frame(ACE2Command.GET_STATUS, seq=0x0102)
        assert frame[3] == 0x02  # SEQ_LO
        assert frame[4] == 0x01  # SEQ_HI

    def test_encode_cmd_byte(self) -> None:
        frame = encode_frame(ACE2Command.GET_STATUS, seq=1)
        assert frame[5] == int(ACE2Command.GET_STATUS)

    def test_encode_payload_length_byte(self) -> None:
        payload = b"\x01\x02\x03"
        frame = encode_frame(ACE2Command.GET_STATUS, seq=1, payload=payload)
        assert frame[6] == 3

    def test_encode_payload_too_large_raises(self) -> None:
        with pytest.raises(ValueError, match="exceeds maximum"):
            encode_frame(ACE2Command.GET_STATUS, seq=1, payload=b"\x00" * 101)

    def test_encode_crc_over_flags_through_payload(self) -> None:
        payload = b"\x01\x02"
        frame = encode_frame(ACE2Command.GET_STATUS, seq=5, payload=payload, flags=FLAGS_REQUEST)
        crc_data = frame[2 : 7 + len(payload)]  # FLAGS through PAYLOAD
        expected_crc = crc16_kermit(crc_data)
        frame_crc = struct.unpack_from("<H", frame, 7 + len(payload))[0]
        assert frame_crc == expected_crc


class TestDecodeFrame:
    def test_decode_discover_request(self) -> None:
        raw = _build_raw_frame(FLAGS_REQUEST, seq=0, cmd=ACE2Command.DISCOVER_DEVICE)
        packet = decode_frame(raw)
        assert packet.crc_valid
        assert packet.command == ACE2Command.DISCOVER_DEVICE
        assert packet.is_request
        assert not packet.is_response

    def test_decode_response_flag(self) -> None:
        raw = _build_raw_frame(FLAGS_RESPONSE, seq=1, cmd=ACE2Command.GET_STATUS)
        packet = decode_frame(raw)
        assert packet.is_response
        assert not packet.is_request

    def test_decode_seq_value(self) -> None:
        raw = _build_raw_frame(FLAGS_REQUEST, seq=0x1234, cmd=ACE2Command.GET_STATUS)
        packet = decode_frame(raw)
        assert packet.seq == 0x1234

    def test_decode_with_payload(self) -> None:
        payload = b"\x08\x01\x10\x00"  # placeholder proto bytes
        raw = _build_raw_frame(FLAGS_REQUEST, seq=1, cmd=ACE2Command.FEED_OR_ROLLBACK, payload=payload)
        packet = decode_frame(raw)
        assert packet.crc_valid
        assert packet.payload == payload

    def test_decode_wrong_crc_detected(self) -> None:
        raw = bytearray(_build_raw_frame(FLAGS_REQUEST, seq=0, cmd=ACE2Command.GET_STATUS))
        raw[-2] ^= 0xFF
        packet = decode_frame(bytes(raw))
        assert not packet.crc_valid

    def test_decode_too_short_raises(self) -> None:
        with pytest.raises(FrameError, match="too short"):
            decode_frame(b"\xFF\xAA\x00")

    def test_decode_bad_header_raises(self) -> None:
        with pytest.raises(FrameError, match="Invalid header"):
            decode_frame(b"\xAA\xFF\x00\x00\x00\x06\x00\x00\x00\xFE")

    def test_decode_bad_footer_raises(self) -> None:
        raw = bytearray(_build_raw_frame(FLAGS_REQUEST, seq=0, cmd=ACE2Command.GET_STATUS))
        raw[-1] = 0x00
        with pytest.raises(FrameError, match="Invalid footer"):
            decode_frame(bytes(raw))

    def test_decode_roundtrip(self) -> None:
        original_payload = b"\x08\x02"
        frame = encode_frame(ACE2Command.DRYING, seq=99, payload=original_payload)
        packet = decode_frame(frame)
        assert packet.crc_valid
        assert packet.seq == 99
        assert packet.command == ACE2Command.DRYING
        assert packet.payload == original_payload


class TestDiscoverFrame:
    def test_discover_request_structure(self) -> None:
        frame = encode_discover_request(seq=0)
        packet = decode_frame(frame)
        assert packet.command == ACE2Command.DISCOVER_DEVICE
        assert packet.payload == b""
        assert packet.flags == FLAGS_REQUEST
        assert packet.crc_valid


class TestCommandEnum:
    def test_all_known_commands_have_values(self) -> None:
        assert ACE2Command.DISCOVER_DEVICE == 0x00
        assert ACE2Command.ASSIGN_DEVICE_ID == 0x01
        assert ACE2Command.GET_STATUS == 0x06
        assert ACE2Command.FEED_OR_ROLLBACK == 0x08
        assert ACE2Command.GET_TEMP == 0x40
        assert ACE2Command.MOTOR_MOVE == 0x48


class TestSlotState:
    def test_all_state_codes_present(self) -> None:
        assert ACE2SlotState.READY == 0x00
        assert ACE2SlotState.FEEDING == 0x01
        assert ACE2SlotState.STUCK_ERROR == 0x85
        assert ACE2SlotState.MOTOR_ERROR == 0x87


class TestFindFrames:
    def test_find_single_frame(self) -> None:
        raw = _build_raw_frame(FLAGS_REQUEST, seq=0, cmd=ACE2Command.GET_STATUS)
        frames = find_frames(raw)
        assert len(frames) == 1
        assert frames[0] == (0, len(raw))

    def test_find_two_frames(self) -> None:
        f1 = _build_raw_frame(FLAGS_REQUEST, seq=0, cmd=ACE2Command.GET_STATUS)
        f2 = _build_raw_frame(FLAGS_RESPONSE, seq=0, cmd=ACE2Command.GET_STATUS)
        frames = find_frames(f1 + f2)
        assert len(frames) == 2

    def test_noise_before_frame(self) -> None:
        noise = b"\x00\x11\x22\x33"
        raw = _build_raw_frame(FLAGS_REQUEST, seq=0, cmd=ACE2Command.DISCOVER_DEVICE)
        frames = find_frames(noise + raw)
        assert len(frames) == 1
        start, end = frames[0]
        assert (noise + raw)[start:end] == raw
