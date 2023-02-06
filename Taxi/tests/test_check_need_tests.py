import datetime
import typing

import freezegun
import git
import pytest

import check_need_tests
from taxi_buildagent.clients import arcadia as arcadia_client
from tests.utils import repository
from tests.utils.examples import backend


class Params(typing.NamedTuple):
    init_repo: typing.Callable[[str], git.Repo]
    branch: str
    pull_requests: typing.List[typing.Dict]
    argv: typing.List[str]
    report_text: typing.Sequence[str] = []
    report_error_text: typing.Sequence[str] = []
    teamcity_report_problems: typing.Sequence[dict] = []


UTC_NOW = datetime.datetime.utcnow()
SEVENTY_DAYS_AGO = UTC_NOW - datetime.timedelta(days=70)
TWO_DAYS_AGO = UTC_NOW - datetime.timedelta(days=2)
THIRTY_DAYS_AGO = UTC_NOW - datetime.timedelta(days=30)
FIVE_SECONDS = datetime.timedelta(seconds=5)

PRINT_UPDATED_AT_FORMAT = '%Y-%m-%d %H:%M:%SZ'


@freezegun.freeze_time(UTC_NOW, tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/head',
                        'updated': TWO_DAYS_AGO,
                        'commits': [
                            repository.Commit('change1', ['taxi/file']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--pr',
                    'pull/1',
                    '--days',
                    '30',
                ],
                report_text=[
                    'Pull Request last update: {}'.format(
                        TWO_DAYS_AGO.strftime(PRINT_UPDATED_AT_FORMAT),
                    ),
                ],
            ),
            id='github good pr',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/head',
                        'updated': TWO_DAYS_AGO,
                        'commits': [
                            repository.Commit('change1', ['taxi/file']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--pr',
                    'refs/pull/1/head',
                    '--days',
                    '30',
                ],
                report_text=[
                    'Pull Request last update: {}'.format(
                        TWO_DAYS_AGO.strftime(PRINT_UPDATED_AT_FORMAT),
                    ),
                ],
            ),
            id='github good pr new format',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/merge',
                        'updated': SEVENTY_DAYS_AGO,
                        'commits': [
                            repository.Commit('some change', ['taxi/file3']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--pr',
                    '1/merge',
                    '--days',
                    '30',
                ],
                report_error_text=['Too old Pull Request. Skip tests.'],
                report_text=[
                    'Pull Request last update: {}'.format(
                        SEVENTY_DAYS_AGO.strftime(PRINT_UPDATED_AT_FORMAT),
                    ),
                ],
                teamcity_report_problems=[
                    {
                        'description': 'Too old Pull Request',
                        'identity': 'old-pr',
                    },
                ],
            ),
            id='github outdated pr',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/head',
                        'updated': THIRTY_DAYS_AGO + FIVE_SECONDS,
                        'commits': [
                            repository.Commit('change1', ['taxi/file']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--pr',
                    'pull/1',
                    '--days',
                    '30',
                ],
                report_text=[
                    'Pull Request last update: {}'.format(
                        (THIRTY_DAYS_AGO + FIVE_SECONDS).strftime(
                            PRINT_UPDATED_AT_FORMAT,
                        ),
                    ),
                ],
            ),
            id='border github good pr',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/head',
                        'updated': THIRTY_DAYS_AGO - FIVE_SECONDS,
                        'commits': [
                            repository.Commit('some change', ['taxi/file3']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--pr',
                    'pull/1',
                    '--days',
                    '30',
                ],
                report_error_text=['Too old Pull Request. Skip tests.'],
                report_text=[
                    'Pull Request last update: {}'.format(
                        (THIRTY_DAYS_AGO - FIVE_SECONDS).strftime(
                            PRINT_UPDATED_AT_FORMAT,
                        ),
                    ),
                ],
                teamcity_report_problems=[
                    {
                        'description': 'Too old Pull Request',
                        'identity': 'old-pr',
                    },
                ],
            ),
            id='border github outdated pr',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/head',
                        'updated': THIRTY_DAYS_AGO - FIVE_SECONDS,
                        'commits': [
                            repository.Commit('some change', ['taxi/file3']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--pr',
                    'refs/pull/1/head',
                    '--days',
                    '30',
                ],
                report_error_text=['Too old Pull Request. Skip tests.'],
                report_text=[
                    'Pull Request last update: {}'.format(
                        (THIRTY_DAYS_AGO - FIVE_SECONDS).strftime(
                            PRINT_UPDATED_AT_FORMAT,
                        ),
                    ),
                ],
                teamcity_report_problems=[
                    {
                        'description': 'Too old Pull Request',
                        'identity': 'old-pr',
                    },
                ],
            ),
            id='border github outdated pr new format',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    {
                        'login': 'pycz',
                        'branch': 'feat/head',
                        'updated': TWO_DAYS_AGO,
                        'commits': [
                            repository.Commit('some change', ['taxi/file3']),
                        ],
                    },
                ],
                argv=[
                    '--provider',
                    'github',
                    '--days',
                    '30',
                    '--pr',
                    'bull/2',
                ],
                report_text=['It is not Pull Request'],
            ),
            id='invalid github pr',
        ),
    ],
)
def test_old_pr_check(
        tmpdir,
        monkeypatch,
        github,
        teamcity_report_problems,
        capsys,
        params: Params,
):
    repo = params.init_repo(tmpdir)
    repo.git.checkout(params.branch)
    monkeypatch.chdir(repo.working_tree_dir)
    github_repo = github.init_repo(
        'taxi', 'backend', next(repo.remotes[0].urls),
    )

    for _pr in params.pull_requests:
        github_repo.create_pr(repo, **_pr)

    capsys.readouterr()

    if params.teamcity_report_problems:
        with pytest.raises(SystemExit) as excinfo:
            check_need_tests.main(params.argv)
        assert (1,) == excinfo.value.args
    else:
        check_need_tests.main(params.argv)

    captured = capsys.readouterr()
    outs = [out for out in captured.out.split('\n') if out]
    errors = [err for err in captured.err.split('\n') if err]

    assert params.teamcity_report_problems == teamcity_report_problems.calls
    # because of teamcity_report_problems also is in stdout
    for text in params.report_text:
        assert text in outs
    assert params.report_error_text == errors


