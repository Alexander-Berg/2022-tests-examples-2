import pathlib
from typing import Callable
from typing import NamedTuple
from typing import Optional

import git
import pytest

import create_conductor_ticket
from taxi_buildagent import agenda
from taxi_buildagent import debian_package
from taxi_buildagent import exceptions
from taxi_buildagent.clients import conductor
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


CONTROL_FILE_CONTENT = (
    """
Source: yandex-taxi-adjust-py3

Package: yandex-taxi-adjust-py3
X-Conductor-Package: yandex-taxi-some-package

Package: yandex-taxi-adjust-stq3
XD-Conductor-Branch: testing

Package: yandex-taxi-adjust-web
XC-Conductor-Ignore: true

Package: yandex-taxi-adjust-cron
XS-Conductor-Unknown: some
""".strip()
)
UNSTRIPPED_CONTENT = (
    """
Source: yandex-taxi-backend-cpp-marketplace-api
Priority: optional
Maintainer: Sergei Kthulhu <k-tulhu@yandex-team.ru>
Standards-Version: 1.0.1
Build-Depends: debhelper (>= 8.0.0),
    libfastcgi-daemon2-dev,
    taxi-deps-py3-2 (>= 1.4),
Homepage: https://github.yandex-team.ru/taxi/backend-cpp.git


Package: yandex-taxi-adjust-cron
Section: libs
Architecture: any
Depends:
    ${shlibs:Depends},
Description:  Fastcgi2 module to provide taxi marketplace_api service

Package: yandex-taxi-some-package
Architecture: any
Depends:
    nginx
Description: Configs for taxi marketplace_api service

Package: yandex-taxi-adjust-stq3
Architecture: any
Depends:
    syslog-ng
Description: Configs for taxi marketplace_api service
""".strip()
)


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    branch: str
    path: str
    version: str
    target_branch: Optional[str] = None
    deploy_branch: Optional[str] = None
    build_type: Optional[str] = None
    fail_message: Optional[str] = None
    teamcity_set_parameters: dict = {}
    is_conductor_disabled: bool = False
    env_vars: dict = {}
    has_control: bool = True
    packages_json_arg: bool = False


