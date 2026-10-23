import requests


class RequestsHttpClient:
    def __init__(
        self,
        session: requests.Session | None = None,
        timeout_seconds: float = 5.0,
    ):
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    def get(self, url: str):
        return self._session.get(
            url,
            timeout=self._timeout_seconds,
        )