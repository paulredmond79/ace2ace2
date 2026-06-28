# Hardware Documentation

## Firmware Requirements

Before connecting the ACE 2 Pro for the first time, update the printer firmware:

| Device | Required Firmware | How to Update |
|--------|------------------|---------------|
| Kobra 3 V2 | **V1.1.2.5** | OTA update from printer menu |
| ACE 2 Pro | V1.1.31 (2026-03-06) or later | OTA via printer menu after connection |

Source: Anycubic ACE 2 Pro Multi-Model Compatibility Guide (official). Confidence: High.

---

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
| 1 | Printer (4-pin port) | ACE 2 Pro bottom-left (6-pin port) | "K3/K3M/S1 Signal Cable" (factory supplied with ACE 2 Pro) | None — use existing |
| 2 | ACE 2 Pro daisy-chain port (back, pin count TBC) | Raspberry Pi USB | Custom Molex pigtail + USB-RS485 adapter | Build — **confirm HW-1 first** |
| 3 | Raspberry Pi USB | ACE Pro (Molex 2×3 port) | Custom Molex 2×3 → USB-A cable | Build |

The Pi sits at the end of the RS485 daisy-chain. From the printer's perspective it appears
as a second ACE 2 Pro node on the same RS485 segment.

---

## Connector Pinouts

> **Source:** decay71/multiACE README and printers-for-people/ACEResearch hardware notes.
> Pinouts are high-confidence from community research but must be verified with a multimeter
> before making any connection. See `docs/Safety.md`.

### ACE 2 Pro — Connectors

The ACE 2 Pro has two RS485 ports:

**Bottom-left port (printer-facing) — 6-pin Molex Micro-Fit 3.0 2×3:**
This is where the factory signal cable connects. The cable has a 6-pin end here and a
4-pin end at the printer. This cable is supplied with the ACE 2 Pro — do not modify it.

Per Anycubic instructions:
- Insert the **4-pin end** into the printer's base port (latch faces downward)
- Insert the **6-pin end** into the ACE 2 Pro bottom-left port (latch faces outward)

**Back panel — two Molex Micro-Fit 3.0 connectors (stacked, HW-1 resolved):**

**Bottom port (4-pin, 2×2) — RS485 daisy-chain, where the Pi connects:**
This is where Cable A's 4-pin Molex end connects.
- Mating housing: Molex `43025-0400` receptacle (or `43020-0400` plug — confirm device connector orientation before ordering)
- Terminals: `43030-0007` female crimp (20–24 AWG) for use with `43025-0400`; or `43031-0007` male tab for use with `43020-0400`
- Signals: RS485 A (D+), RS485 B (D−), GND, VCC (leave VCC unconnected — HW-3)

**Top port (6-pin, 2×3) — purpose unknown (HW-6):**
Not used in the current bridge design. Do not connect.

> ⚠️ **IMPORTANT**: The ACE 2 Pro PCB labels "D+" and "D−" refer to RS485 A and B lines,
> NOT USB signals. Connecting them to USB would destroy hardware.

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
Pin 6 — VCC (NC — do not connect; see HW-7 in docs/Unknowns.md)
```

**Molex part number for mating connector (receptacle):**
- Housing: `43025-0600` (Micro-Fit 3.0 Receptacle, 2×3, 6-circuit)
- Terminals: `43030-0007` (same crimp terminal as above)

---

## Custom Cables

Two custom cables are needed. The factory cable from printer to ACE 2 Pro front port
is already provided with the ACE 2 Pro — do not modify it.

### Cable A: ACE 2 Pro Daisy-Chain → Raspberry Pi (RS485)

This cable uses the same **4-pin → 6-pin signal cable format** as the factory signal cable.
The 4-pin end plugs into the **bottom (daisy-chain) port on the back of the ACE 2 Pro**.
The 6-pin end connects to the **USB-RS485 adapter** (via its screw terminals or Molex port).

```
ACE 2 Pro back                    USB-RS485 adapter
(bottom port)                     (screw terminals / Molex)
Molex Micro-Fit 3.0 4-pin

Pin 1 (RS485 B / D−)  ──────────  B terminal
Pin 2 (RS485 A / D+)  ──────────  A terminal
Pin 4 (GND)           ──────────  GND terminal
Pin 3 (VCC)           — not connected
                                        │
                                   USB-A plug
                                        │
                              Pi USB port → /dev/ttyUSB0
