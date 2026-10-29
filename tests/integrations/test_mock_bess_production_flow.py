import pytest
from http.server import HTTPServer
from threading import Thread
import json
import sqlite3
from dataclasses import replace

from tools.mock_bess.server import BessRequestHandler
from energy_asset_hub.config.app_settings import (build_default_app_settings,)
from energy_asset_hub.main import main



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


def test_mock_bess_production_flow(mock_server, tmp_path):
    db_path = tmp_path / "test_bess.db"
    print(f"SQLite test database: {db_path}")
    settings = replace(
        build_default_app_settings(),
        telemetry_url=(
            f"http://127.0.0.1:"
            f"{mock_server.server_port}/telemetry"
        ),
        sqlite_path=str(db_path),
    )

    main(settings)

    with sqlite3.connect(db_path) as connection:
        packet_rows = connection.execute(
            """
            SELECT packet_id, source_id, ingress_payload
            FROM telemetry_packets
            """
        ).fetchall()

        assert len(packet_rows) == 1

        packet_id, source_id, raw_payload = packet_rows[0]

        assert source_id == "BESS-01-REST"
        assert json.loads(raw_payload)["asset_id"] == "BESS-01"

        attempt_rows = connection.execute(
            """
            SELECT status
            FROM processing_attempts
            WHERE packet_id = ?
            """,
            (packet_id,),
        ).fetchall()

        assert attempt_rows == [("success",)]

        measurements = connection.execute(
            """
            SELECT parameter_name, value
            FROM measurements
            WHERE packet_id = ?
            """,
            (packet_id,),
        ).fetchall()

        assert dict(measurements) == {
            "soc_percent": 72.5,
            "power_kw": -120.0,
            "temperature_c": 28.3,
        }

        issues = connection.execute(
            """
            SELECT field_name, code, severity
            FROM bess_engineering_validation_issues
            WHERE packet_id = ?
            """,
            (packet_id,),
        ).fetchall()

        assert issues == [
            ("power_kw", "VALUE_OUT_OF_RANGE", "error"),
        ]




