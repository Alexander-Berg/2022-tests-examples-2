import dataclasses
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence

import freezegun
import pytest

import arc_checkout
import run_release
from taxi_buildagent import debian_package
from taxi_buildagent import slack_tools
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia


BASE_CHANGELOG: str = 'base_changelog.txt'


@dataclasses.dataclass
class ArcadiaCommit:
    name: str
    data: Sequence[str]
    project_path: str = 'projects/basic-project'


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    exp_package_name: str = 'yandex-taxi-my-service'
    exp_version: str = '0.0.1'
    exp_release_ticket: Optional[str] = 'https://st.yandex-team.ru/TAXIREL-222'
    exp_changes: Sequence[str] = ()
    commits: Sequence[ArcadiaCommit] = ()
    tc_set_parameters_calls: Sequence[Dict[str, Any]] = ()
    tc_report_problems_calls: Sequence[Dict[str, Any]] = ()
    telegram_disabled: str = ''
    slack_disabled: str = ''
    telegram_message: str = ''
    slack_message: str = ''
    no_changes_enabled: str = ''
    st_create_ticket_calls: Sequence[dict] = ()
    created_comment: Optional[dict] = dataclasses.field(
        default_factory=lambda: {
            'text': (
                '====Для следующих тикетов не было обнаружено отчётов о '
                'тестировании:\n'
                'TIKET-123\n\n'
                '====Следующие тикеты находятся в статусе "Открыт":\n'
                'TIKET-123\n\n'
                '====Следующие тикеты не имеют исполнителя:\n'
                'TIKET-123'
            ),
        },
    )


