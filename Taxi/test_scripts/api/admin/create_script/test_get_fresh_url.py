import os

import pytest


@pytest.mark.skipif(
    bool(os.environ.get('IS_TEAMCITY')),
    reason=(
        'even "init --bare" requires authorisation, '
        'so test MUST past locally but may (and will) fail on build agents'
    ),
)
@pytest.mark.config(TAXI_SCRIPTS_FRESH_COMMIT_CHECK_ENABLED=True)
@pytest.mark.parametrize(
    'old_url, new_url',
    [
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/create_issues.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eaa'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/create_issues.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eab'
            ),
            id='tools-py3',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools/'
                'taxi_clownductor/duty_scripts/create_issues.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eaa'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools/'
                'taxi_clownductor/duty_scripts/create_issues.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eab'
            ),
            id='tools',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/dmp/dwh-migrations/dwh_clownductor/test.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eaa'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/dmp/dwh-migrations/dwh_clownductor/test.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eab'
            ),
            id='dwh-migrations',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infranaim/'
                'hiring_billing_yql_scripts/taxi_hiring_taxiparks_gambling/'
                'scouts_billing_yql/billing_sz.yql?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eaa'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infranaim/'
                'hiring_billing_yql_scripts/taxi_hiring_taxiparks_gambling/'
                'scouts_billing_yql/billing_sz.yql?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eab'
            ),
            id='hiring_billing_yql_scripts',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/schemas/'
                'schemas/postgresql/grocery_communications/'
                'grocery_communications/V011__create_emails_db.sql?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eaa'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/schemas/'
                'schemas/postgresql/grocery_communications/'
                'grocery_communications/V011__create_emails_db.sql?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eab'
            ),
            id='schemas',
        ),
    ],
)
async def test_get_fresh_url_on_creation(
        tmp_path, patch, arc_mock, scripts_client, old_url, new_url,
):
    arc_mock(tmp_path)

    @patch('scripts.lib.utils.os.TempDir._make_temp_dir')
    async def _make_temp_dir():
        return str(tmp_path)

    @patch('scripts.lib.utils.os._remove_dir')
    async def _remove_dir(dir_name):
        pass

    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def _check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('scripts.lib.vcs_utils.arc_utils.ArcClient.get_commit_sha')
    async def _get_commit_sha(*args, **kwargs) -> str:
        return 'dde6f0627dc4925c910a47997f160e27b5256eab'

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': old_url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
            'report_to_prod': True,
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 400, await response.body
    data = await response.json()
    assert data['details']['latest_url'] == new_url
