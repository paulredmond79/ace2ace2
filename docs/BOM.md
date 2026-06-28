# Bill of Materials — ACE Bridge

Complete parts list for building one ACE Bridge unit.

> ⚠️ **Before ordering**: Verify the ACE Pro external connector type (HW-2 in
> `docs/Unknowns.md`) and the RS485 bus voltage (HW-3). These affect cable and
> transceiver selection. See `docs/Hardware.md` for full wiring details and
> `docs/Safety.md` for the pre-connection checklist.

---

## Connection overview

| # | Connection | Cable | Action |
|---|-----------|-------|--------|
| 1 | Printer → ACE 2 Pro (front port) | Factory RS485 cable | None — already provided |
| 2 | ACE 2 Pro daisy-chain (back) → Pi | Custom Molex 2×2 pigtail + USB-RS485 adapter | Build |
| 3 | Pi → ACE Pro | Custom Molex 2×3 → USB-A cable | Build |

---

## 1. Compute

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 1 | Raspberry Pi 4B 2GB | SC0193 | raspberrypi.com / Approved Resellers | ~$35 |
| 1 | MicroSD card, 32GB+ A1/A2 | Samsung Pro Endurance or equivalent | Amazon / local | ~$8 |
| 1 | USB-C power supply, 5V/5A | Official Raspberry Pi 27W PSU | raspberrypi.com | ~$12 |

> **Pi 4B** is the primary recommendation: 4× USB ports (one for the USB-RS485 adapter,
> one for the ACE Pro cable), GPIO header, gigabit Ethernet. Pi 5 is a fine substitute.

---

## 2. Cable A: ACE 2 Pro Daisy-Chain → Raspberry Pi (RS485)

This cable connects the daisy-chain port on the **back** of the ACE 2 Pro to the Pi
via a USB-RS485 adapter. The adapter handles the RS485 ↔ USB conversion and plugs
directly into one of the Pi's USB-A ports (`/dev/ttyUSB0`).

### USB-RS485 Adapter

| Qty | Item | Part | Source | Est. Unit Cost |
|-----|------|------|--------|---------------|
| 1 | USB-RS485 adapter with screw terminal block | DSD TECH SH-U11, Waveshare USB TO RS485, or FTDI-based equivalent | Amazon / AliExpress | ~$8–12 |

Choose an adapter with a **screw terminal or detachable connector block** — you will
connect the Molex pigtail wires directly to the A, B, and GND terminals.

### Molex Pigtail (ACE 2 Pro Daisy-Chain End)

| Qty | Item | Molex Part | Source | Est. Unit Cost |
|-----|------|-----------|--------|---------------|
| 1 | Molex Micro-Fit 3.0 Plug housing, 2×2 (4-circuit) | **43025-0400** | Digi-Key / Molex | ~$0.60 |
| 3 | Molex Micro-Fit 3.0 Female crimp terminal, 24–28 AWG | **43030-0007** | Digi-Key / Molex | ~$0.25 each (~$0.75) |
| ~0.5 m | Shielded twisted pair, 24 AWG (3-wire) | Belden 9501 or equivalent | Digi-Key / local | ~$2 |

Wire the pigtail as follows (connect free ends to USB-RS485 adapter terminals):

| Molex Pin | Signal | Adapter Terminal |
|-----------|--------|-----------------|
| Pin 1 | RS485 B (D−) | B |
| Pin 2 | RS485 A (D+) | A |
| Pin 4 | GND | GND |
| Pin 3 | VCC | Not connected |

Connect the cable shield at the ACE 2 Pro end only.

---

## 3. Cable B: Raspberry Pi → ACE Pro (USB)

The ACE Pro uses an internal Molex Micro-Fit 3.0 Male 2×3 connector. This custom cable
presents a USB-A plug to the Pi's USB port, powering and communicating with the ACE Pro.

