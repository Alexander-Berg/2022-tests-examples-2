import pytest

from clowny_alert_manager.generated.cron import run_cron


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on('enable_clownductor_cache', 'use_arc'),
]


@pytest.mark.parametrize(
    ['repo', 'expected_notifications'],
    [
        pytest.param(
            'infra-cfg-juggler_no_deps',
            'expected_notifications_no_deps.json',
            id=(
                'rtc + pg, no dependencies configured, compare next tests '
                'notifications with this test'
            ),
        ),
        pytest.param(
            'infra-cfg-juggler_simple',
            'expected_notifications_simple.json',
            id='rtc -> pg dependency',
        ),
        pytest.param(
            'infra-cfg-juggler_filter',
            'expected_notifications_simple.json',
            id='rtc -> pg dependency, filter takes no effect',
        ),
    ],
)
async def test_simple(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        duty_api_mocks,
        pack_repo,
        repo,
        expected_notifications,
):
    repo_tarball = pack_repo(repo)

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
    notifications = [
        {
            'host': check['host'],
            'service': check['service'],
            'notifications': check.get('notifications'),
        }
        for check in checks_requests
    ]

    assert notifications == load_json(expected_notifications)
