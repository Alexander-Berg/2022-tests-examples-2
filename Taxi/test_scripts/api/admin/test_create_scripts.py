# pylint: disable=protected-access,unused-variable
import datetime

import freezegun
import pytest

from taxi.scripts import db as scripts_db

from scripts.lib.vcs_utils import github_utils


@pytest.fixture(name='secdist')
def _secdist(simple_secdist):
    simple_secdist['settings_override']['ARC_TOKEN'] = 'ARC_TOKEN-888'
    return simple_secdist


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


@pytest.mark.parametrize(
    'urls, request_ids, queue_size, timestamps, need_check',
    [
        (
            [
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/delete_issues_not_nanny.py',
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/create_issues.py',
            ],
            ['123', '124'],
            2,
            ['2022-03-16 12:00:00', '2022-03-16 12:00:01'],
            False,
        ),
        (
            [
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/browse/eda_scripts/'
                'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e',
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/create_issues.py',
            ],
            ['123', '124'],
            3,
            ['2022-03-16 12:00:00', '2022-03-16 12:00:01'],
            False,
        ),
        (
            [
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/browse/eda_scripts/'
                'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e',
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/browse/eda_scripts/'
                'test.py?at=dde6f0627dc4925c910a47997f160e27b5256e0e',
            ],
            ['123', '124'],
            3,
            ['2022-03-16 12:00:00', '2022-03-16 12:00:01'],
            False,
        ),
        (
            [
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/create_issues.py?'
                'rev=dde6f0627dc4925c910a47997f160e27b5256eaa',
            ],
            ['123'],
            1,
            ['2022-03-16 12:00:00'],
            True,
        ),
    ],
)
@pytest.mark.config(
    SCRIPTS_ALLOW_MASTER_BLOB=True,
    SCRIPTS_CHECK_SERVICE_NAME_SETTINGS={
        'enabled': True,
        'specific_names': [],
    },
    SCRIPTS_FEATURES_BY_PROJECT={
        '__default__': {'use_async_archive_creation': True},
    },
)
@pytest.mark.usefixtures('mock_arc', 'secdist')
async def test_queue_archives_from_arcadia(
        urls,
        scripts_client,
        patch,
        db,
        request_ids,
        queue_size,
        timestamps,
        need_check,
):
    await db.queue_archives_from_arcadia.insert_many(
        [
            {
                'ref': 'dde6f0627dc4925c910a47997f160e27b5256eaa',
                'repo': 'tools-py3',
                'vcs': 'arc',
                'path': 'taxi_clownductor',
                'created': datetime.datetime(2022, 3, 16, 10, 0),
                'status': 'in_progress',
                'updated': datetime.datetime(2022, 3, 16, 10, 0),
                'user': 'taxi',
            },
        ],
    )

    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def check_cgroup_exists(group, log_extra=None):
        return group != 'taxi_non-existing-service'

    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def check_ngroup_exists(group, log_extra=None):
        return group != 'taxi_non-existing-service'

    for i, url in enumerate(urls):
        with freezegun.freeze_time(timestamps[i]):
            response = await scripts_client.post(
                '/scripts/',
                json={
                    'url': url,
                    'ticket': 'TAXIBACKEND-1',
                    'python_path': '/usr/lib/yandex/taxi-import',
                    'arguments': [],
                    'comment': 'some comment',
                    'request_id': request_ids[i],
                },
                headers={'X-Yandex-Login': 'd1mbas'},
            )
        result = await response.json()
        assert result['status'] == 'ok', result

    queue = await db.queue_archives_from_arcadia.find().to_list(None)
    assert len(queue) == queue_size
    if need_check:
        queue[0].pop('_id')
        assert queue[0] == {
            'created': datetime.datetime(2022, 3, 16, 10, 0),
            'ref': 'dde6f0627dc4925c910a47997f160e27b5256eaa',
            'repo': 'tools-py3',
            'path': 'taxi_clownductor',
            'status': 'in_progress',
            'updated': datetime.datetime(2022, 3, 16, 12, 0),
            'user': 'taxi',
            'vcs': 'arc',
        }


