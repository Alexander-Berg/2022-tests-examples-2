# pylint: disable=redefined-outer-name,unused-variable
import pytest

from taxi.clients import juggler_api

from logs_errors_filters.generated.cron import run_cron


@pytest.mark.config(
    LOGSERRORS_JUGGLER_SETTINGS={
        'namespace': 'taxi_logserrors.production',
        'remove_unknown_checks': True,
    },
)
@pytest.mark.pgsql(
    'logs_errors_filters', files=['test_juggler_synchronizer.sql'],
)
async def test_juggler_synchronizer(
        patch, patch_aiohttp_session, response_mock, cron_context,
):
    taxi_logserrors_logins = []

    @patch_aiohttp_session(juggler_api.JUGGLER_API_URL)
    def juggler_api_request(method, url, **kwargs):
        if '/api/checks/checks' in url:
            assert (
                kwargs['params']['namespace_name']
                == 'taxi_logserrors.production'
            )
            return response_mock(
                json={
                    'logserrors.taxi.yandex.net': {
                        'taxi_logerrors_cgroup_taxi_imports': {
                            'notifications': [
                                {
                                    'template_name': 'on_status_change',
                                    'template_kwargs': {
                                        'login': ['nevladov'],
                                        'method': ['telegram'],
                                        'status': [
                                            {'from': 'ok', 'to': 'warn'},
                                            {'from': 'warn', 'to': 'ok'},
                                        ],
                                    },
                                },
                            ],
                        },
                        'taxi_logserrors_cgroup_taxi_logserrors': {
                            'notifications': [
                                {
                                    'template_name': 'on_status_change',
                                    'template_kwargs': {
                                        'login': taxi_logserrors_logins,
                                        'method': ['telegram'],
                                        'status': [
                                            {'from': 'ok', 'to': 'warn'},
                                            {'from': 'warn', 'to': 'ok'},
                                        ],
                                    },
                                },
                            ],
                        },
                        'unknown': {},
                    },
                },
            )
        return response_mock(json={})

    await run_cron.main(
        ['logs_errors_filters.crontasks.juggler_synchronizer', '-t', '0'],
    )

    taxi_logserrors_logins.append('nevladov')

    # run again to be sure that there are no extra calls except /checks
    await run_cron.main(
        ['logs_errors_filters.crontasks.juggler_synchronizer', '-t', '0'],
    )

    urls = [call['url'] for call in juggler_api_request.calls]
    assert len([url for url in urls if '/checks/checks' in url]) == 2
    # 1 created and 1 updated
    assert len([url for url in urls if 'add_or_update' in url]) == 2
    # 1 known and 1 unknown and 1 unknown in second launch removed
    assert len([url for url in urls if 'remove_check' in url]) == 3
