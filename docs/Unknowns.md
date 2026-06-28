# Known Unknowns

This document tracks what must still be discovered before the corresponding feature
can be fully implemented. Items are removed when resolved.

---

## RS485 / ACE 2 Pro Protocol

### RS-2: ACE 2 Pro Protobuf Schema
- **Unknown**: The complete `.proto` file for all 78 ACE 2 Pro commands
- **What is known**: Message type names (DryStatus, SlotStatus, FilamentInfo, etc.)
  and 33 command names/bytes from MCU firmware analysis (hakimio gist)
- **How to discover**: Cross-reference with working drivers (Kobra-S1/ACEPRO has partial
  ACE2 support); reconstruct from GET_STATUS response by field analysis
- **Blocks**: ACE 2 Pro emulator payload generation
- **Status**: Partial — command byte values known, field schemas unknown

### RS-3: ACE 2 Pro USB PID
- **Unknown**: The CH343 USB Product ID (PID) for the ACE 2 Pro
- **What is known**: VID = 0x1A86 (WCH/CH343), PID is EEPROM-configurable
- **How to discover**: Run `lsusb` or `bridge inspect-usb` with ACE 2 Pro connected via USB
- **Blocks**: USB driver for ACE 2 Pro discovery (if using USB path rather than RS485 adapter)
- **Status**: Not started

### RS-4: SEQ Counter Collision Handling
- **Unknown**: How the bridge handles SEQ counter conflicts when it coexists on the RS485
  bus with the genuine ACE 2 Pro. Each device gets its own SEQ range during ASSIGN_DEVICE_ID,
  but the interaction needs validation
- **How to discover**: Capture DISCOVER/ASSIGN exchange with two devices; observe SEQ assignments
- **Blocks**: Emulator SEQ management
- **Status**: Not started

---

## USB Protocol (ACE Pro)

### USB-1: ACE Pro USB PID Confirmation
- **Unknown**: PID `0x018A` is from a single community source (decay71/multiACE README)
  with no lsusb screenshot. Could be `0x018A` or another value.
- **How to discover**: Run `lsusb -v` with ACE Pro connected and inspect idProduct field
- **Blocks**: USB device open in production code
- **Status**: Medium confidence in 0x018A — can proceed with it but must confirm on first run

### USB-2: `get_status` Full Response Schema
- **Unknown**: Complete field schema of `get_status` JSON response (all sub-fields of slots,
  dryer_status values, error codes)
- **How to discover**: Run `get_status` repeatedly in different states; observe all fields
- **Blocks**: Full status reporting from ACE Pro driver
- **Status**: Partial — temperature, fan_speed, status, dryer_status, enable_rfid, slots[].status visible in strace

---

## Slot Mapping

### MAP-1: Printer Slot Numbering Scheme
- **Unknown**: Whether the Kobra 3 V2 addresses the second ACE unit as slots 5–8 or
  uses a different scheme (0-indexed? per-device slot 1–4 with different device address?)
- **How to discover**: Capture a filament load command on both ACE units; compare addressing
- **Blocks**: Slot mapping configuration value (currently placeholder: offset=4)
- **Status**: Not started — assumption of offset=4 (printer slots 5–8 map to device slots 1–4)

### MAP-2: ACE 2 Pro Bus Address After ASSIGN
- **Unknown**: After ASSIGN_DEVICE_ID, subsequent frames are addressed by SEQ counter.
  How does the printer target a specific ACE 2 Pro? Is CMD simply broadcast to all and
  only the addressed device responds?
- **How to discover**: Observe multi-device RS485 capture; check which devices respond
- **Blocks**: Emulator addressing model
- **Status**: Hypothesis: SEQ counter uniquely identifies device; CMD sent with SEQ range
  that only the target device accepts

---

## Hardware

### HW-6: ACE 2 Pro Back Panel — Upper Port (6-pin, 2×3) Purpose
- **Known**: The ACE 2 Pro back panel has two Molex Micro-Fit 3.0 connectors:
  - **Bottom (4-pin, 2×2)**: RS485 daisy-chain port — confirmed, where the Pi/signal cable connects (HW-1 resolved)
  - **Top (6-pin, 2×3)**: Purpose unknown
