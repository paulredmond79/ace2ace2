"""Tests for CRC utility functions.

CRC algorithms confirmed for ACE protocols:
- CRC-16/MCRF4XX: ACE Pro (ACE1) — poly 0x1021, init 0xFFFF, reflected
- CRC-16/Kermit (init 0xFFFF): ACE 2 Pro (ACE2) — poly 0x8408, init 0xFFFF

Note: The community implementation uses init=0xFFFF for both, making them
mathematically identical. Standard CRC-16/Kermit uses init=0x0000. Our
crc16_kermit() mirrors what the ACE2 MCU firmware computes (init=0xFFFF).

Sources:
- ACE1 CRC: Kobra-S1/ACEPRO serial_manager.py
- ACE2 CRC: hakimio IDA Pro analysis, MCU function sub_8010464
"""

from ace_bridge.utils.crc import (
    crc16_mcrf4xx,
    crc16_kermit,
    crc16_ibm,
    crc8_xor,
    crc8_sum,
    try_all_crcs,
)


class TestCRC16MCRF4XX:
    def test_known_check_value(self) -> None:
        # Standard check value for CRC-16/MCRF4XX with input b"123456789"
        # Source: https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-mcrf4xx
        assert crc16_mcrf4xx(b"123456789") == 0x6F91

    def test_empty(self) -> None:
        assert crc16_mcrf4xx(b"") == 0xFFFF

    def test_single_byte(self) -> None:
        # Deterministic — just verify it returns an integer in range
        result = crc16_mcrf4xx(b"\x00")
        assert 0 <= result <= 0xFFFF

    def test_consistency(self) -> None:
        data = b"get_status"
        assert crc16_mcrf4xx(data) == crc16_mcrf4xx(data)

    def test_different_inputs_differ(self) -> None:
        assert crc16_mcrf4xx(b"feed_filament") != crc16_mcrf4xx(b"unwind_filament")


class TestCRC16Kermit:
    def test_known_check_value(self) -> None:
        # Our crc16_kermit uses init=0xFFFF (matching ACE2 MCU firmware).
        # This is equivalent to CRC-16/MCRF4XX.
        # Standard CRC-16/Kermit (init=0x0000) = 0x2189; ours = 0x6F91.
        assert crc16_kermit(b"123456789") == 0x6F91

    def test_empty(self) -> None:
        assert crc16_kermit(b"") == 0xFFFF

    def test_matches_mcrf4xx(self) -> None:
        # Both use same poly and init — results should be identical
        data = b"\x00\x01\x06\x00"  # example header bytes
        assert crc16_kermit(data) == crc16_mcrf4xx(data)


class TestOtherCRCs:
    def test_crc16_ibm_known(self) -> None:
        assert crc16_ibm(b"123456789") == 0xBB3D

    def test_crc8_xor_empty(self) -> None:
        assert crc8_xor(b"") == 0

    def test_crc8_xor_single(self) -> None:
        assert crc8_xor(b"\xAA") == 0xAA

    def test_crc8_sum_overflow(self) -> None:
        assert crc8_sum(b"\xFF\x01") == 0x00


class TestTryAllCRCs:
    def test_returns_expected_keys(self) -> None:
        result = try_all_crcs(b"\x01\x02\x03")
        assert "crc16_mcrf4xx" in result
        assert "crc16_kermit" in result
        assert "crc16_ibm" in result
        assert "crc8_xor" in result

    def test_all_values_are_ints(self) -> None:
        for key, val in try_all_crcs(b"\xAA\xBB").items():
            assert isinstance(val, int), f"{key} is not int"

    def test_mcrf4xx_identified(self) -> None:
        # Verify try_all_crcs can identify which algo matches a known value
        data = b"123456789"
        expected = 0x6F91
        candidates = try_all_crcs(data)
        assert candidates["crc16_mcrf4xx"] == expected


# ⚠️ Add these once real capture packets are available:
#
# def test_ace1_crc_from_capture():
#     """Validate CRC matches a real ACE Pro captured packet.
#     Source: captures/YYYY-MM-DD-session.jsonl packet #N
#     """
#     payload = bytes.fromhex("REPLACE")
#     expected_crc = 0xXXXX
#     assert crc16_mcrf4xx(payload) == expected_crc
#
# def test_ace2_crc_from_capture():
#     """Validate CRC matches a real ACE 2 Pro captured frame.
#     Source: captures/YYYY-MM-DD-session.jsonl packet #N
#     CRC covers FLAGS..PAYLOAD bytes.
#     """
#     crc_data = bytes.fromhex("REPLACE")  # FLAGS + SEQ + CMD + LEN + PAYLOAD
#     expected_crc = 0xXXXX
#     assert crc16_kermit(crc_data) == expected_crc
