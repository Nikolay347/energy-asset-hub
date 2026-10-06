import pytest
from energy_asset_hub.domain.configuration.configured_bess_registry import (
    ConfiguredBessRegistry,
)


def test_registry_recognizes_configured_asset():
    registry = ConfiguredBessRegistry(
        asset_ids={
            "BESS-01",
            "BESS-02",
        }
    )

    assert registry.contains("BESS-01") is True


def test_registry_does_not_recognize_unknown_asset():
    registry = ConfiguredBessRegistry(
        asset_ids={
            "BESS-01",
            "BESS-02",
        }
    )

    assert registry.contains("BESS-99") is False


def test_registry_is_not_changed_when_source_set_is_modified():
    asset_ids = {
        "BESS-01",
        "BESS-02",
    }

    registry = ConfiguredBessRegistry(
        asset_ids=asset_ids,
    )

    asset_ids.add("BESS-03")
    asset_ids.remove("BESS-01")

    assert registry.contains("BESS-01") is True
    assert registry.contains("BESS-03") is False


def test_registry_rejects_empty_asset_configuration():
    with pytest.raises(ValueError):
        ConfiguredBessRegistry(
            asset_ids=set(),
        )