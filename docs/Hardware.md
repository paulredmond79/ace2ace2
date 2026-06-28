# Hardware Documentation

## Target Hardware Chain

```
Anycubic Kobra 3 V2 (USB host)
        │
        │ USB-to-RS485 adapter (factory cable)
        │
        ▼ RS485 bus  (A / B / GND)
        │
        ├──────────────────────────────────┐
        │                                  │
        ▼                                  ▼
  ACE 2 Pro #1 (genuine)         Raspberry Pi Bridge
  Molex 4-pin RS485 connector     USB-RS485 adapter or GPIO HAT
                                          │
                                          │ USB (custom cable)
                                          ▼
                                     ACE Pro
                                  Molex 6-pin connector
```

The RS485 bus is a T-junction: the printer, the genuine ACE 2 Pro, and the Pi all share
the same A/B differential pair. The Pi listens as a bus node and emulates a second ACE 2 Pro.

---

## Connector Pinouts

> **Source:** decay71/multiACE README and printers-for-people/ACEResearch hardware notes.
> Pinouts are high-confidence from community research but must be verified with a multimeter
> before making any connection. See `docs/Safety.md`.

### ACE 2 Pro — Molex Micro-Fit 3.0 Female 2×2 (4-pin)

The ACE 2 Pro RS485 port uses a **Molex Micro-Fit 3.0 Female housing, 2×2, 4 pins**.

```
┌───┬───┐   ← Connector face (as fitted to ACE 2 Pro PCB)
│ 1 │ 2 │
├───┼───┤
│ 3 │ 4 │
└───┴───┘

Pin 1 — RS485 B  (D−, labelled "D−" on PCB; this is RS485 B-line)
Pin 2 — RS485 A  (D+, labelled "D+" on PCB; this is RS485 A-line)
Pin 3 — VCC      (do NOT connect — leave unconnected or confirm voltage first)
Pin 4 — GND
```

> ⚠️ **IMPORTANT**: The PCB labels "D+" and "D−" refer to RS485 A and B lines, NOT USB
> D+/D−. These are differential RS485 signals. Connecting them to USB would destroy hardware.

**Molex part number for mating connector (plug):**
- Housing: `43025-0400` (Micro-Fit 3.0 Plug, 2×2, 4-circuit)
- Terminals: `43030-0007` (Micro-Fit 3.0 Female Crimp Terminal, 24–28 AWG)

Connection to RS485 bus:
- Pin 1 (RS485 B / D−) → RS485 bus B-line
- Pin 2 (RS485 A / D+) → RS485 bus A-line
- Pin 4 (GND) → RS485 bus GND (signal ground, not chassis)
- Pin 3 (VCC) — leave unconnected

### ACE Pro — Molex Micro-Fit 3.0 Male 2×3 (6-pin)

The ACE Pro uses a **Molex Micro-Fit 3.0 Male housing, 2×3, 6 pins** for its primary interface.
This connector carries standard USB 2.0 signals plus power.

```
┌───┬───┬───┐   ← Connector face (as fitted to ACE Pro PCB)
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
└───┴───┴───┘

Pin 1 — NC       (do not connect)
Pin 2 — USB D−
Pin 3 — USB D+
Pin 4 — NC       (do not connect)
Pin 5 — GND
Pin 6 — VCC      (do NOT connect — ACE Pro is USB bus-powered from Pi)
```

**Molex part number for mating connector (receptacle):**
- Housing: `43025-0600` (Micro-Fit 3.0 Receptacle, 2×3, 6-circuit)
- Terminals: `43030-0007` (same crimp terminal as above)

---

## Custom Cables

### Cable 1: ACE Pro USB Cable

The ACE Pro does not use a standard USB port externally. You must build a custom cable:

```
Molex Micro-Fit 3.0 Female 2×3  →  USB-A Male (to Pi USB port)

Molex Pin 2 (D−)  ──────────────────  USB-A Pin 2 (D−)
Molex Pin 3 (D+)  ──────────────────  USB-A Pin 3 (D+)
Molex Pin 5 (GND) ──────────────────  USB-A Pin 4 (GND)
Molex Pin 6 (VCC) — DO NOT CONNECT — USB-A Pin 1 (VBUS) already powers the device
```

> ⚠️ **Do not connect Pin 6 (VCC) to USB-A Pin 1 (VBUS).** The ACE Pro draws power
> from the USB bus via the standard VBUS line. Bridging an additional VCC supply will
> cause a short or over-voltage condition.

