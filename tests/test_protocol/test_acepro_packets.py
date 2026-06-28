"""Tests for ACE Pro (ACE1) packet encoding and decoding.

Protocol is confirmed from community RE. These tests validate the encode/decode
implementation against known-format packets.

Source: printers-for-people/ACEResearch, Kobra-S1/ACEPRO
"""

import json
import struct

import pytest

from ace_bridge.protocol.acepro.packets import (
    FRAME_FOOTER,
    FRAME_HEADER,
    FrameError,
    build_request,
    build_response,
    decode_frame,
    encode_frame,
    find_frames,
)
from ace_bridge.utils.crc import crc16_mcrf4xx


def _build_raw_frame(payload: bytes) -> bytes:
    """Helper: build a valid ACE Pro frame from payload bytes."""
    crc = crc16_mcrf4xx(payload)
    length = struct.pack("<H", len(payload))
    crc_bytes = struct.pack("<H", crc)
    return FRAME_HEADER + length + payload + crc_bytes + FRAME_FOOTER


class TestEncodeFrame:
    def test_encode_produces_correct_header_footer(self) -> None:
        frame = encode_frame({"id": 1, "method": "get_status"})
        assert frame[:2] == FRAME_HEADER
        assert frame[-1:] == FRAME_FOOTER

    def test_encode_length_field_is_payload_size(self) -> None:
        payload_dict = {"id": 1, "method": "get_status"}
        frame = encode_frame(payload_dict)
        payload_bytes = json.dumps(payload_dict, separators=(",", ":")).encode()
        encoded_len = struct.unpack_from("<H", frame, 2)[0]
        assert encoded_len == len(payload_bytes)

    def test_encode_crc_is_over_payload_only(self) -> None:
        payload_dict = {"id": 1, "method": "get_status"}
        frame = encode_frame(payload_dict)
        payload_bytes = json.dumps(payload_dict, separators=(",", ":")).encode()
        payload_len = len(payload_bytes)
        crc_in_frame = struct.unpack_from("<H", frame, 4 + payload_len)[0]
        expected_crc = crc16_mcrf4xx(payload_bytes)
        assert crc_in_frame == expected_crc

    def test_encode_exceeds_max_frame_size_raises(self) -> None:
        big_payload = {"data": "x" * 1020}
        with pytest.raises(ValueError, match="exceeds maximum"):
            encode_frame(big_payload)


class TestDecodeFrame:
    def test_decode_valid_frame(self) -> None:
        payload = b'{"id":1,"method":"get_status"}'
        raw = _build_raw_frame(payload)
        packet = decode_frame(raw)
        assert packet.crc_valid
        assert packet.payload_json["method"] == "get_status"
        assert packet.request_id == 1

    def test_decode_response_frame(self) -> None:
        payload = b'{"id":1,"result":{"status":0},"code":0,"msg":"success"}'
        raw = _build_raw_frame(payload)
        packet = decode_frame(raw)
        assert packet.crc_valid
        assert packet.result == {"status": 0}
        assert packet.error_code == 0

    def test_decode_invalid_header_raises(self) -> None:
        bad = b"\x00\xaa\x03\x00" + b"foo" + b"\x00\x00\xfe"
        with pytest.raises(FrameError, match="Invalid header"):
            decode_frame(bad)

    def test_decode_invalid_footer_raises(self) -> None:
        payload = b'{"id":1}'
        crc = crc16_mcrf4xx(payload)
        raw = (
            FRAME_HEADER
            + struct.pack("<H", len(payload))
            + payload
            + struct.pack("<H", crc)
            + b"\x00"
        )
        with pytest.raises(FrameError, match="Invalid footer"):
            decode_frame(raw)

    def test_decode_too_short_raises(self) -> None:
        with pytest.raises(FrameError, match="too short"):
            decode_frame(b"\xff\xaa\x00")

    def test_decode_wrong_crc_detected(self) -> None:
        payload = b'{"id":1,"method":"get_status"}'
        raw = bytearray(_build_raw_frame(payload))
        # Corrupt one CRC byte
        raw[-2] ^= 0xFF
        packet = decode_frame(bytes(raw))
        assert not packet.crc_valid


class TestBuildHelpers:
    def test_build_request_roundtrip(self) -> None:
        frame = build_request("get_status", request_id=42)
        packet = decode_frame(frame)
        assert packet.crc_valid
        assert packet.method == "get_status"
        assert packet.request_id == 42

    def test_build_response_roundtrip(self) -> None:
        frame = build_response(42, {"temp": 25.3, "status": 0})
        packet = decode_frame(frame)
        assert packet.crc_valid
        assert packet.result == {"temp": 25.3, "status": 0}
        assert packet.error_code == 0

    def test_build_request_with_params(self) -> None:
        frame = build_request("feed_filament", 1, params={"index": 0, "length": 100, "speed": 50})
        packet = decode_frame(frame)
        assert packet.payload_json["params"]["index"] == 0


class TestFindFrames:
    def test_find_single_frame(self) -> None:
        payload = b'{"id":1}'
        raw = _build_raw_frame(payload)
        frames = find_frames(raw)
        assert len(frames) == 1
        assert frames[0] == (0, len(raw))

    def test_find_two_frames(self) -> None:
        frame1 = _build_raw_frame(b'{"id":1}')
        frame2 = _build_raw_frame(b'{"id":2}')
        buf = frame1 + frame2
        frames = find_frames(buf)
        assert len(frames) == 2

    def test_find_frames_with_noise_prefix(self) -> None:
        noise = b"\x00\x11\x22"
        frame = _build_raw_frame(b'{"id":1}')
        buf = noise + frame
        frames = find_frames(buf)
        assert len(frames) == 1
        start, end = frames[0]
        assert buf[start:end] == frame
