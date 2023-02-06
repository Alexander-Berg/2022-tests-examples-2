from typing import Callable
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence

import git
import pytest

import rtc_image
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    branch: str
    args: List[str]
    docker_calls: List[str]
    environment: str = 'production'
    version: str = '0.0.1'
    registry_service_name: Optional[str] = None
    commits: Sequence[repository.Commit] = ()
    count_push_problems: int = 0
    fail_message: Optional[str] = None
    extra_args: Optional[str] = None
    image_repo_prefix: Optional[str] = None


@pytest.mark.parametrize(
    'param',
    [
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build', '--push'],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile .',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build'],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile .',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build'],
            extra_args='--ssh=default',
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile --ssh=default .',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--push'],
            docker_calls=[
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--push'],
            count_push_problems=1,
            docker_calls=[
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--push'],
            count_push_problems=2,
            docker_calls=[
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--push'],
            count_push_problems=3,
            fail_message='python exited with code 1',
            docker_calls=[
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/pilorama',
            args=['--build', '--push'],
            docker_calls=[],
        ),
        Params(
            init_repo=backend_py3.init,
            branch='masters/taxi-adjust',
            args=['--build', '--push'],
            version='0.1hotfix666',
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/taxi-adjust '
                '--build-arg VERSION=0.1hotfix666 --pull -t '
                'registry.yandex.net/taxi/taxi-adjust/production:0.1hotfix666 '
                '-f services/taxi-adjust/Dockerfile .',
                'docker push '
                'registry.yandex.net/taxi/taxi-adjust/production:0.1hotfix666',
            ],
        ),
        Params(
            init_repo=backend_py3.init,
            branch='masters/taxi-corp',
            args=['--build', '--push'],
            docker_calls=[],
        ),
        Params(
            init_repo=backend.init,
            branch='develop',
            args=['--build', '--push'],
            registry_service_name='backend-py2',
            docker_calls=[],
        ),
        Params(
            init_repo=backend.init,
            branch='develop',
            args=['--build', '--push'],
            registry_service_name='backend-py2',
            commits=[repository.Commit('add Dockerfile', ['Dockerfile'])],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=. --build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/backend-py2/production:0.0.1 '
                '-f Dockerfile .',
                'docker push '
                'registry.yandex.net/taxi/backend-py2/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build', '--push'],
            commits=[
                repository.Commit(
                    'add Dockerfile',
                    [
                        'services/driver-authorizer/'
                        'Dockerfile.driver-authorizer-maps',
                    ],
                ),
                repository.Commit(
                    'add Dockerfile',
                    [
                        'services/driver-authorizer/'
                        'Dockerfile.driver-authorizer-serp',
                    ],
                ),
            ],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile .',
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/'
                'driver-authorizer-maps/production:0.0.1 '
                '-f services/driver-authorizer/'
                'Dockerfile.driver-authorizer-maps .',
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/'
                'driver-authorizer-serp/production:0.0.1 '
                '-f services/driver-authorizer/'
                'Dockerfile.driver-authorizer-serp .',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/'
                'driver-authorizer-maps/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/'
                'driver-authorizer-serp/production:0.0.1',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build'],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/eda/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile .',
            ],
            image_repo_prefix='eda',
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build', '--push', '--tag-latest'],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile .',
                'docker tag '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                'registry.yandex.net/taxi/driver-authorizer/production:latest',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1',
                'docker push '
                'registry.yandex.net/taxi/driver-authorizer/production:latest',
            ],
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/driver-authorizer',
            args=['--build', '--push', '--tag-latest'],
            commits=[
                repository.Commit(
                    'edit changelog',
                    ['services/driver-authorizer/debian/changelog'],
                    'driver-authorizer (0.0.3resources1) unstable; urgency='
                    'low\n\n  Release ticket https://st.yandex-team.ru'
                    '/TAXIREL-6\n\n  * alberist | Ololo\n\n'
                    ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                    '19 May 2021 17:03:54 +0300\n\n',
                ),
            ],
            docker_calls=[
                'docker build --no-cache --build-arg APP_ENV=production '
                '--build-arg APP_ROOT=services/driver-authorizer '
                '--build-arg VERSION=0.0.1 --pull -t '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                '-f services/driver-authorizer/Dockerfile .',
                'docker tag '
                'registry.yandex.net/taxi/driver-authorizer/production:0.0.1 '
                'registry.yandex.net/taxi/driver-authorizer/production:latest',
            ],
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                args=['--build'],
                commits=[
                    repository.Commit(
                        'add clownductor_namespace',
                        ['services/driver-authorizer/service.yaml'],
                        'clownductor_service_info:\n'
                        '  clownductor_namespace: authorizer\n'
                        '  clownductor_project: taxi-drivers\n',
                    ),
                ],
                docker_calls=[
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer/production:0.0.1 '
                    '-f services/driver-authorizer/Dockerfile .',
                ],
            ),
            id='form_docker_image_prefix_with_clownductor_namespace',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                args=['--build'],
                commits=[
                    repository.Commit(
                        'add clownductor_namespace',
                        ['services/driver-authorizer/service.yaml'],
                        'clownductor_service_info:\n'
                        '  clownductor_namespace: authorizer\n'
                        '  clownductor_project: taxi-drivers\n',
                    ),
                ],
                docker_calls=[
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer/production:0.0.1 '
                    '-f services/driver-authorizer/Dockerfile .',
                ],
                image_repo_prefix='eda',
            ),
            id='form_docker_image_prefix_with_clownductor_namespace_and_env',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                args=['--build'],
                commits=[
                    repository.Commit(
                        'add clownductor_namespace in multialias service',
                        ['services/driver-authorizer/service.yaml'],
                        'clownductor_service_info:\n'
                        '  service:\n'
                        '    clownductor_namespace: authorizer\n'
                        '    clownductor_project: taxi-drivers\n'
                        '  aliases:\n'
                        '    - name: driver-authorizer-maps\n',
                    ),
                    repository.Commit(
                        'add Dockerfile',
                        [
                            'services/driver-authorizer/'
                            'Dockerfile.driver-authorizer-maps',
                        ],
                    ),
                ],
                docker_calls=[
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer/production:0.0.1 '
                    '-f services/driver-authorizer/Dockerfile .',
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer-maps/production:0.0.1 '
                    '-f services/driver-authorizer/'
                    'Dockerfile.driver-authorizer-maps .',
                ],
            ),
            id='multialias_service_-_inheritance_all',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                args=['--build'],
                commits=[
                    repository.Commit(
                        'add clownductor_namespace in multialias service',
                        ['services/driver-authorizer/service.yaml'],
                        'clownductor_service_info:\n'
                        '  service:\n'
                        '    clownductor_namespace: authorizer\n'
                        '    clownductor_project: taxi-drivers\n'
                        '  aliases:\n'
                        '    - name: driver-authorizer-maps\n'
                        '      clownductor_project: taxi-devops\n',
                    ),
                    repository.Commit(
                        'add Dockerfile',
                        [
                            'services/driver-authorizer/'
                            'Dockerfile.driver-authorizer-maps',
                        ],
                    ),
                ],
                docker_calls=[
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer/production:0.0.1 '
                    '-f services/driver-authorizer/Dockerfile .',
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-devops/'
                    'driver-authorizer-maps/production:0.0.1 '
                    '-f services/driver-authorizer/'
                    'Dockerfile.driver-authorizer-maps .',
                ],
            ),
            id='multialias_service_-_inheritance_clownductor_namespace',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                args=['--build', '--push'],
                commits=[
                    repository.Commit(
                        'add clownductor_namespace in multialias service',
                        ['services/driver-authorizer/service.yaml'],
                        'clownductor_service_info:\n'
                        '  service:\n'
                        '    clownductor_namespace: authorizer\n'
                        '    clownductor_project: taxi-drivers\n'
                        '  aliases:\n'
                        '    - name: driver-authorizer-maps\n'
                        '      clownductor_namespace: auto\n',
                    ),
                    repository.Commit(
                        'add Dockerfile',
                        [
                            'services/driver-authorizer/'
                            'Dockerfile.driver-authorizer-maps',
                        ],
                    ),
                ],
                docker_calls=[
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer/production:0.0.1 '
                    '-f services/driver-authorizer/Dockerfile .',
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/auto/taxi-drivers/'
                    'driver-authorizer-maps/production:0.0.1 '
                    '-f services/driver-authorizer/'
                    'Dockerfile.driver-authorizer-maps .',
                    'docker push '
                    'registry.yandex.net/authorizer/taxi-drivers/'
                    'driver-authorizer/production:0.0.1',
                    'docker push '
                    'registry.yandex.net/auto/taxi-drivers/'
                    'driver-authorizer-maps/production:0.0.1',
                ],
            ),
            id='multialias_service_-_inheritance_clownductor_project',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                args=['--build'],
                commits=[
                    repository.Commit(
                        'add clownductor_namespace in multialias service',
                        ['services/driver-authorizer/service.yaml'],
                        'clownductor_service_info:\n'
                        '  service:\n'
                        '    clownductor_project: eda\n'
                        '  aliases:\n'
                        '    - name: driver-authorizer-maps\n'
                        '      clownductor_project: market\n'
                        '      clownductor_namespace: maps\n'
                        '    - name: driver-authorizer-serp\n'
                        '      clownductor_project: cargo\n'
                        '      clownductor_namespace: serp\n',
                    ),
                    repository.Commit(
                        'add Dockerfile.driver-authorizer-maps',
                        [
                            'services/driver-authorizer/'
                            'Dockerfile.driver-authorizer-maps',
                        ],
                    ),
                    repository.Commit(
                        'add Dockerfile.driver-authorizer-serp',
                        [
                            'services/driver-authorizer/'
                            'Dockerfile.driver-authorizer-serp',
                        ],
                    ),
                ],
                docker_calls=[
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/taxi/'
                    'driver-authorizer/production:0.0.1 '
                    '-f services/driver-authorizer/Dockerfile .',
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/maps/market/'
                    'driver-authorizer-maps/production:0.0.1 '
                    '-f services/driver-authorizer/'
                    'Dockerfile.driver-authorizer-maps .',
                    'docker build --no-cache --build-arg APP_ENV=production '
                    '--build-arg APP_ROOT=services/driver-authorizer '
                    '--build-arg VERSION=0.0.1 --pull -t '
                    'registry.yandex.net/serp/cargo/'
                    'driver-authorizer-serp/production:0.0.1 '
                    '-f services/driver-authorizer/'
                    'Dockerfile.driver-authorizer-serp .',
                ],
            ),
            id='multialias_service_-_different_clownductor_namespace',
        ),
    ],
)
def test_rtc_image(
        tmpdir,
        monkeypatch,
        commands_mock,
        teamcity_report_problems,
        param: Params,
) -> None:
    repo = param.init_repo(tmpdir)
    repo.git.checkout(param.branch)
    repository.apply_commits(repo, param.commits)
    monkeypatch.chdir(repo.working_dir)
    monkeypatch.setenv('ENVIRONMENT_TYPE', param.environment)
    monkeypatch.setenv('BUILD_NUMBER', param.version)
    monkeypatch.setattr(rtc_image, 'DOCKER_PUSH_RETRY_INTERVAL', 0.1)
    if param.extra_args is not None:
        monkeypatch.setenv('DOCKER_BUILD_EXTRA_ARGS', param.extra_args)
    if param.registry_service_name is not None:
        monkeypatch.setenv(
            'REGISTRY_SERVICE_NAME', param.registry_service_name,
        )
    if param.image_repo_prefix is not None:
        monkeypatch.setenv('IMAGE_REPO_PREFIX', param.image_repo_prefix)
    push_counter = 0

    @commands_mock('docker')
    def docker_mock(args, **kwargs):
        nonlocal push_counter
        if len(args) > 1 and args[0] == 'docker' and args[1] == 'push':
            push_counter += 1
            if push_counter <= param.count_push_problems:
                return 1
        return 0

    rtc_image.main(param.args)
    assert docker_mock.calls == [
        {'args': docker_call.split(), 'kwargs': {'cwd': None, 'env': None}}
        for docker_call in param.docker_calls
    ]

    if param.fail_message is not None:
        assert teamcity_report_problems.calls == [
            {'description': param.fail_message, 'identity': None},
        ]
