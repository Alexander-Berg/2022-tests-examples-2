import sys
from typing import Callable
from typing import List
from typing import NamedTuple
from typing import Sequence

import git
import pytest

import pypi_package
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    branch: str
    calls: List[str]
    commits: Sequence[repository.Commit] = ()
    count_upload_problems: int = 0
    error: str = ''


@pytest.mark.parametrize(
    'param',
    [
        Params(
            init_repo=backend.init,
            branch='master',
            commits=[
                repository.Commit(
                    'mono no service.yaml', ['setup.py', 'dist/s-th.tar.gz'],
                ),
            ],
            calls=[
                f'{sys.executable} setup.py sdist',
                'twine upload --repository yandex-pypi --username user '
                '--password pswd dist/*',
            ],
        ),
        Params(
            init_repo=backend.init,
            branch='master',
            calls=[],
            error='No setup.py in service, turn off step or add setup.py',
        ),
        Params(
            init_repo=backend.init,
            branch='master',
            commits=[repository.Commit('mono no dist', ['setup.py'])],
            calls=[f'{sys.executable} setup.py sdist'],
            error='No dist/ dir in service, or it\'s empty',
        ),
        Params(
            init_repo=backend.init,
            branch='master',
            commits=[
                repository.Commit(
                    'mono service.yaml turn off all',
                    ['service.yaml'],
                    'teamcity: {deploy-pypi-package: '
                    '{sdist: false, bdist-wheel: false, upload: false}}',
                ),
            ],
            calls=[],
        ),
        Params(
            init_repo=backend.init,
            branch='master',
            count_upload_problems=10,
            commits=[
                repository.Commit(
                    'mono only upload true',
                    ['dist/s-th.tar.gz', 'service.yaml'],
                    'teamcity: {deploy-pypi-package: {upload: true}}',
                ),
            ],
            calls=[
                'twine upload --repository yandex-pypi --username user '
                '--password pswd dist/*',
            ]
            * 11,
        ),
        Params(
            init_repo=uservices.init,
            branch='masters/pilorama',
            commits=[
                repository.Commit(
                    'files',
                    [
                        'services/pilorama/service.yaml',
                        'services/pilorama/dist/s-th.tar.gz',
                        'services/pilorama/setup.py',
                    ],
                    'teamcity: '
                    '{deploy-pypi-package: {bdist-wheel: true, upload: true}}',
                ),
            ],
            calls=[
                f'{sys.executable} setup.py bdist_wheel --universal ',
                'twine upload --repository yandex-pypi --username user '
                '--password pswd dist/*',
            ],
        ),
    ],
)
def test_pypi_package(
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
    monkeypatch.setenv('PYPI_USER', 'user')
    monkeypatch.setenv('PYPI_PASSWORD', 'pswd')
    upload_counter = 0

    @commands_mock('twine')
    def twine_mock(args, **kwargs):
        nonlocal upload_counter
        upload_counter += 1
        if upload_counter <= param.count_upload_problems:
            return 1
        return 0

    @commands_mock(sys.executable)
    def python3_mock(args, **kwargs):
        return 0

    if param.error:
        with pytest.raises(SystemExit):
            pypi_package.main()
        assert teamcity_report_problems.calls == [
            {'description': param.error, 'identity': None},
        ]
    else:
        pypi_package.main()
    assert python3_mock.calls + twine_mock.calls == [
        {'args': call.split(), 'kwargs': {'cwd': None, 'env': None}}
        for call in param.calls
    ]
