"""ACE 2 Pro emulator.

This component faces the printer and behaves like a genuine ACE 2 Pro unit.
It maintains the state that a real ACE 2 Pro would maintain and responds
to all commands the printer might send.

The emulator delegates actual filament operations to the translator, which
in turn controls the real ACE Pro. The emulator itself never communicates
directly with the ACE Pro.

Architecture:
    Printer → [RS485] → ACE2Emulator → Translator → ACEProDriver → [USB] → ACE Pro

⚠️ UNKNOWN: The complete set of commands the printer sends is not yet known.
The emulator will accept all packets but only handle known types; unknown
packets will be logged and passed to the translator as UnknownCommand.

See docs/Unknowns.md RS-5, RS-8.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional, Callable, Awaitable

from ace_bridge.models.commands import AbstractCommand, UnknownCommand
from ace_bridge.models.state import BridgeStatus, BridgeState, DeviceState
from ace_bridge.protocol.ace2.packets import ACE2Packet, ACE2PacketType

logger = logging.getLogger(__name__)

# Callback type: receives an abstract command, returns an optional response command
CommandHandler = Callable[[AbstractCommand], Awaitable[Optional[AbstractCommand]]]


class ACE2Emulator:
    """Emulates an ACE 2 Pro unit on the RS485 bus.

    The emulator:
    1. Receives raw RS485 packets from the printer
    2. Decodes them to abstract commands
    3. Dispatches to the translator
    4. Encodes the translator's response
    5. Sends the encoded response back to the printer

    ⚠️ STUB: Most methods raise NotImplementedError until the RS485 protocol
    is captured and the packet format is known.
    """

    def __init__(
        self,
        address: int,  # RS485 bus address for this emulated unit — ⚠️ Unknown value
        status: BridgeStatus,
        command_handler: Optional[CommandHandler] = None,
    ) -> None:
        self._address = address
        self._status = status
        self._command_handler = command_handler
        self._running = False
        self._packet_queue: asyncio.Queue[ACE2Packet] = asyncio.Queue()

    async def handle_packet(self, packet: ACE2Packet) -> Optional[bytes]:
        """Process a received packet and return the encoded response (if any).

        ⚠️ STUB: Cannot implement response logic until packet format and command
        set are known from capture. See docs/Unknowns.md RS-5.
        """
        logger.debug(
            "Emulator received packet: type=%s address=0x%02X payload=%s",
            packet.packet_type,
            packet.address,
            packet.payload.hex(" ").upper(),
        )

        if not packet.crc_valid:
            logger.warning(
                "CRC validation failed on received packet. "
                "Expected=0x%s Computed=0x%s raw=%s",
                f"{packet.crc_expected:04X}" if packet.crc_expected is not None else "??",
                f"{packet.crc_computed:04X}" if packet.crc_computed is not None else "??",
                packet.raw.hex(" ").upper(),
            )
            self._status.crc_errors += 1
            return None

        self._status.packets_received_upstream += 1

        # Dispatch to command handler if registered
        if self._command_handler is not None:
            abstract_cmd = self._packet_to_command(packet)
            response_cmd = await self._command_handler(abstract_cmd)
            if response_cmd is not None:
                return self._command_to_response_bytes(packet, response_cmd)
        return None

    def _packet_to_command(self, packet: ACE2Packet) -> AbstractCommand:
        """Convert an ACE 2 Pro packet to an abstract command.

        ⚠️ STUB: Requires knowledge of packet format and command set.
        """
        # TODO: Decode packet.packet_type and payload to specific AbstractCommand subclass
        # For now, return UnknownCommand with raw bytes so the translator can log it
        return UnknownCommand(raw_bytes=packet.raw)

    def _command_to_response_bytes(
        self, request: ACE2Packet, response: AbstractCommand
    ) -> bytes:
        """Encode an abstract command response into ACE 2 Pro packet bytes.

        ⚠️ STUB: Requires knowledge of packet encoding.
        """
        # TODO: Implement once packet format is known
        raise NotImplementedError(
            "Response encoding not implemented — ACE 2 Pro packet format unknown. "
            "See docs/Unknowns.md RS-2."
        )

    async def generate_heartbeat(self) -> bytes:
        """Generate a heartbeat packet to send to the printer.

        ⚠️ STUB: Heartbeat format unknown — see docs/Unknowns.md RS-8, RS-9.
        """
        raise NotImplementedError(
            "Heartbeat generation not implemented — heartbeat format unknown. "
            "Capture idle RS485 traffic to identify heartbeat packets. "
            "See docs/Unknowns.md RS-8."
        )
