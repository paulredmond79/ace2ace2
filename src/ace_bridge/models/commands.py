"""Abstract command model.

Device-independent commands — the stable interface between the ACE 2 Pro emulator
(printer-facing) and the ACE Pro driver (device-facing).

Rules:
- Commands must never contain device-specific encoding (no raw bytes here)
- Each command maps 1:1 to a user-visible action on the filament hub
- Add commands here when new packet types are discovered and decoded
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto


class CommandType(Enum):
    """All abstract command types."""

    # Lifecycle
    PING = auto()
    GET_CAPABILITIES = auto()

    # Filament operations
    LOAD_FILAMENT = auto()
    UNLOAD_FILAMENT = auto()
    FEED_FILAMENT = auto()
    RETRACT_FILAMENT = auto()

    # Status
    GET_STATUS = auto()
    GET_SLOT_STATUS = auto()

    # Temperature / dryer
    GET_TEMPERATURE = auto()
    GET_HUMIDITY = auto()
    SET_DRYER_TEMP = auto()
    SET_DRYER_ENABLED = auto()

    UNKNOWN = auto()


@dataclass(frozen=True, kw_only=True)
class AbstractCommand:
    """Base class for all abstract commands."""

    command_type: CommandType
    timestamp: float = field(default_factory=time.monotonic)
    request_id: int | None = None


@dataclass(frozen=True, kw_only=True)
class PingCommand(AbstractCommand):
    """Heartbeat / keepalive ping."""

    command_type: CommandType = field(default=CommandType.PING, init=False)


@dataclass(frozen=True, kw_only=True)
class GetStatusCommand(AbstractCommand):
    """Request full device status."""

    command_type: CommandType = field(default=CommandType.GET_STATUS, init=False)


@dataclass(frozen=True, kw_only=True)
class GetSlotStatusCommand(AbstractCommand):
    """Request status for a specific slot.

    ⚠️ Unknown: whether slots are 0-indexed or 1-indexed in the protocol.
    Assume 1-indexed until capture confirms.
    """

    slot: int
    command_type: CommandType = field(default=CommandType.GET_SLOT_STATUS, init=False)


@dataclass(frozen=True, kw_only=True)
class LoadFilamentCommand(AbstractCommand):
    """Load filament from a specific slot.

    slot: printer-facing slot number (1-8, where 5-8 are on the bridged ACE Pro)
    """

    slot: int
    command_type: CommandType = field(default=CommandType.LOAD_FILAMENT, init=False)


@dataclass(frozen=True, kw_only=True)
class UnloadFilamentCommand(AbstractCommand):
    """Unload filament from the currently loaded slot."""

    slot: int
    command_type: CommandType = field(default=CommandType.UNLOAD_FILAMENT, init=False)


@dataclass(frozen=True, kw_only=True)
class FeedFilamentCommand(AbstractCommand):
    """Feed a specific length of filament (mm)."""

    slot: int
    length_mm: float
    command_type: CommandType = field(default=CommandType.FEED_FILAMENT, init=False)


@dataclass(frozen=True, kw_only=True)
class RetractFilamentCommand(AbstractCommand):
    """Retract a specific length of filament (mm)."""

    slot: int
    length_mm: float
    command_type: CommandType = field(default=CommandType.RETRACT_FILAMENT, init=False)


@dataclass(frozen=True, kw_only=True)
class GetTemperatureCommand(AbstractCommand):
    """Request current temperature reading."""

    command_type: CommandType = field(default=CommandType.GET_TEMPERATURE, init=False)


@dataclass(frozen=True, kw_only=True)
class GetHumidityCommand(AbstractCommand):
    """Request current humidity reading."""

    command_type: CommandType = field(default=CommandType.GET_HUMIDITY, init=False)


@dataclass(frozen=True, kw_only=True)
class SetDryerTempCommand(AbstractCommand):
    """Set dryer target temperature.

    ⚠️ Unknown: valid temperature range and units (Celsius assumed).
    """

    temperature_c: float
    command_type: CommandType = field(default=CommandType.SET_DRYER_TEMP, init=False)


@dataclass(frozen=True, kw_only=True)
class SetDryerEnabledCommand(AbstractCommand):
    """Enable or disable the dryer."""

    enabled: bool
    command_type: CommandType = field(default=CommandType.SET_DRYER_ENABLED, init=False)


@dataclass(frozen=True, kw_only=True)
class UnknownCommand(AbstractCommand):
    """Placeholder for commands not yet identified.

    Raw bytes are preserved so they can be forwarded, logged, and researched.
    """

    raw_bytes: bytes
    command_type: CommandType = field(default=CommandType.UNKNOWN, init=False)
