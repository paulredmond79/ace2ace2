"""Hex dump formatting utilities."""

from __future__ import annotations


def hex_dump(data: bytes, width: int = 16, offset: int = 0, label: str | None = None) -> str:
    """Format bytes as a readable hex dump with ASCII sidebar.

    Example output:
        0000  AA 01 04 10 00 B3 00 00  00 00 00 00 00 00 00 00  |................|
    """
    lines: list[str] = []
    if label:
        lines.append(f"── {label} ({len(data)} bytes) ──")
    for i in range(0, len(data), width):
        chunk = data[i : i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        addr = offset + i
        # Pad hex part to fixed width
        hex_padded = hex_part.ljust(width * 3 - 1)
        lines.append(f"{addr:04X}  {hex_padded}  |{ascii_part}|")
    return "\n".join(lines)


def hex_str(data: bytes, sep: str = " ") -> str:
    """Format bytes as a space-separated hex string. e.g. 'AA 01 04 10'"""
    return sep.join(f"{b:02X}" for b in data)


def parse_hex_str(s: str) -> bytes:
    """Parse a hex string (with or without spaces) to bytes."""
    cleaned = s.replace(" ", "").replace(":", "").replace("-", "")
    return bytes.fromhex(cleaned)


def diff_bytes(a: bytes, b: bytes) -> str:
    """Show byte-level diff between two byte sequences."""
    lines: list[str] = []
    max_len = max(len(a), len(b))
    for i in range(max_len):
        ba = a[i] if i < len(a) else None
        bb = b[i] if i < len(b) else None
        if ba != bb:
            sa = f"{ba:02X}" if ba is not None else "--"
            sb = f"{bb:02X}" if bb is not None else "--"
            lines.append(f"  byte[{i:3d}]: {sa} → {sb}")
    if not lines:
        return "  (identical)"
    return "\n".join(lines)
