import pytest


@pytest.mark.config(SCRIPTS_FEATURES={'convert_gh_to_bb': True})
@pytest.mark.parametrize(
    'url, expected_url',
    [
        (
            (
                'https://github.yandex-team.ru/taxi/tools-py3/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/'
                'taxi_non-existing-service/test.py'
            ),
            (
                'https://bb.yandex-team.ru/projects/taxi/repos/'
                'tools-py3/browse/taxi_non-existing-service/test.py?'
                'at=a27746b6d836de3b10563ce9794ac890b870553a'
            ),
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/'
                'hiring_billing_yql_scripts/'
                'blob/30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'taxi_hiring_billing/m4326_debugging_script.py'
            ),
            (
                'https://bb.yandex-team.ru/projects/taxi/repos/'
                'hiring_billing_yql_scripts/browse/taxi_hiring_billing/'
                'm4326_debugging_script.py?'
                'at=30665de7552ade50fd29b7d059c339e1fc1f93f0'
            ),
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            (
                'https://bb.yandex-team.ru/projects/taxi/repos/'
                'tools/browse/migrations/m4326_debugging_script.py?'
                'at=30665de7552ade50fd29b7d059c339e1fc1f93f0'
            ),
        ),
        (
            (
                'https://github.yandex-team.ru/taxi-dwh/dwh-migrations/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py'
            ),
            (
                'https://bb.yandex-team.ru/projects/taxi/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py?'
                'at=30665de7552ade50fd29b7d059c339e1fc1f93f0'
            ),
        ),
        pytest.param(
            (
                'https://github.yandex-team.ru/taximeter/taxi-cloud-yandex/'
                'blob/93842e47d1cc197cf103e1d42ecea063f2a4711d/src/'
                'Yandex.Taximeter.ScriptRunner/Scripts/Test.cs'
            ),
            (
                'https://github.yandex-team.ru/taximeter/taxi-cloud-yandex/'
                'blob/93842e47d1cc197cf103e1d42ecea063f2a4711d/src/'
                'Yandex.Taximeter.ScriptRunner/Scripts/Test.cs'
            ),
            id='for taximeter do not convert url cause they on arc',
        ),
    ],
)
async def test_context_gh_to_bb(
        patch, scripts_client, find_script, url, expected_url,
):
    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 10,
            'commentWithExternalMessageCount': 10,
        }

    @patch('taxi.clients.taximeter.TaximeterApiClient.script_check')
    async def _script_check(*args, **kwargs):
        pass

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    result = await response.json()
    script_id = result['id']
    script = await find_script(script_id)
    assert script['url'] == expected_url, script


@pytest.fixture(name='mock_arc')
def _mock_arc(patch_method):
    @patch_method('scripts.lib.vcs_utils.arc.Arc.mount')
    async def _mount(self):
        pass

    @patch_method('scripts.lib.vcs_utils.arc.Arc.unmount')
    async def _unmount(self):
        pass

    @patch_method('scripts.lib.vcs_utils.arc.Arc._run_shell_read')
    async def _run_shell_read(self, *cmd, with_cwd=True):
        return b'{"hash": "abcdefg01234"}'


@pytest.mark.config(SCRIPTS_FEATURES={'convert_bb_to_arc': True})
@pytest.mark.parametrize(
    'url, expected_url',
    [
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'tools-py3/browse/taxi_non-existing-service/test.py?'
                'at=a27746b6d836de3b10563ce9794ac890b870553a'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_non-existing-service/test.py?'
                'rev=08e23de73793df24970336d92f4a6f3a498ba485'
            ),
            id='bb_tools-py3',
        ),
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'hiring_billing_yql_scripts/browse/'
                'taxi_hiring_taxiparks_gambling/scouts_billing_yql/'
                'full_wo_duplication.yql?'
                'at=40665de7552ade50fd29b7d059c339e1fc1f93f0'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infranaim/'
                'hiring_billing_yql_scripts/'
                'taxi_hiring_taxiparks_gambling/scouts_billing_yql/'
                'full_wo_duplication.yql?'
                'rev=18e23de73793df24970336d92f4a6f3a498ba485'
            ),
            id='bb-hiring-billing',
        ),
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'tools/browse/migrations/m4326_debugging_script.py?'
                'at=30665de7552ade50fd29b7d059c339e1fc1f93f0'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools/'
                'migrations/m4326_debugging_script.py?'
                'rev=28e23de73793df24970336d92f4a6f3a498ba485'
            ),
            id='bb-tools',
        ),
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py?'
                'at=80665de7552ade50fd29b7d059c339e1fc1f93f0'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/dmp/dwh-migrations/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py?'
                'rev=28e23de73793df24970336d92f4a6f3a498ba485'
            ),
            id='bb-dwh-migration',
        ),
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py?'
                'at=0000000000000000000000000000000000000000'
            ),
            (
                'https://bb.yandex-team.ru/projects/taxi/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py?'
                'at=0000000000000000000000000000000000000000'
            ),
            id='bb-unhashible',
        ),
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/taxi/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py'
            ),
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/dmp/dwh-migrations/'
                'taxi_dmp_taxi_etl/taxi_etl/migrations/DMPDEV_5319.py?'
                'rev=abcdefg01234'
            ),
            id='bb-without_commit',
        ),
    ],
)
async def test_context_bb_to_arc(
        patch, db, scripts_client, find_script, url, expected_url, mock_arc,
):
    await db.scripts_commit_hashes.insert_many(
        [
            {
                'bb_hash': 'a27746b6d836de3b10563ce9794ac890b870553a',
                'arc_hash': '08e23de73793df24970336d92f4a6f3a498ba485',
            },
            {
                'bb_hash': '40665de7552ade50fd29b7d059c339e1fc1f93f0',
                'arc_hash': '18e23de73793df24970336d92f4a6f3a498ba485',
            },
            {
                'bb_hash': '30665de7552ade50fd29b7d059c339e1fc1f93f0',
                'arc_hash': '28e23de73793df24970336d92f4a6f3a498ba485',
            },
            {
                'bb_hash': '80665de7552ade50fd29b7d059c339e1fc1f93f0',
                'arc_hash': '28e23de73793df24970336d92f4a6f3a498ba485',
            },
        ],
    )

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def _create_draft_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 10,
            'commentWithExternalMessageCount': 10,
        }

    @patch('taxi.clients.taximeter.TaximeterApiClient.script_check')
    async def _script_check(*args, **kwargs):
        pass

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    result = await response.json()
    script_id = result['id']
    script = await find_script(script_id)
    assert script['url'] == expected_url, script
