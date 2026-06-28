# ACE Bridge — Claude Code Guide

## Project Purpose

This is a reverse engineering project building a Raspberry Pi protocol bridge.

The bridge sits between an Anycubic Kobra 3 V2 printer and an ACE Pro filament hub,
making the ACE Pro appear to the printer as a second ACE 2 Pro unit.

**Hardware chain:**
```
Anycubic Kobra 3 V2
        │ RS485
        ▼
   ACE 2 Pro (genuine)
        │ RS485
        ▼
 Raspberry Pi Bridge  ← you are building this
        │ USB
        ▼
    ACE Pro
```

## Critical Rules

### Never invent protocol data
If a packet format, CRC algorithm, baud rate, or command value is unknown:
- Document the unknown in `docs/Unknowns.md`
- Add a TODO comment in code
- Build tooling to discover it
- Do NOT guess and hardcode a value

### Safety first
- Never drive RS485 TX unless a valid, validated packet is ready
- Always support read-only sniff mode
- Validate every packet before acting on it
- Fail safe: on any ambiguity, stop transmitting

### Preserve working state
Every commit must leave the project in a working state (tests pass, imports work).

## Repository Layout

```
ace-bridge/
├── src/ace_bridge/          # Main Python package
│   ├── bridge/              # Top-level bridge orchestration
│   ├── rs485/               # RS485 transport (no protocol logic)
│   ├── usb/                 # USB transport (no protocol logic)
│   ├── protocol/            # Packet encode/decode/CRC/validation
│   │   ├── ace2/            # ACE 2 Pro protocol (RS485, printer-facing)
│   │   └── acepro/          # ACE Pro protocol (USB, device-facing)
│   ├── emulator/            # ACE 2 Pro emulator (printer-facing)
│   ├── translator/          # ACE2 ↔ abstract ↔ ACE Pro translation
│   ├── models/              # Abstract command model + state
│   ├── capture/             # Packet capture, logging, replay, export
│   ├── config/              # YAML config loader + validation
│   ├── logging/             # Structured logging
│   └── utils/               # Hex dump, CRC helpers, etc.
├── tests/                   # All test suites
├── docs/                    # Architecture, protocol, hardware docs
├── research/                # Raw research notes, community findings
├── captures/                # Saved packet captures (binary + JSON)
├── config/                  # YAML config files
├── hardware/                # Circuit diagrams, BOM, pinouts
└── scripts/                 # Setup, deploy, utility scripts
```

## Architecture Invariant

**Never do direct packet-to-packet translation.**

The translation path is always:
```
ACE 2 Pro packet
    ↓ decode
Abstract command (models/commands.py)
    ↓ translate
ACE Pro packet
    ↑ encode
```

This means the `emulator` and `driver` layers are independent. Adding a new device
only requires adding a new driver, not touching the emulator.

## Development Commands

```bash
# Install in dev mode
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/ tests/
black --check src/ tests/

# Run the bridge CLI
bridge --help
bridge start --config config/config.yaml --simulate
bridge sniff-rs485 --port /dev/ttyUSB0
bridge sniff-usb --vid 0xXXXX --pid 0xXXXX
bridge capture --output captures/session.jsonl
```

## Key Files

| File | Purpose |
|------|---------|
| `src/ace_bridge/models/commands.py` | Abstract command model — edit this when new commands are discovered |
| `src/ace_bridge/models/state.py` | Device state model — all known state tracked here |
| `docs/Protocol.md` | Protocol documentation — update as reverse engineering progresses |
| `docs/Unknowns.md` | Known unknowns — always check here before implementing anything |
| `research/findings.md` | Community and public research findings |
| `config/config.yaml` | Reference configuration |

## Protocol Status

> **Current state: Pre-capture.** No protocol details have been confirmed by packet
> capture. All protocol assumptions are documented in `docs/Unknowns.md`.
> The priority is to capture real traffic before implementing decode logic.

See `docs/Protocol.md` for the current state of protocol knowledge.

## Adding Protocol Knowledge

When you learn something new about either protocol:

1. Update `docs/Protocol.md` — add the finding with source and confidence
2. Remove the item from `docs/Unknowns.md`
3. Update the relevant model in `src/ace_bridge/protocol/`
4. Add a regression test using a real captured packet
5. Note: never hardcode a value without a source comment citing evidence

## Testing Philosophy

- Most tests must run without hardware
- Use `tests/fixtures/` for captured packet bytes
- Mock transport layers in unit tests
- Integration tests use `--simulate` mode
- Hardware-requiring tests are marked `@pytest.mark.hardware`

## Branch Workflow

- Feature branch: `claude/ace-bridge-setup-ozqqm3`
- Commit small, working increments
- Every commit should pass `pytest` and `mypy`
