# Bill of Materials — ACE Bridge

Complete parts list for building one ACE Bridge unit.

> ⚠️ **Before ordering**: Verify the ACE Pro external connector type (HW-2 in
> `docs/Unknowns.md`) and the RS485 bus voltage (HW-3). These affect cable and
> transceiver selection. See `docs/Hardware.md` for full wiring details and
> `docs/Safety.md` for the pre-connection checklist.

---

## 1. Compute

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 1 | Raspberry Pi 4B 2GB | SC0193 | raspberrypi.com / Approved Resellers | ~$35 |
| 1 | MicroSD card, 32GB+ A1/A2 | Samsung Pro Endurance or equivalent | Amazon / local | ~$8 |
| 1 | USB-C power supply, 5V/5A | Official Raspberry Pi 27W PSU | raspberrypi.com | ~$12 |

> **Pi 4B** is the primary recommendation: 4× USB ports (one for ACE Pro, one for
> USB-RS485 adapter), full-size GPIO header, gigabit Ethernet. Pi 5 is a fine substitute
> if available.

---

## 2. RS485 Interface

### Option A — USB-RS485 Adapter (Recommended for first bring-up)

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 1 | USB-RS485 adapter, CH340 or FTDI | e.g. DSD TECH SH-U11 or Waveshare USB TO RS485 | Amazon | ~$8–12 |

Appears as `/dev/ttyUSB0`. No GPIO wiring required. Easy to swap and test.

### Option B — GPIO RS485 HAT (For permanent installation)

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 1 | RS485 HAT for Raspberry Pi | Waveshare RS485 CAN HAT (B) | waveshare.com / Amazon | ~$18 |

Connects via GPIO header. Uses `/dev/ttyAMA0`. Supports auto-direction control.

> ⚠️ **HW-3 UNRESOLVED**: RS485 bus voltage (5V vs 3.3V) must be measured before
> connecting any transceiver to GPIO pins. If the bus is 5V, a level shifter or
> isolated transceiver is required. See `docs/Unknowns.md`.

### Optional: Isolated RS485 Transceiver

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 1 | Isolated RS485 module | ADM2483 breakout or Mornsun TD501D485H | eBay / LCSC | ~$6–15 |

Recommended if bus voltage is uncertain or if ground loops are a concern.

---

## 3. RS485 Bus T-Junction

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 3 | Wago 221-413 lever connector (3-port) | 221-413 | Wago / Digi-Key / Amazon | ~$0.80 each (~$2.50) |
| 1 | Shielded twisted pair cable, 1–2 m | Belden 9501 or equivalent 22 AWG STP | Digi-Key / local | ~$3–5 |

The Wago 221-413 connectors T-junction the RS485 A, B, and GND lines without
cutting the existing cable. See `docs/Hardware.md` for wiring diagram.

---

## 4. ACE Pro Custom Cable

The ACE Pro uses an internal Molex Micro-Fit 3.0 Male 2×3 connector. A custom cable
is required to connect it to the Pi's USB port.

| Qty | Item | Part / Number | Source | Est. Unit Cost |
|-----|------|--------------|--------|---------------|
| 1 | Molex Micro-Fit 3.0 Receptacle housing, 2×3 (6-circuit) | **43025-0600** | Digi-Key / Molex | ~$0.60 |
| 4 | Molex Micro-Fit 3.0 Female crimp terminal, 24–28 AWG | **43030-0007** | Digi-Key / Molex | ~$0.25 each (~$1.00) |
| 1 | USB-A Male plug with bare wire leads (or stripped USB-A cable) | Generic | Amazon / local | ~$1–2 |
| 0.5 m | 26 AWG hook-up wire, 3 colours (D+, D−, GND) | UL1007 or equivalent | Amazon / local | ~$1 |

> Only pins 2 (D−), 3 (D+), and 5 (GND) are wired. Pin 6 (VCC) must **not** be
> connected to USB VBUS. See `docs/Hardware.md` for pinout.

---

## 5. ACE 2 Pro RS485 Cable (Optional — only if making a Y-cable)

If you prefer a dedicated Y-cable over the Wago T-junction approach, the ACE 2 Pro
uses a Molex Micro-Fit 3.0 Female 2×2 connector.

| Qty | Item | Part / Number | Source | Est. Unit Cost |
|-----|------|--------------|--------|---------------|
| 1 | Molex Micro-Fit 3.0 Plug housing, 2×2 (4-circuit) | **43025-0400** | Digi-Key / Molex | ~$0.50 |
| 3 | Molex Micro-Fit 3.0 Female crimp terminal, 24–28 AWG | **43030-0007** | Digi-Key / Molex | ~$0.25 each (~$0.75) |

---

## 6. Miscellaneous / Assembly

| Qty | Item | Notes | Est. Cost |
|-----|------|-------|-----------|
| 1 | Heat shrink tubing assortment | For cable strain relief | ~$3 |
| 1 | Cable ties / velcro straps | Cable management | ~$2 |
| 1 | Enclosure (optional) | Small ABS project box or DIN rail enclosure | ~$5–15 |
| 1 | Ferrite choke, 5 mm ID (optional) | EMI suppression on RS485 cable near Pi | ~$1 |

---

## 7. Tools (One-Time, Not Consumed)

| Item | Notes | Est. Cost |
|------|-------|-----------|
| Molex crimp tool | Engineer PA-09 or PA-21 recommended — fits Micro-Fit 3.0 terminals | ~$20–35 |
| Digital multimeter | For voltage measurement before connection — **mandatory** | ~$15–30 |
| Wire stripper | 22–28 AWG | ~$10 |
| Soldering iron (optional) | Only needed if not using crimped connections | ~$20+ |
| Oscilloscope (optional) | Useful for verifying RS485 signals and baud rate | ~$50–300 |

---

## Cost Summary

| Category | Est. Cost |
|----------|-----------|
| Raspberry Pi 4B 2GB + SD + PSU | ~$55 |
| RS485 interface (USB adapter, Option A) | ~$10 |
| RS485 T-junction (Wago + cable) | ~$7 |
| ACE Pro custom cable (Molex + wire) | ~$5 |
| ACE 2 Pro Y-cable (Molex, optional) | ~$2 |
| Misc / assembly | ~$10 |
| **Total (excluding tools, Option A RS485)** | **~$89** |
| Tools (one-time) | ~$45–75 |

---

## Sourcing Notes

- **Digi-Key / Mouser**: Best source for genuine Molex parts; minimum order quantities apply
  (Molex terminals typically sold in reels of 100, but break quantities available at Digi-Key)
- **Amazon**: Adequate for Raspberry Pi, SD card, USB adapters, Wago connectors, and wire
- **LCSC**: Cheapest source for crimp terminals and connectors if ordering from China
- **Raspberry Pi resellers**: adafruit.com, pimoroni.com (UK), okdo.com — check local stock

---

## Revision Notes

| Date | Change |
|------|--------|
| 2026-06-28 | Initial BOM — connector part numbers confirmed from community research |
| — | HW-2: ACE Pro external chassis connector unconfirmed — cable design may change |
| — | HW-3: RS485 bus voltage unconfirmed — transceiver selection may change |
