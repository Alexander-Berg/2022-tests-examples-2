# pylint: disable=unused-variable
import pytest

from taxi.scripts import db as scripts_db


Fields = scripts_db.Script.Fields


@pytest.fixture(name='mock_arc')
def _mock_arc(patch_method):
    @patch_method('scripts.lib.vcs_utils.arc.Arc.mount')
    async def _mount(self):
        pass

    @patch_method('scripts.lib.vcs_utils.arc.Arc.unmount')
    async def _unmount(self):
        pass

    @patch_method('scripts.lib.vcs_utils.arc_utils.ArcClient.get_commit_sha')
    async def _get_commit_sha(
            self, user: str, repo: str, reference: str,
    ) -> str:
        return reference


def _case(
        url,
        extra_kwargs,
        status,
        expected_result=None,
        local_relative_path=None,
        id_=None,
):
    return pytest.param(
        url,
        extra_kwargs,
        status,
        expected_result,
        (
            local_relative_path
            or (
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            )
        ),
        id=id_,
    )


@pytest.mark.parametrize(
    'url, extra_kwargs, status, expected_result, local_relative_path',
    [
        _case(
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            {'execute_type': 'psql', 'cgroup': 'taxi_overlord-catalog'},
            200,
            id_='ok',
        ),
        _case(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/schemas/schemas/postgresql/overlord_catalog/'
                'overlord_catalog/0000-basic.sql?'
                'from_pr=2336196&rev=users%2Fnickaleks%2FLAVKABACKEND-7614'
            ),
            {'execute_type': 'psql', 'cgroup': 'taxi_overlord-catalog'},
            200,
            local_relative_path=(
                'taxi/schemas/schemas/postgresql/'
                'overlord_catalog/overlord_catalog/0000-basic.sql'
            ),
            id_='ok for arc pr-based',
        ),
        _case(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/schemas/schemas/postgresql/overlord_catalog/'
                'overlord_catalog/0000-basic.sql?'
                'rev=r9171278'
            ),
            {'execute_type': 'psql', 'cgroup': 'taxi_overlord-catalog'},
            200,
            local_relative_path=(
                'taxi/schemas/schemas/postgresql/'
                'overlord_catalog/overlord_catalog/0000-basic.sql'
            ),
            id_='ok for arc commit-based (merged)',
        ),
        _case(
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                'develop/schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            {'execute_type': 'psql', 'cgroup': 'taxi_overlord-catalog'},
            200,
            id_='ok',
        ),
        _case(
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            {'execute_type': 'psql'},
            406,
            {
                'code': 'INVALID_INPUT',
                'message': 'cgroup must be specified for schemas migration',
                'status': 'error',
            },
            id_='cgroup_is_required',
        ),
        _case(
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            {'cgroup': 'taxi_overlord-catalog'},
            406,
            {
                'code': 'INVALID_INPUT',
                'message': 'Only psql scripts allowed for schemas repo',
                'status': 'error',
            },
            id_='expects_psql_type_only',
        ),
        _case(
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            {'execute_type': 'psql', 'cgroup': 'taxi_overlord_catalog'},
            406,
            {
                'code': 'UNKNOWN_SERVICE',
                'message': (
                    'Unknown or invalid service "taxi_overlord_catalog"'
                ),
                'status': 'error',
            },
            id_='bad_service',
        ),
    ],
)
@pytest.mark.config(
    SCRIPTS_CHECK_SERVICE_NAME_SETTINGS={
        'enabled': True,
        'specific_names': [],
    },
    SCRIPTS_ALLOW_MASTER_BLOB=True,
)
@pytest.mark.usefixtures('create_scripts_common', 'mock_arc')
async def test_check_and_create(
        patch,
        scripts_client,
        find_script,
        url,
        extra_kwargs,
        status,
        expected_result,
        local_relative_path,
):
    @patch('scripts.lib.clients.clownductor.Client.check_ngroup_exists')
    async def check_ngroup_exists(group, log_extra=None):
        return group == 'taxi_overlord-catalog'

    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': [],
            'comment': 'some comment',
            'request_id': '123',
            **extra_kwargs,
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    data = await response.json()
    assert response.status == status, data
    if expected_result is not None:
        assert data == expected_result
    if status == 200:
        script_id = data['id']
        script = await find_script(script_id)
        assert script[Fields.execute_type] == 'psql'
        assert script[Fields.organization] == 'taxi'
        assert script[Fields.project] == 'taxi_overlord-catalog'
        assert script[Fields.local_relative_path] == local_relative_path
        assert script[Fields.arguments] == [
            '--database-name',
            'overlord_catalog',
        ]


@pytest.mark.parametrize(
    'url, extra_args, saved_args',
    [
        (
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            [],
            ['--database-name', 'overlord_catalog'],
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog@1/'
                '0000-basic.sql'
            ),
            [],
            ['--database-name', 'overlord_catalog', '--shards-ids', '1'],
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog@1/'
                '0000-basic.sql'
            ),
            ['--shards-ids', '1'],
            ['--database-name', 'overlord_catalog', '--shards-ids', '1'],
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog@1/'
                '0000-basic.sql'
            ),
            ['--shards-ids=1'],
            ['--database-name', 'overlord_catalog', '--shards-ids=1'],
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            ['--database-name', 'overlord_catalog'],
            ['--database-name', 'overlord_catalog'],
        ),
        (
            (
                'https://github.yandex-team.ru/taxi/schemas/blob/'
                '2623bd2192ab4cea8500282e3a2e0ecabb164500/'
                'schemas/postgresql/overlord_catalog/overlord_catalog/'
                '0000-basic.sql'
            ),
            ['--database-name=overlord_catalog'],
            ['--database-name=overlord_catalog'],
        ),
    ],
)
@pytest.mark.usefixtures('create_scripts_common')
async def test_arguments_extraction(
        scripts_client, find_script, url, extra_args, saved_args,
):
    response = await scripts_client.post(
        '/scripts/',
        json={
            'url': url,
            'ticket': 'TAXIBACKEND-1',
            'python_path': '/usr/lib/yandex/taxi-import',
            'arguments': extra_args,
            'comment': 'some comment',
            'request_id': '123',
            'cgroup': 'taxi_overlord-catalog',
            'execute_type': 'psql',
        },
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    data = await response.json()
    assert response.status == 200, data
    script = await find_script(data['id'])
    assert sorted(script[Fields.arguments]) == sorted(saved_args)
