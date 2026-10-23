from datetime import datetime, timezone


class SystemUtcClock:
    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)