- **Unknown**: What the upper 6-pin port on the ACE 2 Pro back panel is for. Candidates:
  USB connection to the internal CH343 chip (for firmware updates or direct USB access),
  a secondary RS485 port, or something proprietary.
- **How to discover**: Probe with multimeter; check Anycubic documentation for any reference
  to the back-panel 6-pin port; compare signals to USB D+/D− levels vs RS485 levels.
- **Blocks**: Nothing for current bridge design — Pi connects to the 4-pin (bottom) port only.
- **Status**: Not started

### HW-4: ACE Pro Daisy-Chain Connector Protocol
- **Known**: The Molex Micro-Fit 3.0 2×2 connector on the ACE Pro back panel (below the
  2×3 USB connector) is the daisy-chain port for linking additional ACE Pro units together.
- **Unknown**: The protocol carried on this connector. Candidates: proprietary serial,
  RS485, or a variant of the ACE Pro USB protocol. Pinout unknown.
- **How to discover**: Probe with multimeter; sniff with logic analyser or oscilloscope
  while two ACE Pro units are chained; compare pinout to ACE 2 Pro RS485 connector
- **Blocks**: Multi-ACE Pro support (future milestone); not required for current bridge design
- **Status**: Purpose confirmed (user inspection). Protocol and pinout unknown.

### HW-3: RS485 Bus Voltage
- **Unknown**: Signal voltage on RS485 bus (5V or 3.3V differential)
- **How to discover**: Measure with multimeter before any connection
- **Blocks**: RS485 transceiver selection
- **Status**: ⚠️ MUST resolve before hardware connection

---

## Resolved Unknowns

| ID | What | Resolved | Source |
|----|------|----------|--------|
| RS-1 | ACE 2 Pro baud rate | 230400, 8N1 | hakimio gists, Kobra-S1/ACEPRO |
| RS-1b | ACE Pro baud rate | 115200 | Multiple community drivers |
| RS-5 | ACE 2 Pro command set | 78 commands enumerated | hakimio IDA firmware analysis |
| RS-6 | ACE 2 Pro bus topology | RS485 bus, UID-based addressing via DISCOVER/ASSIGN | hakimio |
| RS-7 | Packet frame format (ACE Pro) | 0xFF 0xAA + len(2) + JSON + CRC16/MCRF4XX + 0xFE | printers-for-people/ACEResearch |
| RS-7b | Packet frame format (ACE 2 Pro) | 0xFF 0xAA + FLAGS + SEQ(2) + CMD + LEN + proto + CRC16/Kermit + 0xFE | hakimio |
| RS-4b | CRC algorithm (ACE Pro) | CRC-16/MCRF4XX, poly 0x1021, init 0xFFFF, reflected | Kobra-S1/ACEPRO |
| RS-4c | CRC algorithm (ACE 2 Pro) | CRC-16/Kermit, poly 0x8408, init 0xFFFF | hakimio MCU function sub_8010464 |
| RS-8 | ACE 2 Pro startup/handshake | DISCOVER_DEVICE → ASSIGN_DEVICE_ID sequence | hakimio |
| USB-3 | ACE Pro USB device class | CDC ACM → /dev/ttyACM0 | strace captures |
| USB-4 | ACE Pro payload encoding | JSON-RPC (not binary) | strace captures |
| USB-1b | ACE Pro USB VID | 0x28E9 (GigaDevice GD32F303) | Community, USB database |
| USB-2b | ACE Pro MCU | GD32F303 | printers-for-people HARDWARE.md |
| USB-5 | ACE 2 Pro USB chip | WCH CH343, VID 0x1A86 | hakimio IDA analysis |
| HW-2 | ACE Pro external chassis connector | Molex Micro-Fit 3.0 Male 2×3 (6-pin) — custom cable required | Physical inspection (user photo, 2026-06-28) |
| HW-1 | ACE 2 Pro daisy-chain port (back) connector type | 4-pin Molex Micro-Fit 3.0 2×2 — bottom port on back panel; cable format 4-pin (ACE 2 Pro) → 6-pin (adapter) | Physical inspection (user, 2026-06-28) |

*Date resolved: 2026-06-28 — initial research phase*
