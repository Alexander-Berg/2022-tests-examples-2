import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Sequence

import freezegun
import pytest

import arc_checkout
import run_arcadia_hotfix
from taxi_buildagent import agenda
from taxi_buildagent import slack_tools
from taxi_buildagent.clients import arcadia as arcadia_client
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia


HEADERS = {'Authorization': 'OAuth cool-token'}
REVIEWS_URL = 'http://a.yandex-team.ru/api/v1/review-requests'


def get_pr_call(pr_number: int) -> Dict[str, Any]:
    return {
        'kwargs': {
            'headers': HEADERS,
            'params': {
                'fields': (
                    'author,summary,'
                    'vcs(from_branch,to_branch),merge_commits,'
                    'updated_at,checks(type,status,updated_at)'
                    ',labels,description'
                ),
            },
        },
        'method': 'get',
        'url': f'{REVIEWS_URL}/{pr_number}',
    }


def close_pr_call(pr_number: int) -> Dict[str, Any]:
    return {
        'kwargs': {'headers': HEADERS, 'json': {'state': 'closed'}},
        'method': 'put',
        'url': f'{REVIEWS_URL}/{pr_number}/state',
    }


def comment_pr_call(pr_number):
    return {
        'kwargs': {
            'headers': HEADERS,
            'json': {
                'content': (
                    'Включен в релиз '
                    'https://st.test.yandex-team.ru/TAXIREL-123321'
                ),
            },
        },
        'method': 'post',
        'url': f'{REVIEWS_URL}/{pr_number}/comments',
    }


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    pr_numbers: Sequence[int] = (1, 2)
    ya_calls_args: Sequence[List[str]] = ()
    tc_set_parameters_calls: Sequence[Dict[str, Any]] = ()
    st_update_ticket_calls: Sequence[Dict[str, Any]] = (
        {
            'json': {
                'assignee': 'release-starter',
                'description': (
                    'some\ntext\n\n0.0.0hotfix1:\n'
                    'tester | feat basic-project: add feature\n'
                    'tester | feat basic-project: fix feature'
                ),
                'followers': {'add': ['tester']},
                'summary': 'summary, 0.0.0hotfix1',
            },
            'ticket': 'TAXIREL-123321',
        },
    )
    st_create_comment_calls: Sequence[Dict[str, Any]] = ()
    tc_report_problems_calls: Sequence[Dict[str, Any]] = ()
    arcadia_pr_calls: Sequence[Dict[str, Any]] = (
        get_pr_call(1),
        get_pr_call(2),
    )
    base_changelog: str = 'base_changelog.txt'
    exp_changelog: str = 'exp_changelog.txt'
    exp_feature: str = 'fixed feature code'
    commits_after_hotfix: Sequence[str] = (
        'edit changelog 0.0.0hotfix1',
        'feat basic-project: fix feature',
        'feat basic-project: add feature',
    )
    pull_request_path: str = 'basic-project'
    telegram_disabled: str = ''
    slack_disabled: str = ''
    telegram_message: str = ''
    slack_message: str = ''


