import pytest
from datetime import datetime, timezone
from energy_asset_hub.config.app_settings import AppSettings
from energy_asset_hub.main import main, run_bess_once
from energy_asset_hub.main import (
    main,
    run_bess_once,
    run_from_default_settings,
)



class FakeTelemetryAdapter:
    def __init__(self, packet):
        self._packet = packet

    def fetch_packet(self):
        return self._packet


class FakeClock:
    def __init__(self, current_time):
        self._current_time = current_time

    def now_utc(self):
        return self._current_time


class RecordingPacketProcessingService:
    def __init__(self):
        self.calls = []

    def process_packet(
        self,
        packet,
        processed_at_utc,
        source_timezone,
    ):
        self.calls.append(
            {
                "packet": packet,
                "processed_at_utc": processed_at_utc,
                "source_timezone": source_timezone,
            }
        )


class FakeRuntime:
    def __init__(
        self,
        telemetry_adapter,
        packet_processing_service,
    ):
        self.telemetry_adapter = telemetry_adapter
        self.packet_processing_service = packet_processing_service


def test_run_bess_once_fetches_and_processes_packet():
    packet = object()

    processing_service = RecordingPacketProcessingService()

    runtime = FakeRuntime(
        telemetry_adapter=FakeTelemetryAdapter(packet),
        packet_processing_service=processing_service,
    )

    current_time = datetime(
        2026, 10, 20, 18, 30, 0,
        tzinfo=timezone.utc,
    )

    clock = FakeClock(current_time)

    run_bess_once(
        runtime=runtime,
        clock=clock,
        source_timezone="Europe/Kyiv",
    )

    assert processing_service.calls == [
        {
            "packet": packet,
            "processed_at_utc": current_time,
            "source_timezone": "Europe/Kyiv",
        }
    ]


def test_main_builds_runtime_from_settings_and_runs_once(monkeypatch):
    settings = AppSettings(
        asset_id="BESS-01",
        source_id="BESS-01-REST",
        telemetry_url="http://bess-device/telemetry",
        source_timezone="Europe/Kyiv",
        sqlite_path="energy_asset_hub.db",
    )

    class FakeConnection:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    fake_runtime = object()

    build_runtime_calls = []
    run_calls = []

    def fake_connect(sqlite_path):
        assert sqlite_path == "energy_asset_hub.db"
        return fake_connection

    def fake_build_bess_runtime(**kwargs):
        build_runtime_calls.append(kwargs)
        return fake_runtime

    def fake_run_bess_once(
        runtime,
        clock,
        source_timezone,
    ):
        run_calls.append(
            {
                "runtime": runtime,
                "clock": clock,
                "source_timezone": source_timezone,
            }
        )

    monkeypatch.setattr(
        "energy_asset_hub.main.sqlite3.connect",
        fake_connect,
    )
    monkeypatch.setattr(
        "energy_asset_hub.main.build_bess_runtime",
        fake_build_bess_runtime,
    )
    monkeypatch.setattr(
        "energy_asset_hub.main.run_bess_once",
        fake_run_bess_once,
    )

    main(settings)

    assert len(build_runtime_calls) == 1

    build_call = build_runtime_calls[0]

    assert build_call["source_id"] == "BESS-01-REST"
    assert build_call["telemetry_url"] == "http://bess-device/telemetry"
    assert build_call["connection"] is fake_connection

    assert build_call["configured_registry"].contains("BESS-01")
    assert (
        build_call["default_limits_registry"].get("BESS-01")
        is not None
    )
    assert (
        build_call["default_soc_rule_registry"].get("BESS-01")
        is not None
    )

    assert len(run_calls) == 1
    assert run_calls[0]["runtime"] is fake_runtime
    assert run_calls[0]["source_timezone"] == "Europe/Kyiv"
    assert fake_connection.closed is True


def test_main_closes_connection_when_run_fails(monkeypatch):
    settings = AppSettings(
        asset_id="BESS-01",
        source_id="BESS-01-REST",
        telemetry_url="http://bess-device/telemetry",
        source_timezone="Europe/Kyiv",
        sqlite_path="energy_asset_hub.db",
    )

    class FakeConnection:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()
    fake_runtime = object()

    def fake_connect(sqlite_path):
        return fake_connection

    def fake_build_bess_runtime(**kwargs):
        return fake_runtime

    def failing_run_bess_once(
        runtime,
        clock,
        source_timezone,
    ):
        raise RuntimeError("processing failed")

    monkeypatch.setattr(
        "energy_asset_hub.main.sqlite3.connect",
        fake_connect,
    )
    monkeypatch.setattr(
        "energy_asset_hub.main.build_bess_runtime",
        fake_build_bess_runtime,
    )
    monkeypatch.setattr(
        "energy_asset_hub.main.run_bess_once",
        failing_run_bess_once,
    )

    with pytest.raises(
        RuntimeError,
        match="processing failed",
    ):
        main(settings)

    assert fake_connection.closed is True


def test_run_from_default_settings_passes_settings_to_main(monkeypatch):
    fake_settings = object()
    main_calls = []

    def fake_build_default_app_settings():
        return fake_settings

    def fake_main(settings):
        main_calls.append(settings)

    monkeypatch.setattr(
        "energy_asset_hub.main.build_default_app_settings",
        fake_build_default_app_settings,
    )
    monkeypatch.setattr(
        "energy_asset_hub.main.main",
        fake_main,
    )

    run_from_default_settings()

    assert main_calls == [fake_settings]


