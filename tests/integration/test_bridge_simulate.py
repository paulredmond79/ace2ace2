"""Integration test: bridge in simulate mode.

Tests the full bridge stack without hardware.
"""

import asyncio

import pytest

from ace_bridge.bridge.bridge import Bridge
from ace_bridge.config.schema import BridgeFullConfig


@pytest.mark.asyncio
async def test_bridge_starts_and_stops_in_simulate_mode() -> None:
    config = BridgeFullConfig()
    config.bridge.simulate = True
    bridge = Bridge(config)

    # Start bridge and cancel after short time
    task = asyncio.create_task(bridge.run())
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Bridge should not have crashed
    from ace_bridge.models.state import BridgeState

    # State is STOPPING because we cancelled it
    assert bridge.status.state in (BridgeState.IDLE, BridgeState.STOPPING)


@pytest.mark.asyncio
async def test_bridge_real_mode_raises_not_implemented() -> None:
    config = BridgeFullConfig()
    config.bridge.simulate = False
    config.bridge.read_only = True
    bridge = Bridge(config)

    with pytest.raises(NotImplementedError):
        await bridge.run()
