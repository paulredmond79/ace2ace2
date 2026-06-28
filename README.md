# ACE Bridge

A Raspberry Pi protocol bridge that allows an Anycubic **ACE Pro** to appear as a second **ACE 2 Pro** on an Anycubic Kobra 3 V2 printer.

## Hardware Topology

```
Anycubic Kobra 3 V2
        │ RS485 (230400 baud, via USB-to-RS485 adapter)
        ▼
   ACE 2 Pro (genuine, slots 1–4)
        │ RS485 (same bus)
        ▼
 ┌─────────────────┐
 │  Raspberry Pi   │  ← ACE Bridge (this project)
 │  Bridge         │
 └──────┬──────────┘
        │ USB CDC (115200 baud)
        ▼
    ACE Pro (slots 5–8 from printer's perspective)
```

The bridge emulates a second ACE 2 Pro on the RS485 bus, translating commands to and from the ACE Pro over USB. The printer believes it is communicating with two compatible ACE 2 Pro units.

## Status: Active Development — Pre-Hardware Phase

Protocol research is complete. Both protocols are well understood from community reverse engineering. Hardware capture is the next step before production implementation.

See [docs/Roadmap.md](docs/Roadmap.md) for milestone progress.

## Protocol Knowledge

| Protocol | Status | Confidence |
|----------|--------|------------|
| ACE Pro (ACE1) USB | **Frame format known**, JSON-RPC commands documented | High |
| ACE 2 Pro RS485 | **Frame format known**, 78 commands enumerated, protobuf payload | High |
| ACE 2 Pro protobuf schema | Partially reconstructed from MCU analysis | Medium |
| USB VID/PID (ACE Pro) | VID 0x28E9, PID 0x018A (needs hardware confirmation) | Medium |
| USB VID/PID (ACE 2 Pro) | VID 0x1A86, PID unknown | Low |

See [docs/Protocol.md](docs/Protocol.md) for full protocol documentation.

## Architecture

```
Printer (RS485)
    │
ACE 2 Pro Emulator        ← Looks like a real ACE 2 Pro to the printer
    │
Translation Layer         ← Maps abstract commands, remaps slot numbers
    │
Abstract Command Model    ← Device-independent: LOAD_FILAMENT, SET_TEMP, etc.
    │
ACE Pro Driver (USB)      ← Controls real ACE Pro over USB CDC
    │
ACE Pro Hardware
```

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Run tests (no hardware required)
pytest

# Inspect connected USB devices (find ACE Pro VID/PID)
bridge inspect-usb

# Sniff RS485 traffic (read-only)
bridge sniff-rs485 --port /dev/ttyUSB0

# Decode a capture file
bridge decode --input captures/session.jsonl

# Decode a hex packet
bridge decode-hex "FF AA 03 00 00 06 00 xx xx FE"

# Start in simulation mode
bridge start --simulate
```

## Development

```bash
# Type check
mypy src/

# Lint + format
ruff check src/ tests/
black src/ tests/
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/Architecture.md](docs/Architecture.md) | Software architecture and layer design |
| [docs/Protocol.md](docs/Protocol.md) | Protocol specifications (ACE1 + ACE2) |
| [docs/Hardware.md](docs/Hardware.md) | Hardware requirements and BOM |
| [docs/Safety.md](docs/Safety.md) | Safety rules before connecting hardware |
| [docs/Unknowns.md](docs/Unknowns.md) | Known unknowns — check before implementing |
| [docs/Roadmap.md](docs/Roadmap.md) | Development milestones |
| [docs/Research.md](docs/Research.md) | Community research summary |
| [research/findings.md](research/findings.md) | Raw research notes |

## Community Research Sources

Key community reverse engineering repositories:

- [printers-for-people/ACEResearch](https://github.com/printers-for-people/ACEResearch) — ACE1 strace captures
- [hakimio gists](https://gist.github.com/hakimio/4916ff69add458fdc51aeea76f21efb9) — ACE2 MCU firmware IDA analysis
- [Kobra-S1/ACEPRO](https://github.com/Kobra-S1/ACEPRO) — Working Klipper driver for ACE1+ACE2
- [szkrisz/ACEPROSV08](https://github.com/szkrisz/ACEPROSV08) — Klipper ACE1 driver

## Technology Stack

Python 3.11+, asyncio, pyserial, pyusb, typer, rich, pydantic, pytest, mypy, ruff

## Safety

Read [docs/Safety.md](docs/Safety.md) **before connecting any hardware**. The bridge
defaults to `read_only: true` — it will never transmit until explicitly enabled.

## Contributing

This is an open-source reverse engineering project. Protocol knowledge evolves
as captures and analysis progress. See [docs/Development.md](docs/Development.md)
for contribution guidelines.

When adding protocol knowledge:
1. Document the source and confidence in `docs/Protocol.md`
2. Remove from `docs/Unknowns.md`
3. Add a test using real captured bytes

## License

See [LICENSE](LICENSE).
