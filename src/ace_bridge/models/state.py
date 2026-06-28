"""Device state model.

Single source of truth for all device state observed or inferred during bridge operation.
All state is asyncio-safe (no locks needed if accessed only from the event loop).

⚠️ Unknown: The complete state space is not yet known. Fields will be added as
protocol capture reveals what state the ACE 2 Pro maintains and reports.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto


class FilamentState(Enum):
    """State of a single filament slot."""

    UNKNOWN = auto()
    EMPTY = auto()  # No filament present
    LOADED = auto()  # Filament present and threaded
    LOADING = auto()  # Load operation in progress
    UNLOADING = auto()  # Unload operation in progress
    ERROR = auto()  # Sensor/motor error on this slot


class DryerState(Enum):
    """State of the dryer."""

    UNKNOWN = auto()
    OFF = auto()
    HEATING = auto()  # Ramping up to target temp
    DRYING = auto()  # At or near target temp
    COOLING = auto()  # Cooling down
    ERROR = auto()


class BridgeState(Enum):
    """Overall bridge operational state."""

    STARTING = auto()
    IDLE = auto()
    BUSY = auto()
    ERROR = auto()
    STOPPING = auto()


@dataclass
class SlotState:
    """State of a single filament slot.

    slot_number: 1-indexed slot number in the printer's coordinate space
    """

    slot_number: int
    filament_state: FilamentState = FilamentState.UNKNOWN
    filament_type: str | None = None  # e.g. "PLA", "PETG" — ⚠️ unknown if reported
    filament_colour: str | None = None  # ⚠️ unknown if reported
    last_updated: float = field(default_factory=time.monotonic)

    def update(self, state: FilamentState) -> None:
        self.filament_state = state
        self.last_updated = time.monotonic()


@dataclass
class DryerStatus:
    """Current dryer state and readings.

    ⚠️ Unknown: temperature and humidity precision, units, and valid ranges.
    """

    state: DryerState = DryerState.UNKNOWN
    current_temp_c: float | None = None
    target_temp_c: float | None = None
    humidity_pct: float | None = None
    last_updated: float = field(default_factory=time.monotonic)

    def update(
        self,
        state: DryerState,
        current_temp: float | None = None,
        target_temp: float | None = None,
        humidity: float | None = None,
    ) -> None:
        self.state = state
        if current_temp is not None:
            self.current_temp_c = current_temp
        if target_temp is not None:
            self.target_temp_c = target_temp
        if humidity is not None:
            self.humidity_pct = humidity
        self.last_updated = time.monotonic()


@dataclass
class DeviceState:
    """Complete state for the ACE Pro device being controlled.

    This represents the real ACE Pro state, maintained by the driver.
    The emulator reports a translated version of this to the printer.
    """

    num_slots: int = 4  # ACE Pro has 4 slots
    slots: dict[int, SlotState] = field(default_factory=dict)
    dryer: DryerStatus = field(default_factory=DryerStatus)
    is_busy: bool = False
    error_code: int | None = None
    firmware_version: str | None = None  # ⚠️ Unknown if reported
    last_heartbeat: float | None = None

    def __post_init__(self) -> None:
        if not self.slots:
            # ACE Pro slots are 1-indexed
            self.slots = {i: SlotState(slot_number=i) for i in range(1, self.num_slots + 1)}

    def slot(self, n: int) -> SlotState:
        if n not in self.slots:
            raise ValueError(f"Slot {n} does not exist (valid: 1-{self.num_slots})")
        return self.slots[n]


@dataclass
class BridgeStatus:
    """Overall bridge operational status, for monitoring and CLI display."""

    state: BridgeState = BridgeState.STARTING
    upstream_device_state: DeviceState = field(default_factory=DeviceState)
    packets_received_upstream: int = 0
    packets_sent_upstream: int = 0
    packets_received_downstream: int = 0
    packets_sent_downstream: int = 0
    crc_errors: int = 0
    unknown_packets: int = 0
    uptime_start: float = field(default_factory=time.monotonic)

    @property
    def uptime_seconds(self) -> float:
        return time.monotonic() - self.uptime_start
