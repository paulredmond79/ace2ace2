# Testing

## Philosophy

- **Hardware is not required** for most tests
- Real captured packets are the gold standard for protocol tests
- Simulation mode enables full end-to-end testing without any hardware
- Hardware tests are isolated with `@pytest.mark.hardware`

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/                # Real captured packet bytes
│   ├── ace2_pro/
│   └── ace_pro/
├── test_protocol/
│   ├── test_ace2_decode.py  # ACE 2 Pro packet decode
│   ├── test_ace2_encode.py  # ACE 2 Pro packet encode
│   ├── test_acepro_decode.py
│   └── test_crc.py
├── test_transport/
│   ├── test_rs485.py        # Mock serial port
│   └── test_usb.py          # Mock USB device
├── test_emulator/
│   └── test_ace2_emulator.py
├── test_translator/
│   └── test_translator.py
├── test_state/
│   └── test_state_machine.py
├── test_capture/
│   └── test_capture_writer.py
├── test_cli/
│   └── test_cli.py
└── integration/
    ├── test_bridge_simulate.py  # Full bridge in simulate mode
    └── test_replay.py           # Replay capture files
```

## Running Tests

```bash
# All non-hardware tests (CI default)
pytest

# With coverage
pytest --cov=ace_bridge --cov-report=term-missing --cov-fail-under=80

# Hardware tests only (requires connected Pi + devices)
pytest -m hardware -v

# Skip slow tests
pytest -m "not slow"

# Single module
pytest tests/test_protocol/ -v
```

## Test Markers

```python
@pytest.mark.hardware   # Requires physical hardware
@pytest.mark.slow       # Takes >5 seconds
@pytest.mark.integration # Requires full bridge stack
```

Register in `pyproject.toml` under `[tool.pytest.ini_options]`.

## Writing Protocol Tests

The most important tests are protocol encode/decode tests anchored to real captured bytes.

```python
# tests/test_protocol/test_ace2_decode.py

def test_decode_heartbeat_response():
    # Source: captures/2026-07-01-idle.jsonl, packet #3
    # Confidence: High — repeated pattern in 100+ captures
    raw = bytes.fromhex("AA 01 04 10 00 xx xx".replace(" ", ""))
    packet = decode_ace2_packet(raw)
    assert packet.packet_type == PacketType.HEARTBEAT_RESPONSE
    assert packet.address == 0x01
    assert packet.crc_valid
```

**Rule**: Never write a protocol test without citing the capture source in a comment.

## Mock Transports

Use `MockRS485` and `MockUSB` for unit testing without hardware:

```python
from tests.mocks import MockRS485, MockUSB

async def test_emulator_responds_to_heartbeat():
    transport = MockRS485()
    transport.inject(b"...")  # simulate incoming packet
    emulator = ACE2Emulator(transport=transport)
    await emulator.process_one()
    assert transport.last_sent == b"..."  # expected response
```

## Regression Tests

For every bug fixed, add a regression test that:
1. Uses the exact bytes that triggered the bug
2. Is named `test_regression_<description>`
3. Has a comment linking to the issue

## CI Checks

CI runs on every push:
1. `ruff check src/ tests/`
2. `black --check src/ tests/`
3. `mypy src/`
4. `pytest --cov=ace_bridge --cov-fail-under=70`

All must pass for a PR to merge.
