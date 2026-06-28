# Hardware Documentation

## Target Hardware Chain

```
Anycubic Kobra 3 V2
        │
        │ Factory RS485 cable (came with ACE 2 Pro — no action needed)
        │
        ▼
  ACE 2 Pro (genuine)
  [front RS485 port]
        │
  [daisy-chain RS485 port on back]
        │
        │ Custom cable: Molex 2×2 → USB-RS485 adapter → USB-A
        │
        ▼
  Raspberry Pi Bridge
        │
        │ Custom cable: USB-A → Molex 2×3
        │
        ▼
     ACE Pro
```

**Three connections total:**

| # | From | To | Cable | Action needed |
|---|------|----|-------|---------------|
| 1 | Printer | ACE 2 Pro (front port) | Factory RS485 cable | None — use existing |
| 2 | ACE 2 Pro (daisy-chain port, back) | Raspberry Pi USB | Custom Molex 2×2 pigtail + USB-RS485 adapter | Build custom cable |
| 3 | Raspberry Pi USB | ACE Pro | Custom Molex 2×3 → USB-A cable | Build custom cable |

The Pi sits at the end of the RS485 daisy-chain. From the printer's perspective it appears
as a second ACE 2 Pro node on the same RS485 segment.

---

## Connector Pinouts

> **Source:** decay71/multiACE README and printers-for-people/ACEResearch hardware notes.
> Pinouts are high-confidence from community research but must be verified with a multimeter
> before making any connection. See `docs/Safety.md`.

### ACE 2 Pro — Molex Micro-Fit 3.0 Female 2×2 (4-pin)

The ACE 2 Pro has two RS485 ports using this connector: one on the front (connected to
the printer via the factory cable) and one on the back (the daisy-chain port). Both use
the same **Molex Micro-Fit 3.0 Female housing, 2×2, 4 pins**. You connect to the **back
(daisy-chain) port** only.

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

**Molex part number for mating connector:**

> ⚠️ **HW-1 UNRESOLVED**: The exact mating housing depends on whether the ACE 2 Pro
> PCB has a plug header (43045 series, male pins) or a receptacle housing (43025 series,
> female sockets). Verify physically before ordering:
> - If device has **plug header** (male pins) → cable needs **43025-0400** receptacle housing (female socket contacts 43030-0007)
> - If device has **receptacle housing** (female sockets) → cable needs **43020-0400** plug housing (male tab contacts 43031-0007)

Assumed configuration (plug header on device, receptacle on cable — most common for PCB connectors):
- Housing: `43025-0400` (Micro-Fit 3.0 Receptacle, 2×2, 4-circuit)
- Terminals: `43030-0007` (Micro-Fit 3.0 Female Crimp Terminal, 20–24 AWG)

Connection to USB-RS485 adapter (daisy-chain port → Pi):
- Pin 1 (RS485 B / D−) → adapter B terminal
- Pin 2 (RS485 A / D+) → adapter A terminal
- Pin 4 (GND) → adapter GND terminal
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
Pin 6 — VCC/VBUS (connect to USB-A Pin 1 — provides bus power from Pi to ACE Pro)
```

**Molex part number for mating connector (receptacle):**
- Housing: `43025-0600` (Micro-Fit 3.0 Receptacle, 2×3, 6-circuit)
- Terminals: `43030-0007` (same crimp terminal as above)

---

## Custom Cables

Two custom cables are needed. The factory cable from printer to ACE 2 Pro front port
is already provided with the ACE 2 Pro — do not modify it.

### Cable A: ACE 2 Pro Daisy-Chain → Raspberry Pi (RS485)

This cable connects the **daisy-chain port on the back of the ACE 2 Pro** to a
**USB-RS485 adapter**, which then plugs into a Pi USB port.

```
ACE 2 Pro back port                  USB-RS485 adapter
Molex Micro-Fit 3.0 Female 2×2       (screw terminals)

Pin 1 (RS485 B / D−)  ─────────────  B terminal
Pin 2 (RS485 A / D+)  ─────────────  A terminal
Pin 4 (GND)           ─────────────  GND terminal
Pin 3 (VCC)           — not connected
                                           │
                                      USB-A plug
                                           │
                                    Pi USB port → /dev/ttyUSB0
