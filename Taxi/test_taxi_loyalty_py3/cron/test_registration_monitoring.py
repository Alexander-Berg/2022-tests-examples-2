# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import juggler

from taxi_loyalty_py3.generated.cron import run_cron


@pytest.mark.now('2019-04-14 00:00.000000')
@pytest.mark.config(
    LOYALTY_REGISTRATION_MONITORING=dict(
        enabled=True, newbie_level=dict(warning=6), period=0,
    ),
)
async def test_monitoring_ok(patch_aiohttp_session, patch, response_mock):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, json, **kwargs):
        return response_mock(status=200, json=dict())

    await run_cron.main(
        ['taxi_loyalty_py3.crontasks.registration_monitoring', '-t', '0'],
    )

    juggler_calls = juggler_request.calls
    assert len(juggler_calls) == 1

    assert juggler_calls[0]['json']['events'] == [
        dict(
            host='test',
            service='registration-monitoring',
            status='OK',
            description='New accounts count is 5',
        ),
    ]


@pytest.mark.now('2019-04-14 00:00.000000')
@pytest.mark.config(
    LOYALTY_REGISTRATION_MONITORING=dict(
        enabled=True, newbie_level=dict(warning=3, critical=6), period=0,
    ),
)
async def test_monitoring_warn(patch_aiohttp_session, patch, response_mock):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, json, **kwargs):
        return response_mock(status=200, json=dict())

    await run_cron.main(
        ['taxi_loyalty_py3.crontasks.registration_monitoring', '-t', '0'],
    )

    juggler_calls = juggler_request.calls
    assert len(juggler_calls) == 1

    assert juggler_calls[0]['json']['events'] == [
        dict(
            host='test',
            service='registration-monitoring',
            status='WARN',
            description='New accounts count is more than 3',
        ),
    ]


@pytest.mark.now('2019-04-14 00:00.000000')
@pytest.mark.config(
    LOYALTY_REGISTRATION_MONITORING=dict(
        enabled=True, newbie_level=dict(critical=3), period=0,
    ),
)
async def test_monitoring_crit(patch_aiohttp_session, patch, response_mock):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, json, **kwargs):
        return response_mock(status=200, json=dict())

    await run_cron.main(
        ['taxi_loyalty_py3.crontasks.registration_monitoring', '-t', '0'],
    )

    juggler_calls = juggler_request.calls
    assert len(juggler_calls) == 1

    assert juggler_calls[0]['json']['events'] == [
        dict(
            host='test',
            service='registration-monitoring',
            status='CRIT',
            description='New accounts count is more than 3',
        ),
    ]


@pytest.mark.now('2019-04-14 00:00.000000')
@pytest.mark.config(LOYALTY_REGISTRATION_MONITORING=dict(enabled=False))
async def test_monitoring_disabled(
        patch_aiohttp_session, patch, response_mock,
):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, json, **kwargs):
        return response_mock(status=200, json=dict())

    await run_cron.main(
        ['taxi_loyalty_py3.crontasks.registration_monitoring', '-t', '0'],
    )

    juggler_calls = juggler_request.calls
    assert len(juggler_calls) == 1

    assert juggler_calls[0]['json']['events'] == [
        dict(
            host='test',
            service='registration-monitoring',
            status='WARN',
            description='Registration monitoring disabled',
        ),
    ]


@pytest.mark.now('2019-04-14 02:30.000000')
@pytest.mark.config(
    LOYALTY_REGISTRATION_MONITORING=dict(
        enabled=True, newbie_level=dict(), period=10,
    ),
)
async def test_monitoring_statistic(patch_aiohttp_session, patch):
    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        pass

    await run_cron.main(
        ['taxi_loyalty_py3.crontasks.registration_monitoring', '-t', '0'],
    )

    juggler_calls = juggler_request.calls
    assert len(juggler_calls) == 1
