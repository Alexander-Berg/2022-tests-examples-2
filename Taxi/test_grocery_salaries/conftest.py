# pylint: disable=redefined-outer-name
import pytest
import yt.wrapper

import grocery_salaries.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from grocery_salaries.utils import jns_helpers

pytest_plugins = ['grocery_salaries.generated.service.pytest_plugins']


@pytest.fixture
def mock_yt(yt_client, monkeypatch, yt_apply):
    def get_client(*args, **kwargs):
        return yt_client

    monkeypatch.setattr(yt.wrapper, 'YtClient', get_client)


@pytest.fixture
def mock_jns(monkeypatch):
    class JNSMock:
        def __init__(self):
            self.sent = []

        async def send_msg_to_channel(self, *args, **kwargs) -> None:
            self.sent.append(kwargs)

    mock = JNSMock()
    monkeypatch.setattr(
        jns_helpers, '_send_msg_to_channel', mock.send_msg_to_channel,
    )
    return mock