```

**Parts needed:**
- 1× Molex `43025-0400` housing (see mating note above — verify connector type first)
- 3× Molex `43030-0007` crimp terminals (20–24 AWG)
- 1× USB-RS485 adapter (CH340 or FTDI-based, with screw terminal block)
- ~0.5–1 m **3-conductor shielded cable**, 22–24 AWG (e.g. Alpha Wire 5563 or Belden 9533)

Use a 3-conductor shielded cable: separate insulated conductors for A, B, and GND. Do not
use the shield/drain as the GND conductor — connect the shield at the ACE 2 Pro end only
for EMI rejection, with GND carried on its own insulated conductor.

### Cable B: Raspberry Pi → ACE Pro (USB)

**Confirmed (physical inspection, 2026-06-28):** The ACE Pro back panel exposes the
Molex Micro-Fit 3.0 Male 2×3 connector externally. There is no standard USB port on
the chassis — this custom cable is required.

> Note: A second Molex 2×2 connector is also present on the back panel (lower, below
> the 2×3). Its purpose is unknown (HW-4 in `docs/Unknowns.md`). Do not connect to it.

Build this cable to connect the Pi to the ACE Pro:

```
Molex Micro-Fit 3.0 Female 2×3  →  USB-A Male (to Pi USB port)

Pin 2 (USB D−)       ──────────  USB-A Pin 2 (D−)
Pin 3 (USB D+)       ──────────  USB-A Pin 3 (D+)
Pin 5 (GND)          ──────────  USB-A Pin 4 (GND)
Pin 6 (VCC / VBUS)   ──────────  USB-A Pin 1 (VBUS) — bus power from Pi to ACE Pro
Pin 1, Pin 4         — not connected
```

Pin 6 (VCC) is the VBUS input that powers the ACE Pro from the Pi's USB port. It must
be connected. Without it the device receives no power and will not enumerate.

Use 24 AWG wire for all conductors. Keep cable length under 2 m for USB 2.0 signal integrity.

**Parts needed:**
- 1× Molex `43025-0600` housing (2×3 Female receptacle)
- 4× Molex `43030-0007` crimp terminals, 20–24 AWG (4 wires: D−, D+, GND, VBUS)
- 1× USB-A Male plug with bare wire leads (or cut a USB-A cable and strip the end)

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

### Option A: USB-RS485 Adapter (Recommended)

A USB-to-RS485 adapter is the simplest approach. It terminates at a screw terminal block
on one end (for the Molex pigtail from the ACE 2 Pro daisy-chain port) and a USB-A plug
on the other end (into the Pi). Appears as `/dev/ttyUSB0`.

**Recommended:** CH340-based or FTDI FT232H-based adapters with screw terminals.
- Adapter A terminal → ACE 2 Pro daisy-chain Pin 2 (RS485 A)
- Adapter B terminal → ACE 2 Pro daisy-chain Pin 1 (RS485 B)
- Adapter GND terminal → ACE 2 Pro daisy-chain Pin 4 (GND)
- Many adapters handle DE/RE direction switching automatically

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

> Full BOM with part numbers and sourcing notes: see [`docs/BOM.md`](BOM.md).

| Qty | Item | Part / Notes | Est. Cost |
|-----|------|-------------|-----------|
| 1 | Raspberry Pi 4B (2GB) | Or Pi 5 | ~$35–45 |
| 1 | USB-RS485 adapter with screw terminals | CH340 or FTDI-based | ~$8–12 |
| 1 | USB-C power supply | 5V/5A, official Pi supply | ~$10 |
| 1 | MicroSD card | 32GB+ Class 10 / A1 | ~$8 |
| 1 | Molex housing 2×2 | `43025-0400` — Cable A (daisy-chain → adapter) | ~$0.60 |
| 1 | Molex housing 2×3 | `43025-0600` — Cable B (Pi → ACE Pro) | ~$0.60 |
| 10 | Molex crimp terminals | `43030-0007`, 20–24 AWG | ~$2 |
| 1 | USB-A Male plug or stripped USB-A cable | Cable B (Pi → ACE Pro) | ~$2 |
| 0.5 m | 3-conductor shielded cable, 22–24 AWG | Cable A (daisy-chain RS485 run — needs separate A, B, GND conductors) | ~$3 |
| 1 | Molex crimp tool | Engineer PA-09 or PA-21 | ~$20 (one-time) |

**Total approximate cost (excluding Pi):** ~$35–50

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
