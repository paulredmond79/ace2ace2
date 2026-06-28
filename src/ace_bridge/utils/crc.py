"""CRC calculation utilities.

Implements the two CRC algorithms used by the ACE family protocols:
- CRC-16/MCRF4XX: used by ACE Pro (ACE1) over JSON payload
- CRC-16/Kermit: used by ACE 2 Pro (ACE2) over FLAGS..PAYLOAD

Both algorithms confirmed from community reverse engineering.
See docs/Protocol.md for sources and confidence levels.
"""

from __future__ import annotations


def crc16_mcrf4xx(data: bytes) -> int:
    """CRC-16/MCRF4XX — used by ACE Pro (ACE1).

    Parameters:
        Polynomial: 0x1021
        Init: 0xFFFF
        Reflected input: yes
        Reflected output: yes
        XOR out: 0x0000

    Confirmed by: Kobra-S1/ACEPRO serial_manager.py, printers-for-people/ACEResearch
    Applied over: JSON payload bytes only (not header/footer/length)
    """
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408  # 0x8408 = bit-reverse of 0x1021
            else:
                crc >>= 1
    return crc


def crc16_kermit(data: bytes) -> int:
    """CRC-16/Kermit — used by ACE 2 Pro (ACE2).

    Parameters:
        Polynomial: 0x8408 (bit-reversed 0x1021)
        Init: 0xFFFF
        Reflected input: yes
        Reflected output: yes
        XOR out: 0x0000

    Confirmed by: hakimio IDA Pro firmware analysis, MCU function sub_8010464
    Applied over: FLAGS byte through end of PAYLOAD (not 0xFF 0xAA header or 0xFE footer)

    Note: CRC-16/Kermit and CRC-16/MCRF4XX use the same polynomial and reflection,
    but may differ in init or xorout depending on context. Both should be validated
    against real captures. See docs/Unknowns.md for remaining uncertainty.
    """
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0x8408
            else:
                crc >>= 1
    return crc


def crc16_ibm(data: bytes) -> int:
    """CRC-16/IBM (Modbus). Kept for comparison during CRC identification."""
    crc = 0x0000
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def crc8_xor(data: bytes) -> int:
    """XOR-sum checksum. Kept for comparison."""
    result = 0
    for b in data:
        result ^= b
    return result


def crc8_sum(data: bytes) -> int:
    """Byte-sum checksum mod 256. Kept for comparison."""
    return sum(data) & 0xFF


def try_all_crcs(data: bytes) -> dict[str, int]:
    """Compute all candidate CRCs for unknown protocol identification.

    Use during reverse engineering to identify which algorithm matches
    the checksum bytes in a captured packet.

    Example:
        raw = bytes.fromhex("7b226d6574686f64223a22676574f")  # JSON payload
        checksum_word = 0xB3A2  # Last 2 bytes of captured packet
        candidates = try_all_crcs(raw)
        for name, val in candidates.items():
            if val == checksum_word: print(f"Match: {name}")
    """
    return {
        "crc16_mcrf4xx": crc16_mcrf4xx(data),
        "crc16_mcrf4xx_lo": crc16_mcrf4xx(data) & 0xFF,
        "crc16_mcrf4xx_hi": (crc16_mcrf4xx(data) >> 8) & 0xFF,
        "crc16_kermit": crc16_kermit(data),
        "crc16_kermit_lo": crc16_kermit(data) & 0xFF,
        "crc16_kermit_hi": (crc16_kermit(data) >> 8) & 0xFF,
        "crc16_ibm": crc16_ibm(data),
        "crc8_xor": crc8_xor(data),
        "crc8_sum": crc8_sum(data),
    }