```

Note: the 6-pin end of the cable carries the same 3 active signals (A, B, GND) on the
equivalent pins. Wire only these 3 conductors to the RS485 adapter's screw terminals.

> The official Anycubic cascade kit includes a "signal adapter cable" (4-pin → 6-pin)
> and a "USB-to-RS485 cable" with a matching 6-pin Molex connector. If you can obtain
> the Anycubic accessories, use them. Otherwise build the 4-pin Molex pigtail above
> and terminate directly at the RS485 adapter's screw terminals.

**Parts needed:**
- 1× Molex 4-pin housing — confirm device port gender before ordering:
  - Device port = receptacle (socket) → cable needs **plug** `43020-0400` + `43031-0007` male tab contacts
  - Device port = plug (pin header) → cable needs **receptacle** `43025-0400` + `43030-0007` female crimp contacts
- 3× Molex crimp contacts matching your housing choice (`43031-0007` or `43030-0007`), 20–24 AWG
- 1× USB-RS485 adapter (CH340 or FTDI-based, with screw terminal block)
- ~0.5–1 m **3-conductor shielded cable**, 22–24 AWG (e.g. Alpha Wire 5563 or Belden 9533)

Use a 3-conductor shielded cable: separate insulated conductors for A, B, and GND. Do not
use the shield/drain as the GND conductor — connect the shield at the ACE 2 Pro end only
for EMI rejection, with GND carried on its own insulated conductor.

### Cable B: Raspberry Pi → ACE Pro (USB)

**Confirmed (physical inspection, 2026-06-28):** The ACE Pro back panel exposes the
Molex Micro-Fit 3.0 Male 2×3 connector externally. There is no standard USB port on
the chassis — this custom cable is required.

> Note: A second Molex 2×2 connector is present on the back panel (lower, below the 2×3).
> This is the ACE Pro daisy-chain port for linking additional ACE Pro units together.
> Its protocol and pinout are unknown (HW-4 in `docs/Unknowns.md`). Do not connect to it
> for the current bridge design — the Pi connects via the 2×3 port above it.

Build this cable to connect the Pi to the ACE Pro:

```
Molex Micro-Fit 3.0 Female 2×3  →  USB-A Male (to Pi USB port)

Pin 2 (USB D−)       ──────────  USB-A Pin 2 (D−)
Pin 3 (USB D+)       ──────────  USB-A Pin 3 (D+)
Pin 5 (GND)          ──────────  USB-A Pin 4 (GND)
Pin 6 (VCC)          — not connected (NC — see HW-7)
Pin 1, Pin 4         — not connected
```

> ⚠️ **HW-7 open**: Pin 6 VCC connection is disputed between sources. The high-confidence
> community source (printers-for-people/ACEResearch) says Pin 6 is NC. Leave it unconnected
> until confirmed on hardware. See `docs/Unknowns.md` HW-7.

Use 24 AWG wire for all conductors. Keep cable length under 2 m for USB 2.0 signal integrity.

**Parts needed:**
- 1× Molex `43025-0600` housing (2×3 Female receptacle)
- 3× Molex `43030-0007` crimp terminals, 20–24 AWG (3 wires: D−, D+, GND)
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
- **Self-powered from mains** (IEC C14 inlet + rocker switch on right back panel). The ACE Pro
  does not draw power from the Pi's USB port.
- The USB connection to the Pi carries data only (D−, D+, GND). Pin 6 VCC is left NC per the
  interim HW-7 stance — do not use a powered USB hub to supply VBUS. See `docs/Unknowns.md` HW-7.

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
| 1 | Molex housing for Cable A (confirm orientation) | `43020-0400` plug (if device port is receptacle) OR `43025-0400` receptacle (if device port is plug) | ~$0.60 |
| 1 | Molex housing 2×3 | `43025-0600` — Cable B (Pi → ACE Pro) | ~$0.60 |
| 10 | Molex crimp terminals | `43030-0007` (female, 20–24 AWG) for all uses EXCEPT Cable A with `43020-0400`, which needs `43031-0007` (male tab) for those 3 contacts | ~$2 |
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