@pytest.mark.parametrize(
    'url,fails,code,err_detail',
    [
        ('', True, 406, 'Url must be specified'),
        (
            'https://github.com/',
            True,
            406,
            'domain should be one of \'a.yandex-team.ru\' or '
            '\'bb.yandex-team.ru\' or \'github.yandex-team.ru\'',
        ),
        (
            'https://github.yandex-team.ru/',
            True,
            406,
            github_utils._GOOD_EXAMPLE_MESSAGE,
        ),
        (
            (
                'https://github.yandex-team.ru/some/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            True,
            406,
            (
                f'Bad organization "some", should be one of: '
                '[\'eda\', \'taxi\', \'taxi-dwh\', \'taximeter\']'
            ),
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                'master/migrations/m4326_debugging_script.py'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/tools-py3/blob/'
                'b09a372c660c4b3d774a157604151a282b32c6d3/'
                'taxi_clownductor/duty_scripts/delete_issues_not_nanny.py'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://a.yandex-team.ru/arc_vcs/taxi/infra/tools-py3/'
                'taxi_clownductor/duty_scripts/delete_issues_not_nanny.py'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/raw/eda_scripts/'
                'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/browse/eda_scripts/'
                'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://bb.yandex-team.ru/users/d1mbas/repos/'
                'infrastructure_admin_scripts/browse/eda_scripts/'
                'test.py?at=cce6f0627dc4925c910a47997f160e27b5256e0e'
            ),
            True,
            406,
            'Repo must exist in project namespace',
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/'
                'hiring_billing_yql_scripts/'
                'blob/30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'taxi_hiring_billing/m4326_debugging_script.py'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/browse/eda_prod_mysql_galera/'
                '1019_25/2019_12_25_13_45_EDADEV-25287.sql'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/raw/'
                'eda_prod_mysql_galera/1019_25/'
                '2019_12_25_13_45_EDADEV-25287.sql?at=refs%2Fheads%2Fmaster'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/backend-py3/blob/'
                '0ce7ba7f3b38e91dc288b093db005eeb6282aa2a/'
                'corp-orders/corp_orders/storage/postgresql/schemas/v5.sql'
            ),
            True,
            406,
            'Repo "backend-py3" is not allowed for organization "taxi"',
        ),
        (
            (
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'some_bad_repo/raw/'
                'eda_prod_mysql_galera/1019_25/'
                '2019_12_25_13_45_EDADEV-25287.sql?at=refs%2Fheads%2Fmaster'
            ),
            True,
            406,
            'Repo "some_bad_repo" is not allowed for organization "eda"',
        ),
        (
            (
                'https://github.yandex-team.ru/taximeter/taxi-cloud-yandex/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/src/'
                'Yandex.Taximeter.ScriptRunner/Scripts/ReplicateQcHistory.cs'
            ),
            False,
            200,
            '',
        ),
        (
            (
                'https://github.yandex-team.ru/taximeter/taxi-cloud-some/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/src/'
                'Yandex.Taximeter.ScriptRunner/Scripts/ReplicateQcHistory.cs'
            ),
            True,
            406,
            (
                'Repo "taxi-cloud-some" is not allowed '
                'for organization "taximeter"'
            ),
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/tools-py3/'
                'blob/a27746b6d836de3b10563ce9794ac890b870553a/'
                'taxi_non-existing-service/test.py'
            ),
            True,
            406,
            'Unknown or invalid service "taxi_non-existing-service"',
        ),
        pytest.param(
            (
                'https://bb.yandex-team.ru/projects/TAXI/repos/'
                'dwh-migrations/browse/'
                'taxi_dmp-meta-etl/migrations/test_script.py'
            ),
            False,
            200,
            '',
            id='bb mirror for dwh-migrations repo',
        ),
    ],
)
@pytest.mark.config(
    SCRIPTS_ALLOW_MASTER_BLOB=True,
    SCRIPTS_CHECK_SERVICE_NAME_SETTINGS={
        'enabled': True,
        'specific_names': [],
    },
)
@pytest.mark.usefixtures('mock_arc', 'secdist')
async def test_script_url_acceptable(
        patch, scripts_client, url, fails, code, err_detail,
):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.taximeter.TaximeterApiClient.script_check')
    async def script_check_taximeter_mock(*args, **kwargs):
        pass

    @patch('scripts.lib.clients.conductor.Client.check_cgroup_exists')
    async def check_cgroup_exists(group, log_extra=None):
        return group != 'taxi_non-existing-service'

    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def check_ngroup_exists(group, log_extra=None):
        return group != 'taxi_non-existing-service'

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
    if fails:
        assert result['status'] == 'error'
        assert result['message'] == err_detail
        assert result['code'] in {'bad_script_url', 'UNKNOWN_SERVICE'}
    else:
        assert result['status'] == 'ok', result
    assert response.status == code