class ArcParams(typing.NamedTuple):
    arcadia_pr_calls: typing.Sequence[dict]
    argv: typing.List[str]
    report_text: typing.Sequence[str] = []
    report_error_text: typing.Sequence[str] = []
    teamcity_report_problems: typing.Sequence[dict] = []
    pull_request_date: datetime.datetime = UTC_NOW


@freezegun.freeze_time(UTC_NOW, tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ArcParams(
                argv=[
                    '--provider',
                    'arcanum',
                    '--days',
                    '30',
                    '--pr',
                    'users/robot-stark/taxi/some_service/0/head',
                ],
                report_error_text=['Too old Pull Request. Skip tests.'],
                report_text=[
                    'Pull Request last update: {}'.format(
                        SEVENTY_DAYS_AGO.strftime(PRINT_UPDATED_AT_FORMAT),
                    ),
                ],
                teamcity_report_problems=[
                    {
                        'description': 'Too old Pull Request',
                        'identity': 'old-pr',
                    },
                ],
                arcadia_pr_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth valid token'},
                            'params': {
                                'fields': (
                                    'author,summary,'
                                    'vcs(from_branch,to_branch),merge_commits,'
                                    'updated_at,'
                                    'checks(type,status,updated_at),labels,'
                                    'description'
                                ),
                            },
                        },
                        'method': 'get',
                        'url': (
                            'http://a.yandex-team.ru/api/v1/review-requests/0'
                        ),
                    },
                ],
                pull_request_date=SEVENTY_DAYS_AGO,
            ),
            id='outdated arc pr',
        ),
        pytest.param(
            ArcParams(
                argv=[
                    '--provider',
                    'arcanum',
                    '--days',
                    '30',
                    '--pr',
                    'users/robot-stark/taxi/some_service/2/merge_pin',
                ],
                report_error_text=['Too old Pull Request. Skip tests.'],
                report_text=[
                    'Pull Request last update: {}'.format(
                        (THIRTY_DAYS_AGO - FIVE_SECONDS).strftime(
                            PRINT_UPDATED_AT_FORMAT,
                        ),
                    ),
                ],
                teamcity_report_problems=[
                    {
                        'description': 'Too old Pull Request',
                        'identity': 'old-pr',
                    },
                ],
                arcadia_pr_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth valid token'},
                            'params': {
                                'fields': (
                                    'author,summary,'
                                    'vcs(from_branch,to_branch),merge_commits,'
                                    'updated_at,'
                                    'checks(type,status,updated_at),labels,'
                                    'description'
                                ),
                            },
                        },
                        'method': 'get',
                        'url': (
                            'http://a.yandex-team.ru/api/v1/review-requests/2'
                        ),
                    },
                ],
                pull_request_date=THIRTY_DAYS_AGO - FIVE_SECONDS,
            ),
            id='outdated border arc pr',
        ),
        pytest.param(
            ArcParams(
                argv=[
                    '--provider',
                    'arcanum',
                    '--days',
                    '30',
                    '--pr',
                    'users/robot-stark/taxi/some_service/0',
                ],
                report_text=['It is not Pull Request'],
                arcadia_pr_calls=[],
            ),
            id='invalid arc pr',
        ),
        pytest.param(
            ArcParams(
                argv=[
                    '--provider',
                    'arcanum',
                    '--days',
                    '30',
                    '--pr',
                    'users/robot-stark/taxi/some_service/3/merge_head',
                ],
                report_text=[
                    'Pull Request last update: {}'.format(
                        (THIRTY_DAYS_AGO + FIVE_SECONDS).strftime(
                            PRINT_UPDATED_AT_FORMAT,
                        ),
                    ),
                ],
                arcadia_pr_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth valid token'},
                            'params': {
                                'fields': (
                                    'author,summary,'
                                    'vcs(from_branch,to_branch),merge_commits,'
                                    'updated_at,'
                                    'checks(type,status,updated_at),labels,'
                                    'description'
                                ),
                            },
                        },
                        'method': 'get',
                        'url': (
                            'http://a.yandex-team.ru/api/v1/review-requests/3'
                        ),
                    },
                ],
                pull_request_date=THIRTY_DAYS_AGO + FIVE_SECONDS,
            ),
            id='good border arc pr',
        ),
        pytest.param(
            ArcParams(
                argv=[
                    '--provider',
                    'arcanum',
                    '--days',
                    '30',
                    '--pr',
                    'users/robot-stark/taxi/some_service/1/head',
                ],
                report_text=[
                    'Pull Request last update: {}'.format(
                        TWO_DAYS_AGO.strftime(PRINT_UPDATED_AT_FORMAT),
                    ),
                ],
                arcadia_pr_calls=[
                    {
                        'kwargs': {
                            'headers': {'Authorization': 'OAuth valid token'},
                            'params': {
                                'fields': (
                                    'author,summary,'
                                    'vcs(from_branch,to_branch),merge_commits,'
                                    'updated_at,'
                                    'checks(type,status,updated_at),labels,'
                                    'description'
                                ),
                            },
                        },
                        'method': 'get',
                        'url': (
                            'http://a.yandex-team.ru/api/v1/review-requests/1'
                        ),
                    },
                ],
                pull_request_date=TWO_DAYS_AGO,
            ),
            id='good arc pr',
        ),
    ],
)
def test_old_arc_pr_check(
        teamcity_report_problems,
        params: ArcParams,
        capsys,
        patch_requests,
        monkeypatch,
        load_json,
):
    @patch_requests(arcadia_client.API_URL + 'v1/review-requests')
    def mock_arcadia_pr(method, url, **kwargs):
        assert params.pull_request_date is not None
        response = {
            'data': {
                'author': {'name': 'some author'},
                'merge_commits': [],
                'summary': 'some bug fix',
                'updated_at': params.pull_request_date.strftime(
                    PRINT_UPDATED_AT_FORMAT,
                ),
                'vcs': {},
                'checks': [],
                'labels': [],
            },
        }

        return patch_requests.response(status_code=200, json=response)

    monkeypatch.setenv('ARCADIA_TOKEN', 'valid token')

    if params.teamcity_report_problems:
        with pytest.raises(SystemExit) as excinfo:
            check_need_tests.main(params.argv)
        assert (1,) == excinfo.value.args
    else:
        check_need_tests.main(params.argv)

    captured = capsys.readouterr()
    outs = [out for out in captured.out.split('\n') if out]
    errors = [err for err in captured.err.split('\n') if err]

    assert params.teamcity_report_problems == teamcity_report_problems.calls
    # because of teamcity_report_problems also is in stdout
    for text in params.report_text:
        assert text in outs
    assert params.report_error_text == errors
    assert mock_arcadia_pr.calls == params.arcadia_pr_calls
