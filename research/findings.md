# Research Findings

> Last updated: 2026-06-28 — Initial research phase

This document captures raw research notes. See `docs/Research.md` for the structured
summary and `docs/Protocol.md` for the engineering reference.

---

## ACE Pro (ACE1) — USB Protocol

### Source: printers-for-people/ACEResearch

URL: https://github.com/printers-for-people/ACEResearch
Confidence: High
Type: Community RE, strace captures

**PROTOCOL.md documents:**

Frame format (confirmed by strace write() syscalls):
```
[0xFF][0xAA][LEN_LO][LEN_HI][...JSON payload...][CRC_LO][CRC_HI][0xFE]
```

- Header: `0xFF 0xAA`
- Length: 2 bytes LE (JSON payload bytes only)
- Payload: UTF-8 JSON
- CRC: CRC-16/MCRF4XX (poly 0x1021, init 0xFFFF, reflected I/O) over JSON payload only
- Footer: `0xFE`
- Max frame: 1024 bytes. Exceeding this freezes device.
- Keepalive: 3s timeout — device disconnects if no complete frame received in 3s
- Risk: If bytes 0xFF 0xAA appear in payload, device can freeze. Implementations must guard against this.

HARDWARE.md documents:
- MCU: GD32F303 (GigaDevice, STM32-compatible)
- USB hub chip: GL852G
- Physical connector: Molex Micro-Fit 3.0 Male 2×3 (6-pin)
  - Pin 2: D−, Pin 3: D+, Pin 5: GND, Pin 6: VCC (NOT connected)
- USB class: CDC ACM → appears as /dev/ttyACM0

Raw strace captures available in raw_data/:
- dryer-power-cycle.strace
- print-pyramid-color-test.strace (shows get_status with real field values)
- slot4-extrude.strace

### Source: decay71/multiACE

URL: https://github.com/decay71/multiACE
Confidence: Medium
Type: Community driver (Snapmaker U1, up to 4 ACE units)

Confirms VID: 0x28E9, PID: 0x018A
Notes: "ACE Pro should show as vendor 28e9, product 018a"
Caveat: Single community source, no lsusb screenshot. GD32F303 DFU bootloader
uses 28E9:0189 — 018A is adjacent. Needs confirmation with real hardware.

ACE2 Pro physical connector documented:
- Molex Micro-Fit 3.0 Female 2×2 (4-pin)
- Pin 1: D−, Pin 2: D+, Pin 4: GND, Pin 3: VCC (NOT connected)

### Source: Kobra-S1/ACEPRO

URL: https://github.com/Kobra-S1/ACEPRO
Confidence: High
Type: Working Klipper driver

Confirms:
- 115200 baud for ACE Pro
- CRC-16/MCRF4XX implementation (serial_manager.py)
- JSON-RPC command set

---

## ACE 2 Pro — RS485/USB Protocol

### Source: hakimio gists

URLs:
- IDA MCU analysis: https://gist.github.com/hakimio/4916ff69add458fdc51aeea76f21efb9
- OTA script: https://gist.github.com/hakimio/39c71fa7174e699c6470b7c79323b189
- Protocol shell: https://gist.github.com/hakimio/551915aa02b7e248721bed672ad46e0b

Confidence: High
Type: MCU firmware reverse engineering (IDA Pro)

**Firmware analysis confirms:**

Frame format:
```
[0xFF][0xAA][FLAGS:1][SEQ_LO:1][SEQ_HI:1][CMD:1][LEN:1][...payload...][CRC_LO:1][CRC_HI:1][0xFE]
```
- Header: 0xFF 0xAA
- FLAGS: 0x00 host→ACE, 0x80 ACE→host response
- SEQ: 2-byte sequence counter, validated against expected value
- CMD: 1 byte (78 commands enumerated)
- LEN: 1 byte payload length (max 100 bytes)
- Payload: Protocol Buffers proto3
- CRC-16/Kermit: poly 0x8408, init 0xFFFF, over FLAGS through PAYLOAD
  - MCU function: sub_8010464
- Footer: 0xFE

