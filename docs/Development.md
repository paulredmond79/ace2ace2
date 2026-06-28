# Development Guide

## Prerequisites

- Python 3.12+
- Git
- `libusb` (for pyusb): `sudo apt install libusb-1.0-0-dev`
- RS485 hardware (optional for software development)

## Environment Setup

```bash
# Clone the repository
git clone https://github.com/paulredmond79/ace2ace2.git
cd ace2ace2

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
bridge --help
pytest --collect-only
```

## Running Tests

```bash
# All tests (no hardware required)
pytest

# With coverage report
pytest --cov=ace_bridge --cov-report=term-missing

# Hardware tests (requires connected devices)
pytest -m hardware

# Specific module
pytest tests/test_protocol/

# Verbose output
pytest -v
```

## Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/ tests/

# Formatting
black src/ tests/

# All checks in one go
ruff check src/ tests/ && black --check src/ tests/ && mypy src/
```

## Working with Captures

Place capture files in `captures/`. Supported formats:
- `.jsonl` — line-delimited JSON (native format)
- `.bin` — raw binary RS485/USB bytes
- `.pcapng` — Wireshark PCAP next generation

```bash
# View a capture
bridge decode --input captures/session.jsonl

# Replay against simulator
bridge replay --input captures/session.jsonl --simulate

# Export to CSV
bridge decode --input captures/session.jsonl --output csv > session.csv
```

## Adding Protocol Support

When a new packet type is discovered:

1. Add the packet to `docs/Protocol.md` with source and confidence
2. Remove from `docs/Unknowns.md`
3. Add a Pydantic model in `src/ace_bridge/protocol/ace2/packets.py` (or `acepro/`)
4. Add a decode function in the protocol module
5. Add a unit test in `tests/test_protocol/` using the real captured bytes
6. Add a mapping in `src/ace_bridge/translator/` if it requires translation

Always cite the source of packet format knowledge in a comment:
```python
# Source: captures/2026-07-01-load-seq.jsonl, packet #14
# Confidence: High — confirmed by replaying against real hardware
LOAD_FILAMENT_CMD = 0x12
```

## Development Workflow

### Iterative Loop

1. Capture traffic (RS485 or USB)
2. Decode with `bridge decode`
3. Identify new packet types
4. Add to protocol model with test
5. Update translator if needed
6. Run tests
7. Commit

### Commit Discipline

- Every commit must pass `pytest` and `mypy`
- Commit messages: `type(scope): description`
  - `feat(protocol): add LOAD_FILAMENT decode for ACE 2 Pro`
  - `fix(rs485): correct baud rate after capture confirms 115200`
  - `docs(unknowns): resolve RS-1 baud rate`
  - `test(emulator): add heartbeat response regression test`

### Branch Strategy

- `main` — stable, tested code
- `claude/ace-bridge-setup-ozqqm3` — active development
- `feat/...` — individual features

## Project Milestones

See `docs/Roadmap.md` for the full development roadmap.

## Module Conventions

### Every Source Module Must Have

- Module-level docstring describing purpose and scope
- Type hints on all functions and methods
- Pydantic models for all data structures crossing module boundaries

### Transport Modules (`rs485/`, `usb/`)

- No protocol logic whatsoever
- Only deal with raw bytes
- Raise transport-layer exceptions (`RS485Error`, `USBError`)

### Protocol Modules (`protocol/`)

- Only deal with byte sequences and packet models
- No I/O
- Fully unit-testable without hardware

### Test Fixtures

Place captured packet bytes in `tests/fixtures/`:
```
tests/fixtures/
  ace2_pro/
    startup_sequence.bin
    load_filament_slot1.bin
  ace_pro/
    usb_init.bin
```

Reference in tests:
```python
from tests.fixtures import load_fixture
packet_bytes = load_fixture("ace2_pro/startup_sequence.bin")
```

## Raspberry Pi Deployment

```bash
# On the Pi
git clone https://github.com/paulredmond79/ace2ace2.git
cd ace2ace2
pip install -e ".[dev]"

# Configure
cp config/config.yaml config/local.yaml
# Edit local.yaml with your hardware ports

# Start in read-only sniff mode first
bridge sniff-rs485 --port /dev/ttyAMA0

# Start bridge (simulate first)
bridge start --config config/local.yaml --simulate

# Start real bridge (once confident)
bridge start --config config/local.yaml
```

## Debugging

### Enable packet tracing

```bash
bridge start --config config/local.yaml --log-level DEBUG --trace-packets
```

### Inspect USB device

```bash
bridge inspect-usb
# Or manually:
lsusb -v | grep -A 20 "ACE"
```

### Decode a single hex string

```bash
bridge decode-hex "AA 01 04 12 01 00 B3"
```
