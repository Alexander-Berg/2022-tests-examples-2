# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dataclasses
from typing import Callable
from typing import Dict
from typing import Optional

import pytest

from uconfigs_plugins import *  # noqa: F403 F401


@dataclasses.dataclass
class _SettingsItem:
    answer: Dict
    path: str
    mock: Optional[Callable] = None


@pytest.fixture(autouse=True)
def config_schemas(mockserver):
    class _Settings:
        defaults = _SettingsItem(
            answer={'commit': 'hash', 'defaults': {}},
            path='/configs-admin-uconfigs-noauth/v1/configs/defaults/',
        )
        commit = _SettingsItem(
            answer={'commit': 'hash'},
            path='/configs-admin-uconfigs-noauth/v1/schemas/actual_commit/',
        )

        @property
        def defaults_times_called(self):
            return self.defaults.mock.times_called

    def mock_generator(settings_item):
        @mockserver.json_handler(settings_item.path)
        def _handler(request):
            if settings_item.answer is None:
                raise RuntimeError(f'{field} mock disabled')
            return settings_item.answer

        return _handler

    settings = _Settings()
    for field in ('defaults', 'commit'):
        settings_item = getattr(settings, field)
        settings_item.mock = mock_generator(settings_item)

    return settings
