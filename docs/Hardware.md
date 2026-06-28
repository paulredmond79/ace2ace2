# Hardware Documentation

## Target Hardware Chain

```
Anycubic Kobra 3 V2
        │ RS485
        ▼
   ACE 2 Pro (genuine)
        │ RS485 (daisy-chain — ⚠️ topology unconfirmed)
        ▼
 ┌─────────────────────────────┐
 │      Raspberry Pi Bridge    │
 │                             │
 │  GPIO → RS485 transceiver   │
 │  USB port → ACE Pro         │
 └─────────────────────────────┘
```

## Recommended Raspberry Pi

**Recommendation: Raspberry Pi 4B (2GB)**

Rationale:
- Gigabit Ethernet for remote access and firmware updates
- 4× USB 3.0 ports (one for ACE Pro, one for USB-RS485 dongle if needed)
- GPIO header for RS485 HAT
- Sufficient RAM and CPU for asyncio bridge with capture logging
- Wide availability and well-supported

Alternatives:
- **Pi Zero 2W**: Adequate CPU, but limited USB ports (1×). Requires USB hub if
  both RS485-USB adapter and ACE Pro are USB. Compact but harder to debug.
- **Pi 5**: More than enough power but overkill. Fine if available.
- **Pi CM4**: Suitable for a more permanent embedded installation.

> ⚠️ **DECISION PENDING**: Confirm that the ACE 2 Pro RS485 daisy-chain allows
> the bridge to intercept and inject packets as a node on the bus. If the topology
> does not support this, the hardware design may need revision.

## RS485 Interface

### Option A: GPIO UART + RS485 HAT (Recommended)

Use the Pi's hardware UART (`/dev/ttyAMA0`) with an RS485 transceiver HAT.

**Recommended HAT:** Waveshare RS485/CAN HAT or similar
- Automatic TX/RX direction control via GPIO or auto-direction chip
- Isolation: recommended (see Isolation section)
- 3.3V GPIO compatible

GPIO pins used (RPi 4B):
```
GPIO 14 (TXD) → RS485 transceiver DI
GPIO 15 (RXD) → RS485 transceiver RO
GPIO 18       → DE/RE (direction control, if not auto)
```

> ⚠️ **UNKNOWN**: Whether the ACE 2 Pro RS485 bus is 5V or 3.3V. Measure before
> connecting. A 5V RS485 bus will damage 3.3V GPIO without a level shifter.

### Option B: USB-RS485 Adapter

Use a USB-to-RS485 adapter (e.g. FTDI FT232H-based).

Advantages:
- No GPIO voltage concerns
- Easy to swap/test
- Appears as `/dev/ttyUSB0`

Disadvantages:
- Extra USB port used
- Slightly higher latency
- Another failure point

### RS485 Bus Parameters

⚠️ **ALL UNKNOWN** — measure with oscilloscope before connecting:

| Parameter | Required Action |
|-----------|----------------|
| Baud rate | Capture and measure |
| Voltage | Measure on bus before connecting |
| Termination | Check if bus is already terminated |
| Half/Full duplex | Confirm (RS485 is half-duplex by default) |
| Number of nodes | Count devices on bus |

## USB Interface

The ACE Pro connects via USB. The Pi's built-in USB ports can drive this directly.

**USB requirements:**
- VID/PID: ⚠️ Unknown — run `lsusb` with ACE Pro connected to identify
- Power: The ACE Pro may draw significant current from USB. Check USB specification
  or measure. Consider a powered USB hub if necessary.

## Power

### Raspberry Pi Power
- Supply: 5V/3A (minimum), 5V/5A recommended for Pi 4B
- Use official Pi power supply or quality USB-C supply
- Avoid powering from printer USB — current and stability unknown

### ACE Pro USB Power
- ⚠️ Unknown power draw — measure before deployment
- If >500mA, use powered USB hub

### Isolation Recommendation

If budget allows, use an isolated RS485 transceiver between the Pi and the RS485 bus.
This protects the Pi from ground loops and voltage spikes from the printer/ACE 2 Pro.

Recommended: ADM2483 or similar isolated RS485 transceiver.

If isolation is not used, ensure common ground between Pi and RS485 bus.

## Bill of Materials (Preliminary)

| Item | Part | Notes |
|------|------|-------|
| Raspberry Pi | Pi 4B 2GB | Or Pi 5 |
| RS485 HAT | Waveshare RS485/CAN HAT | Or equivalent |
| USB-C Power Supply | 5V/5A | Official Pi supply preferred |
| MicroSD Card | 32GB+ Class 10 | For OS |
| RS485 Cable | Shielded twisted pair | Match existing cable spec |
| RJ12/RJ45 connector | TBD | Match ACE 2 Pro connector — ⚠️ measure |
| USB Cable | Type-A to ACE Pro connector | ⚠️ check ACE Pro port type |
| Enclosure | DIN rail or small project box | |
| Ferrite beads | Optional | For EMI suppression |

> ⚠️ **UNKNOWN**: ACE 2 Pro connector type (RJ12? RJ45? Proprietary?) — inspect
> before ordering cables.

## Grounding and Shielding

- Connect cable shields at one end only (printer end) to avoid ground loops
- Ensure Pi ground and RS485 bus ground are connected
- Keep RS485 cable away from motor cables (EMI)

## Connector Pinout

**ACE 2 Pro RS485 connector pinout**: ⚠️ UNKNOWN — must be measured with multimeter
before any connection. Do not assume pinout.

**ACE Pro USB connector**: ⚠️ UNKNOWN — inspect device physically.

## Safety Before First Connection

1. Power off all devices
2. Measure RS485 bus voltage with multimeter (A and B lines to GND)
3. Verify voltage is within RS485 transceiver spec (typically ±15V max)
4. Verify common ground continuity
5. Connect RS485 in receive-only mode first (DE low, RE low)
6. Enable bridge in `read_only: true` mode for first test
7. Verify received packets look sane before enabling TX

See `docs/Safety.md` for complete pre-connection checklist.
