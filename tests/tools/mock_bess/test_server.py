from http.server import HTTPServer
from threading import Thread
import json
import pytest
from urllib.request import urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from tools.mock_bess.server import run_server
from tools.mock_bess.server import BessRequestHandler


@pytest.fixture
def mock_server():
    server = HTTPServer(
        ("127.0.0.1", 0),
        BessRequestHandler,
    )

    thread = Thread(
        target=server.serve_forever,
        daemon=True,
    )
    thread.start()

    try:
        yield server
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def test_get_telemetry_returns_http_200(mock_server):


    url = (
        f"http://127.0.0.1:"
        f"{mock_server.server_port}/telemetry"
    )

    with urlopen(url, timeout=2) as response:
        assert response.status == 200




def test_get_telemetry_returns_json(mock_server):


    url = (
        f"http://127.0.0.1:"
        f"{mock_server.server_port}/telemetry"
    )

    with urlopen(url, timeout=2) as response:
        assert response.status == 200
        assert response.headers.get("Content-Type") == "application/json"

        payload = json.loads(response.read())

    assert isinstance(payload, dict)


def test_unknown_route_returns_http_404(mock_server):
    url = (
        f"http://127.0.0.1:"
        f"{mock_server.server_port}/unknown"
    )

    with pytest.raises(HTTPError) as exc_info:
        urlopen(url, timeout=2)

    assert exc_info.value.code == 404


def test_run_server_starts_and_closes_http_server():
    with patch("tools.mock_bess.server.HTTPServer") as server_class:
        server = server_class.return_value

        run_server(host="127.0.0.1", port=8000)

    server_class.assert_called_once_with(
        ("127.0.0.1", 8000),
        BessRequestHandler,
    )
    server.serve_forever.assert_called_once_with()
    server.server_close.assert_called_once_with()




