import dataclasses
import datetime as dt

OFFLINE_STATUS = 'offline'
ONLINE_STATUS = 'online'


@dataclasses.dataclass
class OnlineDbEvent:
    park_id: str
    driver_id: str
    status: str
    updated_at: dt.datetime