@pytest.mark.parametrize('deploy_analyzer_code', [200, 400, 500])
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                path='',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-100'
                    ),
                },
                version='2.1.1',
            ),
            id='backend-cpp master',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='develop',
                path='',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-100'
                    ),
                },
                version='2.1.1',
            ),
            id='backend-cpp develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-123'
                    ),
                },
                version='3.0.0hotfix25',
            ),
            id='backend-cpp antifraud',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/surger',
                path='surger',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-124'
                    ),
                },
                version='3.3.5',
            ),
            id='backend-cpp surger',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                path='',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-123'
                    ),
                },
                version='3.0.224',
            ),
            id='backend master',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                path='',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-123'
                    ),
                },
                version='3.0.224',
            ),
            id='backend develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-1'
                    ),
                },
                version='0.1.1',
            ),
            id='backend-py3 taxi-adjust',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-corp',
                path='services/taxi-corp',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-2'
                    ),
                },
                version='0.1.2',
            ),
            id='backend-py3 taxi-corp',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-corp-data',
                path='services/taxi-corp-data',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-3'
                    ),
                },
                version='0.1.3',
            ),
            id='backend-py3 taxi-corp-data',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taximeter',
                path='services/taximeter',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-4'
                    ),
                },
                version='0.1.4',
            ),
            id='backend-py3 taximeter',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-fleet',
                path='services/taxi-fleet',
                is_conductor_disabled=True,
                teamcity_set_parameters={
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-5'
                    ),
                },
                version='3.0.224',
            ),
            id='backend-py3 taxi-fleet',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-1'
                    ),
                },
                version='1.1.1',
            ),
            id='uservices driver-authorizer',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer2',
                path='services/driver-authorizer2',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-2'
                    ),
                },
                version='2.2.2',
            ),
            id='uservices driver-authorizer2',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                deploy_branch='release-kraken',
                build_type='release',
                target_branch='prestable',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-1'
                    ),
                },
                version='1.1.1',
            ),
            id='uservices driver-authorizer release',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                build_type='release',
                target_branch='prestable',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-1'
                    ),
                },
                version='1.1.1',
            ),
            id='uservices driver-authorizer release2',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                build_type='custom-unstable',
                target_branch='unstable',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-1'
                    ),
                },
                version='1.1.1',
            ),
            id='uservices driver-authorizer custom unstable',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                deploy_branch='release-kraken',
                build_type='some',
                fail_message='wrong build type some',
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'wrong build type some',
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-1'
                    ),
                },
                version='3.0.224',
            ),
            id='uservices driver-authorizer fail',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path='services/pilorama',
                build_type='release',
                target_branch='my-deploy-branch',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-3'
                    ),
                },
                version='1.1.1',
            ),
            id='uservices pilorama release',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path='services/pilorama',
                build_type='custom-testing',
                target_branch='testing',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-3'
                    ),
                },
                version='1.1.1',
            ),
            id='uservices pilorama custom testing',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path='services/pilorama',
                build_type='custom-testings',
                fail_message='wrong build type custom-testings',
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'wrong build type custom-testings',
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-3'
                    ),
                },
                version='3.0.224',
            ),
            id='uservices pilorama custom fail',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path='services/pilorama',
                build_type='custom-testing',
                target_branch='testing',
                teamcity_set_parameters={
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-3'
                    ),
                },
                version='3.0.224',
                is_conductor_disabled=True,
                env_vars={'CONDUCTOR_DISABLE': '1'},
            ),
            id='uservices_pilorama_custom_testing_no_ticket',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                path='',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-100'
                    ),
                },
                version='2.1.1',
                has_control=False,
            ),
            id='backend-cpp package.json',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                path='',
                deploy_branch='release-kraken',
                target_branch='release-kraken',
                teamcity_set_parameters={
                    'env.CONDUCTOR_TICKET': (
                        'https://c.yandex-team.ru/tickets/123'
                    ),
                    'env.RELEASE_TICKET': (
                        'https://st.yandex-team.ru/TAXIREL-100'
                    ),
                },
                version='2.1.1',
                packages_json_arg=True,
            ),
            id='backend-cpp package.json args',
        ),
    ],
)
def test_create_conductor_ticket(
        patch_requests,
        tmpdir,
        monkeypatch,
        deploy_analyzer_code,
        teamcity_report_problems,
        teamcity_set_parameters,
        params: Params,
):
    monkeypatch.setenv('CONDUCTOR_TOKEN', 'press-the-brake')
    if params.deploy_branch is not None:
        monkeypatch.setenv('DEPLOY_BRANCH', params.deploy_branch)
    if params.build_type is not None:
        monkeypatch.setenv('TEAMCITY_BUILD_TYPE', params.build_type)
    for var_name, var_value in params.env_vars.items():
        monkeypatch.setenv(var_name, var_value)

    @patch_requests('https://c.yandex-team.ru/auth_update/ticket_add')
    def conticket(method, url, **kwargs):
        text = 'text\nURL: https://c.yandex-team.ru/tickets/123'
        return patch_requests.response(status_code=200, text=text)

    @patch_requests('http://conductor-deploy-analyzer.taxi.yandex.net/api/')
    def deploy_analyzer(method, url, **kwargs):
        return patch_requests.response(deploy_analyzer_code)

    repo = params.init_repo(tmpdir)
    monkeypatch.chdir(repo.working_tree_dir)
    repo.git.checkout(params.branch)

    expected_package = {'0': 'yandex-taxi-import'}
    expected_version = {'0': params.version}

    if not params.has_control or params.packages_json_arg:
        package_json = pathlib.Path(params.path, 'package.json')
        package_json.write_text('{"meta":{"name":"yandex-taxi-import"}}')
        package_dev_json = pathlib.Path(params.path, 'package-dev.json')
        package_dev_json.write_text(
            '{"meta":{"name":"yandex-taxi-import-dev"}}',
        )
        if params.packages_json_arg:
            expected_package = {'0': 'yandex-taxi-import-dev'}
            expected_version = {'0': params.version}
        else:
            expected_package = {
                '0': 'yandex-taxi-import',
                '1': 'yandex-taxi-import-dev',
            }
            expected_version = {'0': params.version, '1': params.version}
        debian_control = pathlib.Path(params.path, 'debian', 'control')
        debian_control.unlink()

    argv = []
    if params.packages_json_arg:
        argv = ['--packages-json', 'package-dev.json']
    create_conductor_ticket.main(argv)

    assert params.teamcity_set_parameters == {
        call['name']: call['value'] for call in teamcity_set_parameters.calls
    }

    if params.fail_message is not None:
        assert teamcity_report_problems.calls == [
            {'description': params.fail_message, 'identity': None},
        ]
        assert conticket.calls == []
        assert deploy_analyzer.calls == []
        return

    if params.is_conductor_disabled:
        assert conticket.calls == []
        assert deploy_analyzer.calls == []
        return

    ticket_comment = '* Mister Twister | commit message\n\n'
    release_ticket = params.teamcity_set_parameters['env.RELEASE_TICKET']
    relticket_message = 'Release ticket ' + release_ticket + '\n\n'
    ticket_comment = relticket_message + ticket_comment

    assert conticket.calls == [
        {
            'url': 'https://c.yandex-team.ru/auth_update/ticket_add',
            'method': 'get',
            'kwargs': {
                'allow_redirects': True,
                'headers': {'Authorization': 'OAuth press-the-brake'},
                'json': {
                    'package': expected_package,
                    'ticket': {
                        'branch': params.target_branch,
                        'comment': ticket_comment,
                    },
                    'version': expected_version,
                },
                'timeout': conductor.API_TIMEOUT,
            },
        },
    ]
    assert deploy_analyzer.calls == [
        {
            'method': 'get',
            'url': (
                'http://conductor-deploy-analyzer.taxi.yandex.net/api/'
                'add_ticket'
            ),
            'kwargs': {
                'allow_redirects': True,
                'params': {'ticket': '123'},
                'timeout': 5.0,
            },
        },
    ]


@pytest.mark.parametrize(
    'branch,file_content',
    [
        ('testing', CONTROL_FILE_CONTENT),
        ('unstable', CONTROL_FILE_CONTENT),
        ('testing', UNSTRIPPED_CONTENT),
    ],
)
def test_deb_packages_parse(tmpdir, monkeypatch, branch, file_content):
    monkeypatch.setattr(
        'tests.utils.repository.CONTROL_FILE_CONTENT', file_content,
    )

    repo = backend_cpp.init(tmpdir)
    monkeypatch.chdir(repo.working_tree_dir)
    repo.git.checkout('master')

    project = agenda.open_project()
    package = debian_package.parse_debian_dir(project.abspath)

    if branch == 'testing':
        pack = create_conductor_ticket.extract_packages_from_control(
            package, branch,
        )
        assert pack == {
            'yandex-taxi-adjust-cron',
            'yandex-taxi-some-package',
            'yandex-taxi-adjust-stq3',
        }
    else:
        with pytest.raises(exceptions.BuildAgentError):
            create_conductor_ticket.extract_packages_from_control(
                package, branch,
            )
