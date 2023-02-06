# pylint: disable=too-many-lines
import dataclasses
import json
import os
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import git
import yaml

import clownductor_report
from tests.utils import pytest_wraps
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    service_name: str
    init_repo: Optional[Callable[[str], git.Repo]]
    service_aliases: List[Dict[str, str]] = dataclasses.field(
        default_factory=list,
    )
    docker_image: Optional[str] = None
    services_dir: Optional[str] = None
    environment: Optional[str] = None
    secdist_vars: Optional[dict] = None
    changelog: Optional[str] = None
    configs: Optional[List[str]] = None
    configs_sources: Optional[List[dict]] = None
    grants_sources: Optional[dict] = None
    grants: Optional[dict] = None
    report_disabled_by_env: bool = False
    report_disabled_by_yaml: Optional[bool] = None
    secdist_report_disabled: bool = False
    tool_debug: bool = False
    has_release_ticket: bool = True
    has_conductor_ticket: bool = True
    has_docker_image: bool = True
    multiple_docker_images: Tuple[str, ...] = ()
    is_dockerfile_in_service_dir: bool = False
    teamcity_messages: Optional[Dict[str, str]] = None
    teamcity_report_problems: Dict[str, Optional[str]] = dataclasses.field(
        default_factory=dict,
    )
    deploy_link: str = ''
    service_info_link: str = ''
    enable_release_without_changelog: bool = False
    clownductor_error: Optional[Dict] = None
    deploy_branch: Optional[str] = None
    commits: Optional[List[repository.Commit]] = None
    migration_tickets: Optional[List[str]] = None
    image_repo_prefix: str = 'taxi'
    docker_image_prefix: str = ''
    deploy_type: Optional[str] = None
    sandbox_resources: Optional[List[Dict[str, Union[bool, str]]]] = None
    sandbox_resources_yaml: Optional[List[Dict[str, str]]] = None
    clownductor_service_info: Optional[dict] = None
    expected_ya_calls_args: Optional[List] = None
    logbroker_config: Optional[Dict] = None
    db_info: Optional[Dict] = None


