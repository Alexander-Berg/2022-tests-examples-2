from typing import NamedTuple
from typing import Optional
from typing import Sequence

import freezegun
import pytest

import run_buildtype_for_prs
import taxi_buildagent.clients.teamcity as teamcity_client
from tests.utils.examples import backend


SKIP_RUN_LABEL = 'test/should_skip'


class Params(NamedTuple):
    branch_template: str = '{number}/head'
    pull_requests: Sequence[dict] = ()
    fail_message: Optional[dict] = None
    arcadia_path: str = ''


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(pull_requests=[]), id='backend without pull-requests',
        ),
        pytest.param(
            Params(pull_requests=[{'branch': '1/head'}]),
            id='backend with one pull-request',
        ),
        pytest.param(
            Params(
                pull_requests=[
                    {
                        'number': 3,
                        'branch': '3/head',
                        'labels': ['deploy:unstable'],
                    },
                ],
            ),
            id='backend with labeled pull-request',
        ),
        pytest.param(
            Params(
                pull_requests=[
                    {'branch': '1/head'},
                    {'branch': '2/head', 'labels': ['deploy:unstable']},
                    {'branch': '3/head', 'labels': ['deploy:testing']},
                    {'branch': '4/head'},
                    {'branch': '5/head'},
                ],
            ),
            id='backend with several pull-request',
        ),
        pytest.param(
            Params(
                pull_requests=[
                    {'number': 1585, 'branch': 'pull/1585'},
                    {
                        'number': 503,
                        'branch': 'pull/503',
                        'labels': ['deploy:unstable'],
                    },
                    {
                        'number': 64,
                        'branch': 'pull/64',
                        'labels': ['deploy:testing', 'deploy:unstable'],
                    },
                    {'number': 7073, 'branch': 'pull/7073'},
                    {
                        'number': 3154,
                        'branch': 'pull/3154',
                        'labels': ['deploy:testing'],
                    },
                    {
                        'number': 79,
                        'branch': 'pull/79',
                        'labels': ['deploy:unstable'],
                    },
                    {
                        'number': 11182,
                        'branch': 'pull/11182',
                        'labels': ['deploy:testing'],
                    },
                ],
                branch_template='pull/{number}',
            ),
            id='backend with random ids pull-request',
        ),
        pytest.param(
            Params(
                pull_requests=[
                    {
                        'author': {'name': 'litvitskiy'},
                        'vcs': {
                            'from_branch': 'users/litvitskiy/f/persuggest',
                            'to_branch': 'trunk',
                        },
                        'id': '1772393',
                        'summary': 'Initial',
                        'checks': [],
                        'labels': [],
                    },
                    {
                        'author': {'name': 'rshahaev'},
                        'vcs': {
                            'from_branch': 'users/rshahaev/pd_log',
                            'to_branch': 'trunk',
                        },
                        'id': '1772354',
                        'summary': 'pd log',
                        'checks': [],
                        'labels': [{'name': 'taxi/deploy:testing'}],
                    },
                ],
                branch_template='users/robot-stark/taxi/backend/{number}/head',
                arcadia_path='taxi/backend',
            ),
            id='backend arcanum path',
        ),
        pytest.param(
            Params(
                pull_requests=[
                    {
                        'author': {'name': 'ilya-biyumen'},
                        'vcs': {
                            'from_branch': 'users/ilya-biyumen/942-unconfirm',
                            'to_branch': 'trunk',
                        },
                        'id': '1964950',
                        'summary': 'feat eats-proactive-support: add order',
                        'checks': [
                            {
                                'type': 'approved',
                                'status': 'pending',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'test-build-type',
                                'status': 'failure',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                        ],
                        'labels': [
                            {'name': 'taxi/deploy:testing'},
                            {'name': SKIP_RUN_LABEL},
                        ],
                    },
                    {
                        'id': '1955049',
                        'author': {'name': 'makarov-and'},
                        'vcs': {
                            'from_branch': 'users/makarov-and/f/EDA-915-pick',
                            'to_branch': 'trunk',
                        },
                        'summary': 'feat eats-tracking: BDU widgets',
                        'checks': [
                            {
                                'type': 'approved',
                                'status': 'pending',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'comment_issues_closed',
                                'status': 'failure',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'test-build-type',
                                'status': 'success',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                        ],
                        'labels': [],
                    },
                ],
                branch_template='users/robot-stark/taxi/backend/{number}/head',
                arcadia_path='taxi/backend',
            ),
            id='backend arcanum skip failed',
        ),
        pytest.param(
            Params(
                pull_requests=[
                    {
                        'author': {'name': 'bugaevskiy'},
                        'vcs': {
                            'from_branch': 'users/bugaevskiy/1',
                            'to_branch': 'trunk',
                        },
                        'id': '1234',
                        'summary': 'feat all: break stuff',
                        'checks': [
                            {
                                'type': 'approved',
                                'status': 'success',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'test-build-type',
                                'status': 'failure',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                        ],
                        'labels': [
                            {'name': 'taxi/deploy:testing'},
                            {'name': 'taxi/automerge-huge'},
                            {'name': SKIP_RUN_LABEL},
                        ],
                    },
                    {
                        'author': {'name': 'bugaevskiy'},
                        'vcs': {
                            'from_branch': 'users/bugaevskiy/2',
                            'to_branch': 'trunk',
                        },
                        'id': '1235',
                        'summary': 'feat all: tested today',
                        'checks': [
                            {
                                'type': 'approved',
                                'status': 'pending',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'test-build-type',
                                'status': 'success',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                        ],
                        'labels': [
                            {'name': 'taxi/automerge-huge'},
                            {'name': SKIP_RUN_LABEL},
                        ],
                    },
                    {
                        'author': {'name': 'bugaevskiy'},
                        'vcs': {
                            'from_branch': 'users/bugaevskiy/3',
                            'to_branch': 'trunk',
                        },
                        'id': '1236',
                        'summary': 'feat all: forgot to add automerge',
                        'checks': [
                            {
                                'type': 'approved',
                                'status': 'pending',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'test-build-type',
                                'status': 'success',
                                'updated_at': '2018-04-20 19:02:56.000001Z',
                            },
                        ],
                        'labels': [{'name': 'taxi/automerge-huge'}],
                    },
                    {
                        'author': {'name': 'bugaevskiy'},
                        'vcs': {
                            'from_branch': 'users/bugaevskiy/4',
                            'to_branch': 'trunk',
                        },
                        'id': '1237',
                        'summary': 'feat all: still running tests',
                        'checks': [
                            {
                                'type': 'approved',
                                'status': 'success',
                                'updated_at': '2018-04-23T14:20:56.000001Z',
                            },
                            {
                                'type': 'test-build-type',
                                'status': 'pending',
                                'updated_at': '2018-04-20T14:20:56.000001Z',
                            },
                        ],
                        'labels': [
                            {'name': 'taxi/automerge-huge'},
                            {'name': SKIP_RUN_LABEL},
                        ],
                    },
                ],
                branch_template='users/robot-stark/taxi/backend/{number}/head',
                arcadia_path='taxi/backend',
            ),
            id='backend arcanum automerge',
        ),
    ],
)
def test_run_tc_builds_for_pr(
        patch_requests,
        tmpdir,
        github,
        monkeypatch,
        teamcity_report_problems,
        params: Params,
):
    @patch_requests('https://teamcity.taxi.yandex-team.ru/app/rest/buildQueue')
    def build_type_trigger(method, url, **kwargs):
        return patch_requests.response(status_code=200)

    @patch_requests('http://a.yandex-team.ru/api/v1/review-requests')
    def arcanum_review_request(method, url, **kwargs):
        return patch_requests.response(
            json={'data': {'review_requests': params.pull_requests}},
        )

    repo = backend.init(tmpdir)
    if not params.arcadia_path:
        github_repo = github.init_repo(
            'taxi', 'backend', next(repo.remotes[0].urls),
        )
        for prq in params.pull_requests:
            github_repo.create_pr(repo, **prq)

    teamcity_token = 'secret_token'
    timeout = 15
    allow_redirects = True
    verify = False
    headers = {
        'Origin': 'https://teamcity.taxi.yandex-team.ru/',
        'Accept': 'application/json',
    }

    argv = ['--build-type-id', 'test-build-type']
    if params.arcadia_path:
        argv.extend(['--arcadia-path', params.arcadia_path])
    monkeypatch.setenv('ARCADIA_TOKEN', 'irrelevant token')
    monkeypatch.setenv('TEAMCITY_TOKEN', teamcity_token)
    monkeypatch.setenv('TEAMCITY_BRANCH_TEMPLATE', params.branch_template)

    run_buildtype_for_prs.main(argv)

    expected_trigger_calls = []
    for pull_req in params.pull_requests:
        if params.arcadia_path:
            number = pull_req['id']
            branch_name = params.branch_template.replace('{number}', number)
            labels = [label['name'] for label in pull_req['labels']]
        else:
            branch_name = pull_req['branch']
            labels = pull_req.get('labels', [])

        if SKIP_RUN_LABEL in labels:
            continue
        expected_trigger_calls.append(
            {
                'method': 'POST',
                'url': (
                    'https://teamcity.taxi.yandex-team.ru/app/rest/'
                    'buildQueue'
                ),
                'kwargs': {
                    'auth': teamcity_client.HTTPBearerAuth(teamcity_token),
                    'timeout': timeout,
                    'verify': verify,
                    'allow_redirects': allow_redirects,
                    'headers': headers,
                    'json': {
                        'triggeringOptions': {'queueAtTop': False},
                        'buildType': {'id': argv[1]},
                        'branchName': branch_name,
                    },
                },
            },
        )
    assert build_type_trigger.calls == expected_trigger_calls

    if params.arcadia_path:
        arcanum_calls = arcanum_review_request.calls
        for call in arcanum_calls:
            call.pop('kwargs')

        assert arcanum_calls == [
            {
                'method': 'get',
                'url': 'http://a.yandex-team.ru/api/v1/review-requests',
            },
        ]
