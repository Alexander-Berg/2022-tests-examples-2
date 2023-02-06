# pylint: disable=unused-variable
import pytest

from taxi.scripts import db as scripts_db


Fields = scripts_db.Script.Fields


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
    'url, status, local_relative_path, project, organization',
    [
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/infra/tools-py3/clownductor/test_script.py'
            ),
            200,
            'taxi/infra/tools-py3/clownductor/test_script.py',
            'clownductor',
            'taxi',
            id_='ok for arc pr-based',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/infra/tools/clownductor/test_script.py'
            ),
            200,
            'taxi/infra/tools/clownductor/test_script.py',
            'taxi',
            'taxi',
            id_='ok for arc pr-based-tools',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                '/taxi/infranaim/hiring_billing_yql_scripts/'
                'taxi_hiring_taxiparks_gambling/scouts_billing_yql/'
                'scouts_billing_yql/test.yql'
            ),
            200,
            (
                'taxi/infranaim/hiring_billing_yql_scripts/'
                'taxi_hiring_taxiparks_gambling/scouts_billing_yql/'
                'scouts_billing_yql/test.yql'
            ),
            'hiring_billing_yql_scripts',
            'hiring_billing_yql_scripts',
            id_='ok for arc pr-based-infranaim',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                '/taxi/dmp/dwh-migrations/'
                'dwh_clownductor/'
                'test.py'
            ),
            200,
            'taxi/dmp/dwh-migrations/dwh_clownductor/test.py',
            'dwh-migrations',
            'taxi-dwh',
            id_='ok for arc pr-based-dwh',
        ),
        pytest.param(
            (
                'https://a.yandex-team.ru/arc_vcs/'
                'taxi/github/taximeter/taxi-cloud-yandex/'
                'src/Yandex.Taximeter.ScriptRunner/Scripts/TestScript.cs'
            ),
            200,
            'taxi/github/taximeter/taxi-cloud-yandex/src/'
            'Yandex.Taximeter.ScriptRunner/Scripts/TestScript.cs',
            'taximeter',
            'taximeter',
            id_='ok for arc pr-based-taximeter',
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
@pytest.mark.usefixtures('create_scripts_common', 'mock_arc', 'secdist')
async def test_check_and_create(
        patch,
        scripts_client,
        find_script,
        url,
        status,
        local_relative_path,
        project,
        organization,
):
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
    data = await response.json()
    assert response.status == status, data
    script_id = data['id']
    script = await find_script(script_id)
    assert script[Fields.execute_type] == 'python'
    assert script[Fields.organization] == organization
    assert script[Fields.project] == project
    assert script[Fields.local_relative_path] == local_relative_path
