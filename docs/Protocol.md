# Protocol Documentation

> **Status: Research phase complete — significant community RE data available.**
>
> Both protocols are substantially understood from community reverse engineering.
> Capture tooling and testing against real hardware are the next steps before
> production implementation.

---

## ACE Pro (ACE1) — USB CDC Protocol

### Physical Layer

| Parameter | Value | Confidence | Source |
|-----------|-------|------------|--------|
| Interface | USB CDC ACM | High | Community RE, strace captures |
| Speed | Full Speed (12 Mbps) | High | GD32F303 spec |
| MCU | GD32F303 (GigaDevice) | High | printers-for-people/ACEResearch HARDWARE.md |
| VID | `0x28E9` | High | decay71/multiACE, USB database |
| PID | `0x018A` | Medium | decay71/multiACE README only — needs lsusb confirmation |
| Class | CDC ACM | High | strace captures, Linux devnode /dev/ttyACM0 |
| Baud rate | 115200 | High | Multiple independent drivers |
| USB hub chip | GL852G | High | printers-for-people HARDWARE.md |
| Symlink | `/dev/serial/by-id/usb-ANYCUBIC_ACE_0-if00` | High | strace captures |

### Physical Connector (ACE Pro PCB)

Molex Micro-Fit 3.0 Male, 2×3 (6-pin):
- Pin 2: D−
- Pin 3: D+
- Pin 5: GND
- Pin 6: VCC — **NC per printers-for-people/ACEResearch (high confidence)**; conflicting claim
  in lower-confidence source says must connect to USB-A VBUS. Leave unconnected until confirmed
  on hardware. See HW-7 in `docs/Unknowns.md`.
- Pin 1, Pin 4: NC (do not connect)

Source: printers-for-people/ACEResearch (Pin 6 NC); physical inspection (2026-06-28) confirms
HW-2 connector type. Confidence: High for connector type; HW-7 open for Pin 6 VCC connection.

### Frame Format

```
[0xFF][0xAA][LEN_LO][LEN_HI][...JSON payload...][CRC_LO][CRC_HI][0xFE]
```

| Field | Size | Description |
|-------|------|-------------|
| `0xFF` | 1 | Frame start byte |
| `0xAA` | 1 | Frame start byte |
| `LEN_LO` | 1 | JSON payload length, little-endian low byte |
| `LEN_HI` | 1 | JSON payload length, little-endian high byte |
| Payload | variable | UTF-8 JSON |
| `CRC_LO` | 1 | CRC-16/MCRF4XX low byte |
| `CRC_HI` | 1 | CRC-16/MCRF4XX high byte |
| `0xFE` | 1 | Frame end byte |

**Source:** printers-for-people/ACEResearch strace captures (direct write() syscall observation).
**Confidence: High.**

### CRC Algorithm

- Algorithm: CRC-16/MCRF4XX
- Polynomial: 0x1021
- Init: 0xFFFF
- Reflected input: yes
- Reflected output: yes
- XOR out: 0x0000
- Computed over: JSON payload bytes only (not header/footer/length fields)
- Output: 2 bytes, little-endian

Reference: https://reveng.sourceforge.io/crc-catalogue/16.htm#crc.cat.crc-16-mcrf4xx

**Confidence: High** — confirmed by working drivers (Kobra-S1/ACEPRO `serial_manager.py`).

### Safety Constraints

1. **Maximum frame size**: 1024 bytes total. Frames exceeding this freeze the device unrecoverably.
2. **3-second keepalive**: Device disconnects if no complete valid frame received within 3 seconds.
3. **Header byte collision**: If bytes `0xFF 0xAA` appear within the JSON payload, the device
   may misparse a frame. Implementations should sanitise payloads or use JSON escaping.

### JSON-RPC Command Set

Messages use JSON-RPC style:
```json
// Request
{"id": 1, "method": "get_status", "params": {}}

// Response
{"id": 1, "result": {...}, "code": 0, "msg": "success"}
```

**Confirmed commands** (from strace captures + working driver code):

