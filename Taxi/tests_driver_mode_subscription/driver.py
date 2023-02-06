import datetime
from typing import Any
from typing import Dict
from typing import Optional

import pytz


class Profile:
    def __init__(
            self,
            dbid_uuid: str,
            delimeter_index: Optional[int] = None,
            locale: Optional[str] = None,
    ):
        self._dbid_uuid = dbid_uuid
        self._locale = locale
        if delimeter_index is None:
            self.delimeter_index = self._dbid_uuid.find('_')
            assert self.delimeter_index > 0
            assert self.profile_id().find('_') == -1
        else:
            # naive implementation for legacy tests support
            # which include driver_park_id_profile_id with multiple underscores
            self.delimeter_index = delimeter_index

    @classmethod
    def create(cls, park_id: str, profile_id: str):
        return cls(
            dbid_uuid=park_id + '_' + profile_id, delimeter_index=len(park_id),
        )

    def __eq__(self, other):
        if isinstance(other, str):
            return self._dbid_uuid == other
        if isinstance(other, Profile):
            return self._dbid_uuid == other.dbid_uuid()
        return False

    def __hash__(self):
        return self._dbid_uuid.__hash__()

    def park_id(self):
        return self._dbid_uuid[: self.delimeter_index]

    def profile_id(self):
        return self._dbid_uuid[self.delimeter_index + 1 :]

    def dbid_uuid(self):
        return self._dbid_uuid

    def session(self):
        return self.park_id() + '_session'

    def locale(self):
        return self._locale if self._locale is not None else 'ru'


_EPOCH = datetime.datetime(1970, 1, 1)


class Mode:
    def __init__(
            self,
            work_mode: str,
            started_at_iso: Optional[str] = None,
            started_at: Optional[datetime.datetime] = None,
            mode_settings: Optional[Dict[str, Any]] = None,
    ):
        self.work_mode: str = work_mode
        assert not (started_at and started_at_iso)
        self.started_at: datetime.datetime = _EPOCH
        if started_at_iso:
            self.started_at = datetime.datetime.fromisoformat(started_at_iso)
        elif started_at:
            self.started_at = started_at
        self.mode_settings = mode_settings

    def started_at_iso(self):
        return self.started_at.replace(tzinfo=pytz.utc).isoformat()

    def __eq__(self, other):
        if isinstance(other, Mode):
            return (
                self.work_mode == other.work_mode
                and self.started_at == other.started_at
            )
        return False
