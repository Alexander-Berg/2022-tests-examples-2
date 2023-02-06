import dataclasses
import pathlib
from typing import Dict
from typing import Optional
from typing import Sequence
import unittest.mock

import create_pr
from taxi_buildagent.clients import github
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia
from tests.utils.examples import uservices


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    files_to_add: Dict[str, str]
    extra_args: Sequence[str] = ()
    ya_calls: Optional[Sequence[dict]] = None
    arc_calls: Optional[Sequence[dict]] = None
    startrek_message: Optional[str] = None


@pytest_wraps.parametrize(
    [
        Params(
            pytest_id='successful-pr',
            files_to_add={
                'awesome-file': 'content',
                'another-file': 'more content',
            },
        ),
    ],
)
def test_create_github_pr(
        monkeypatch, chdir, tmpdir, patch_requests, params: Params,
):
    fake_push_to_origin = unittest.mock.MagicMock()
    monkeypatch.setattr('taxi_buildagent.clients.github.API_TOKEN', 'foobar')
    monkeypatch.setattr(
        'taxi_buildagent.tools.vcs.git_repo.Repo.push_branch',
        fake_push_to_origin,
    )

    fake_create_pr = unittest.mock.MagicMock(
        return_value=patch_requests.response(
            status_code=201,
            json={
                'number': 1,
                'head': {
                    'repo': {
                        'owner': {'login': 'rumkex'},
                        'ssh_url': 'foo@bar:baz.git',
                    },
                    'ref': 'develop',
                },
                'mergeable': True,
                'merged': False,
                'merge_commit_sha': None,
                'html_url': 'http://git.example.com/owner/repo/pulls/1234',
                'statuses_url': (
                    'http://git.example.com/owner/repo/pulls/1234/st'
                ),
                'updated_at': 'never',
                'state': 'open',
                'base': {'ref': 'develop'},
            },
        ),
    )
    patch_requests(github.BASE_URL)(fake_create_pr)

    repo = uservices.init(tmpdir)
    repo_path = pathlib.Path(repo.working_tree_dir)
    chdir(repo_path)

    for file, contents in params.files_to_add.items():
        with open(repo_path / file, 'w') as file_to_add:
            file_to_add.write(contents)

    create_pr.main(
        [
            '--repo',
            'my-fancy-repo',
            '--branch',
            'robot-branch',
            '--title',
            'feat all: I need to merge this',
            '--body',
            'A succinct description message',
            'awesome-file',
            'another-file',
        ],
    )

    fake_push_to_origin.assert_called_once_with(
        'robot-branch', remote='pr-origin',
    )
    fake_create_pr.assert_called_once_with(
        'POST',
        'https://github.yandex-team.ru/api/v3/repos/my-fancy-repo/pulls',
        headers={'Authorization': 'token foobar'},
        json={
            'base': 'develop',
            'head': 'robot-branch',
            'title': 'feat all: I need to merge this',
            'body': 'A succinct description message',
        },
    )
    assert not repo.is_dirty()
    assert all(remote.name != 'pr-origin' for remote in repo.remotes)


BASE_ARC_PARAMS = Params(
    pytest_id='successful-pr',
    files_to_add={'awesome-file': 'content', 'another-file': 'more content'},
    ya_calls=[
        {
            'args': [
                'ya',
                'pr',
                'create',
                '--no-interactive',
                '--wait',
                '--json',
                '--push',
                '--publish',
                '--merge',
            ],
        },
        {
            'args': [
                'ya',
                'pr',
                'edit',
                '--id',
                '12345',
                '--summary',
                'feat all: I need to merge this',
                '--description',
                'Relates: SOMETAXI-queue',
            ],
        },
    ],
    arc_calls=[
        {'args': ['arc', 'info', '--json']},
        {
            'args': [
                'arc',
                'checkout',
                '-b',
                'users/arcanum-robot-branch',
                'trunk',
            ],
        },
        {'args': ['arc', 'add', 'awesome-file', 'another-file']},
        {
            'args': [
                'arc',
                'commit',
                '--message',
                'feat all: I need to merge this\n\nRelates: SOMETAXI-queue',
                '--force',
            ],
        },
        {'args': ['arc', 'reset', '--hard', '--force']},
        {'args': ['arc', 'info', '--json']},
        {
            'args': [
                'arc',
                'branch',
                '-D',
                'users/arcanum-robot-branch',
                '--force',
            ],
        },
    ],
)


@pytest_wraps.parametrize(
    [
        BASE_ARC_PARAMS,
        dataclasses.replace(
            BASE_ARC_PARAMS,
            pytest_id='pr-with-notify',
            extra_args=[
                '--notify-ticket',
                'https://st.yandex-team.ru/TAXIREL-1',
            ],
            startrek_message=(
                'Необходимо одобрить изменения в репозитории.\n'
                '%%feat all: I need to merge this%%\n'
                'https://a.yandex-team.ru/review/12345/details\n'
                'Подтвердите изменения перед закрытием тикета.\n'
            ),
        ),
    ],
)
def test_create_arcanum_pr(
        monkeypatch, tmpdir, commands_mock, startrek, params: Params,
):
    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        command = args[2]
        if command == 'create':
            return '{"id":12345}'
        if command == 'edit':
            return ''
        return 0

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"branch": "trunk"}'
        return 0

    work_dir = arcadia.init_dummy(tmpdir)
    repo_path = pathlib.Path(work_dir)
    monkeypatch.chdir(work_dir)

    for file, contents in params.files_to_add.items():
        with open(repo_path / file, 'w') as file_to_add:
            file_to_add.write(contents)

    create_pr.main(
        [
            '--repo',
            'arcadia',
            '--branch',
            'users/arcanum-robot-branch',
            '--title',
            'feat all: I need to merge this',
            '--body',
            'Relates: SOMETAXI-queue',
            'awesome-file',
            'another-file',
            *params.extra_args,
        ],
    )

    ya_mock_calls = ya_mock.calls
    for call in ya_mock_calls:
        call.pop('kwargs')

    assert ya_mock_calls == params.ya_calls

    arc_mock_calls = arc_mock.calls
    for call in arc_mock_calls:
        call.pop('kwargs')

    assert arc_mock_calls == params.arc_calls

    if params.startrek_message:
        calls = startrek.create_comment.calls
        assert len(calls) == 1
        assert calls[0]['json']['text'] == params.startrek_message
    else:
        assert not startrek.create_comment.calls
