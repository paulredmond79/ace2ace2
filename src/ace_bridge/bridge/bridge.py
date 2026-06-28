"""Bridge orchestrator.

Wires all layers together:
- RS485 transport (upstream, printer-facing)
- ACE 2 Pro emulator
- Command translator
- ACE Pro USB driver (downstream, device-facing)
- Capture writer
- Heartbeat task

The bridge is the single entry point for the `bridge start` CLI command.

⚠️ STUB: Cannot start real operation until:
- RS485 protocol is known (milestone 3)
- USB driver is implemented (milestone 6)
- Emulator is complete (milestone 7)

The bridge can run in simulate mode without hardware.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional
import time

from ace_bridge.config.schema import BridgeFullConfig
from ace_bridge.models.state import BridgeStatus, BridgeState

logger = logging.getLogger(__name__)


class Bridge:
    """Main bridge orchestrator.

    Usage:
        config = load_config(Path("config/config.yaml"))
        bridge = Bridge(config)
        await bridge.run()
    """

    def __init__(self, config: BridgeFullConfig) -> None:
        self._config = config
        self._status = BridgeStatus()
        self._running = False
        self._tasks: list[asyncio.Task[None]] = []

    async def run(self) -> None:
        """Start the bridge and run until cancelled or error."""
        logger.info(
            "Bridge starting (simulate=%s read_only=%s)",
            self._config.bridge.simulate,
            self._config.bridge.read_only,
        )
        self._status.state = BridgeState.STARTING

        if self._config.bridge.simulate:
            await self._run_simulate()
        else:
            await self._run_real()

    async def _run_simulate(self) -> None:
        """Run bridge in simulation mode — no hardware required."""
        logger.info("Running in SIMULATE mode — no hardware will be accessed")
        self._status.state = BridgeState.IDLE
        self._running = True
        try:
            while self._running:
                await asyncio.sleep(1.0)
                logger.debug("Bridge simulate heartbeat (uptime=%.0fs)", self._status.uptime_seconds)
        except asyncio.CancelledError:
            pass
        finally:
            self._status.state = BridgeState.STOPPING
            logger.info("Bridge simulate stopped")

    async def _run_real(self) -> None:
        """Run bridge with real hardware.

        ⚠️ STUB: Not yet implemented. Requires:
        - RS485 driver (milestone 1)
        - USB driver (milestone 6)
        - Emulator (milestone 7)
        - Translator (milestone 8)
        """
        raise NotImplementedError(
            "Real bridge operation not yet implemented. "
            "Hardware drivers must be implemented first. "
            "Run with --simulate for testing. "
            "See docs/Roadmap.md milestones 1–9."
        )

    async def stop(self) -> None:
        """Gracefully stop the bridge."""
        logger.info("Bridge stopping")
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._status.state = BridgeState.STOPPING

    @property
    def status(self) -> BridgeStatus:
        return self._status
