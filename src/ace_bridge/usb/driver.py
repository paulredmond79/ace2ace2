"""USB transport driver for ACE Pro.

Responsibilities:
- Find and open the ACE Pro USB device by VID/PID
- Read from bulk IN endpoint
- Write to bulk OUT endpoint
- Handle USB reconnection

NOT responsible for:
- Protocol interpretation
- Packet framing

⚠️ UNKNOWN: VID, PID, endpoint addresses — see docs/Unknowns.md USB-1 to USB-3.
⚠️ UNKNOWN: Whether the ACE Pro uses CDC-ACM (appears as serial port) or vendor-specific
  bulk endpoints. This changes whether to use pyserial or pyusb.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class USBError(Exception):
    """Transport-level USB error."""


@dataclass
class USBConfig:
    """USB device configuration.

    ⚠️ UNKNOWN: All values must be filled from `lsusb -v` output.
    """

    vid: int = 0x0000  # ⚠️ Unknown — run lsusb with ACE Pro connected
    pid: int = 0x0000  # ⚠️ Unknown
    endpoint_in: int = 0x81  # ⚠️ Unknown — typical bulk IN address
    endpoint_out: int = 0x01  # ⚠️ Unknown — typical bulk OUT address
    interface: int = 0  # ⚠️ Unknown — usually 0
    read_timeout_ms: int = 100
    write_timeout_ms: int = 1000


class USBDriver:
    """Async USB transport driver for ACE Pro.

    Opens the ACE Pro by VID/PID and provides async read/write.

    Usage:
        config = USBConfig(vid=0xXXXX, pid=0xXXXX)
        async with USBDriver(config) as driver:
            data = await driver.read(64)
            await driver.write(b"...")
    """

    def __init__(self, config: USBConfig) -> None:
        self._config = config
        self._device: object | None = None  # usb.core.Device once VID/PID known
        self._rx_count = 0
        self._tx_count = 0

    async def __aenter__(self) -> USBDriver:
        await self.open()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def open(self) -> None:
        """Find and open the ACE Pro USB device.

        ⚠️ STUB: Cannot implement until VID/PID is known (docs/Unknowns.md USB-1).
        """
        if self._config.vid == 0x0000:
            raise USBError(
                "ACE Pro VID is 0x0000 — unknown. "
                "Run 'bridge inspect-usb' with ACE Pro connected to find VID/PID. "
                "See docs/Unknowns.md USB-1."
            )

        logger.info(
            "Opening ACE Pro USB device VID=0x%04X PID=0x%04X",
            self._config.vid,
            self._config.pid,
        )

        # TODO: Implement once VID/PID is known
        # import usb.core
        # self._device = usb.core.find(idVendor=self._config.vid, idProduct=self._config.pid)
        # if self._device is None:
        #     raise USBError(f"ACE Pro device not found (VID=0x{self._config.vid:04X})")
        # self._device.set_configuration()
        raise NotImplementedError(
            "USB driver not yet implemented — VID/PID unknown. See docs/Unknowns.md USB-1."
        )

    async def close(self) -> None:
        """Release USB device."""
        if self._device is not None:
            # TODO: usb.util.release_interface(self._device, self._config.interface)
            self._device = None
            logger.info("ACE Pro USB device released")

    async def read(self, num_bytes: int) -> bytes:
        """Read from bulk IN endpoint."""
        if self._device is None:
            raise USBError("Device not open")
        # TODO: self._device.read(self._config.endpoint_in, num_bytes, self._config.read_timeout_ms)
        raise NotImplementedError("USB read not yet implemented")

    async def write(self, data: bytes) -> None:
        """Write to bulk OUT endpoint."""
        if self._device is None:
            raise USBError("Device not open")
        # TODO: self._device.write(self._config.endpoint_out, data, self._config.write_timeout_ms)
        raise NotImplementedError("USB write not yet implemented")

    async def list_devices(self) -> list[dict[str, int]]:
        """List all connected USB devices with VID/PID for inspection.

        This works without knowing the ACE Pro VID/PID in advance.
        """
        try:
            import usb.core  # type: ignore[import-untyped]

            devices = usb.core.find(find_all=True)
            return [{"vid": d.idVendor, "pid": d.idProduct} for d in devices]
        except ImportError:
            logger.warning("pyusb not installed — cannot enumerate USB devices")
            return []

    @property
    def rx_count(self) -> int:
        return self._rx_count

    @property
    def tx_count(self) -> int:
        return self._tx_count