| Qty | Item | Molex Part | Source | Est. Unit Cost |
|-----|------|-----------|--------|---------------|
| 1 | Molex Micro-Fit 3.0 Receptacle housing, 2×3 (6-circuit) | **43025-0600** | Digi-Key / Molex | ~$0.60 |
| 3 | Molex Micro-Fit 3.0 Female crimp terminal, 24–28 AWG | **43030-0007** | Digi-Key / Molex | ~$0.25 each (~$0.75) |
| 1 | USB-A Male plug with bare wire leads, or cut USB-A cable | Generic | Amazon / local | ~$1–2 |
| ~0.5 m | 26 AWG hook-up wire, 3 colours | UL1007 or equivalent | Amazon / local | ~$1 |

Wire as follows:

| Molex Pin | Signal | USB-A Pin |
|-----------|--------|----------|
| Pin 2 | USB D− | Pin 2 (D−) |
| Pin 3 | USB D+ | Pin 3 (D+) |
| Pin 5 | GND | Pin 4 (GND) |
| Pin 1 | NC | — |
| Pin 4 | NC | — |
| Pin 6 | VCC | **Do NOT connect** to VBUS |

> ⚠️ **Pin 6 (VCC) must not be connected to USB-A VBUS.** The ACE Pro is bus-powered
> by the Pi. Bridging a second supply causes a short or over-voltage condition.

---

## 4. Miscellaneous / Assembly

| Qty | Item | Notes | Est. Cost |
|-----|------|-------|-----------|
| 1 | Heat shrink tubing assortment | Strain relief on both custom cables | ~$3 |
| 1 | Cable ties / velcro straps | Cable management | ~$2 |
| 1 | Enclosure (optional) | Small ABS project box or DIN rail enclosure | ~$5–15 |
| 1 | Ferrite choke, 5 mm ID (optional) | EMI suppression on RS485 cable near Pi | ~$1 |

---

## 5. Tools (One-Time, Not Consumed)

| Item | Notes | Est. Cost |
|------|-------|-----------|
| Molex crimp tool | Engineer PA-09 or PA-21 recommended — fits Micro-Fit 3.0 terminals | ~$20–35 |
| Digital multimeter | **Mandatory** — for verifying pinout and bus voltage before connection | ~$15–30 |
| Wire stripper | 22–28 AWG | ~$10 |
| Soldering iron (optional) | Only if not crimping; crimping is strongly preferred | ~$20+ |
| Oscilloscope (optional) | Useful for verifying RS485 signal quality | ~$50–300 |

---

## 6. Cost Summary

| Category | Est. Cost |
|----------|-----------|
| Raspberry Pi 4B 2GB + SD + PSU | ~$55 |
| Cable A: USB-RS485 adapter | ~$10 |
| Cable A: Molex 2×2 pigtail parts | ~$4 |
| Cable B: Molex 2×3 + USB-A parts | ~$4 |
| Misc / assembly | ~$7 |
| **Total (excluding tools)** | **~$80** |
| Tools (one-time) | ~$45–75 |

---

## 7. Sourcing Notes

- **Digi-Key / Mouser**: Best source for genuine Molex housings and terminals. Terminals
  are sold in reels of 100 but break quantities are available at Digi-Key.
- **Amazon**: Adequate for Pi, SD card, USB-RS485 adapters, and hook-up wire.
- **LCSC**: Cheapest for Molex equivalents if ordering from China.
- **Raspberry Pi resellers**: adafruit.com, pimoroni.com (UK), okdo.com.

---

## 8. Revision Notes

| Date | Change |
|------|--------|
| 2026-06-28 | Revised topology: daisy-chain through ACE 2 Pro back port — no T-junction |
| 2026-06-28 | Removed Wago connectors; added USB-RS485 adapter as Cable A component |
| — | HW-2: ACE Pro external chassis connector unconfirmed — Cable B design may change |
| — | HW-3: RS485 bus voltage unconfirmed — transceiver spec may change |