Use 26 AWG or thicker wire for D+ and D−. Keep cable length under 2 m to maintain
USB 2.0 signal integrity.

**Parts needed:**
- 1× Molex `43025-0600` housing
- 4× Molex `43030-0007` crimp terminals (use 3 wires + one blank for Pin 1/4 if desired)
- 1× USB-A Male plug with bare wire ends (or an USB-A cable, cut and stripped)

### Cable 2: ACE 2 Pro RS485 Cable

The ACE 2 Pro RS485 cable taps into the existing RS485 bus. Options:

**Option A — Splice into existing cable (least disruptive):**
Use Wago 221-413 lever connectors (3-port) to T-junction the A, B, and GND lines.
No cutting of existing connectors required.

**Option B — Make a Y-cable:**
Build a custom Molex 4-pin plug that mirrors the existing ACE 2 Pro cable and break
out extra A/B/GND wires for the Pi's RS485 interface.

Use shielded twisted pair (e.g. Belden 9501 or similar) for the RS485 run to the Pi.
Connect shield at the printer/bus end only.

---

## RS485 Bus T-Junction

The RS485 bus must be extended to add the Pi as a third node. The recommended approach
is passive T-junction using lever connectors:

```
Printer RS485 cable  →  ┌─── Wago 221-413 (A-line) ───┬─── ACE 2 Pro (A)
                        │                              └─── Pi RS485 (A)
                        │
                        ├─── Wago 221-413 (B-line) ───┬─── ACE 2 Pro (B)
                        │                              └─── Pi RS485 (B)
                        │
                        └─── Wago 221-413 (GND)    ───┬─── ACE 2 Pro (GND)
                                                       └─── Pi RS485 (GND)
```

**Wago 221-413**: 3-conductor, 0.2–4 mm² wire, rated to 32A/450V. Easy to open/close
without tools. Available from most electronics suppliers.

> ⚠️ Keep the stub from the T-junction to the Pi as short as possible (under 20 cm
> ideally). Long stubs create reflections on RS485 buses at high baud rates.

---

## Recommended Raspberry Pi

**Recommendation: Raspberry Pi 4B (2GB)**

Rationale:
- 4× USB 3.0 ports (one for ACE Pro, one for USB-RS485 adapter)
- GPIO header for optional RS485 HAT
- Sufficient RAM and CPU for asyncio bridge with capture logging
- Wide availability and well-supported

Alternatives:
- **Pi Zero 2W**: Adequate CPU, but only 1× USB port — needs a USB hub for both adapters.
- **Pi 5**: More than enough; fine if available.
- **Pi CM4**: Good for a permanent embedded installation.

---

## RS485 Interface Options

### Option A: USB-RS485 Adapter (Recommended for first bring-up)

A USB-to-RS485 adapter is the easiest starting point. It requires no GPIO wiring and
appears as `/dev/ttyUSB0`.

**Recommended:** CH340-based or FTDI FT232H-based USB-RS485 adapters.
- Connect adapter A → RS485 bus A-line
- Connect adapter B → RS485 bus B-line
- Connect adapter GND → RS485 bus GND
- Many adapters handle DE/RE automatically

### Option B: GPIO UART + RS485 HAT

Use the Pi's hardware UART (`/dev/ttyAMA0`) with an RS485 transceiver HAT.

GPIO pins (RPi 4B):
```
GPIO 14 (TXD) → RS485 transceiver DI
GPIO 15 (RXD) → RS485 transceiver RO
GPIO 18       → DE/RE (direction control, if not auto-direction chip)
```

> ⚠️ **UNKNOWN (HW-3)**: RS485 bus voltage is unconfirmed. The bus may be 5V or 3.3V.
> A 5V bus will damage 3.3V GPIO pins without a level shifter. Measure before connecting.
> See `docs/Unknowns.md`.

**Recommended HAT:** Waveshare RS485/CAN HAT or similar, with integrated RS485 transceiver.
If isolation is desired, use a HAT with ADM2483 or equivalent isolated transceiver.

### RS485 Bus Parameters

| Parameter | Value | Confidence |
|-----------|-------|-----------|
| Baud rate | 230400, 8N1 | High — confirmed from community drivers |
| Voltage | Unknown | ⚠️ Measure before connecting |
| Termination | Unknown | Check if bus is already terminated with oscilloscope |
| Half/full duplex | Half-duplex | Standard RS485; confirmed from protocol analysis |