USB chip: WCH CH343 (USB-to-UART bridge)
VID: 0x1A86 (WCH/Nanjing Qinheng)
PID: Unknown (CH343 supports EEPROM-configurable PID)
Baud: 230400, 8N1

MCU: STM32F1 Cortex-M3
Firmware base: 0x08008000
Flash: ~71.6 KB
MCU unique ID registers: 0x1FFFF7E8, 0x1FFFF7EC, 0x1FFFF7F0

Discovery protocol:
1. CMD 0x00 DISCOVER_DEVICE: host broadcasts, ACE responds with 96-bit STM32 UID
2. CMD 0x01 ASSIGN_DEVICE_ID: host sends UID + initial SEQ byte; ACE validates and starts tracking SEQ

78 total commands (key ones):
- 0x00: DISCOVER_DEVICE
- 0x01: ASSIGN_DEVICE_ID
- 0x02–0x05: IAP OTA upgrade
- 0x06: GET_STATUS
- 0x07: GET_INFO
- 0x08: FEED_OR_ROLLBACK
- 0x09: STOP_FEED_OR_ROLLBACK
- 0x0A: UPDATE_SPEED
- 0x0B: DRYING
- 0x0C: SET_DRY_TEMP
- 0x0D: GET_RFID_CACHE
- 0x0E: SET_RFID_ENABLE
- 0x14: SET_PRINTER_STATUS
- 0x40: GET_TEMP
- 0x42: SET_VALVE
- 0x46: FLASH_LED
- 0x47: SET_FAN
- 0x48: MOTOR_MOVE

Slot state codes:
- 0x00: READY
- 0x01: FEEDING
- 0x02: ROLLBACK
- 0x03: ASSISTING
- 0x81: FEED_ERROR
- 0x82: ROLLBACK_ERROR
- 0x83: ASSIST_ERROR
- 0x84: PRELOAD_ERROR
- 0x85: STUCK_ERROR
- 0x86: TANGLED_ERROR
- 0x87: MOTOR_ERROR

---

## Kobra 3 V2 Multi-ACE Configuration

- Ships with 1 ACE Pro → 4 colors
- 8-color via second ACE Pro + "8-color connection module" (sold separately)
- ACE Pro and ACE 2 Pro CANNOT be mixed on same printer
- ACE 2 Pro requires: printer firmware update + signal adapter cable + USB-to-RS485 cable kit
- Max with ACE Pro: 2 units = 8 colors
- RS485 bus carries ACE 2 Pro signals through USB-to-RS485 adapter from printer USB port

---

## Existing Community Drivers (Reference Implementations)

| Repo | Language | Protocol | Status |
|------|----------|----------|--------|
| Kobra-S1/ACEPRO | Python | ACE1 + ACE2 | Working |
| szkrisz/ACEPROSV08 | Python | ACE1 | Working |
| swilsonnc/ACEPROK1Max | Python | ACE1 | Working |
| agrloki/ValgACE | Python | ACE1 | Working |
| decay71/multiACE | Python | ACE1 + ACE2 | Working |
| utkabobr/DuckACE | Python | ACE1 | WIP |
| BlackFrogKok/BunnyACE | Python | ACE1 | WIP (ref'd by Anycubic) |
| ANYCUBIC-3D/Klipper-go | Go | ACE1 + ACE2 | Official |

---

## RFID Tags

Source: DnG-Crafts/ACE-RFID (https://github.com/DnG-Crafts/ACE-RFID)
Tag types: NTAG213, NTAG215, Ultralight C
Data format: JSON payload in NDEF text record
Fields: material name, color, diameter, weight, remaining, temperature settings

---

## Remaining Open Questions

1. Confirmed USB PID for ACE Pro (0x018A is from one source only)
2. USB PID for ACE 2 Pro CH343 (EEPROM-configurable, not documented)
3. Complete protobuf .proto schema for ACE 2 Pro messages
4. Full ACE 2 Pro command payload encodings (only names known, not field layouts)
5. Whether "Kobra 3 V2 8-color connection module" is a passive USB hub or active device
6. Whether the bridge must emulate the ACE 2 Pro's DISCOVER/ASSIGN handshake exactly
