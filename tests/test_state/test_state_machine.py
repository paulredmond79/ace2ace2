"""Tests for device state model."""

import pytest

from ace_bridge.models.state import (
    DeviceState,
    SlotState,
    FilamentState,
    DryerState,
    DryerStatus,
    BridgeStatus,
    BridgeState,
)


def test_device_state_initialises_slots() -> None:
    state = DeviceState(num_slots=4)
    assert len(state.slots) == 4
    for i in range(1, 5):
        assert i in state.slots


def test_slot_state_default_is_unknown() -> None:
    state = DeviceState()
    for slot in state.slots.values():
        assert slot.filament_state == FilamentState.UNKNOWN


def test_slot_update_changes_state() -> None:
    state = DeviceState()
    state.slot(1).update(FilamentState.LOADED)
    assert state.slot(1).filament_state == FilamentState.LOADED


def test_slot_out_of_range_raises() -> None:
    state = DeviceState(num_slots=4)
    with pytest.raises(ValueError, match="Slot 5 does not exist"):
        state.slot(5)


def test_dryer_update() -> None:
    dryer = DryerStatus()
    dryer.update(DryerState.DRYING, current_temp=45.0, target_temp=50.0, humidity=20.0)
    assert dryer.state == DryerState.DRYING
    assert dryer.current_temp_c == 45.0
    assert dryer.humidity_pct == 20.0


def test_bridge_status_uptime_increases() -> None:
    import time
    status = BridgeStatus()
    time.sleep(0.01)
    assert status.uptime_seconds > 0.0


def test_bridge_status_starts_in_starting_state() -> None:
    status = BridgeStatus()
    assert status.state == BridgeState.STARTING
