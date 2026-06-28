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
| 1 | Printer (4-pin) → ACE 2 Pro bottom-left (6-pin) | "K3/K3M/S1 Signal Cable" (factory supplied with ACE 2 Pro) | None |
| 2 | ACE 2 Pro daisy-chain back port → Pi USB | Custom Molex pigtail + USB-RS485 adapter | Build — **confirm HW-1 first** |
| 3 | Pi USB → ACE Pro (Molex 2×3) | Custom Molex 2×3 → USB-A cable | Build |

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

**Confirmed (physical inspection, 2026-06-28):** The daisy-chain port on the back of the
ACE 2 Pro is the **top connector** on the back panel — Molex Micro-Fit 3.0 **6-pin (2×3)**.
The back panel also has a lower 4-pin (2×2) connector whose purpose is unknown (HW-5) —
do not connect to it.

> ⚠️ **Connector orientation**: Confirm whether the device has a plug (pin header) or
> receptacle (socket) before ordering the housing. If the device has a receptacle, use
> `43025-0600` (cable receptacle). If the device has a plug header, use `43020-0600`.

| Qty | Item | Molex Part | Source | Est. Unit Cost |
|-----|------|-----------|--------|---------------|
| 1 | Molex Micro-Fit 3.0 6-pin housing (confirm orientation — see note above) | **43025-0600** receptacle or **43020-0600** plug | Digi-Key / Molex | ~$0.60 |
| 3 | Molex Micro-Fit 3.0 Female crimp terminal, 20–24 AWG | **43030-0007** | Digi-Key / Molex | ~$0.25 each (~$0.75) |
| ~0.5 m | 3-conductor shielded cable, 22–24 AWG | Alpha Wire 5563 or Belden 9533 (not 9501 — 2-conductor only) | Digi-Key / local | ~$2–3 |

Wire the pigtail as follows (connect free ends to USB-RS485 adapter terminals):

| Molex Pin | Signal | Adapter Terminal |
|-----------|--------|-----------------|
| Pin 1 | RS485 B (D−) | B |
| Pin 2 | RS485 A (D+) | A |
| Pin 4 | GND | GND (insulated conductor — do not use shield/drain as GND) |
| Pin 3 | VCC | Not connected |

Connect the cable shield at the ACE 2 Pro end only.

---

## 3. Cable B: Raspberry Pi → ACE Pro (USB)

**Confirmed (physical inspection, 2026-06-28):** The ACE Pro external chassis port is
the Molex Micro-Fit 3.0 Male 2×3. No standard USB port is present. Build this cable.

| Qty | Item | Molex Part | Source | Est. Unit Cost |
|-----|------|-----------|--------|---------------|
| 1 | Molex Micro-Fit 3.0 Receptacle housing, 2×3 (6-circuit) | **43025-0600** | Digi-Key / Molex | ~$0.60 |
| 4 | Molex Micro-Fit 3.0 Female crimp terminal, 20–24 AWG | **43030-0007** | Digi-Key / Molex | ~$0.25 each (~$1.00) |
| 1 | USB-A Male plug with bare wire leads, or cut USB-A cable | Generic | Amazon / local | ~$1–2 |
| ~0.5 m | 24 AWG hook-up wire, 4 colours | UL1007 or equivalent | Amazon / local | ~$1 |

Wire as follows:

| Molex Pin | Signal | USB-A Pin |
|-----------|--------|----------|
| Pin 2 | USB D− | Pin 2 (D−) |
| Pin 3 | USB D+ | Pin 3 (D+) |
| Pin 5 | GND | Pin 4 (GND) |
| Pin 6 | VCC / VBUS | Pin 1 (VBUS) — **must connect** to power the ACE Pro |
| Pin 1 | NC | — |
| Pin 4 | NC | — |

Pin 6 (VCC) is the VBUS input to the ACE Pro. Without it connected to USB-A Pin 1, the
device receives no power and will not enumerate on the Pi's USB bus.

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
| 2026-06-28 | Fixed Cable B: Pin 6 (VCC/VBUS) must connect to USB-A VBUS to power ACE Pro |
| 2026-06-28 | Fixed Cable A: specify 3-conductor shielded cable; Belden 9501 is 2-conductor only |
| 2026-06-28 | Fixed crimp terminal AWG: 43030-0007 is 20–24 AWG; changed wire spec to 24 AWG |
| 2026-06-28 | Added Molex housing mating caveat: 43025 vs 43020 depends on device connector type |
| 2026-06-28 | HW-1 resolved: ACE 2 Pro daisy-chain port is top 6-pin (2×3) connector on back panel |
| — | HW-2: ACE Pro external chassis connector unconfirmed — Cable B may not be needed |
| — | HW-3: RS485 bus voltage unconfirmed — transceiver spec may change |
