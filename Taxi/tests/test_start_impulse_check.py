import pytest

import start_impulse_check
from taxi_buildagent.clients import impulse
from tests.utils.examples import arcadia


START_SCAN_URL = impulse.IMPULSE_URL + '/api/v1/control/tasks'
RELEASE_TICKET_ID = 'TAXIREL-51498'
CALLBACK_URL = (
    impulse.IMPULSE_URL
    + f'/api/v1/webhook/secnotify/startrek/{RELEASE_TICKET_ID}?tvm_id=2017557'
)
ORGANIZATION_ID = 362
PROJECTS_URL = (
    impulse.IMPULSE_URL
    + f'/api/v1/storage/organizations/{ORGANIZATION_ID}/projects'
)
PROJECT_ID = 86493
SERVICE_YAML_IMPULSE_ENABLED = """
teamcity:
    impulse-checks: true
"""
SERVICE_YAML_IMPULSE_DISABLED = """
teamcity:
    impulse-checks: false
"""
ARC_INFO_CONTENT = """{
    "summary": "test",
    "date": "2022-03-04T14:07:31+03:00",
    "hash": "91ff05c64be03ce491620e8c95251d3d3df08caf",
    "remote_head": "91ff05c64be03ce491620e8c95251d3d3df08caf",
    "branch": "trunk",
    "remote": "trunk",
    "author": "olegsavinov"
}"""


def test_scan_skip(capfd, commands_mock, monkeypatch, tmpdir):
    work_dir = arcadia.init_dummy(tmpdir)
    service_dir = work_dir / 'services/eats-automation-places'
    service_yaml = service_dir / 'service.yaml'
    service_dir.mkdir(exist_ok=True, parents=True)
    service_yaml.write_text(data=SERVICE_YAML_IMPULSE_DISABLED)
    monkeypatch.chdir(work_dir)

    monkeypatch.setenv('BUILD_BRANCH', 'eats-automation-places')
    monkeypatch.setenv('STARTREK_RELEASE_QUEUE', 'TAXIREL')
    monkeypatch.setenv('RELEASE_TICKET', RELEASE_TICKET_ID)

    # pylint: disable=unused-variable
    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'info':
            return ARC_INFO_CONTENT
        return ''

    start_impulse_check.main(['--repo-type=backend-py3', '--repo-dir=.'])
    stdout, _ = capfd.readouterr()
    assert (
        'ImPulse checks for service disabled! Skipping current step.' in stdout
    )


@pytest.mark.parametrize(
    'get_projects_response,create_project_response,start_scan_response',
    [
        pytest.param(
            {
                'ok': True,
                'result': [
                    {
                        'id': 86493,
                        'name': 'eats-automation-places',
                        'slug': 'eats_automation_places',
                        'organization_id': ORGANIZATION_ID,
                        'tracker_queue': 'TAXIREL',
                        'abc_service_id': 0,
                        'tags': None,
                        'notification_settings': {},
                        'build_codeql_index': False,
                        'Deleted': False,
                        'statistics': {},
                    },
                ],
            },
            None,
            {
                'ok': True,
                'result': {'id': '5f6f4d99-41e3-44e0-91fa-95c4dd74043c'},
            },
            id='start scan without project creation',
        ),
        pytest.param(
            {'ok': True, 'result': []},
            {
                'ok': True,
                'result': {
                    'id': 86493,
                    'name': 'eats-automation-places',
                    'slug': 'eats_automation_places',
                    'organization_id': ORGANIZATION_ID,
                    'tracker_queue': 'TAXIREL',
                    'abc_service_id': 0,
                    'tags': None,
                    'notification_settings': {},
                    'build_codeql_index': False,
                    'Deleted': False,
                },
            },
            {
                'ok': True,
                'result': {'id': '5f6f4d99-41e3-44e0-91fa-95c4dd74043c'},
            },
            id='start scan with project creation',
        ),
    ],
)
def test_start_scan(
        patch_requests,
        monkeypatch,
        get_projects_response,
        create_project_response,
        start_scan_response,
        tmpdir,
        commands_mock,
):
    work_dir = arcadia.init_dummy(tmpdir)
    service_dir = work_dir / 'services/eats-automation-places'
    service_yaml = service_dir / 'service.yaml'
    service_dir.mkdir(exist_ok=True, parents=True)
    service_yaml.write_text(data=SERVICE_YAML_IMPULSE_ENABLED)
    monkeypatch.chdir(work_dir)

    # pylint: disable=unused-variable
    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'info':
            return ARC_INFO_CONTENT
        return ''

    @patch_requests(PROJECTS_URL)
    def impulse_projects_mock(method, url, **kwargs):
        if method == 'GET':
            return patch_requests.response(
                status_code=200, json=get_projects_response,
            )
        return patch_requests.response(
            status_code=200, json=create_project_response,
        )

    @patch_requests(START_SCAN_URL)
    def impulse_start_scan_mock(method, url, **kwargs):
        return patch_requests.response(
            status_code=200, json=start_scan_response,
        )

    monkeypatch.setenv('BUILD_BRANCH', 'eats-automation-places')
    monkeypatch.setenv('STARTREK_RELEASE_QUEUE', 'TAXIREL')
    monkeypatch.setenv('RELEASE_TICKET', RELEASE_TICKET_ID)

    start_impulse_check.main(['--repo-type=backend-py3', '--repo-dir=.'])

    _responses = [
        {
            'kwargs': {
                'headers': {'Authorization': 'OAuth None'},
                'json': None,
                'params': None,
                'timeout': 5.0,
                'verify': False,
            },
            'method': 'GET',
            'url': PROJECTS_URL,
        },
    ]

    if create_project_response:
        _responses.append(
            {
                'kwargs': {
                    'headers': {'Authorization': 'OAuth None'},
                    'json': {
                        'name': 'eats-automation-places',
                        'slug': 'eats_automation_places',
                        'tracker_queue': 'TAXIREL',
                    },
                    'params': None,
                    'timeout': 5.0,
                    'verify': False,
                },
                'method': 'POST',
                'url': PROJECTS_URL,
            },
        )

    assert impulse_projects_mock.calls == _responses
    assert impulse_start_scan_mock.calls == [
        {
            'kwargs': {
                'headers': {'Authorization': 'OAuth None'},
                'json': {
                    'organization_id': ORGANIZATION_ID,
                    'project_id': PROJECT_ID,
                    'parameters': {
                        'codeql_lang': 'python',
                        'codeql_qls': 'python-secaudit.qls',
                        'config_paths': ['python'],
                        'repositories': [
                            {
                                'branch': '',
                                'url': (
                                    'a.yandex-team.ru/arc/trunk/arcadia/taxi/'
                                    'backend-py3/services/'
                                    'eats-automation-places'
                                ),
                            },
                        ],
                    },
                    'analysers': ['semgrep_scan', 'yadi_scan', 'codeql_scan'],
                    'callback_url': CALLBACK_URL,
                },
                'params': None,
                'timeout': 5.0,
                'verify': False,
            },
            'method': 'POST',
            'url': START_SCAN_URL,
        },
    ]
