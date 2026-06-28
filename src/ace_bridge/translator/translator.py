"""Command translator.

Translates between printer-facing abstract commands and ACE Pro-facing abstract commands.

The key responsibility is slot remapping:
- Printer addresses slots 5-8 (or similar) on the bridge unit
- ACE Pro has slots 1-4
- The translator maps printer slot N → ACE Pro slot N - offset

The translator is the ONLY place where slot number remapping happens.
Neither the emulator nor the driver should know about each other's slot numbering.

⚠️ UNKNOWN: The actual slot numbering scheme used by the printer.
See docs/Unknowns.md MAP-1, MAP-2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from ace_bridge.models.commands import (
    AbstractCommand,
    CommandType,
    FeedFilamentCommand,
    GetSlotStatusCommand,
    LoadFilamentCommand,
    RetractFilamentCommand,
    UnknownCommand,
    UnloadFilamentCommand,
)
from ace_bridge.models.state import DeviceState

logger = logging.getLogger(__name__)


@dataclass
class SlotMapping:
    """Maps printer slot numbers to ACE Pro slot numbers.

    Example: slot_offset=4 means printer slot 5 → ACE Pro slot 1.

    ⚠️ Unknown: The correct offset — see docs/Unknowns.md MAP-1.
    """

    slot_offset: int = 4  # ⚠️ Placeholder — confirm from capture

    def printer_to_device(self, printer_slot: int) -> int:
        """Convert printer slot number to ACE Pro slot number."""
        device_slot = printer_slot - self.slot_offset
        if device_slot < 1:
            raise ValueError(
                f"Printer slot {printer_slot} maps to device slot {device_slot} "
                f"(offset={self.slot_offset}) — invalid. Check slot mapping config."
            )
        return device_slot

    def device_to_printer(self, device_slot: int) -> int:
        """Convert ACE Pro slot number to printer slot number."""
        return device_slot + self.slot_offset


class CommandTranslator:
    """Translates abstract commands between printer-space and device-space.

    Printer-space: slots numbered as the printer understands them (e.g. 5-8)
    Device-space: slots numbered as ACE Pro understands them (1-4)

    The translator also propagates state from the ACE Pro driver back to the
    emulator so the emulator can report accurate status to the printer.
    """

    def __init__(self, slot_mapping: SlotMapping, device_state: DeviceState) -> None:
        self._mapping = slot_mapping
        self._device_state = device_state

    def translate_to_device(self, command: AbstractCommand) -> AbstractCommand | None:
        """Translate a printer-facing command to a device-facing command.

        Returns None if the command requires no action on the ACE Pro
        (e.g. a status query that can be answered from cached state).
        """
        match command.command_type:
            case CommandType.LOAD_FILAMENT:
                assert isinstance(command, LoadFilamentCommand)
                device_slot = self._mapping.printer_to_device(command.slot)
                logger.info(
                    "Translating LOAD_FILAMENT: printer slot %d → device slot %d",
                    command.slot,
                    device_slot,
                )
                return LoadFilamentCommand(slot=device_slot)

            case CommandType.UNLOAD_FILAMENT:
                assert isinstance(command, UnloadFilamentCommand)
                device_slot = self._mapping.printer_to_device(command.slot)
                return UnloadFilamentCommand(slot=device_slot)

            case CommandType.FEED_FILAMENT:
                assert isinstance(command, FeedFilamentCommand)
                device_slot = self._mapping.printer_to_device(command.slot)
                return FeedFilamentCommand(slot=device_slot, length_mm=command.length_mm)

            case CommandType.RETRACT_FILAMENT:
                assert isinstance(command, RetractFilamentCommand)
                device_slot = self._mapping.printer_to_device(command.slot)
                return RetractFilamentCommand(slot=device_slot, length_mm=command.length_mm)

            case CommandType.GET_SLOT_STATUS:
                assert isinstance(command, GetSlotStatusCommand)
                device_slot = self._mapping.printer_to_device(command.slot)
                return GetSlotStatusCommand(slot=device_slot)

            case (
                CommandType.PING
                | CommandType.GET_STATUS
                | CommandType.GET_TEMPERATURE
                | CommandType.GET_HUMIDITY
            ):
                # Pass through without slot translation
                return command

            case CommandType.UNKNOWN:
                assert isinstance(command, UnknownCommand)
                logger.warning(
                    "Unknown command received: %s — logging and passing through",
                    command.raw_bytes.hex(" ").upper(),
                )
                return command

            case _:
                logger.debug("Command %s requires no device action", command.command_type)
                return None
