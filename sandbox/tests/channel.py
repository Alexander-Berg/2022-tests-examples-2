import pytest

from sandbox.sandboxsdk import channel as sdk1_channel
from sandbox.sandboxsdk import sandboxapi


@pytest.fixture()
def channel(server, api_su_session):
    sandboxapi_instance = sandboxapi.Sandbox(
        url=api_su_session.url,
        auth=api_su_session.transport.auth,
    )
    return sdk1_channel.SandboxChannel(sandboxapi_instance=sandboxapi_instance)


class TestChannel:
    def test__sandbox_instance(self, channel):
        assert isinstance(channel.sandbox, sandboxapi.Sandbox)
        assert channel.sandbox.ping()
