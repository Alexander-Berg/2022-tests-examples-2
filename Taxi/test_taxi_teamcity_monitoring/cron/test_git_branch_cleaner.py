from typing import Dict
from typing import List
from typing import NamedTuple

from aiohttp import web
import pytest

from taxi_teamcity_monitoring.crontasks.git_branch_cleaner import (
    run_git_branch_cleaner,
)
from taxi_teamcity_monitoring.generated.cron import run_cron


class Params(NamedTuple):
    all_branches: List[Dict]
    all_pull_requests: List[Dict]
    expected_github_calls: List[Dict]
    logger_error_list: List[str] = []


_ALL_PULL_REQUESTS_MOCK = [
    {
        'url': 'pr-url',
        'html_url': 'html-pr-url',
        'number': 15,
        'state': 'closed',
        'head': {'ref': 'feature/123-pr', 'label': 'some-user:feature/123-pr'},
        'base': {'ref': 'develop', 'label': 'taxi:develop'},
    },
]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                all_branches=[
                    {'name': 'some-branch-1'},
                    {'name': 'develop'},
                    {'name': 'feature/123-pr'},
                    {'name': 'masters/nice-service'},
                    {'name': 'master/yet-another-branch'},
                    {'name': 'develop/my'},
                ],
                all_pull_requests=_ALL_PULL_REQUESTS_MOCK,
                expected_github_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches?protected=false',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls?state=open',
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/taxi/some_repo/git/refs/heads/'
                            'some-branch-1'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/taxi/some_repo/git/refs/heads/'
                            'master/yet-another-branch'
                        ),
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/taxi/some_repo/git/refs/heads/' 'develop/my'
                        ),
                    },
                ],
            ),
            id='common',
        ),
        pytest.param(
            Params(
                all_branches=[
                    {'name': 'develop'},
                    {'name': 'feature/123-pr'},
                    {'name': 'masters/nice-service'},
                    {'name': 'master'},
                ],
                all_pull_requests=_ALL_PULL_REQUESTS_MOCK,
                expected_github_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches?protected=false',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls?state=open',
                    },
                ],
            ),
            id='without branches for delete',
        ),
        pytest.param(
            Params(
                all_branches=[
                    {'name': 'develop'},
                    {'name': 'feature/123-pr'},
                    {'name': 'masters/nice-service'},
                    {'name': 'master'},
                    {'name': 'failed-branch'},
                ],
                all_pull_requests=_ALL_PULL_REQUESTS_MOCK,
                expected_github_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches?protected=false',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls?state=open',
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/taxi/some_repo/git/refs/heads/'
                            'failed-branch'
                        ),
                    },
                ],
                logger_error_list=[
                    'Cannot delete branch: github response, status: 422, '
                    'body: '
                    'GithubError(message=\'Some message\', '
                    'documentation_url=\'documentation_url\', '
                    'url=None, status=None, '
                    'errors=None)',
                ],
            ),
            id='cannot delete branch',
        ),
        pytest.param(
            Params(
                all_branches=[
                    {'name': 'develop'},
                    {'name': 'feature/123-pr'},
                    {'name': 'masters/nice-service'},
                    {'name': 'master'},
                    {'name': 'no-access'},
                ],
                all_pull_requests=_ALL_PULL_REQUESTS_MOCK,
                expected_github_calls=[
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/branches?protected=false',
                    },
                    {
                        'method': 'GET',
                        'url': 'repos/taxi/some_repo/pulls?state=open',
                    },
                    {
                        'method': 'DELETE',
                        'url': (
                            'repos/taxi/some_repo/git/refs/heads/' 'no-access'
                        ),
                    },
                ],
                logger_error_list=[
                    'Cannot delete branch: github response, status: 404, '
                    'body: '
                    'GithubError(message=\'Some message\', '
                    'documentation_url=\'documentation_url\', '
                    'url=None, status=None, '
                    'errors=None)',
                ],
            ),
            id='cannot delete branch no-access',
        ),
    ],
)
@pytest.mark.config(
    TEAMCITY_MONITORING_GIT_BRANCH_CLEANER_ENABLED=True,
    TEAMCITY_MONITORING_GIT_BRANCH_CLEANER_REPOS=[
        {'organization': 'taxi', 'repo': 'some_repo'},
    ],
    TEAMCITY_MONITORING_GIT_BRANCH_CLEANER_SKIP_LIST=[
        '^master$',
        '^masters/',
        '^develop$',
        '^gh-pages$',
    ],
)
def test_git_branch_cleaner(monkeypatch, mock_github, params):
    @mock_github('/api/v3/repos/', prefix=True)
    async def github_request(request):
        error_data = {
            'message': 'Some message',
            'documentation_url': 'documentation_url',
        }
        if request.path.endswith('/branches'):
            return web.json_response(params.all_branches)
        if request.path.endswith('/pulls'):
            return web.json_response(params.all_pull_requests)
        if 'failed-branch' in request.path:
            return web.json_response(status=422, data=error_data)
        if 'no-access' in request.path:
            return web.json_response(status=404, data=error_data)
        if '/git/refs/heads/' in request.path:
            return web.json_response(status=204)

    _logger_error_messages = []
    original_logger_error = run_git_branch_cleaner.logger.error

    def _wrapper_logger_error(*args, **kwargs):
        log_str = args[0]
        output_string = log_str % args[1:]
        _logger_error_messages.append(output_string)
        return original_logger_error(*args, **kwargs)

    monkeypatch.setattr(
        'taxi_teamcity_monitoring.crontasks.'
        'git_branch_cleaner.run_git_branch_cleaner.logger.error',
        _wrapper_logger_error,
    )

    run_cron.main(
        [
            'taxi_teamcity_monitoring.crontasks.'
            'git_branch_cleaner.run_git_branch_cleaner',
            '-t',
            '0',
        ],
    )

    assert github_request.times_called == len(params.expected_github_calls)
    i = 0
    while github_request.has_calls:
        gh_req = github_request.next_call()['request']
        assert gh_req.method == params.expected_github_calls[i]['method']
        short_url = str(gh_req.url).split('/', maxsplit=6)[6]
        assert short_url == params.expected_github_calls[i]['url']
        i += 1
    assert _logger_error_messages == params.logger_error_list
