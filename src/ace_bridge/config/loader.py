"""YAML configuration file loader."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import yaml

from ace_bridge.config.schema import BridgeFullConfig

logger = logging.getLogger(__name__)


def load_config(path: Optional[Path] = None) -> BridgeFullConfig:
    """Load and validate configuration from a YAML file.

    If no path is given, returns default configuration with safe defaults
    (read_only=True, simulate=False, unknown VID/PID).
    """
    if path is None:
        logger.info("No config file specified — using defaults")
        return BridgeFullConfig()

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    logger.info("Loading config from %s", path)
    with path.open() as f:
        raw = yaml.safe_load(f)

    if raw is None:
        logger.warning("Config file %s is empty — using defaults", path)
        return BridgeFullConfig()

    config = BridgeFullConfig.model_validate(raw)
    _log_warnings(config)
    return config


def _log_warnings(config: BridgeFullConfig) -> None:
    """Log warnings for any obviously incomplete config values."""
    if config.ace_pro.usb_vid == 0x0000:
        logger.warning(
            "ace_pro.usb_vid is 0x0000 — ACE Pro VID is unknown. "
            "Run 'bridge inspect-usb' to find it."
        )
    if config.ace_pro.usb_pid == 0x0000:
        logger.warning("ace_pro.usb_pid is 0x0000 — ACE Pro PID is unknown.")
    if config.bridge.read_only:
        logger.warning(
            "bridge.read_only=true — bridge will NOT transmit. "
            "This is safe for capture/sniff sessions."
        )
