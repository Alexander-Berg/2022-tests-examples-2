import dataclasses
import functools
import json
import pathlib
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import List
from typing import NamedTuple
from unittest import mock

import git
import pytest

import create_masters_branches
from taxi_buildagent import utils
from tests.utils import repository
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    new_services: List[str]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                new_services=['new-service-one', 'new-service-two'],
            ),
            id='backend_py3',
        ),
        pytest.param(
            Params(init_repo=uservices.init, new_services=['new-service']),
            id='uservices',
        ),
        pytest.param(
            Params(init_repo=uservices.init, new_services=[]),
            id='without_new_services',
        ),
    ],
)
def test_create_masters(params, monkeypatch, tmpdir):
    repo = params.init_repo(tmpdir)
    monkeypatch.chdir(repo.working_tree_dir)
    commit_new_services(params.new_services, repo)

    create_masters_branches.main()

    origin = git.Repo(next(repo.remotes[0].urls))
    for service in params.new_services:
        branch_name = 'masters/' + service
        try:
            origin.git.show_branch(branch_name)
        except git.CommandError:
            pytest.fail(f'No branch {branch_name} in origin repository')


def commit_new_services(services, repo):
    services_dir = pathlib.Path(
        utils.load_yaml('services.yaml')
        .get('services', {})
        .get('directory', '.'),
    )
    for service in services:
        repository.commit_debian_dir(
            repo=repo, package_name=service, path=services_dir / service,
        )


@dataclasses.dataclass(frozen=True)
class ArcadiaParams:
    branches: List[str]
    pushed_branches: List[str]
    file_contents: Dict[str, str]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ArcadiaParams(
                file_contents={
                    'uservices/service/nested/debian/changelog': '',
                    'service/debian/changelog': '',
                },
                branches=['arcadia/users/robot-taxi-teamcity/taxi/service'],
                pushed_branches=[],
            ),
            id='nothing to push',
        ),
        pytest.param(
            ArcadiaParams(
                file_contents={
                    'uservices/service/nested/debian/changelog': '',
                    'another-service/debian/changelog': '',
                    'service/debian/changelog': '',
                },
                branches=['arcadia/users/robot-taxi-teamcity/taxi/service'],
                pushed_branches=[
                    'users/robot-taxi-teamcity/taxi/another-service',
                ],
            ),
            id='push one service of many',
        ),
        pytest.param(
            ArcadiaParams(
                file_contents={
                    'uservices/service/nested/debian/changelog': '',
                    'another-service/debian/changelog': '',
                    'service/debian/changelog': '',
                },
                branches=[],
                pushed_branches=[
                    'users/robot-taxi-teamcity/taxi/another-service',
                    'users/robot-taxi-teamcity/taxi/service',
                ],
            ),
            id='push many services',
        ),
        pytest.param(
            ArcadiaParams(
                file_contents={
                    'uservices/services/another/debian/changelog': '',
                    'uservices/services/nested/debian/changelog': '',
                    'service/debian/changelog': '',
                    'uservices/services.yaml': """
                        services:
                          directory: services
                    """,
                },
                branches=[],
                pushed_branches=[
                    'users/robot-taxi-teamcity/taxi/uservices/another',
                    'users/robot-taxi-teamcity/taxi/uservices/nested',
                    'users/robot-taxi-teamcity/taxi/service',
                ],
            ),
            id='push many nested services',
        ),
        pytest.param(
            ArcadiaParams(
                file_contents={
                    'uservices/services/another/debian/changelog': '',
                    'uservices/services/nested/debian/changelog': '',
                    'uservices/services.yaml': """
                        services:
                          directory: services
                    """,
                },
                branches=[
                    'arcadia/users/robot-taxi-teamcity/taxi/uservices/another',
                ],
                pushed_branches=[
                    'users/robot-taxi-teamcity/taxi/uservices/nested',
                ],
            ),
            id='push one of many nested services',
        ),
        pytest.param(
            ArcadiaParams(
                file_contents={'service/debian/changelog': ''},
                branches=[
                    'arcadia/users/robot-taxi-teamcity/taxi/service/nested',
                ],
                pushed_branches=[],
            ),
            id='do not push nested branches',
        ),
    ],
)
def test_create_masters_arcadia(params: ArcadiaParams, monkeypatch, tmpdir):
    arcadia_dir = pathlib.Path(tmpdir) / 'arcadia'
    (arcadia_dir / '.arc').mkdir(parents=True)
    current_dir = arcadia_dir / 'taxi'

    files = set()
    for filename, content in params.file_contents.items():
        files.add(filename)
        file_path = current_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    @functools.lru_cache(maxsize=None)
    def _mock_arc(path: pathlib.Path):
        return mock_arc_client(current_dir / path, files, params.branches)

    monkeypatch.chdir(current_dir)
    monkeypatch.setattr(
        'taxi_buildagent.tools.vcs.arc_repo._ArcClient', _mock_arc,
    )

    create_masters_branches.main()

    root_arc = _mock_arc(current_dir)
    root_arc.fetch.assert_called_once_with('users/robot-taxi-teamcity/')

    for branch in params.pushed_branches:
        root_arc.assert_has_calls(
            (
                mock.call.branch(branch, 'deadbeef~1'),
                mock.call.push(f'{branch}:{branch}', error=True),
                mock.call.branch('-D', branch),
            ),
        )


def mock_arc_client(
        path: pathlib.Path, files: Iterable[str], branches: Iterable[str],
) -> mock.MagicMock:
    arc = mock.MagicMock()
    arc.path = path
    arc.ls_files.return_value = '\n'.join(files)
    arc.branch.return_value = json.dumps(
        [{'name': branch} for branch in branches],
    )
    arc.info.return_value = json.dumps({'branch': 'trunk'})
    arc.log.return_value = json.dumps(
        [
            {'commit': 'foobar', 'message': 'do good'},
            {'commit': 'deadbeef', 'message': 'improve all'},
        ],
    )
    return arc
