import pytest


# root conftest for service userver-sample
pytest_plugins = ['userver_sample_plugins.pytest_plugins']


@pytest.fixture
async def userver_sample_send_signal(
        uservice_daemon_userver_sample, ensure_daemon_started,
):
    instance = await ensure_daemon_started(uservice_daemon_userver_sample)
    process = instance.process

    async def _wrapper(signal: int):
        process.send_signal(signal)

    return _wrapper