PARAMS = [
    Params(
        pytest_id='alias_equals_service_name',
        service_name='taxi-adjust',
        service_aliases=[{'service_name': 'taxi-adjust'}],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='configs_passing',
        service_name='taxi-adjust',
        service_aliases=[{'service_name': 'taxi-adjust'}],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        configs=['HTTP_CLIENT_THREADS', 'TVM_API_URL'],
    ),
    Params(
        pytest_id='configs_groups_passing',
        service_name='taxi-adjust',
        service_aliases=[{'service_name': 'taxi-adjust'}],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        configs=['TVM_API_URL', 'HTTP_CLIENT_THREADS', 'TVM_API_URL'],
        configs_sources=[{'name': 'TVM_API_URL', 'libraries': ['tvm-lib']}],
    ),
    Params(
        pytest_id='no_aliases',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        environment='production',
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='some_aliases',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust'},
            {'service_name': 'taxi-adjust-py3'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='unstable',
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='report_disabled_by_env',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust-py3'},
            {'service_name': 'taxi-adjust'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        report_disabled_by_env=True,
    ),
    Params(
        pytest_id='report_disabled_by_yaml',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust-py3'},
            {'service_name': 'taxi-adjust'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        report_disabled_by_yaml=True,
    ),
    Params(
        pytest_id='tool_debug_enabled',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust-py3'},
            {'service_name': 'taxi-adjust'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        tool_debug=True,
    ),
    Params(
        pytest_id='has_no_release_ticket',
        service_name='pilorama',
        service_aliases=[{'service_name': 'pilorama'}],
        init_repo=uservices.init,
        services_dir='services',
        has_release_ticket=False,
    ),
    Params(
        pytest_id='has_no_conductor_ticket',
        service_name='pilorama',
        init_repo=uservices.init,
        services_dir='services',
        has_conductor_ticket=False,
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='has_no_docker_image',
        service_name='pilorama',
        service_aliases=[
            {'service_name': 'pilorama'},
            {'service_name': 'taxi-pilorama'},
        ],
        init_repo=uservices.init,
        services_dir='services',
        has_docker_image=False,
    ),
    Params(
        pytest_id='has_no_service_yaml',
        service_name='service_name',
        init_repo=backend.init,
        teamcity_report_problems={
            'description': 'Changelog not found',
            'identity': None,
        },
    ),
    Params(
        pytest_id='clownductor_return_422',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'service_name'},
            {'service_name': 'taxi-adjust'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        clownductor_error={
            'code': 422,
            'message': 'Unknown service with name "taxi-adjust"',
        },
    ),
    Params(
        pytest_id='clownductor_return_400',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'service_name'},
            {'service_name': 'taxi-adjust'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        clownductor_error={
            'code': 400,
            'message': (
                'Bad Request for url: http://clownductor.taxi.'
                'yandex.net/api/teamcity_deploy'
            ),
        },
    ),
    Params(
        pytest_id='has_no_service_yaml_no_check',
        service_name='service_name',
        init_repo=backend.init,
        changelog='Unable to load change log for service '
        '\'service_name\'. You can see this message because '
        'env.ENABLE_RELEASE_WITHOUT_CHANGELOG was set'
        ' in release build options.',
        enable_release_without_changelog=True,
    ),
    Params(
        pytest_id='dockerfile_service_dir',
        service_name='service_name',
        init_repo=backend.init,
        is_dockerfile_in_service_dir=True,
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='has_secdist_vars_no_aliases',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        environment='production',
        secdist_vars={'postgresql_settings': {'$postgresql_settings': None}},
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='has_secdist_vars_some_aliases',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust'},
            {'service_name': 'taxi-adjust-py3'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='unstable',
        secdist_vars={'postgresql_settings': {'$postgresql_settings': None}},
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='has_secdist_report_disabled_some_aliases',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust'},
            {'service_name': 'taxi-adjust-py3'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='unstable',
        secdist_vars={'postgresql_settings': {'$postgresql_settings': None}},
        secdist_report_disabled=True,
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='multiple_dockerfiles',
        service_name='driver-authorizer2',
        init_repo=uservices.init,
        services_dir='services',
        has_docker_image=False,
        multiple_docker_images=(
            'driver-authorizer2-maps',
            'driver-authorizer2-serp',
        ),
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='multiple_dockerfiles_multiple_alias',
        service_name='driver-authorizer2',
        service_aliases=[
            {'service_name': 'driver-authorizer1-maps'},
            {'service_name': 'driver-authorizer1-serp'},
        ],
        init_repo=uservices.init,
        services_dir='services',
        has_conductor_ticket=False,
        has_docker_image=False,
        multiple_docker_images=(
            'driver-authorizer2-maps',
            'driver-authorizer2-serp',
        ),
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='log_deploy_link',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        environment='production',
        changelog='* Mister Twister | commit message',
        has_conductor_ticket=False,
        deploy_link='https://deploy/go',
        teamcity_messages={
            'buildStatus': 'text=\'Deploy: https://deploy/go\'',
            'setParameter': (
                'name=\'env.NANNY_DEPLOY_LINK\' value=\'https://deploy/go\''
            ),
        },
    ),
    Params(
        pytest_id='log_service_info_link',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        environment='production',
        changelog='* Mister Twister | commit message',
        has_conductor_ticket=False,
        service_info_link='https://service/info',
        teamcity_messages={
            'buildStatus': 'text=\'Service_info: https://service/info\'',
        },
    ),
    Params(
        pytest_id='log_deploy_link_service_info_link',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        environment='production',
        changelog='* Mister Twister | commit message',
        has_conductor_ticket=False,
        deploy_link='https://deploy/go',
        service_info_link='https://service/info',
        teamcity_messages={
            'buildStatus': (
                'text=\'Deploy: https://deploy/go|n'
                'Service_info: https://service/info\''
            ),
            'setParameter': (
                'name=\'env.NANNY_DEPLOY_LINK\' value=\'https://deploy/go\''
            ),
        },
    ),
    Params(
        pytest_id='one_multiple_dockerfiles',
        service_name='driver-authorizer2',
        service_aliases=[{'service_name': 'driver-authorizer2-maps'}],
        init_repo=uservices.init,
        services_dir='services',
        has_conductor_ticket=False,
        has_docker_image=False,
        multiple_docker_images=('driver-authorizer2-maps',),
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='no_repository',
        service_name='logistic-dispatcher',
        docker_image='taxi/logistic-dispatcher/testing:666',
        init_repo=None,
        environment='testing',
    ),
    Params(
        pytest_id='both_conductor_clownductor',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        environment='production',
        changelog='* Mister Twister | commit message',
        deploy_link='https://deploy/go',
        service_info_link='https://service/info',
        teamcity_messages={
            'buildStatus': (
                'text=\'Deploy: https://deploy/go|n'
                'Service_info: https://service/info|nConductor: '
                'https://c.yandex-team.ru/tickets/1803736\''
            ),
            'setParameter': (
                'name=\'env.NANNY_DEPLOY_LINK\' value=\'https://deploy/go\''
            ),
        },
    ),
    Params(
        pytest_id='name_differs_aliases',
        service_name='driver-authorizer2',
        service_aliases=[
            {'service_name': 'yaga-shord0'},
            {'service_name': 'yaga-shord1'},
            {'service_name': 'yaga-shord2'},
        ],
        init_repo=uservices.init,
        services_dir='services',
        changelog='* Mister Twister | commit message',
    ),
    Params(
        pytest_id='has_branch_name',
        service_name='taxi-adjust',
        environment='testing',
        init_repo=backend_py3.init,
        services_dir='services',
        changelog='* Mister Twister | commit message',
        deploy_branch='tank',
    ),
    Params(
        pytest_id='has_commits_with_migrations',
        service_name='pilorama',
        init_repo=uservices.init,
        services_dir='services',
        migration_tickets=[
            'https://st.yandex-team.ru/TAXITOOLS-1',
            'https://st.yandex-team.ru/TAXITOOLS-2',
            'https://st.yandex-team.ru/TAXITOOLS-3',
        ],
        commits=[
            repository.Commit(
                'edit changelog pilorama/1.1.2\n\n'
                'Migration tickets:\n'
                'https://st.yandex-team.ru/TAXITOOLS-1\n'
                'https://st.yandex-team.ru/TAXITOOLS-2\n'
                'https://st.yandex-team.ru/TAXITOOLS-3',
                ['services/pilorama/debian/changelog'],
                '(\n\n -',  # changelog can't be empty
            ),
        ],
    ),
    Params(
        pytest_id='other_image_prefix',
        service_name='driver-authorizer',
        init_repo=uservices.init,
        services_dir='services',
        changelog='* Mister Twister | commit message',
        image_repo_prefix='eda',
    ),
    Params(
        pytest_id='rebuild_deploy_type',
        service_name='driver-authorizer',
        init_repo=uservices.init,
        services_dir='services',
        changelog='* Mister Twister | commit message',
        deploy_type='rebuild',
    ),
    Params(
        pytest_id='sandbox_resources',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        commits=[
            repository.Commit(
                'edit changelog',
                ['services/taxi-adjust/debian/changelog'],
                'taxi-adjust (0.0.3resources123) unstable; urgency='
                'low\n\n  Release ticket https://st.yandex-team.ru'
                '/TAXIREL-6\n\n  * alberist | Ololo\n\n'
                ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                '19 May 2021 17:03:54 +0300\n\n',
            ),
        ],
        changelog='* alberist | Ololo',
        sandbox_resources=[
            {
                'resource_id': '321',
                'resource_type': 'TEST_TYPE',
                'task_id': '123456789',
                'task_type': 'TYPE',
                'local_path': 'path',
                'is_dynamic': True,
            },
        ],
        sandbox_resources_yaml=[
            {
                'source-path': 'path',
                'destination-path': 'path',
                'owner': '1',
                'type': 'TEST_TYPE',
            },
        ],
        expected_ya_calls_args=[
            [
                'ya',
                'upload',
                'path',
                '--owner',
                '1',
                '--ttl',
                'inf',
                '--type',
                'TEST_TYPE',
                '--json-output',
                '--attr',
                'version=0.0.3resources123',
                '--attr',
                'environment=production',
            ],
        ],
    ),
    Params(
        pytest_id='sandbox_resource_deploy_with_changelog_tag',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        changelog='deploy-type:resource\n* alberist | Ololo',
        commits=[
            repository.Commit(
                'edit changelog',
                ['services/taxi-adjust/debian/changelog'],
                'taxi-adjust (0.0.3resources1hotfix1) '
                'unstable; urgency=low\n\n  Release ticket '
                'https://st.yandex-team.ru/TAXIREL-6\n\n'
                '  deploy-type:resource\n'
                '  * alberist | Ololo\n\n'
                ' -- buildfarm <buildfarm@yandex-team.ru>'
                '  Wed, 19 May 2021 17:03:54 +0300\n\n',
            ),
        ],
        sandbox_resources=[
            {
                'resource_id': '321',
                'resource_type': 'TEST_TYPE',
                'task_id': '123456789',
                'task_type': 'TYPE',
                'local_path': 'path',
                'is_dynamic': True,
            },
        ],
        sandbox_resources_yaml=[
            {
                'source-path': 'path',
                'destination-path': 'path',
                'owner': '1',
                'type': 'TEST_TYPE',
            },
        ],
        expected_ya_calls_args=[
            [
                'ya',
                'upload',
                'path',
                '--owner',
                '1',
                '--ttl',
                'inf',
                '--type',
                'TEST_TYPE',
                '--json-output',
                '--attr',
                'version=0.0.3resources1hotfix1',
                '--attr',
                'environment=production',
            ],
        ],
    ),
    Params(
        pytest_id='service_deploy_despite_resources_in_version',
        service_name='taxi-adjust',
        init_repo=backend_py3.init,
        services_dir='services',
        changelog='* alberist | Ololo',
        commits=[
            repository.Commit(
                'edit changelog',
                ['services/taxi-adjust/debian/changelog'],
                'taxi-adjust (0.0.3hotfix1resources1hotfix1testing123) '
                'unstable; urgency=low\n\n  Release ticket '
                'https://st.yandex-team.ru/TAXIREL-6\n\n  * alberist | '
                'Ololo\n\n -- buildfarm <buildfarm@yandex-team.ru>'
                '  Wed, 19 May 2021 17:03:54 +0300\n\n',
            ),
        ],
    ),
    Params(
        pytest_id='support_project_name',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust', 'project_name': 'adjust'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        clownductor_service_info={'clownductor_project': 'adjust'},
    ),
    Params(
        pytest_id='support_project_name_aliases',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust', 'project_name': 'adjust'},
            {'service_name': 'taxi-adjust1'},
            {'service_name': 'taxi-adjust2', 'project_name': 'adjust2'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        clownductor_service_info={
            'service': {
                'name': 'taxi-adjust',
                'clownductor_project': 'adjust',
            },
            'aliases': [
                {'name': 'taxi-adjust2'},
                {'name': 'taxi-adjust2', 'clownductor_project': 'adjust2'},
            ],
        },
    ),
    Params(
        pytest_id='support_project_name_aliases',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust', 'project_name': 'adjust'},
            {'service_name': 'taxi-adjust1'},
            {'service_name': 'taxi-adjust2', 'project_name': 'adjust2'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        docker_image_prefix='taxi/adjust',
        clownductor_service_info={
            'service': {
                'name': 'taxi-adjust',
                'clownductor_project': 'adjust',
                'clownductor_namespace': 'taxi',
            },
            'aliases': [
                {'name': 'taxi-adjust2'},
                {'name': 'taxi-adjust2', 'clownductor_project': 'adjust2'},
            ],
        },
    ),
    Params(
        pytest_id='support_grants_ability',
        service_name='taxi-adjust',
        service_aliases=[{'service_name': 'taxi-adjust'}],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        grants_sources={
            'tvm': ['cargo-c2c', 'cargo-claims'],
            'hostnames': {
                'production': ['cargo-c2c.taxi.yandex.net'],
                'testing': ['cargo-c2c.taxi.tst.yandex.net'],
                'unstable': ['cargo-claims.taxi.dev.yandex.net'],
            },
        },
        grants={
            'tvm': ['cargo-c2c', 'cargo-claims'],
            'hostnames': ['cargo-c2c.taxi.tst.yandex.net'],
        },
    ),
    Params(
        pytest_id='simple_logbroker_config',
        service_name='taxi-adjust',
        service_aliases=[{'service_name': 'taxi-adjust'}],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        logbroker_config={
            'is_default_docker_layout': True,
            'configurations': [
                {
                    'configuration': {
                        'topic_writers': [
                            {
                                'logbroker_installation': (
                                    'logbroker.yandex.net'
                                ),
                                'topic_path': 'taxi/topic1',
                                'service_environment': 'production',
                            },
                        ],
                    },
                },
            ],
        },
    ),
    Params(
        pytest_id='multiple_dockerfiles_logbroker_config',
        service_name='driver-authorizer2',
        init_repo=uservices.init,
        services_dir='services',
        has_docker_image=False,
        multiple_docker_images=(
            'driver-authorizer2-maps',
            'driver-authorizer2-pp',
            'driver-authorizer2-serp',
        ),
        changelog='* Mister Twister | commit message',
        logbroker_config={
            'is_default_docker_layout': False,
            'configurations': [
                {
                    'clownductor_service': 'driver-authorizer2-maps',
                    'configuration': {
                        'topic_writers': [
                            {
                                'logbroker_installation': (
                                    'logbroker.yandex.net'
                                ),
                                'topic_path': 'taxi/topic1',
                                'service_environment': 'production',
                            },
                        ],
                    },
                },
                {
                    'clownductor_service': 'driver-authorizer2-serp',
                    'configuration': {
                        'topic_writers': [
                            {
                                'logbroker_installation': (
                                    'logbroker.yandex.net'
                                ),
                                'topic_path': 'taxi/topic2',
                                'service_environment': 'production',
                            },
                        ],
                    },
                },
            ],
        },
    ),
    Params(
        pytest_id='simple_logbroker_config_multiple_aliases',
        service_name='taxi-adjust',
        service_aliases=[
            {'service_name': 'taxi-adjust-shard0'},
            {'service_name': 'taxi-adjust-shard1'},
        ],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        logbroker_config={
            'is_default_docker_layout': True,
            'configurations': [
                {
                    'configuration': {
                        'topic_writers': [
                            {
                                'logbroker_installation': (
                                    'logbroker.yandex.net'
                                ),
                                'topic_path': 'taxi/topic1',
                                'service_environment': 'production',
                            },
                        ],
                    },
                },
            ],
        },
    ),
    Params(
        pytest_id='simple_db_info_config',
        service_name='taxi-adjust',
        service_aliases=[{'service_name': 'taxi-adjust'}],
        init_repo=backend_py3.init,
        services_dir='services',
        environment='testing',
        changelog='* Mister Twister | commit message',
        db_info={
            'pg_databases': [
                {
                    'db_name': 'arcadia_test_old',
                    'connections_max_pool_size': 4,
                },
                {'db_name': 'arcadia_test', 'connections_max_pool_size': 2},
            ],
        },
    ),
]


@pytest_wraps.parametrize(PARAMS)
def test_clownductor_report(
        commands_mock,
        monkeypatch,
        tmpdir,
        patch_requests,
        sandbox,
        teamcity_report_problems,
        teamcity_messages,
        params: Params,
) -> None:
    repo = None
    if params.init_repo:
        repo = make_repo(params, tmpdir)

    monkeypatch.setenv('BUILD_NUMBER', '666')
    if params.report_disabled_by_env:
        monkeypatch.setenv('CLOWNDUCTOR_REPORT_DISABLED', '1')
    secdist_vars = params.secdist_vars
    if params.secdist_report_disabled:
        monkeypatch.setenv('SECDIST_REPORT_DISABLED', '1')
        secdist_vars = None
    if params.tool_debug:
        monkeypatch.setattr('clownductor_report.DEBUG', True)
    if not params.report_disabled_by_env and not params.tool_debug:
        monkeypatch.setenv('CLOWNDUCTOR_TOKEN', 'secret')
    if params.has_release_ticket:
        monkeypatch.setenv(
            'RELEASE_TICKET', 'https://st.yandex-team.ru/TAXIREL-5358',
        )
    if params.has_conductor_ticket:
        monkeypatch.setenv(
            'CONDUCTOR_TICKET', 'https://c.yandex-team.ru/tickets/1803736',
        )
    if params.enable_release_without_changelog:
        monkeypatch.setenv('ENABLE_RELEASE_WITHOUT_CHANGELOG', '1')
    if params.image_repo_prefix != 'taxi':
        monkeypatch.setenv('IMAGE_REPO_PREFIX', params.image_repo_prefix)
    if params.sandbox_resources:
        sandbox.patch_all()

    @patch_requests(clownductor_report.CLOWNDUCTOR_URL)
    def _report_to_clownductor(*args, **kwargs):
        if params.clownductor_error:
            return patch_requests.response(
                status_code=params.clownductor_error['code'],
                json={'error': params.clownductor_error['message']},
            )

        data = {'job_id': 666}
        if params.deploy_link:
            data['deploy_link'] = params.deploy_link
        if params.service_info_link:
            data['service_info_link'] = params.service_info_link
        return patch_requests.response(status_code=200, json=data)

    @commands_mock('ya')
    def _ya(args, **kwargs):
        assert str(kwargs['cwd']) == os.path.join(
            repo.working_dir, params.services_dir or '', params.service_name,
        )
        return json.dumps({'task': {'id': 123456789}, 'resource_id': 321})

    argv = ['--service-name', params.service_name]
    if repo:
        argv.extend(['--repo', repo.working_dir])
    elif params.docker_image:
        argv.extend(['--docker-image', params.docker_image])
    if params.environment:
        argv.extend(['--environment', params.environment])
    if params.deploy_branch:
        argv.extend(['--deploy-branch', params.deploy_branch])
    if params.deploy_type:
        argv.extend(['--deploy-type', params.deploy_type])

    clownductor_report.main(argv)

    if params.report_disabled_by_env:
        assert _report_to_clownductor.calls == []
        return

    if params.report_disabled_by_yaml:
        assert _report_to_clownductor.calls == []
        return

    if params.teamcity_report_problems:
        assert _report_to_clownductor.calls == []
        assert teamcity_report_problems.calls == [
            params.teamcity_report_problems,
        ]
        return

    if (
            params.environment in ('production', None)
            and not params.has_release_ticket
    ):
        assert teamcity_report_problems.calls == [
            {
                'description': (
                    'When environment type is production link to release'
                    ' ticket must present in RELEASE_TICKET env variable'
                ),
                'identity': None,
            },
        ]
        return

    if params.clownductor_error:
        if params.clownductor_error['code'] == 422:
            description = (
                f'Clownductor returns {params.clownductor_error["code"]} '
                f'error code with this message: {{\'error\': '
                f'\'{params.clownductor_error["message"]}\'}}. '
                f'More information about this kind of error here: '
                f'https://wiki.yandex-team.ru/taxi/backend/automatization/'
                f'faq/#padenieclownductor'
            )
        elif 400 <= params.clownductor_error['code'] < 500:
            description = (
                f'Clownductor returns {params.clownductor_error["code"]} '
                f'error code. It\'s Client Error with following message: '
                f'{{\'error\': \'{params.clownductor_error["message"]}\'}}.'
            )
        else:
            description = (
                f'Clownductor returns {params.clownductor_error["code"]} '
                f'error code. It\'s Server Error with following message: '
                f'{{\'error\': \'{params.clownductor_error["message"]}\'}}.'
            )
        assert teamcity_report_problems.calls == [
            {'description': description, 'identity': None},
        ]
        return

    if params.tool_debug:
        assert _report_to_clownductor.calls == []
    else:
        if not (params.has_docker_image or params.multiple_docker_images):
            assert _report_to_clownductor.calls == []
            return
        aliases = params.service_aliases or [
            {'service_name': params.service_name},
        ]
        if params.multiple_docker_images and not params.service_aliases:
            aliases = [
                {'service_name': image_name}
                for image_name in params.multiple_docker_images
            ]
        expected_ya_calls_args = params.expected_ya_calls_args or []
        ya_calls_args = [call['args'] for call in _ya.calls]
        assert expected_ya_calls_args == ya_calls_args
        expected_call = construct_request_call(
            environment=params.environment,
            aliases=aliases,
            service_name=params.service_name,
            repo_prefix=params.docker_image_prefix or params.image_repo_prefix,
            sandbox_resources=params.sandbox_resources,
            multiple_docker_images=params.multiple_docker_images,
            has_release_ticket=params.has_release_ticket,
            has_conductor_ticket=params.has_conductor_ticket,
            secdist_vars=secdist_vars,
            changelog=params.changelog,
            configs=params.configs,
            configs_sources=params.configs_sources,
            deploy_branch=params.deploy_branch,
            migration_tickets=params.migration_tickets,
            deploy_type=params.deploy_type,
            grants=params.grants,
            logbroker_config=params.logbroker_config,
            db_info=params.db_info,
        )
        clownductor_calls = _report_to_clownductor.calls
        assert len(clownductor_calls) == 1
        assert expected_call == clownductor_calls[0]

    assert (params.teamcity_messages or {}) == {
        call['message_name']: call['value'] for call in teamcity_messages.calls
    }


def make_repo(params, tmpdir):
    repo = params.init_repo(tmpdir)
    masters_branch = f'masters/{params.service_name}'
    if masters_branch in repo.branches:
        repo.git.checkout(masters_branch)
    service_dir_parts: List[str] = []
    if params.services_dir:
        service_dir_parts.append(params.services_dir)
    service_dir_parts.append(params.service_name)

    service_yaml_content: dict = {}
    if params.report_disabled_by_yaml:
        service_yaml_content['teamcity'] = {
            'clownductor-disabled': params.report_disabled_by_yaml,
        }

    if params.service_aliases:
        service_yaml_content.update(
            {
                'clownductor': {
                    'aliases': [
                        alias['service_name']
                        for alias in params.service_aliases
                    ],
                },
            },
        )

    if params.clownductor_service_info:
        service_yaml_content[
            'clownductor_service_info'
        ] = params.clownductor_service_info

    if params.sandbox_resources_yaml:
        service_yaml_content.setdefault('clownductor', {})[
            'sandbox-resources'
        ] = params.sandbox_resources_yaml

    dumped = yaml.safe_dump(service_yaml_content)
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'add service.yaml',
                files=[os.path.join(*service_dir_parts, 'service.yaml')],
                files_content=dumped,
            ),
        ],
    )
    if params.has_docker_image:
        if not params.is_dockerfile_in_service_dir:
            dockerfile_path = os.path.join(*service_dir_parts, 'Dockerfile')
        else:
            dockerfile_path = os.path.join(
                *service_dir_parts, '..', 'Dockerfile',
            )
        repository.apply_commits(
            repo,
            [repository.Commit('add Dockerfile', files=[dockerfile_path])],
        )
    for name in params.multiple_docker_images:
        if not params.is_dockerfile_in_service_dir:
            dockerfile_path = os.path.join(
                *service_dir_parts, f'Dockerfile.{name}',
            )
        else:
            dockerfile_path = os.path.join(
                *service_dir_parts, '..', f'Dockerfile.{name}',
            )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    f'add Dockerfile.{name}', files=[dockerfile_path],
                ),
            ],
        )
    if params.secdist_vars:
        testsuite_values_path = os.path.join(
            'generated',
            'services',
            params.service_name,
            'secdist',
            'testsuite_values.json',
        )
        files_content = (
            '{"postgresql_settings": {"$postgresql_settings": null}}'
        )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    'add vars',
                    files=[testsuite_values_path],
                    files_content=files_content,
                ),
            ],
        )
    if params.configs:
        configs_path = os.path.join(
            'generated',
            'services',
            params.service_name,
            'configs',
            'configs.json',
        )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    'add configs',
                    files=[configs_path],
                    files_content=json.dumps(params.configs),
                ),
            ],
        )
    if params.configs_sources:
        configs_sources_path = os.path.join(
            'generated',
            'services',
            params.service_name,
            'configs',
            'configs_sources.json',
        )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    'add configs-groups',
                    files=[configs_sources_path],
                    files_content=json.dumps(params.configs_sources),
                ),
            ],
        )
    if params.grants_sources:
        grants_sources_path = os.path.join(
            'generated', 'services', params.service_name, 'grants.yaml',
        )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    'add grants',
                    files=[grants_sources_path],
                    files_content=json.dumps(params.grants_sources),
                ),
            ],
        )
    if params.logbroker_config:
        logbroker_config_path = os.path.join(
            'generated',
            'services',
            params.service_name,
            'push-client',
            'logbroker.yaml',
        )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    'add logbroker config',
                    files=[logbroker_config_path],
                    files_content=yaml.dump(params.logbroker_config),
                ),
            ],
        )
    if params.db_info:
        db_info_path = os.path.join(
            'generated',
            'services',
            params.service_name,
            'db_info',
            f'db_info.{params.environment}.yaml',
        )
        repository.apply_commits(
            repo,
            [
                repository.Commit(
                    'add db_info',
                    files=[db_info_path],
                    files_content=yaml.dump(params.db_info),
                ),
            ],
        )
    if params.commits:
        repository.apply_commits(repo, params.commits)
    return repo


