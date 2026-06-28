# Architecture

## Overview

The ACE Bridge is a Raspberry Pi application that implements a bidirectional protocol bridge,
allowing an Anycubic ACE Pro filament hub to appear as a second ACE 2 Pro unit to an
Anycubic Kobra 3 V2 printer.

## Hardware Topology

```
Anycubic Kobra 3 V2
        │
        │  RS485 bus
        │
        ▼
   ACE 2 Pro (genuine unit, slot 1–4)
        │
        │  RS485 bus (daisy-chain or separate?)
        │  ⚠️ UNKNOWN: exact topology TBD from capture
        ▼
 ┌─────────────────┐
 │  Raspberry Pi   │  ← ACE Bridge
 │                 │
 │  RS485 HAT  USB │
 └──────┬──────┬───┘
        │      │
        │      │  USB
        │      ▼
        │   ACE Pro (slot 5–8 from printer's perspective)
        │
        │  RS485 (upstream, towards printer)
        ▼
   [same bus as above]
```

## Software Layers

```
┌──────────────────────────────────────┐
│           CLI (typer)                │  bridge start / sniff / decode ...
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│         Bridge Orchestrator          │  Wires layers together, lifecycle
└──────┬───────────────────┬───────────┘
       │                   │
┌──────▼──────┐   ┌────────▼────────┐
│ ACE 2 Pro   │   │  ACE Pro        │
│ Emulator    │   │  Driver         │
│             │   │                 │
│ Looks like  │   │ Controls real   │
│ an ACE 2    │   │ ACE Pro via USB │
│ Pro to the  │   │                 │
│ printer     │   │                 │
└──────┬──────┘   └────────┬────────┘
       │                   │
       └─────────┬─────────┘
                 │
┌────────────────▼─────────────────────┐
│         Translation Layer            │  ACE2 ↔ Abstract ↔ ACEPro
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│       Abstract Command Model         │  LOAD_FILAMENT, SET_TEMP, etc.
│       + State Manager                │  Slot status, temps, errors
└──────┬──────────────────┬────────────┘
       │                  │
┌──────▼──────┐   ┌───────▼──────┐
│  Protocol   │   │  Protocol    │
│  ACE 2 Pro  │   │  ACE Pro     │
│  (RS485)    │   │  (USB)       │
└──────┬──────┘   └───────┬──────┘
       │                  │
┌──────▼──────┐   ┌───────▼──────┐
│  RS485      │   │  USB         │
│  Transport  │   │  Transport   │
└─────────────┘   └──────────────┘
```

## Layer Responsibilities

### Transport Layers (`rs485/`, `usb/`)
- Raw byte I/O only
- No awareness of packet boundaries or protocol
- Async read/write with configurable timeouts
- Error counting (framing errors, USB errors)

### Protocol Layers (`protocol/ace2/`, `protocol/acepro/`)
- Packet framing: find start/end bytes in byte stream
- Encode/decode packet fields
- CRC calculation and validation
- Addressing (device address within RS485 bus)
- No application logic

### Emulator (`emulator/`)
- Maintains state that a real ACE 2 Pro would maintain
- Responds to all commands a printer might send
- Delegates actual work to the translator
- Never communicates directly with ACE Pro

### Driver (`TODO: move to dedicated driver module`)
- Controls ACE Pro over USB
- Translates abstract commands to ACE Pro-specific commands
- Reports ACE Pro state back as abstract state events

### Translator (`translator/`)
- Maps abstract commands from emulator → driver direction
- Maps abstract state from driver → emulator direction
- Handles slot remapping (printer slot N → ACE Pro slot M)

### Abstract Command Model (`models/commands.py`)
- Device-independent representation of all operations
- Example: `LoadFilament(slot=5)` maps to `LoadFilament(slot=1)` on ACE Pro
- This is the stable interface between emulator and driver

### State Manager (`models/state.py`)
- Single source of truth for all device state
- Slot occupancy, temperatures, humidity, errors, motor activity
- Thread-safe (asyncio-compatible)

### Capture (`capture/`)
- Passive observation of all traffic on both interfaces
- Timestamped hex dumps
- JSON/CSV/PCAP export
- Replay from capture file for offline debugging

### Config (`config/`)
- YAML-based, validated with Pydantic
- All hardware parameters, slot mappings, timeouts

## Design Decisions

### Abstract Command Layer (why not direct packet translation)

Direct packet translation would couple the two protocols tightly. If the ACE 2 Pro
protocol changes, every packet handler would need updating. By introducing an abstract
command layer, the emulator and driver are independently evolvable.

The cost is an extra encoding/decoding step. Given the low throughput of these filament
change operations, this cost is negligible.

### Asyncio

Both RS485 and USB I/O are I/O-bound and benefit from cooperative multitasking.
Asyncio allows the bridge to handle the upstream RS485 and downstream USB concurrently
without threads, keeping state management simpler.

### Pydantic for config and models

Pydantic provides validated, typed config loading and model definitions at no runtime
cost once parsed. Given Python 3.12 and Pydantic v2, this is fast enough for our use.

## State Machine

```
IDLE ──────────────────► LOADING
  ▲                         │
  │                         ▼
  │                    LOADED ──► UNLOADING
  │                         │
  └─────────────────────────┘
       + DRYING, ERROR, UNKNOWN states
```

See `models/state.py` for the full state model.

## Concurrency Model

```
Main event loop (asyncio)
    │
    ├── rs485_reader_task     — reads bytes from upstream RS485
    ├── rs485_writer_task     — sends bytes upstream on RS485
    ├── usb_reader_task       — reads bytes from ACE Pro USB
    ├── usb_writer_task       — sends bytes to ACE Pro USB
    ├── packet_router_task    — dispatches decoded packets
    ├── heartbeat_task        — sends periodic heartbeats
    └── capture_writer_task   — flushes capture log to disk
```

All inter-task communication via `asyncio.Queue`.

## Configuration Model

```yaml
printer:
  rs485_port: /dev/ttyUSB0
  baud_rate: 115200          # ⚠️ UNKNOWN — placeholder
  address: 0x01              # ⚠️ UNKNOWN — bridge RS485 address

ace_pro:
  usb_vid: 0x0000            # ⚠️ UNKNOWN — fill after capture
  usb_pid: 0x0000            # ⚠️ UNKNOWN — fill after capture
  usb_endpoint_in: 0x81      # ⚠️ UNKNOWN
  usb_endpoint_out: 0x01     # ⚠️ UNKNOWN

mapping:
  slot_offset: 4             # ACE Pro slot 1 = printer slot 5

bridge:
  simulate: false
  capture_enabled: true
  capture_path: captures/
  log_level: INFO
  read_only: false           # Safety: if true, never transmit
```