@pytest.mark.config(SCRIPTS_ST_QUEUES=['TAXIDWH'])
async def test_dwh_scripts_creation(scripts_client, patch):
    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 10,
            'commentWithExternalMessageCount': 10,
        }

    response = await scripts_client.post(
        '/scripts/',
        json={
            'ticket': 'TAXIDWH-2461',
            'python_path': 'FAKE_PYPATH',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '1234',
            'url': (
                'https://github.yandex-team.ru/taxi-dwh/dwh-migrations/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'test/test.py'
            ),
        },
        headers={'X-Yandex-Login': 'test'},
    )

    assert response.status == 200
    result = await response.json()
    assert result['status'] == 'ok'


@pytest.mark.config(SCRIPTS_ST_QUEUES=['NAIMBACKEND'])
async def test_hiring_billing_scripts_creation(db, patch, scripts_client):
    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        pass

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_draft')
    async def get_draft_mock(*args, **kwargs):
        return approval

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def get_drafts_mock(*args, **kwargs):
        return [approval]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def get_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 10,
            'commentWithExternalMessageCount': 10,
        }

    response = await scripts_client.post(
        '/scripts/',
        json={
            'ticket': 'NAIMBACKEND-2461',
            'python_path': 'FAKE_PYPATH',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '1234',
            'url': (
                'https://github.yandex-team.ru/taxi/'
                'hiring_billing_yql_scripts/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'taxi_hiring_scripts/test.py'
            ),
        },
        headers={'X-Yandex-Login': 'test'},
    )

    assert response.status == 200
    result = await response.json()
    assert result['status'] == 'ok'

    _id = result['id']
    approval = {
        'change_doc_id': f'scripts_{_id}',
        'created_by': 'd1mbas',
        'id': 3,
        'description': '',
        'approvals': [],
        'run_manually': False,
        'status': scripts_db.ScriptStatus.NEED_APPROVAL,
    }

    script = await db.scripts.find_one(_id)
    assert script['organization'] == 'hiring_billing_yql_scripts'

    response = await scripts_client.get(
        f'/{_id}/', headers={'X-Yandex-Login': 'test'},
    )
    script = await response.json()
    assert script['organization'] == 'hiring_billing_yql_scripts'

    response = await scripts_client.get(
        '/scripts/',
        params={'organization': 'hiring_billing_yql_scripts'},
        headers={'X-Yandex-Login': 'test'},
    )
    result = await response.json()
    assert len(result['items']) == 1
    assert result['items'][0]['organization'] == 'hiring_billing_yql_scripts'