@freezegun.freeze_time(
    '2020-09-01 20:59:59', tz_offset=3, ignore=['grpc._channel'],
)
@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(
            pytest_id='simple_case',
            exp_changes=[
                '* tester | PR merge',
                '* tester | feat driver-authorizer: oh...',
                '* tester | feat kek: kek',
                '* tester | feat ololo: ololo',
            ],
            st_create_ticket_calls=[
                {
                    'json': {
                        'assignee': None,
                        'components': [100, 42],
                        'description': (
                            'TIKET-123\n'
                            'tester | PR '
                            'merge(((https://a.yandex-team.ru/arc/commit/11 '
                            '11)))\n\n'
                            'Common changes:\n'
                            'https://st.yandex-team.ru/TICKET-9999\n'
                            'https://st.yandex-team.ru/TIKET-890'
                        ),
                        'followers': ['tester'],
                        'queue': 'TAXIREL',
                        'summary': 'my-service my-service 0.0.1',
                    },
                },
            ],
            commits=[
                ArcadiaCommit(
                    name='feat ololo: ololo\n\nIssue: TIKET-123',
                    data=[
                        'services/my-service/service.yaml',
                        'services/my-service/src/main.cpp',
                    ],
                ),
                ArcadiaCommit(
                    name='feat driver-authorizer: oh...\n\n'
                    'Relates: TICKET-9999',
                    data=['services/driver-authorizer/service.yaml'],
                ),
                ArcadiaCommit(
                    name=(
                        'feat kek: kek\nTests: Вроде потестил\n'
                        'Relates: TIKET-890'
                    ),
                    data=['services1.yaml'],
                ),
                ArcadiaCommit(
                    name='PR merge',
                    data=['services/my-service/debian/changelog'],
                ),
            ],
            tc_set_parameters_calls=[
                {'name': 'env.AFFECTED_USERS', 'value': 'tester'},
            ],
            telegram_message=(
                'New release started\n'
                'Ticket: [TAXIREL-222]'
                '(https://st.yandex-team.ru/TAXIREL-222)\n'
                'Service name: `my-service`\n'
                'Package: `yandex-taxi-my-service`\n'
                'Version: `0.0.1`\n\n'
                '@tg\\_tester'
            ),
            slack_message=(
                'New release started\n'
                'Ticket: <https://st.test.yandex-team.ru/TAXIREL-222|'
                'TAXIREL-222>\n'
                'Service name: `my-service`\n'
                'Package: `yandex-taxi-my-service`\n'
                'Version: `0.0.1`\n'
                '\ntester'
            ),
        ),
        Params(
            pytest_id='no_changes',
            st_create_ticket_calls=[],
            commits=[],
            exp_package_name='',
            exp_version='',
            exp_changes=[],
            tc_set_parameters_calls=[
                {
                    'name': 'env.BUILD_PROBLEM',
                    'value': 'No changes to release',
                },
            ],
            tc_report_problems_calls=[
                {'description': 'No changes to release', 'identity': None},
            ],
            telegram_message='',
            slack_message='',
            created_comment=None,
        ),
        Params(
            pytest_id='no_changes_with_enabled_flag',
            commits=[],
            tc_set_parameters_calls=[],
            no_changes_enabled='1',
            exp_version='0.0.0',
            exp_changes=['* Denis Teterin | Initial release'],
            created_comment=None,
        ),
        Params(
            pytest_id='dependant_project_case',
            exp_changes=[
                '* tester | included2_dependant_change',
                '* tester | included3_dependant_change',
                '* tester | included_dependant_change',
            ],
            st_create_ticket_calls=[
                {
                    'json': {
                        'assignee': None,
                        'components': [100, 42],
                        'description': (
                            'Common libraries changes:\n'
                            'tester '
                            '| included2_dependant_change(((https://'
                            'a.yandex-team.ru/arc/commit/11 11)))\n'
                            'tester '
                            '| included3_dependant_change((('
                            'https://a.yandex-team.ru/arc/commit/12 12)))\n'
                            'tester '
                            '| included_dependant_change(((https://'
                            'a.yandex-team.ru/arc/commit/8 8)))'
                        ),
                        'followers': ['tester'],
                        'queue': 'TAXIREL',
                        'summary': 'my-service my-service 0.0.1',
                    },
                },
            ],
            commits=[
                ArcadiaCommit(
                    name='included_dependant_change',
                    project_path='projects/other-proj',
                    data=['schemas/mongo/lavka_isr_invoices.yaml'],
                ),
                ArcadiaCommit(
                    name='excluded_dependant_change',
                    project_path='projects/other-proj',
                    data=['schemas/services/social/service.yaml'],
                ),
                ArcadiaCommit(
                    name='excluded2_dependant_change',
                    project_path='projects/other-proj',
                    data=['schemas/services/social/services.yaml'],
                ),
                ArcadiaCommit(
                    name='included2_dependant_change',
                    project_path='projects/other-proj',
                    data=[
                        'schemas/mongo/zendesk_messages.yaml',
                        'schemas/services/teamcity/client.yaml',
                        'schemas/stq/driver_set_remove_tag.yaml',
                    ],
                ),
                ArcadiaCommit(
                    name='included3_dependant_change',
                    project_path='projects/other-proj',
                    data=['ml/taxi_ml_cxx/objects.cpp'],
                ),
            ],
            created_comment=None,
            tc_set_parameters_calls=[
                {'name': 'env.AFFECTED_USERS', 'value': 'tester'},
            ],
            telegram_message=(
                'New release started\n'
                'Ticket: [TAXIREL-222]'
                '(https://st.yandex-team.ru/TAXIREL-222)\n'
                'Service name: `my-service`\n'
                'Package: `yandex-taxi-my-service`\n'
                'Version: `0.0.1`\n\n'
                '@tg\\_tester'
            ),
            slack_message=(
                'New release started\n'
                'Ticket: <https://st.test.yandex-team.ru/TAXIREL-222|'
                'TAXIREL-222>\n'
                'Service name: `my-service`\n'
                'Package: `yandex-taxi-my-service`\n'
                'Version: `0.0.1`\n'
                '\ntester'
            ),
        ),
    ],
)
def test_arc_release(
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
        staff_persons_mock,
):
    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    project_path = arcadia_path / 'projects' / 'basic-project'
    service_path = project_path / 'services' / 'my-service'
    changelog_path = service_path / 'debian' / 'changelog'

    monkeypatch.setenv('TELEGRAM_BOT_CHAT_ID', 'tchatid')
    monkeypatch.setenv('RELEASE_TICKET_SUMMARY', 'my-service')
    monkeypatch.setenv('TELEGRAM_DISABLED', params.telegram_disabled)
    monkeypatch.setenv('SLACK_DISABLED', params.slack_disabled)
    monkeypatch.setenv('ADD_FOLLOWERS', '1')
    monkeypatch.setenv('ARCADIA_TOKEN', 'cool-token')
    monkeypatch.setenv('NO_CHANGES_RELEASE_ENABLED', params.no_changes_enabled)

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        return ''

    @patch_requests(slack_tools.SLACK_POST_URL)
    def slack_send_message(method, url, **kwargs):
        return patch_requests.response(json={'ok': True}, content='ok')

    with arcadia_builder:
        arcadia.init_arcadia_basic_project(arcadia_builder)

    arc_checkout.main([str(arcadia_path), '--branch', 'trunk'])

    assert teamcity_report_problems.calls == []

    repo = arc_repo.Repo(arcadia_path, from_root=True)

    master_branch = (
        repo.stable_branch_prefix + 'projects/basic-project/my-service'
    )
    repo.checkout_new_branch(master_branch, 'trunk')
    changelog_path.parent.mkdir(exist_ok=True, parents=True)
    changelog_path.write_text(load(BASE_CHANGELOG))
    repo.add_paths_to_index([str(changelog_path)])
    repo.commit('release 0.0.0')
    repo.arc.push('--force', '--set-upstream', master_branch)

    with arcadia_builder:
        for commit in params.commits:
            arcadia.update_arcadia_project(
                arcadia_builder,
                {data: '' for data in commit.data},
                commit.name,
                project_path=commit.project_path,
            )

    repo.fetch_remote(master_branch)

    monkeypatch.chdir(project_path)
    repo.checkout(master_branch)

    run_release.main([])

    if changelog_path.exists():
        with changelog_path.open(encoding='utf-8') as fin:
            changelog = debian_package.parse_changelog(fin)
        assert changelog.package_name == params.exp_package_name
        assert changelog.version == params.exp_version
        assert sorted(changelog.changes) == list(params.exp_changes)
    else:
        assert params.exp_package_name == ''
        assert params.exp_version == ''
        assert list(params.exp_changes) == []

    assert ya_mock.calls == []
    assert teamcity_set_parameters.calls == list(
        params.tc_set_parameters_calls,
    )
    assert teamcity_report_problems.calls == list(
        params.tc_report_problems_calls,
    )

    if params.created_comment is None:
        assert startrek.create_comment.calls == []
    else:
        calls = startrek.create_comment.calls
        expected_calls = [{'json': params.created_comment}]
        assert calls == expected_calls

    assert startrek.create_ticket.calls == list(params.st_create_ticket_calls)

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