@freezegun.freeze_time(
    '2020-09-01 20:59:59', tz_offset=3, ignore=['grpc._channel'],
)
@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(
            pytest_id='simple_case', telegram_disabled='1', slack_disabled='1',
        ),
        Params(
            pytest_id='simple_revision_case',
            st_update_ticket_calls=[
                {
                    'json': {
                        'assignee': 'release-starter',
                        'description': (
                            'some\ntext\n\n7270531hotfix1:\n'
                            'tester | feat basic-project: add feature\n'
                            'tester | feat basic-project: fix feature'
                        ),
                        'followers': {'add': ['tester']},
                        'summary': 'summary, 7270531hotfix1',
                    },
                    'ticket': 'TAXIREL-123321',
                },
            ],
            base_changelog='revision_base_changelog.txt',
            exp_changelog='revision_exp_changelog.txt',
            commits_after_hotfix=(
                'edit changelog 7270531hotfix1',
                'feat basic-project: fix feature',
                'feat basic-project: add feature',
            ),
            telegram_disabled='1',
            slack_disabled='1',
        ),
        Params(
            pytest_id='unmerged_case',
            pr_numbers=[3],
            st_update_ticket_calls=[
                {
                    'json': {
                        'assignee': 'release-starter',
                        'description': (
                            'some\ntext\n\n0.0.0hotfix1:\n' 'TAXITOOLS-3112'
                        ),
                        'followers': {'add': ['buildfarm']},
                        'summary': 'summary, 0.0.0hotfix1',
                    },
                    'ticket': 'TAXIREL-123321',
                },
            ],
            st_create_comment_calls=[
                {
                    'json': {
                        'text': (
                            '====Для следующих тикетов не было '
                            'обнаружено отчётов о тестировании:\n'
                            'TAXITOOLS-3112\n\n'
                            '====Следующие тикеты не имеют '
                            'исполнителя:\n'
                            'TAXITOOLS-3112'
                        ),
                    },
                },
                {
                    'json': {
                        'text': (
                            'Следующие пулл-реквесты были включены в '
                            'хотфикс 0.0.0hotfix1, но не были '
                            'замержены в trunk:\n'
                            'https://a.yandex-team.ru/review/3'
                        ),
                    },
                },
            ],
            arcadia_pr_calls=[
                get_pr_call(3),
                close_pr_call(3),
                comment_pr_call(3),
            ],
            exp_changelog='unmerged_exp_changelog.txt',
            exp_feature='hot fixed feature code',
            commits_after_hotfix=(
                'edit changelog 0.0.0hotfix1',
                'feat hotfix: support unmerged prs',
            ),
            telegram_disabled='1',
            slack_disabled='1',
        ),
        Params(
            pytest_id='simple_case_messangers_reports',
            st_update_ticket_calls=[
                {
                    'json': {
                        'assignee': 'release-starter',
                        'description': (
                            'some\ntext\n\n7270531hotfix1:\n'
                            'tester | feat basic-project: add feature\n'
                            'tester | feat basic-project: fix feature'
                        ),
                        'followers': {'add': ['tester']},
                        'summary': 'summary, 7270531hotfix1',
                    },
                    'ticket': 'TAXIREL-123321',
                },
            ],
            base_changelog='revision_base_changelog.txt',
            exp_changelog='revision_exp_changelog.txt',
            commits_after_hotfix=(
                'edit changelog 7270531hotfix1',
                'feat basic-project: fix feature',
                'feat basic-project: add feature',
            ),
            telegram_message=(
                'New hotfix started\n'
                'Ticket: [TAXIREL-123321]'
                '(https://st.test.yandex-team.ru/TAXIREL-123321)\n'
                'Package: `yandex-taxi-my-service`\n'
                'Version: `7270531hotfix1`\n'
                '\ntester'
            ),
            slack_message=(
                'New hotfix started\n'
                'Ticket: <https://st.test.yandex-team.ru/TAXIREL-123321|'
                'TAXIREL-123321>\n'
                'Package: `yandex-taxi-my-service`\n'
                'Version: `7270531hotfix1`\n'
                '\ntester'
            ),
        ),
        Params(
            pytest_id='other_proj_case',
            pull_request_path='other-proj/schemas/mongo',
            st_update_ticket_calls=[
                {
                    'json': {
                        'assignee': 'release-starter',
                        'description': (
                            'some\ntext\n\n7270531hotfix1:\n'
                            'tester | feat basic-project: add feature\n'
                            'tester | feat basic-project: fix feature'
                        ),
                        'followers': {'add': ['tester']},
                        'summary': 'summary, 7270531hotfix1',
                    },
                    'ticket': 'TAXIREL-123321',
                },
            ],
            base_changelog='revision_base_changelog.txt',
            exp_changelog='revision_exp_changelog.txt',
            commits_after_hotfix=(
                'edit changelog 7270531hotfix1',
                'feat basic-project: fix feature',
                'feat basic-project: add feature',
            ),
            telegram_disabled='1',
            slack_disabled='1',
        ),
    ],
)
def test_arc_hotfix(
        params: Params,
        commands_mock,
        monkeypatch,
        tmp_path,
        load,
        load_json,
        startrek,
        teamcity_set_parameters,
        teamcity_report_problems,
        patch_requests,
        arcadia_builder,
        telegram,
):
    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    projects_path = arcadia_path / 'projects'
    project_path = projects_path / 'basic-project'
    service_path = project_path  # mono
    changelog_path = service_path / 'debian' / 'changelog'
    feature_path = service_path / 'feature1'

    startrek.ticket_status = 'testing'
    monkeypatch.setattr('taxi_buildagent.tickets.USER_NAME', 'release-starter')
    monkeypatch.setenv('TELEGRAM_BOT_CHAT_ID', 'tchatid')
    monkeypatch.setenv('RELEASE_TICKET_SUMMARY', 'my-service')
    monkeypatch.setenv('TELEGRAM_DISABLED', params.telegram_disabled)
    monkeypatch.setenv('SLACK_DISABLED', params.slack_disabled)
    monkeypatch.setenv('ADD_FOLLOWERS', '1')
    monkeypatch.setenv('ARCADIA_TOKEN', 'cool-token')

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        command = args[2]
        if command == 'create':
            return '{"id":12345}'
        return ''

    @patch_requests(arcadia_client.API_URL + 'v1/review-requests')
    def mock_arcadia_pr(method, url, **kwargs):
        if method == 'get':
            pr_number = url.rsplit('/', maxsplit=1)[-1]
            return patch_requests.response(
                status_code=200, json=load_json(f'pr_{pr_number}.json'),
            )
        return patch_requests.response(status_code=200, json={})

    # sorting by date doesn't work in tests, reversing gives expected result
    monkeypatch.setattr(agenda, 'sort_commits', reversed)

    @patch_requests(slack_tools.SLACK_POST_URL)
    def slack_send_message(method, url, **kwargs):
        return patch_requests.response(json={'ok': True}, content='ok')

    with arcadia_builder:
        arcadia.init_arcadia_basic_project(arcadia_builder)

    arc_checkout.main([str(arcadia_path), '--branch', 'trunk'])
    assert teamcity_report_problems.calls == []

    repo = arc_repo.Repo(arcadia_path, from_root=True)

    master_branch = repo.stable_branch_prefix + 'projects/basic-project'
    repo.checkout_new_branch(master_branch, 'r2')
    changelog_path.parent.mkdir(exist_ok=True, parents=True)
    changelog_path.write_text(load(params.base_changelog))
    repo.add_paths_to_index([str(changelog_path)])
    repo.commit('release 0.0.0')
    repo.arc.push('--force', '--set-upstream', master_branch)

    release_branch = 'releases/tplatform/projects/basic-project/0.0.0'
    repo.checkout_new_branch(release_branch, master_branch)
    repo.arc.push('--force', '--set-upstream', release_branch)

    pr_branch = 'users/sanyash/feature/hotfix_unmerged_prs'
    repo.checkout_new_branch(pr_branch, master_branch)

    file_dir = projects_path / params.pull_request_path
    file_dir.mkdir(parents=True, exist_ok=True)
    file_path = file_dir / 'feature1'
    file_path.write_text('hot fixed feature code')
    repo.add_paths_to_index([str(file_path)])
    repo.commit('hotfix')
    repo.arc.push('--force', '--set-upstream', pr_branch)

    # FIXME(TAXITOOLS-3888): shouldn't be a special case for monoprojects
    monkeypatch.setenv('MASTER_BRANCH', master_branch)

    repo.fetch_remote(master_branch)
    before_hotfix = repo.get_commit(repo.REMOTE_PREFIX + master_branch)

    monkeypatch.chdir(project_path)
    repo.checkout(master_branch)
    run_arcadia_hotfix.main(list(map(str, params.pr_numbers)))
    repo.checkout(master_branch)

    assert [call['args'] for call in ya_mock.calls] == list(
        params.ya_calls_args,
    )
    assert teamcity_set_parameters.calls == list(
        params.tc_set_parameters_calls,
    )
    assert teamcity_report_problems.calls == list(
        params.tc_report_problems_calls,
    )
    assert startrek.update_ticket.calls == list(params.st_update_ticket_calls)
    assert startrek.create_comment.calls == list(
        params.st_create_comment_calls,
    )
    assert mock_arcadia_pr.calls == list(params.arcadia_pr_calls)
    assert changelog_path.read_text() == load(params.exp_changelog)
    assert feature_path.read_text() == params.exp_feature

    repo.fetch_remote(master_branch)
    after_hotfix = repo.get_commit(repo.REMOTE_PREFIX + master_branch)
    commits = repo.get_commits_between_branches(before_hotfix, after_hotfix)
    assert [commit.subject for commit in commits] == list(
        params.commits_after_hotfix,
    )

    calls = telegram.calls
    if calls:
        assert calls == [
            {
                'chat_id': 'tchatid',
                'disable_notification': False,
                'parse_mode': 'Markdown',
                'text': params.telegram_message,
                'disable_web_page_preview': True,
            },
        ]

    calls = slack_send_message.calls
    if len(calls) == 1:
        assert calls[0]['method'] == 'POST'
        blocks = calls[0]['kwargs']['json']['attachments'][0]['blocks']
        slack_message = blocks[0]['fields'][0]['text']
        assert slack_message == params.slack_message
    elif len(calls) > 1:
        assert False, 'Should not be more than one slack post messages'
