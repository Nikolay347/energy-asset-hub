from energy_asset_hub.integrations.bess_api.requests_http_client import (
    RequestsHttpClient,
)



class FakeResponse:
    pass


class FakeSession:
    def __init__(self, response):
        self._response = response
        self.requested_url = None
        self.requested_timeout = None

    def get(self, url: str, timeout: float):
        self.requested_url = url
        self.requested_timeout = timeout
        return self._response


def test_http_client_performs_get_with_timeout():
    response = FakeResponse()
    session = FakeSession(response)

    client = RequestsHttpClient(
        session=session,
        timeout_seconds=5.0,
    )

    result = client.get("http://bess-device/telemetry")

    assert result is response
    assert session.requested_url == "http://bess-device/telemetry"
    assert session.requested_timeout == 5.0

