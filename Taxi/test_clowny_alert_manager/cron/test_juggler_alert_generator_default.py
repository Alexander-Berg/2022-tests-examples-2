import pytest

from taxi.clients import juggler_api

from clowny_alert_manager.generated.cron import run_cron


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on('enable_clownductor_cache', 'use_arc'),
]


async def test_default_checkfile(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        duty_api_mocks,
        pack_repo,
):
    repo_tarball = pack_repo('infra-cfg-juggler_default_checkfile')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )
    checks_requests = [
        x['kwargs']['json']
        for x in juggler_api_mocks.checks_add_or_update.calls
    ]

    def srt(data):
        return sorted(
            data, key=lambda x: (x['namespace'], x['host'], x['service']),
        )

    assert srt(checks_requests) == srt(
        load_json('expected_checks_default_checkfile.json'),
    )


@pytest.mark.parametrize(
    ['repo_path', 'expected_delete_times_called'],
    [('infra-cfg-juggler_delete_missing', 1)],
)
@pytest.mark.features_on(
    'juggler_alert_generator_cleanup_checks',
    'juggler_alert_generator_smart_cleanup',
)
async def test_corrupted_checkfile(
        mockserver,
        juggler_api_mocks,
        patch_aiohttp_session,
        response_mock,
        mock_juggler_get_checks,
        load_json,
        patch,
        duty_api_mocks,
        pack_repo,
        repo_path,
        expected_delete_times_called,
):
    mock_juggler_get_checks(
        load_json('server_check_corrupted.json'), ignore_filters=True,
    )

    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/remove_check', 'POST',
    )
    def checks_remove(method, url, **kwargs):
        assert kwargs['params'] == {
            'do': 1,
            'host_name': 'some_host',
            'service_name': 'some_service',
            'project': 'taxi.eda',
        }

        return response_mock(json={})

    repo_tarball = pack_repo(repo_path)

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert len(checks_remove.calls) == expected_delete_times_called
