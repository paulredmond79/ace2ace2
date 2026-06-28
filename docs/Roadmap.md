# Roadmap

Each milestone leaves the project in a working state. No milestone should be marked
complete if tests fail or imports are broken.

---

## Milestone 0: Repository Foundation ✅
*Complete when: repo structure exists, CLAUDE.md present, all docs stubbed, CI linting passes*

- [x] Repository structure
- [x] `pyproject.toml` with all dependencies
- [x] `CLAUDE.md`
- [x] Documentation stubs (Architecture, Protocol, Hardware, Safety, Unknowns, Research)
- [x] `.gitignore`
- [ ] GitHub Actions CI (lint + test)
- [ ] Source package skeleton (`src/ace_bridge/`)
- [ ] Basic CLI shell (`bridge --help`)

---

## Milestone 1: Research & Protocol Capture Tooling
*Complete when: can capture and hex-dump live RS485 traffic*

- [ ] `bridge sniff-rs485`: reads RS485, pretty-prints hex dump
- [ ] `bridge sniff-usb`: lists USB devices; reads USB endpoints
- [ ] `bridge inspect-usb`: dumps USB descriptors for connected ACE Pro
- [ ] Capture file format defined (JSONL)
- [ ] Capture writer (timestamps, direction, raw hex)
- [ ] `bridge decode --input captures/file.jsonl`: hex dump viewer
- [ ] `Research.md` populated with community findings
- [ ] `Unknowns.md` RS-1 (baud rate) resolved

---

## Milestone 2: USB Investigation (ACE Pro)
*Complete when: VID/PID known, USB endpoints identified, raw USB bytes captured*

- [ ] ACE Pro VID/PID documented
- [ ] USB descriptors captured and documented
- [ ] USB endpoint IN/OUT identified
- [ ] Raw USB bytes readable with `bridge sniff-usb`
- [ ] `Protocol.md` USB section partially populated
- [ ] Unknowns USB-1, USB-2, USB-3 resolved

---

## Milestone 3: RS485 Investigation (ACE 2 Pro)
*Complete when: baud rate confirmed, packet framing understood, first packets decoded*

- [ ] Baud rate confirmed by oscilloscope or trial
- [ ] Packet frame format identified (start byte, length, CRC)
- [ ] CRC algorithm confirmed
- [ ] RS485 addressing scheme understood
- [ ] At least heartbeat and status packets decoded
- [ ] `Protocol.md` RS485 section populated
- [ ] Unknowns RS-1 through RS-6 resolved

---

## Milestone 4: Packet Decoder
*Complete when: can decode real captured packets to structured objects*

- [ ] ACE 2 Pro packet model (`protocol/ace2/packets.py`)
- [ ] ACE Pro packet model (`protocol/acepro/packets.py`)
- [ ] CRC implementation and validation
- [ ] Packet encoder (for generating valid packets)
- [ ] `bridge decode` shows decoded fields, not just hex
- [ ] Unit tests with real captured bytes
- [ ] Regression test suite for known packet types

---

## Milestone 5: Abstract Command Model & State
*Complete when: all discovered commands have abstract representations*

- [ ] `models/commands.py` — all known abstract commands
- [ ] `models/state.py` — full device state model
- [ ] State machine implementation
- [ ] Unit tests for state transitions
- [ ] Slot mapping configuration

---

## Milestone 6: ACE Pro Driver
*Complete when: can send commands to real ACE Pro and receive responses*

- [ ] USB transport layer (`usb/driver.py`)
- [ ] ACE Pro protocol encode/decode
- [ ] Command → ACE Pro packet mapping
- [ ] ACE Pro state polling
- [ ] Driver unit tests (mock USB)
- [ ] Hardware integration test (`@pytest.mark.hardware`)

---

## Milestone 7: ACE 2 Pro Emulator
*Complete when: bridge responds to printer as if it were an ACE 2 Pro*

- [ ] RS485 transport layer (`rs485/driver.py`)
- [ ] Emulator state machine (`emulator/ace2_emulator.py`)
- [ ] Correct response to all known printer commands
- [ ] Heartbeat generation
- [ ] `bridge simulate` mode (no real hardware needed)
- [ ] Emulator unit tests (mock RS485)

---

## Milestone 8: Translation Layer
*Complete when: abstract commands bridge emulator ↔ driver*

- [ ] Translator implementation
- [ ] Slot mapping (printer slot 5 → ACE Pro slot 1)
- [ ] State propagation (ACE Pro state → emulator state)
- [ ] Translator unit tests
- [ ] Replay test: take a real capture and verify translated output

---

## Milestone 9: End-to-End Bridge
*Complete when: printer communicates with ACE Pro through bridge as if it were ACE 2 Pro*

- [ ] Bridge orchestrator (`bridge/bridge.py`)
- [ ] Full asyncio task management
- [ ] `bridge start` command fully functional
- [ ] Integration test with simulated printer and ACE Pro
- [ ] Error handling and recovery
- [ ] Graceful shutdown

---

## Milestone 10: Production Hardening
*Complete when: bridge runs reliably over 24h print jobs*

- [ ] Long-running stability test
- [ ] Memory leak check
- [ ] Reconnection after USB disconnect
- [ ] Reconnection after RS485 errors
- [ ] Performance profiling (latency < threshold)
- [ ] Systemd service file for autostart on Pi
- [ ] Watchdog timer integration

---

## Milestone 11: Extended Features
*Complete when: nice-to-have features are implemented*

- [ ] Web status dashboard (minimal)
- [ ] PCAP export for Wireshark analysis
- [ ] CSV export of packet log
- [ ] Filament change statistics
- [ ] `bridge status` live view with Rich TUI
- [ ] Firmware version detection

---

## Future (Speculative)

- Automated protocol discovery (fuzzing in safe mode)
- OTA update mechanism for bridge itself
