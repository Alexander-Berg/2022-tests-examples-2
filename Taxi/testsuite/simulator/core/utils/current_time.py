"""
    Utility for storing current mocked time
"""

import datetime

from testsuite.plugins import mocked_time as mocked_time_plugin


class CurrentTime:
    _MOCKED_TIME: mocked_time_plugin.MockedTime

    @classmethod
    def set_fixtures(cls, mocked_time: mocked_time_plugin.MockedTime) -> None:
        cls._MOCKED_TIME = mocked_time

    @classmethod
    def set(cls, timestamp: datetime.datetime) -> None:
        cls._MOCKED_TIME.set(timestamp)

    @classmethod
    def get(cls) -> datetime.datetime:
        return cls._MOCKED_TIME.now()