| Method | Direction | Description |
|--------|-----------|-------------|
| `get_status` | host→ACE | Poll device state, slots, temp, fan, dryer |
| `get_info` | host→ACE | Device firmware version |
| `get_filament_info` | host→ACE | Filament data for a slot (material/RFID) |
| `drying` | host→ACE | Start drying (params: temp, fan_speed, duration) |
| `drying_stop` | host→ACE | Stop drying |
| `feed_filament` | host→ACE | Feed from slot (params: index, length, speed) |
| `stop_feed_filament` | host→ACE | Stop feeding |
| `unwind_filament` | host→ACE | Retract (params: index, length, speed) |
| `update_unwinding_speed` | host→ACE | Update retract speed |
| `stop_unwind_filament` | host→ACE | Stop retraction |
| `start_feed_assist` | host→ACE | Enable buffer assist mode |
| `stop_feed_assist` | host→ACE | Disable buffer assist mode |
| `enable_rfid` | host→ACE | Enable RFID reader |
| `disable_rfid` | host→ACE | Disable RFID reader |

Source: Kobra-S1/ACEPRO, szkrisz/ACEPROSV08, strace captures. Confidence: High.

### `get_status` Response Fields (partial)

From strace captures:
```json
{
  "result": {
    "temp": 25.3,
    "fan_speed": 0,
    "status": 0,
    "dryer_status": 0,
    "enable_rfid": 1,
    "slots": [{"status": 0}, {"status": 0}, {"status": 0}, {"status": 0}]
  }
}
```

Full field schema is partially documented. See `research/findings.md`.

---

## ACE 2 Pro — RS485/USB Protocol

### Physical Layer

| Parameter | Value | Confidence | Source |
|-----------|-------|------------|--------|
| Interface chip | WCH CH343 (USB-to-UART) | High | hakimio IDA firmware analysis |
| VID | `0x1A86` (WCH) | High | Known CH343 VID |
| PID | Unknown | Unknown | CH343 uses EEPROM-configurable PID |
| Baud rate | 230400 | High | hakimio shell gist, Kobra-S1/ACEPRO |
| Data format | 8N1 | High | hakimio OTA script |
| Physical interface | RS485 | High | MCU UART4 at 0x40004C00 |
| MCU | STM32F1 Cortex-M3 | High | hakimio IDA analysis |
| Firmware base | `0x08008000` | High | hakimio |
| Min firmware | V1.1.31 (2026-03-06) | High | hakimio |

### Physical Connectors (ACE 2 Pro)

**Bottom-left port (printer-facing) — 6-pin Molex Micro-Fit 3.0 2×3:**
This is where the factory "K3/K3M/S1 Signal Cable" connects.
- 4-pin end → printer base port (latch faces downward)
- 6-pin end → ACE 2 Pro bottom-left port (latch faces outward)

Source: Anycubic installation instructions + official Compatibility Guide. Confidence: High.

**Back panel — two Molex Micro-Fit 3.0 connectors (stacked, HW-1 resolved):**

Bottom port (4-pin, 2×2) — RS485 daisy-chain, **where the Pi connects**:
- Pin 1: RS485 B (D−)
- Pin 2: RS485 A (D+)
- Pin 3: VCC — leave unconnected until bus voltage confirmed (HW-3)
- Pin 4: GND

Top port (6-pin, 2×3) — purpose unknown (HW-6). Do not connect.

### Frame Format

```
[0xFF][0xAA][FLAGS][SEQ_LO][SEQ_HI][CMD][LEN][...payload...][CRC_LO][CRC_HI][0xFE]
```

| Field | Size | Description |
|-------|------|-------------|
| `0xFF` | 1 | Frame start |
| `0xAA` | 1 | Frame start |
| FLAGS | 1 | `0x00` = host→ACE request; `0x80` = ACE→host response |
| SEQ_LO | 1 | Sequence counter, low byte |
| SEQ_HI | 1 | Sequence counter, high byte |
| CMD | 1 | Command byte (0x00–0x4E+) |
| LEN | 1 | Payload length (max 100 bytes) |
| Payload | 0–100 | Protocol Buffers proto3 encoded |
| CRC_LO | 1 | CRC-16/Kermit, low byte |
| CRC_HI | 1 | CRC-16/Kermit, high byte |
| `0xFE` | 1 | Frame end |

