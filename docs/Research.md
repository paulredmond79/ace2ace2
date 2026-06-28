# Research

This document summarises publicly available information about the ACE Pro, ACE 2 Pro,
and Kobra 3 V2. All sources are cited. Confidence is rated: High / Medium / Low / Unknown.

> **Last updated: 2026-06-28**

---

## Summary of Knowledge State

| Area | Knowledge Level | Blocker |
|------|----------------|---------|
| ACE 2 Pro RS485 protocol | None confirmed | Need capture |
| ACE Pro USB VID/PID | None confirmed | Need lsusb |
| ACE Pro USB protocol | None confirmed | Need capture |
| Kobra 3 V2 multi-ACE setup | Partial (community reports) | Need capture |
| RS485 baud rate | Unknown | Need oscilloscope |
| Slot addressing | Unknown | Need capture |

---

## Community and Public Research

### Klipper / Moonraker ACE Support

- **Status**: Research in progress — see below for findings to be filled in after
  web research phase.
- **Relevance**: Klipper implementations of ACE support would reveal packet formats,
  addresses, and commands.

> ⚠️ Research agent findings will be inserted here once available.
> See `research/findings.md` for raw notes.

### GitHub Repositories

Repositories to investigate:

| Repository | Relevance | Status |
|------------|-----------|--------|
| Anycubic official (if any) | Firmware source, protocol | Not found yet |
| Community Klipper ACE integration | RS485 protocol details | Searching |
| Slicer integrations | Command set hints | Searching |

> ⚠️ Populate this table with actual findings from research phase.

### Reddit / Forum Discussions

Sources to investigate:
- r/anycubic
- r/3Dprinting
- Anycubic community forum
- Printables community

> ⚠️ Populate with actual thread URLs and findings.

---

## ACE 2 Pro — Known Facts

| Fact | Source | Confidence |
|------|--------|------------|
| Uses RS485 for printer communication | Physical inspection | High |
| Part of Kobra 3 V2 multi-material system | Product documentation | High |
| Supports 4 filament slots | Product documentation | High |
| Has built-in dryer | Product documentation | High |
| Baud rate: UNKNOWN | — | Unknown |
| Packet format: UNKNOWN | — | Unknown |

---

## ACE Pro — Known Facts

| Fact | Source | Confidence |
|------|--------|------------|
| Uses USB for communication | Physical inspection | High |
| Older device, preceded ACE 2 Pro | Product timeline | High |
| Supports 4 filament slots | Product documentation | High |
| Has dryer capability | Product documentation | Medium |
| VID/PID: UNKNOWN | — | Unknown |
| USB device class: UNKNOWN | — | Unknown |

---

## Kobra 3 V2 — Known Facts

| Fact | Source | Confidence |
|------|--------|------------|
| Supports multi-material printing | Product documentation | High |
| Uses ACE 2 Pro for filament management | Product documentation | High |
| Supports 2 ACE 2 Pro units (8 filaments total) | Product documentation | Medium |
| RS485 bus between printer and ACE units | Physical inspection | High |

---

## Methodology for Capture-Based Research

### RS485 Capture

Equipment needed:
- Logic analyser (Saleae Logic, DSLogic, or similar)
- OR: USB-RS485 adapter in receive-only mode
- OR: Oscilloscope with RS485 decode

Steps:
1. Connect logic analyser probes to RS485 A and B lines (do not disconnect originals)
2. Set voltage threshold appropriate for signal level
3. Configure analyser for async serial decode
4. Try baud rates: 9600, 19200, 38400, 57600, 115200, 250000, 500000
5. Power on printer + ACE 2 Pro; capture startup sequence
6. Trigger filament changes; capture those sequences
7. Save captures in `.sal` / `.logicdata` / `.csv` format to `captures/`

Alternative (software-only):
Use `bridge sniff-rs485 --port /dev/ttyUSB0 --baud 115200` and try each baud rate.

### USB Capture

Equipment:
- Linux host with usbmon enabled
- Wireshark with USB capture

Steps:
```bash
# Load usbmon
sudo modprobe usbmon

# Find ACE Pro USB bus
lsusb  # note Bus number

# Capture with Wireshark
sudo wireshark -i usbmon<N>

# Or with tshark
sudo tshark -i usbmon<N> -w captures/ace_pro_<date>.pcapng
```

Or use `bridge sniff-usb` once implemented.

### Packet Analysis

Once captures are available:
1. Run `bridge decode --input captures/file.bin` to view hex dumps
2. Look for repeating patterns (headers, lengths)
3. Try common CRC algorithms: CRC8, CRC16/IBM, CRC16/CCITT, XOR8
4. Compare packets triggered by known actions (load slot 1 vs load slot 2)

---

## References

> ⚠️ This section will be populated as research progresses.
> Each entry should include URL, summary, date accessed, and confidence.

### Placeholder entries (to be researched and confirmed):

1. Anycubic ACE 2 Pro product page
2. Kobra 3 V2 specifications
3. Klipper ACE integration (if exists)
4. Community reverse engineering threads
5. Open-source printer firmware references
