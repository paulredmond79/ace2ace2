"""Shared pytest fixtures for all test modules."""

from pathlib import Path

import pytest

from ace_bridge.config.schema import BridgeFullConfig


@pytest.fixture
def default_config() -> BridgeFullConfig:
    """A default config with safe settings for testing."""
    config = BridgeFullConfig()
    config.bridge.simulate = True
    config.bridge.read_only = True
    return config


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def ace2_fixtures_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "ace2_pro"


@pytest.fixture
def acepro_fixtures_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "ace_pro"