@pytest.mark.config(SCRIPTS_ALLOW_MASTER_BLOB=True)
@pytest.mark.parametrize(
    'request_url, expected_url',
    [
        (
            (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                'master/migrations/m4326_debugging_script.py'
            ),
            (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '12345/migrations/m4326_debugging_script.py'
            ),
        ),
        (
            (
                'https://bb.yandex-team.ru/projects/EDA/repos/'
                'infrastructure_admin_scripts/browse/eda_prod_mysql_galera/'
                '1019_25/2019_12_25_13_45_EDADEV-25287.sql'
            ),
            (
                'https://bb.yandex-team.ru/projects/eda/repos/'
                'infrastructure_admin_scripts/browse/eda_prod_mysql_galera/'
                '1019_25/2019_12_25_13_45_EDADEV-25287.sql?at=12345'
            ),
        ),
    ],
)
async def test_saving_exact_commit(
        mongodb, patch, scripts_client, request_url, expected_url,
):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.github.GithubClient.get_commit_sha')
    async def get_commit_sha_github(*args, **kwargs):
        return '12345'

    @patch('taxi.clients.bitbucket.BitBucketClient.get_commit_sha')
    async def get_commit_sha_bitbucket(*args, **kwargs):
        return '12345'

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': request_url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200
    script = mongodb.scripts.find_one({'request_id': '123'})
    assert script['url'] == expected_url


@pytest.mark.config(SCRIPTS_PREPARE_ARGUMENTS=True)
@pytest.mark.parametrize(
    'input_args, saved_arguments',
    [
        ([], []),
        (['--key val'], ['--key', 'val']),
        (['-k val'], ['-k', 'val']),
        (['--key', 'val'], ['--key', 'val']),
        (['--key single long val'], ['--key', 'single long val']),
        (['--key val', 'val'], ['--key', 'val', 'val']),
        (['--key=val'], ['--key=val']),
        (
            ['--psql-options --echo-all -A'],
            ['--psql-options', '--echo-all -A'],
        ),
        (['--psql-options=--echo-all -A'], ['--psql-options=--echo-all -A']),
        (['long val'], ['long val']),
        (['long val --key'], ['long val --key']),  # possible, but bad case
        (['--key=--sub-key1 --sub-key2'], ['--key=--sub-key1 --sub-key2']),
        (['--key=single long val'], ['--key=single long val']),
        (['-k=single long val'], ['-k=single long val']),
    ],
)
async def test_prepare_arguments(
        mongodb, patch, scripts_client, input_args, saved_arguments,
):
    @patch('scripts.lib.st_utils._check_ticket_queue_and_get_info')
    async def check_ticket_mock(*args, **kwargs):
        return {
            'commentWithoutExternalMessageCount': 0,
            'commentWithExternalMessageCount': 0,
        }

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                '30665de7552ade50fd29b7d059c339e1fc1f93f0/'
                'migrations/m4326_debugging_script.py'
            ),
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': input_args,
            'comment': 'some comment',
            'request_id': '123',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200

    script = mongodb.scripts.find_one({'request_id': '123'})
    assert script['arguments'] == saved_arguments


@pytest.mark.config(SCRIPTS_FEATURES={'report_to_prod': True})
async def test_create_for_report_in_prod(
        patch, patch_aiohttp_session, response_mock, scripts_client,
):
    @patch_aiohttp_session(
        'http://scripts.taxi.yandex.net/v1/cross-env/check-ticket/',
    )
    def handler(*args, **kwargs):
        return response_mock(
            json={
                'result': 'fail',
                'status': 400,
                'msg': 'Wrong ticket queue',
                'code': 'invalid_ticket',
            },
        )

    @patch('taxi.clients.approvals.ApprovalsApiClient.create_draft')
    async def create_draft_mock(*args, **kwargs):
        return {}

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': (
                'https://github.yandex-team.ru/taxi/tools/blob/'
                'master/migrations/m4326_debugging_script.py'
            ),
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
            'report_to_prod': True,
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    data = await response.json()
    assert response.status == 400
    assert data == {
        'status': 'error',
        'message': 'Wrong ticket queue',
        'code': 'invalid_ticket',
    }
