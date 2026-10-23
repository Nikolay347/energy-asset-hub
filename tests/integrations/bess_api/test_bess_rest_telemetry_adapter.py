import pytest
from uuid import UUID
from datetime import datetime, timezone
from energy_asset_hub.integrations.bess_api.bess_rest_telemetry_adapter import (BessRestTelemetryAdapter,)
from energy_asset_hub.integrations.bess_api.requests_http_client import (RequestsHttpClient,)


class FakeHttpResponse:
    def __init__(self, payload: dict, error: Exception | None = None,):
        self._payload = payload
        self._error = error
        self.json_called = False

    def raise_for_status(self) -> None:
        if self._error is not None:
            raise self._error

    def json(self) -> dict:
        self.json_called = True
        return self._payload


class FakeHttpClient:
    def __init__(self, response: FakeHttpResponse):
        self._response = response
        self.requested_urls = []

    def get(self, url: str):
        self.requested_urls.append(url)
        return self._response


class FakeClock:
    def __init__(self, now_utc: datetime):
        self._now_utc = now_utc

    def now_utc(self) -> datetime:
        return self._now_utc


class FakePacketIdGenerator:
    def __init__(self, packet_id: str):
        self._packet_id = packet_id

    def next_id(self) -> str:
        return self._packet_id


def test_adapter_creates_ingress_telemetry_packet_from_rest_payload():
    payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-16T12:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    received_at_utc = datetime(
        2026, 10, 16, 9, 30, 5,
        tzinfo=timezone.utc,
    )

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
    )

    packet = adapter.create_packet(
        packet_id="PKT-REST-0001",
        payload=payload,
        received_at_utc=received_at_utc,
    )

    assert packet.packet_id == "PKT-REST-0001"
    assert packet.source_id == "BESS-01-REST"
    assert packet.received_at_utc == received_at_utc
    assert packet.to_dict() == payload

def test_adapter_preserves_invalid_rest_payload_without_validation():
    payload = {
        "asset_id": "BESS-01",
        "timestamp": "invalid-timestamp",
        "soc_percent": "invalid-soc",
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    received_at_utc = datetime(
        2026, 10, 16, 9, 30, 5,
        tzinfo=timezone.utc,
    )

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
    )

    packet = adapter.create_packet(
        packet_id="PKT-REST-0002",
        payload=payload,
        received_at_utc=received_at_utc,
    )

    assert packet.to_dict() == payload


def test_adapter_fetches_rest_payload_and_creates_ingress_packet():
    payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-16T12:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    response = FakeHttpResponse(payload)
    http_client = FakeHttpClient(response)

    received_at_utc = datetime(
        2026, 10, 16, 9, 30, 5,
        tzinfo=timezone.utc,
    )

    clock = FakeClock(received_at_utc)
    packet_id_generator = FakePacketIdGenerator("PKT-REST-0003")

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
        packet_id_generator=packet_id_generator,
    )

    packet = adapter.fetch_packet()

    assert http_client.requested_urls == [
        "http://mock-bess/telemetry"
    ]

    assert packet.packet_id == "PKT-REST-0003"
    assert packet.source_id == "BESS-01-REST"
    assert packet.received_at_utc == received_at_utc
    assert packet.to_dict() == payload


def test_adapter_does_not_create_packet_when_http_request_fails():
    response = FakeHttpResponse(
        payload={
            "asset_id": "BESS-01",
        },
        error=RuntimeError("HTTP 500"),
    )

    http_client = FakeHttpClient(response)

    clock = FakeClock(
        datetime(
            2026, 10, 16, 9, 30, 5,
            tzinfo=timezone.utc,
        )
    )

    packet_id_generator = FakePacketIdGenerator("PKT-REST-0004")

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
        packet_id_generator=packet_id_generator,
    )

    with pytest.raises(RuntimeError, match="HTTP 500"):
        adapter.fetch_packet()

    assert response.json_called is False


def test_adapter_sets_received_at_utc_from_clock():
    payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-17T20:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    response = FakeHttpResponse(payload)
    http_client = FakeHttpClient(response)

    expected_received_at_utc = datetime(
        2026, 10, 17, 17, 30, 5,
        tzinfo=timezone.utc,
    )

    clock = FakeClock(expected_received_at_utc)
    packet_id_generator = FakePacketIdGenerator("PKT-REST-0005")

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
        packet_id_generator=packet_id_generator,
    )

    packet = adapter.fetch_packet()

    assert packet.received_at_utc == expected_received_at_utc


def test_adapter_sets_generated_packet_id():
    payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-19T09:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    response = FakeHttpResponse(payload)
    http_client = FakeHttpClient(response)

    clock = FakeClock(
        datetime(
            2026, 10, 19, 6, 30, 5,
            tzinfo=timezone.utc,
        )
    )

    packet_id_generator = FakePacketIdGenerator(
        "2f7b7c41-3fa6-4f2f-9e77-6c18f4a0a7d1"
    )

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
        packet_id_generator=packet_id_generator,
    )

    packet = adapter.fetch_packet()

    assert (
        packet.packet_id
        == "2f7b7c41-3fa6-4f2f-9e77-6c18f4a0a7d1"
    )


def test_adapter_uses_uuid4_generator_by_default():
    payload = {
        "asset_id": "BESS-01",
        "timestamp": "2026-10-19T09:30:00+03:00",
        "soc_percent": 72.5,
        "power_kw": -120.0,
        "temperature_c": 28.3,
    }

    response = FakeHttpResponse(payload)
    http_client = FakeHttpClient(response)

    clock = FakeClock(
        datetime(
            2026, 10, 19, 6, 30, 5,
            tzinfo=timezone.utc,
        )
    )

    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        http_client=http_client,
        telemetry_url="http://mock-bess/telemetry",
        clock=clock,
    )

    packet = adapter.fetch_packet()

    parsed_uuid = UUID(packet.packet_id)

    assert parsed_uuid.version == 4


def test_adapter_uses_requests_http_client_by_default():
    adapter = BessRestTelemetryAdapter(
        source_id="BESS-01-REST",
        telemetry_url="http://mock-bess/telemetry",
    )

    assert isinstance(adapter._http_client, RequestsHttpClient)



