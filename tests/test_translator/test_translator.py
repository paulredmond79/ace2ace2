"""Tests for the command translator and slot mapping."""

import pytest

from ace_bridge.models.commands import (
    FeedFilamentCommand,
    LoadFilamentCommand,
    PingCommand,
    UnknownCommand,
    UnloadFilamentCommand,
)
from ace_bridge.models.state import DeviceState
from ace_bridge.translator.translator import CommandTranslator, SlotMapping


class TestSlotMapping:
    def test_printer_to_device_with_offset_4(self) -> None:
        mapping = SlotMapping(slot_offset=4)
        assert mapping.printer_to_device(5) == 1
        assert mapping.printer_to_device(6) == 2
        assert mapping.printer_to_device(8) == 4

    def test_device_to_printer_with_offset_4(self) -> None:
        mapping = SlotMapping(slot_offset=4)
        assert mapping.device_to_printer(1) == 5
        assert mapping.device_to_printer(4) == 8

    def test_invalid_printer_slot_raises(self) -> None:
        mapping = SlotMapping(slot_offset=4)
        with pytest.raises(ValueError, match="invalid"):
            mapping.printer_to_device(3)  # 3 - 4 = -1, invalid


class TestCommandTranslator:
    def setup_method(self) -> None:
        self.mapping = SlotMapping(slot_offset=4)
        self.state = DeviceState()
        self.translator = CommandTranslator(self.mapping, self.state)

    def test_load_filament_remaps_slot(self) -> None:
        cmd = LoadFilamentCommand(slot=5)
        result = self.translator.translate_to_device(cmd)
        assert isinstance(result, LoadFilamentCommand)
        assert result.slot == 1

    def test_unload_filament_remaps_slot(self) -> None:
        cmd = UnloadFilamentCommand(slot=6)
        result = self.translator.translate_to_device(cmd)
        assert isinstance(result, UnloadFilamentCommand)
        assert result.slot == 2

    def test_feed_filament_remaps_slot(self) -> None:
        cmd = FeedFilamentCommand(slot=5, length_mm=10.0)
        result = self.translator.translate_to_device(cmd)
        assert isinstance(result, FeedFilamentCommand)
        assert result.slot == 1
        assert result.length_mm == 10.0

    def test_ping_passes_through(self) -> None:
        cmd = PingCommand()
        result = self.translator.translate_to_device(cmd)
        assert result is cmd  # Same object, no translation needed

    def test_unknown_command_passes_through(self) -> None:
        cmd = UnknownCommand(raw_bytes=b"\xaa\xbb")
        result = self.translator.translate_to_device(cmd)
        assert isinstance(result, UnknownCommand)
        assert result.raw_bytes == b"\xaa\xbb"