---

## USB Interface (ACE Pro)

The Pi connects to the ACE Pro via USB using the custom Molex-to-USB-A cable described above.
The ACE Pro enumerates as USB CDC ACM and appears as `/dev/ttyACM0`.

| Parameter | Value | Confidence |
|-----------|-------|-----------|
| USB VID | 0x28E9 (GigaDevice) | High |
| USB PID | 0x018A | Medium — single community source, confirm with `lsusb` |
| USB Class | CDC ACM | High — confirmed from strace captures |
| Device path | `/dev/ttyACM0` | Expected; may vary if other CDC devices present |

Verify with:
```bash
bridge inspect-usb
# or
lsusb -v | grep -A5 "28e9"
```

---

## Power

### Raspberry Pi
- Supply: 5V/3A minimum; 5V/5A recommended for Pi 4B
- Use official Pi USB-C supply or equivalent quality supply
- Do not power Pi from printer USB — current and stability are unknown

### ACE Pro
- Powered via USB from the Pi. The standard USB-A port supplies up to 500 mA (USB 2.0)
  or 900 mA (USB 3.0).
- The ACE Pro's actual draw is unconfirmed — measure before deploying on a 500 mA port.
- If draw exceeds 500 mA, use a powered USB hub between Pi and ACE Pro.

### Isolation

Consider using an isolated RS485 transceiver (ADM2483 or similar) between the Pi and
the RS485 bus. This protects the Pi from ground loops and voltage spikes from the printer.

If not isolated, ensure common GND between Pi and RS485 bus.

---

## Bill of Materials

| Qty | Item | Part / Notes | Est. Cost |
|-----|------|-------------|-----------|
| 1 | Raspberry Pi 4B (2GB) | Or Pi 5 | ~$35–45 |
| 1 | USB-RS485 adapter | CH340 or FTDI-based | ~$5–10 |
| 1 | USB-C power supply | 5V/5A, official Pi supply | ~$10 |
| 1 | MicroSD card | 32GB+ Class 10 / A1 | ~$8 |
| 1 | Molex housing 2×3 | `43025-0600` (ACE Pro cable) | ~$1 |
| 1 | Molex housing 2×2 | `43025-0400` (ACE 2 Pro cable, if making Y-cable) | ~$1 |
| 10 | Molex crimp terminals | `43030-0007`, 24–28 AWG | ~$2 |
| 1 | USB-A Male plug or cable | For ACE Pro custom cable | ~$2 |
| 3 | Wago 221-413 | 3-port lever connectors for RS485 T-junction | ~$3 |
| 1 | Shielded twisted pair | For Pi→RS485 bus run, 1–2 m | ~$3 |
| 1 | Molex crimp tool | PA-09 or Engineer PA-21 | ~$20 (one-time) |

**Total approximate cost (excluding Pi):** ~$35–55

> ⚠️ **HW-2 UNRESOLVED**: The ACE Pro external chassis connector type is unconfirmed.
> The Molex 6-pin connector is the internal PCB connector; a physical inspection is required
> to confirm whether the external port is this Molex connector or a standard USB receptacle.
> See `docs/Unknowns.md` HW-2.

---

## Grounding and Shielding

- Connect cable shields at one end only (printer/bus end) to avoid ground loops
- Ensure Pi GND and RS485 bus GND are connected at a single point
- Keep RS485 cable away from stepper motor cables (EMI)
- Use twisted pair for the RS485 run — standard CAT5 pairs work at these cable lengths

---

## Safety Before First Connection

1. Power off ALL devices (printer, ACE 2 Pro, ACE Pro, Raspberry Pi)
2. Verify the Molex connector pinout matches the table above using a multimeter:
   - Probe Pin 2 (D+) vs Pin 4 (GND) — should read RS485 A-line potential
   - Probe Pin 1 (D−) vs Pin 4 (GND) — should read RS485 B-line potential
3. Measure RS485 A-line to GND and B-line to GND (DC and AC) — note the voltage
4. Confirm measured voltage is within spec of your RS485 transceiver
5. Connect GND first, then A and B lines
6. Set `read_only: true` in `config/config.yaml` before any bridge start
7. Run `bridge sniff-rs485` and confirm packets decode correctly before enabling TX

See `docs/Safety.md` for the complete pre-connection checklist.