**Source:** hakimio gist (IDA Pro MCU firmware reverse engineering). **Confidence: High.**

CRC field covers: FLAGS through end of PAYLOAD (not the 0xFF 0xAA header or 0xFE footer).

### CRC Algorithm

- Algorithm: CRC-16/Kermit (aka CRC-16/IBM-SDLC)
- Polynomial: 0x8408 (bit-reversed 0x1021)
- Init: 0xFFFF
- Reflected: yes (naturally, by polynomial form)
- XOR out: 0x0000
- MCU function: `sub_8010464`

**Confidence: High** — confirmed by IDA analysis of MCU CRC function.

Note: CRC-16/Kermit and CRC-16/MCRF4XX use the same polynomial but may differ in init
or xorout. Both should be validated against real captures.

### Device Discovery and Addressing

ACE 2 Pro uses a two-step discovery protocol that allows multiple units on one RS485 bus:

#### Step 1: DISCOVER_DEVICE (CMD `0x00`)
- Host broadcasts with empty payload
- Each ACE 2 Pro on the bus responds with its 96-bit STM32 unique ID:
  - Word 0 from `0x1FFFF7E8`
  - Word 1 from `0x1FFFF7EC`
  - Word 2 from `0x1FFFF7F0`

#### Step 2: ASSIGN_DEVICE_ID (CMD `0x01`)
- Host sends: target UID (3×32-bit words) + initial SEQ counter byte
- The ACE unit matching the UID accepts, stores the SEQ, begins tracking increments
- Subsequent frames must increment SEQ; device validates each frame's SEQ matches expected

This mechanism allows the bridge to assign itself a specific SEQ range to avoid
collisions with the genuine ACE 2 Pro unit on the same bus.

**Confidence: High** — reverse engineered from MCU firmware.

### Command Set (78 commands)

Key commands confirmed from MCU firmware analysis:

| CMD | Name | Description |
|-----|------|-------------|
| 0x00 | DISCOVER_DEVICE | Broadcast; ACE responds with STM32 UID |
| 0x01 | ASSIGN_DEVICE_ID | Assign SEQ counter to addressed unit |
| 0x02 | IAP_UPGRADE | Announce OTA firmware upgrade |
| 0x03 | IAP_FIRMWARE | Send 64-byte firmware data chunk |
| 0x04 | IAP_UPGRADE_FINISH | Commit OTA and reboot |
| 0x05 | IAP_VERSION | Query bootloader version |
| 0x06 | GET_STATUS | Poll full device status |
| 0x07 | GET_INFO | Device firmware version info |
| 0x08 | FEED_OR_ROLLBACK | Feed/retract filament |
| 0x09 | STOP_FEED_OR_ROLLBACK | Stop feed/retract |
| 0x0A | UPDATE_SPEED | Update motor speed during operation |
| 0x0B | DRYING | Start/stop drying |
| 0x0C | SET_DRY_TEMP | Set dryer target temperature |
| 0x0D | GET_RFID_CACHE | Read cached RFID data |
| 0x0E | SET_RFID_ENABLE | Enable/disable RFID reader |
| 0x0F | LINEAR_KEY_CALIBRATE | Calibrate linear key sensor |
| 0x10 | GET_MATERIAL_INFO | Read material database |
| 0x11 | SET_SLOT_STATUS | Force set slot state |
| 0x12 | SET_MATERIAL_NAME | Set material label for slot |
| 0x13 | SET_FEED_CHECK | Configure encoder-based feed validation |
| 0x14 | SET_PRINTER_STATUS | Tell ACE what printer is doing |
| 0x40 | GET_TEMP | Read temperature sensor |
| 0x41 | SET_DRY_POWER | Set dryer power level |
| 0x42 | SET_VALVE | Control air valve |
| 0x44 | GET_FILAMENT_INFO | Read live RFID filament info |
| 0x46 | FLASH_LED | Control LED |
| 0x47 | SET_FAN | Set fan speed |
| 0x48 | MOTOR_MOVE | Direct motor control |
| 0x49 | GET_SENSOR_STATE | Read sensors |
| 0x4B | DRY_CMD | Extended drying command |
| 0x4C | GET_FEED_INFO | Read feed status |
| 0x4D | MOTOR_TEST | Test motor |
| 0x4E | GET_MOTOR_STATUS | Read motor state |