def construct_request_call(
        environment: Optional[str],
        aliases: List[Dict[str, str]],
        has_conductor_ticket: bool,
        has_release_ticket: bool,
        service_name: str,
        repo_prefix: str,
        sandbox_resources: Optional[List[Dict[str, Union[bool, str]]]],
        multiple_docker_images: Tuple[str, ...],
        secdist_vars: Optional[dict],
        changelog: Optional[str],
        configs: Optional[List[str]],
        configs_sources: Optional[List[dict]],
        deploy_branch: Optional[str],
        migration_tickets: Optional[List[str]],
        deploy_type: Optional[str],
        grants: Optional[dict],
        logbroker_config: Optional[Dict],
        db_info: Optional[dict],
) -> dict:
    if not environment:
        environment = 'production'
    request: dict = {
        'args': (
            'POST',
            'http://clownductor.taxi.yandex.net/api/teamcity_deploy',
        ),
        'kwargs': {
            'data': None,
            'json': {
                'env': environment,
                'service_name': aliases[0]['service_name'],
                'aliases': aliases,
            },
            'headers': {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-YaTaxi-Api-Key': 'secret',
            },
        },
    }
    if logbroker_config:
        if logbroker_config['is_default_docker_layout']:
            for alias in aliases:
                alias['logbroker_configuration'] = logbroker_config[
                    'configurations'
                ][0]['configuration']
        else:
            logbroker_config_map = {
                config['clownductor_service']: config['configuration']
                for config in logbroker_config['configurations']
            }
            for alias in aliases:
                configuration = logbroker_config_map.get(alias['service_name'])
                if configuration:
                    alias['logbroker_configuration'] = configuration
    if has_conductor_ticket:
        request['kwargs']['json']['conductor_ticket'] = 1803736
    if has_release_ticket:
        request['kwargs']['json'][
            'release_ticket'
        ] = 'https://st.yandex-team.ru/TAXIREL-5358'
    if sandbox_resources:
        request['kwargs']['json']['sandbox_resources'] = sandbox_resources
    else:
        if multiple_docker_images:
            dockerfile = (
                f'{repo_prefix}/{multiple_docker_images[0]}/{environment}:666'
            )
        else:
            dockerfile = f'{repo_prefix}/{service_name}/{environment}:666'
        request['kwargs']['json']['docker_image'] = dockerfile
    if secdist_vars:
        request['kwargs']['json']['secdist'] = secdist_vars
    if changelog:
        request['kwargs']['json']['changelog'] = changelog
    if configs:
        request['kwargs']['json']['configs'] = sorted(set(configs))
    if configs_sources:
        request['kwargs']['json']['configs_info'] = configs_sources
    if deploy_branch:
        request['kwargs']['json']['branch_name'] = deploy_branch
    if migration_tickets:
        request['kwargs']['json']['migration_tickets'] = migration_tickets
    if deploy_type:
        request['kwargs']['json']['deploy_type'] = deploy_type
    project_name = aliases[0].get('project_name')
    if project_name:
        request['kwargs']['json']['project_name'] = project_name
    if grants:
        request['kwargs']['json']['destinations'] = grants
    if db_info:
        request['kwargs']['json']['db_info'] = db_info
    return request
