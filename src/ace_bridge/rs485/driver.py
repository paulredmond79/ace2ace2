"""RS485 transport driver.

Responsibilities:
- Open and configure the serial port
- Read and write raw bytes
- Control DE/RE GPIO pins for half-duplex direction switching
- Report transport-level errors

NOT responsible for:
- Packet framing
- Protocol interpretation
- Addressing

⚠️ UNKNOWN: Baud rate, parity, stop bits — see docs/Unknowns.md RS-1.
Configure via config/config.yaml; do not hardcode.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import serial
import serial.serialutil

logger = logging.getLogger(__name__)


class RS485Error(Exception):
    """Transport-level RS485 error."""


@dataclass
class RS485Config:
    """RS485 port configuration.

    ⚠️ UNKNOWN: All values except port are unknown until capture.
    These defaults are placeholders and MUST be confirmed by capture.
    """

    port: str = "/dev/ttyAMA0"
    baud_rate: int = 115200  # ⚠️ Unknown — placeholder
    parity: str = "N"  # ⚠️ Unknown — placeholder (N=None, E=Even, O=Odd)
    stop_bits: int = 1  # ⚠️ Unknown — placeholder
    byte_size: int = 8
    timeout_s: float = 0.1
    write_timeout_s: float = 1.0
    de_re_pin: int | None = None  # GPIO BCM pin for DE/RE control; None = no GPIO control
    read_only: bool = True  # Safety: default read-only


class RS485Driver:
    """Async RS485 transport driver.

    Usage:
        config = RS485Config(port="/dev/ttyAMA0", baud_rate=115200)
        async with RS485Driver(config) as driver:
            data = await driver.read(64)
            if not config.read_only:
                await driver.write(b"...")
    """

    def __init__(self, config: RS485Config) -> None:
        self._config = config
        self._serial: serial.Serial | None = None
        self._rx_count = 0
        self._tx_count = 0
        self._error_count = 0

    async def __aenter__(self) -> RS485Driver:
        await self.open()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def open(self) -> None:
        """Open the serial port."""
        cfg = self._config
        logger.info(
            "Opening RS485 port %s at %d baud (read_only=%s)",
            cfg.port,
            cfg.baud_rate,
            cfg.read_only,
        )
        try:
            self._serial = serial.Serial(
                port=cfg.port,
                baudrate=cfg.baud_rate,
                parity=cfg.parity,
                stopbits=cfg.stop_bits,
                bytesize=cfg.byte_size,
                timeout=cfg.timeout_s,
                write_timeout=cfg.write_timeout_s,
            )
        except serial.serialutil.SerialException as e:
            raise RS485Error(f"Failed to open {cfg.port}: {e}") from e
        self._set_direction_receive()
        logger.info("RS485 port opened: %s", cfg.port)

    async def close(self) -> None:
        """Close the serial port, always switching to receive first."""
        self._set_direction_receive()
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info("RS485 port closed: %s", self._config.port)

    async def read(self, num_bytes: int) -> bytes:
        """Read up to num_bytes from the RS485 bus.

        Returns whatever is available (may be less than num_bytes).
        Caller is responsible for packet assembly.
        """
        if not self._serial:
            raise RS485Error("Port not open")
        loop = asyncio.get_event_loop()
        data: bytes = await loop.run_in_executor(None, self._serial.read, num_bytes)
        if data:
            self._rx_count += len(data)
            logger.debug("RS485 RX [%d bytes]: %s", len(data), data.hex(" ").upper())
        return data

    async def read_until(self, expected: bytes, max_bytes: int = 256) -> bytes:
        """Read until expected byte sequence is found or max_bytes reached."""
        buf = bytearray()
        while len(buf) < max_bytes:
            b = await self.read(1)
            if not b:
                break
            buf.extend(b)
            if buf[-len(expected) :] == expected:
                break
        return bytes(buf)

    async def write(self, data: bytes) -> None:
        """Write bytes to the RS485 bus.

        Raises RS485Error if read_only mode is enabled.
        Controls DE pin around the write if configured.
        """
        if self._config.read_only:
            raise RS485Error("RS485 write blocked: read_only=true in config")
        if not self._serial:
            raise RS485Error("Port not open")

        logger.debug("RS485 TX [%d bytes]: %s", len(data), data.hex(" ").upper())
        loop = asyncio.get_event_loop()
        try:
            self._set_direction_transmit()
            await loop.run_in_executor(None, self._serial.write, data)
            # Wait for UART TX buffer to drain before releasing bus
            await loop.run_in_executor(None, self._serial.flush)
        finally:
            self._set_direction_receive()
        self._tx_count += len(data)

    def _set_direction_transmit(self) -> None:
        """Assert DE HIGH to enable RS485 transmit."""
        if self._config.de_re_pin is not None:
            # Import RPi.GPIO lazily — not available on non-Pi systems
            try:
                import RPi.GPIO as GPIO  # type: ignore[import-untyped]

                GPIO.output(self._config.de_re_pin, GPIO.HIGH)
            except ImportError:
                pass  # Not on a Pi; acceptable in simulation/test

    def _set_direction_receive(self) -> None:
        """Assert DE LOW to switch RS485 to receive mode."""
        if self._config.de_re_pin is not None:
            try:
                import RPi.GPIO as GPIO

                GPIO.output(self._config.de_re_pin, GPIO.LOW)
            except ImportError:
                pass

    @property
    def rx_count(self) -> int:
        return self._rx_count

    @property
    def tx_count(self) -> int:
        return self._tx_count

    @property
    def error_count(self) -> int:
        return self._error_count
