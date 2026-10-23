from energy_asset_hub.integrations.telemetry_adapter import (
    TelemetryAdapter,
)
from energy_asset_hub.integrations.bess_api.bess_rest_telemetry_adapter import (
    BessRestTelemetryAdapter,
)


def test_bess_rest_adapter_implements_telemetry_adapter_contract():
    adapter: TelemetryAdapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
    )

    assert hasattr(adapter, "fetch_packet")