Source: hakimio IDA Pro firmware analysis. Confidence: High.

### Payload Encoding

Payloads are **Protocol Buffers proto3** encoded. The full `.proto` schema has not been
published publicly. Proto message types known to exist:

- `DryStatus`
- `SlotStatus`
- `FilamentInfo`
- `WorkState`
- Enums: `SlotState`, `FilamentState`, `DryState`

### Slot State Codes

| Value | State | Meaning |
|-------|-------|---------|
| 0x00 | READY | Idle |
| 0x01 | FEEDING | Actively feeding |
| 0x02 | ROLLBACK | Actively retracting |
| 0x03 | ASSISTING | Buffer assist active |
| 0x81 | FEED_ERROR | Encoder below threshold |
| 0x82 | ROLLBACK_ERROR | Retract motion error |
| 0x83 | ASSIST_ERROR | Hardware fault during assist |
| 0x84 | PRELOAD_ERROR | Preload failure |
| 0x85 | STUCK_ERROR | Filament jam |
| 0x86 | TANGLED_ERROR | Filament tangle |
| 0x87 | MOTOR_ERROR | Motor driver fault |

Source: hakimio firmware analysis. Confidence: High.

### Feed Check Mechanism

The ACE 2 Pro validates motor movement via encoder. Configuration:
- `check_length`: range 3–254
- `error_length`: range 3 to check_length
- Scale factor: 1.2342× (hard-coded at `0x8009EAC`)
- Error triggers: `deficit > error_length × 1.2342 encoder units`

---

## Relationship Between ACE1 and ACE2 Protocols

| Aspect | ACE Pro (ACE1) | ACE 2 Pro (ACE2) |
|--------|----------------|-----------------|
| Physical | USB CDC ACM | RS485 via CH343→USB |
| Baud | 115200 | 230400 |
| Header | `0xFF 0xAA` | `0xFF 0xAA` |
| Footer | `0xFE` | `0xFE` |
| Length | 2 bytes LE (JSON) | 1 byte (proto payload) |
| Payload encoding | JSON-RPC | Protocol Buffers proto3 |
| CRC algorithm | CRC-16/MCRF4XX | CRC-16/Kermit |
| Addressing | None (point-to-point USB) | UID-based via DISCOVER/ASSIGN |
| Sequence counter | None | Required, validated |

**The protocols share the same frame delimiters but differ significantly in payload
encoding and header structure.** They are NOT interchangeable.

---

## Capture Checklist

Items remaining before implementation (now that frame format is known):

**ACE Pro (ACE1):**
- [ ] `lsusb -v` output with ACE Pro connected (confirm PID 0x018A)
- [ ] `get_status` response with populated fields
- [ ] `feed_filament` request and completion sequence
- [ ] Error response format

**ACE 2 Pro:**
- [ ] CH343 USB PID (`lsusb` output)
- [ ] DISCOVER_DEVICE exchange capture
- [ ] ASSIGN_DEVICE_ID exchange capture
- [ ] GET_STATUS request/response with protobuf decode
- [ ] FEED_OR_ROLLBACK exchange
- [ ] Complete protobuf schema reconstruction

---

## Implementation Priority

Given what is now known, implementation should proceed as:

1. **ACE Pro (ACE1) driver first** — protocol is fully understood (JSON), no unknown encoding
2. **ACE 2 Pro emulator second** — need to emulate towards the printer
3. **Protobuf schema third** — required for ACE Pro driver messages to bridge

The ACE 2 Pro protocol requires protobuf, which requires the schema.
Community implementations (Kobra-S1/ACEPRO) can be referenced for the schema
reconstruction, but the bridge must implement its own to avoid licensing issues.
