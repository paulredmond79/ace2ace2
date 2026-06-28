"""Configuration schema — Pydantic models for YAML config validation."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PrinterConfig(BaseModel):
    """RS485 configuration for the upstream connection (towards printer/ACE 2 Pro)."""

    rs485_port: str = "/dev/ttyAMA0"
    baud_rate: int = 115200       # ⚠️ Unknown — placeholder
    parity: str = "N"             # ⚠️ Unknown — N, E, or O
    stop_bits: int = 1            # ⚠️ Unknown
    de_re_pin: Optional[int] = None  # GPIO BCM pin for direction control
    address: int = 0x02           # ⚠️ Unknown — RS485 address for this bridge unit

    @field_validator("parity")
    @classmethod
    def valid_parity(cls, v: str) -> str:
        if v not in ("N", "E", "O"):
            raise ValueError(f"parity must be N, E, or O — got {v!r}")
        return v


class ACEProConfig(BaseModel):
    """USB configuration for the downstream ACE Pro device."""

    usb_vid: int = 0x0000         # ⚠️ Unknown — run lsusb to find
    usb_pid: int = 0x0000         # ⚠️ Unknown
    usb_endpoint_in: int = 0x81   # ⚠️ Unknown
    usb_endpoint_out: int = 0x01  # ⚠️ Unknown
    usb_interface: int = 0        # ⚠️ Unknown
    read_timeout_ms: int = 100
    write_timeout_ms: int = 1000


class MappingConfig(BaseModel):
    """Slot mapping between printer slot space and ACE Pro slot space."""

    slot_offset: int = Field(
        default=4,
        description="Printer slot N maps to ACE Pro slot N-offset. e.g. offset=4: slot5→slot1",
        ge=0,
    )


class BridgeConfig(BaseModel):
    """Bridge operational settings."""

    simulate: bool = False
    read_only: bool = True       # Safety: default read-only
    capture_enabled: bool = True
    capture_path: str = "captures/"
    log_level: str = "INFO"
    log_file: Optional[str] = None
    heartbeat_interval_s: float = 1.0  # ⚠️ Unknown — placeholder
    command_timeout_s: float = 5.0

    @field_validator("log_level")
    @classmethod
    def valid_log_level(cls, v: str) -> str:
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid:
            raise ValueError(f"log_level must be one of {valid}")
        return v.upper()


class BridgeFullConfig(BaseModel):
    """Root configuration model."""

    printer: PrinterConfig = Field(default_factory=PrinterConfig)
    ace_pro: ACEProConfig = Field(default_factory=ACEProConfig)
    mapping: MappingConfig = Field(default_factory=MappingConfig)
    bridge: BridgeConfig = Field(default_factory=BridgeConfig)
