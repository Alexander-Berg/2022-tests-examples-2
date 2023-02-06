from typing import Callable
from typing import List
from typing import NamedTuple

import git
import pytest

import download_deb_packages
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    branch: str
    args: List[str]
    version: str
    docker_pull_msg: List[str]


@pytest.mark.parametrize(
    'param',
    [
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                args=[],
                version='0.1.1',
                docker_pull_msg=[
                    'docker',
                    'pull',
                    'registry.yandex.net/taxi/taxi-integration-xenial-unstable'
                    ':latest',
                ],
            ),
            id='simple_example',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                args=['--build-number-suffix', 'xotfix0.2.4'],
                version='0.1.1xotfix0.2.4',
                docker_pull_msg=[
                    'docker',
                    'pull',
                    'registry.yandex.net/taxi/taxi-integration-xenial-unstable'
                    ':latest',
                ],
            ),
            id='build_number_arg',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer2',
                args=[],
                version='2.2.2',
                docker_pull_msg=[
                    'docker',
                    'pull',
                    'registry.yandex.net/taxi/taxi-integration-trusty-unstable'
                    ':latest',
                ],
            ),
            id='trusty_os',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer2',
                args=['--build-number-suffix', 'rebuild1.8.1'],
                version='2.2.2rebuild1.8.1',
                docker_pull_msg=[
                    'docker',
                    'pull',
                    'registry.yandex.net/taxi/taxi-integration-trusty-unstable'
                    ':latest',
                ],
            ),
            id='os_n_build_arg',
        ),
    ],
)
def test_download_deb_packages(
        tmpdir,
        monkeypatch,
        commands_mock,
        teamcity_report_build_number,
        param: Params,
) -> None:
    repo = param.init_repo(tmpdir)
    repo.git.checkout(param.branch)
    monkeypatch.chdir(repo.working_dir)

    @commands_mock('docker')
    def docker_mock(*args, **kwargs):
        return 0

    download_deb_packages.main(param.args)

    docker_calls = docker_mock.calls
    assert len(docker_calls) == 2
    assert list(*docker_calls[0]['args']) == param.docker_pull_msg
    assert list(*docker_calls[1]['args'])[:2] == ['docker', 'run']

    calls = teamcity_report_build_number.calls
    if '--build-number-suffix' in param.args:
        assert len(calls) == 1
        assert calls[0]['build_number'] == param.version
    else:
        assert not calls
