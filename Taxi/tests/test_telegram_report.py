import typing

import git
import pytest

from taxi_buildagent import report_utils
from taxi_buildagent import slack_tools
from taxi_buildagent.clients import staff
import telegram_report
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import dmp
from tests.utils.examples import uservices

SLACK_POST_URL = 'https://slack.com/api/chat.postMessage'


class Params(typing.NamedTuple):
    init_repo: typing.Callable[[str], git.Repo]
    branch: str
    chat_id: typing.Optional[str]
    build_type: str
    build_id: str
    build_problem: typing.Optional[str] = None
    conductor_ticket: typing.Optional[str] = None
    nanny_deploy_link: typing.Optional[str] = None
    users: typing.Optional[str] = None
    staff_calls: typing.Sequence[str] = ()
    telegram_messages: typing.Sequence[str] = ()
    args: typing.List[str] = []
    teamcity_status_response: typing.Optional[bytes] = None
    build_status: typing.Optional[str] = None
    slack_channel: str = ''
    slack_message: typing.Optional[str] = None
    slack_color: str = slack_tools.COLOR_GOOD
    disable_telegram: bool = False
    extra_environment: typing.Dict[str, str] = {}


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                chat_id='1234',
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
                staff_calls=['alberist', 'vasya'],
                telegram_messages=[
                    'backend [Release]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321)'
                    ' created\n'
                    '[Ticket](c.ru/1234)\n\n'
                    '@tg\\_alberist, @tg\\_vasya',
                ],
            ),
            id='backend release',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                chat_id='1234',
                build_type='custom-unstable',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
                staff_calls=['alberist', 'vasya'],
                telegram_messages=[
                    'backend [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321)'
                    ' (unstable) created\n'
                    '[Ticket](c.ru/1234)\n\n'
                    '@tg\\_alberist, @tg\\_vasya',
                ],
            ),
            id='backend custom',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                chat_id=None,
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
            ),
            id='backend release report disabled',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                chat_id='',
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
            ),
            id='backend release report disabled2',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                chat_id='3333',
                build_type='release',
                build_id='222',
                conductor_ticket='http://1234',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Release antifraud]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=222)'
                    ' created\n'
                    '[Ticket](http://1234)\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='backend-cpp antifraud release',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                chat_id='3333',
                build_type='custom-testing',
                build_id='222',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Custom taxi-adjust]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=222)'
                    ' (testing) created\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='backend-py3 adjust custom no ticket',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='release',
                build_id='312',
                conductor_ticket='http://2222/',
                telegram_messages=[
                    'backend [Release driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312)'
                    ' created\n'
                    '[Ticket](http://2222/)',
                ],
            ),
            id='uservices driver-authorizer release no users',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='release',
                build_id='312',
                build_problem='failed to build',
                conductor_ticket='http://2222/',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Release driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) FAILED:\n'
                    'failed to build\n'
                    '[Ticket](http://2222/)\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='uservices driver-authorizer release fail',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                chat_id='777',
                build_type='release',
                build_id='312',
                build_problem='            ',
                conductor_ticket='http://2222/',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Release pilorama]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312)'
                    ' created\n'
                    '[Ticket](http://2222/)\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='uservices pilorama release no fail',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_problem='merge failed',
                conductor_ticket='http://2222/',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Custom driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) (unstable) FAILED:\n'
                    'merge failed\n'
                    '[Ticket](http://2222/)\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='uservices driver-authorizer custom fail',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                args=['--report-only-failed'],
                teamcity_status_response=b'FAILURE',
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_problem='merge failed',
                conductor_ticket='http://2222/',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Custom driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) (unstable) FAILED:\n'
                    'merge failed\n'
                    '[Ticket](http://2222/)\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='uservices telegram report with failed',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                args=['--report-only-failed', '--triggered-user', 'oyaso'],
                teamcity_status_response=b'FAILURE',
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_problem='merge failed',
                conductor_ticket='http://2222/',
                users='oyaso',
                staff_calls=['oyaso'],
                telegram_messages=[
                    'backend [Custom driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) (unstable) FAILED:\n'
                    'merge failed\n'
                    '[Ticket](http://2222/)\n\n'
                    '@tg\\_oyaso',
                ],
            ),
            id='uservices telegram report triggered users',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                args=['--report-only-failed', '--triggered-user', 'n/a'],
                teamcity_status_response=b'FAILURE',
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_problem='merge failed',
                conductor_ticket='http://2222/',
                users='oyaso',
                staff_calls=[],
                telegram_messages=[],
            ),
            id='uservices telegram report with n/a user',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                args=['--report-only-failed'],
                teamcity_status_response=b'FAILURE',
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_status='SUCCESS',
            ),
            id='uservices telegram report if success build but failure status',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                chat_id='1234',
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                nanny_deploy_link='n.ya.ru/deploy/9876',
                users='alberist vasya',
                staff_calls=['alberist', 'vasya'],
                telegram_messages=[
                    'backend [Release]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321)'
                    ' created\n'
                    '[Ticket](c.ru/1234) | [Deploy](n.ya.ru/deploy/9876)\n\n'
                    '@tg\\_alberist, @tg\\_vasya',
                ],
                slack_channel='some-channel',
                slack_message=(
                    'backend <https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321|Release> created\n'
                    '<c.ru/1234|Ticket> | <n.ya.ru/deploy/9876|Deploy>\n\n'
                    '@alberist, @vasya'
                ),
                slack_color=slack_tools.COLOR_GOOD,
            ),
            id='slack and telegram',
        ),
        pytest.param(
            Params(
                args=[],
                init_repo=backend.init,
                branch='master',
                chat_id='1234',
                build_problem='Build problem',
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
                staff_calls=['alberist', 'vasya', 'rumkex'],
                telegram_messages=[
                    'backend [Release]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321) FAILED:\n'
                    'Build problem\n'
                    'PRs require attention:\n'
                    '@tg\\_rumkex [#1](http://my-pr/1) - something\n'
                    '@tg\\_rumkex [#1](http://my-pr/1) - PR conflict '
                    '[#2](http://my-pr/2) @tg\\_alberist\n'
                    '[Ticket](c.ru/1234)\n\n'
                    '@tg\\_alberist, @tg\\_vasya',
                ],
                slack_channel='some-channel',
                slack_message=(
                    'backend '
                    '<https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321|Release> FAILED:\n'
                    'Build problem\n'
                    'PRs require attention:\n'
                    '@rumkex <http://my-pr/1|#1> - something\n'
                    '@rumkex <http://my-pr/1|#1> - PR conflict '
                    '<http://my-pr/2|#2> @alberist\n'
                    '<c.ru/1234|Ticket>\n\n'
                    '@alberist, @vasya'
                ),
                slack_color=slack_tools.COLOR_DANGER,
                extra_environment={
                    'CUSTOM_BUILD_REPORT': report_utils.dump_pr_reports(
                        [
                            report_utils.PullRequestReport(
                                pull_request=report_utils.PullRequest(
                                    1,
                                    'http://my-pr/1',
                                    'rumkex',
                                    None,
                                    None,
                                    None,
                                ),
                                reason='something',
                                category=report_utils.CATEGORY_EXCLUDED_PR,
                            ),
                            report_utils.PullRequestReport(
                                pull_request=report_utils.PullRequest(
                                    1,
                                    'http://my-pr/1',
                                    'rumkex',
                                    None,
                                    None,
                                    None,
                                ),
                                reason='PR conflict',
                                category=report_utils.CATEGORY_MERGE_CONFLICT,
                                other_pr=report_utils.PullRequest(
                                    url='http://my-pr/2',
                                    number=2,
                                    staff_user='alberist',
                                    title=None,
                                    labels=None,
                                    from_branch=None,
                                ),
                            ),
                        ],
                    ),
                },
            ),
            id='slack and telegram with default envvars',
        ),
        pytest.param(
            Params(
                args=[
                    '--pr-reports',
                    'CUSTOM_REPORT_VAR',
                    '--pr-reports',
                    'EXTRA_REPORT_VAR',
                    '--build-problem-from',
                    'BUILD_PROBLEM_2',
                ],
                init_repo=backend.init,
                branch='master',
                chat_id='1234',
                build_problem='Build problem',
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
                staff_calls=['alberist', 'vasya', 'rumkex'],
                telegram_messages=[
                    'backend [Release]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321) FAILED:\n'
                    'Build problem\n'
                    'Other source: another build problem\n'
                    'PRs require attention:\n'
                    '@tg\\_rumkex [#1](http://my-pr/1) - something\n'
                    '@tg\\_rumkex [#1](http://my-pr/1) - PR conflict '
                    '[#2](http://my-pr/2) @tg\\_alberist\n'
                    '@tg\\_rumkex [#3](http://my-pr/3) - PR conflict\n'
                    '[Ticket](c.ru/1234)\n\n'
                    '@tg\\_alberist, @tg\\_vasya',
                ],
                slack_channel='some-channel',
                slack_message=(
                    'backend '
                    '<https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=4321|Release> FAILED:\n'
                    'Build problem\n'
                    'Other source: another build problem\n'
                    'PRs require attention:\n'
                    '@rumkex <http://my-pr/1|#1> - something\n'
                    '@rumkex <http://my-pr/1|#1> - PR conflict '
                    '<http://my-pr/2|#2> @alberist\n'
                    '@rumkex <http://my-pr/3|#3> - PR conflict\n'
                    '<c.ru/1234|Ticket>\n\n'
                    '@alberist, @vasya'
                ),
                slack_color=slack_tools.COLOR_DANGER,
                extra_environment={
                    'CUSTOM_REPORT_VAR': report_utils.dump_pr_reports(
                        [
                            report_utils.PullRequestReport(
                                pull_request=report_utils.PullRequest(
                                    1,
                                    'http://my-pr/1',
                                    'rumkex',
                                    None,
                                    None,
                                    None,
                                ),
                                reason='something',
                                category=report_utils.CATEGORY_EXCLUDED_PR,
                            ),
                            report_utils.PullRequestReport(
                                pull_request=report_utils.PullRequest(
                                    1,
                                    'http://my-pr/1',
                                    'rumkex',
                                    None,
                                    None,
                                    None,
                                ),
                                reason='PR conflict',
                                category=report_utils.CATEGORY_MERGE_CONFLICT,
                                other_pr=report_utils.PullRequest(
                                    url='http://my-pr/2',
                                    number=2,
                                    staff_user='alberist',
                                    title=None,
                                    labels=None,
                                    from_branch=None,
                                ),
                            ),
                        ],
                    ),
                    'EXTRA_REPORT_VAR': report_utils.dump_pr_reports(
                        [
                            report_utils.PullRequestReport(
                                pull_request=report_utils.PullRequest(
                                    3,
                                    'http://my-pr/3',
                                    'rumkex',
                                    None,
                                    None,
                                    None,
                                ),
                                reason='PR conflict',
                                category=report_utils.CATEGORY_MERGE_CONFLICT,
                            ),
                        ],
                    ),
                    'BUILD_PROBLEM_2': 'Other source: another build problem',
                },
            ),
            id='slack and telegram with custom reports',
        ),
        pytest.param(
            Params(
                args=['--disable-telegram'],
                init_repo=backend.init,
                branch='master',
                chat_id='1234',
                build_type='release',
                build_id='4321',
                conductor_ticket='c.ru/1234',
                users='alberist vasya',
                staff_calls=['alberist', 'vasya'],
                disable_telegram=True,
                slack_channel='some-channel',
                slack_message=(
                    'backend '
                    '<https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=4321|Release> created\n'
                    '<c.ru/1234|Ticket>\n\n'
                    '@alberist, @vasya'
                ),
            ),
            id='disable telegram',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                args=['--report-only-failed'],
                teamcity_status_response=b'FAILURE',
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_problem='merge failed',
                conductor_ticket='http://2222/',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Custom driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) (unstable) FAILED:\n'
                    'merge failed\n'
                    '[Ticket](http://2222/)\n\n'
                    '@tg\\_alberist',
                ],
                slack_channel='some-channel',
                slack_message=(
                    'backend '
                    '<https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312|Custom driver-authorizer>'
                    ' (unstable) FAILED:\n'
                    'merge failed\n'
                    '<http://2222/|Ticket>\n\n'
                    '@alberist'
                ),
                slack_color=slack_tools.COLOR_DANGER,
            ),
            id='uservices telegram and slack report with failed',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                args=['--report-only-failed'],
                teamcity_status_response=b'SUCCESS',
                branch='masters/driver-authorizer',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                users='alberist',
                staff_calls=['alberist', 'rumkex'],
                telegram_messages=[
                    'backend [Custom driver-authorizer]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) (unstable) created\n'
                    'PRs require attention:\n'
                    '@tg\\_rumkex [#1](http://my-pr/1) - something\n\n'
                    '@tg\\_alberist',
                ],
                slack_channel='some-channel',
                slack_message=(
                    'backend '
                    '<https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312|Custom driver-authorizer>'
                    ' (unstable) created\n'
                    'PRs require attention:\n'
                    '@rumkex <http://my-pr/1|#1> - something\n\n'
                    '@alberist'
                ),
                extra_environment={
                    'CUSTOM_BUILD_REPORT': report_utils.dump_pr_reports(
                        [
                            report_utils.PullRequestReport(
                                pull_request=report_utils.PullRequest(
                                    1,
                                    'http://my-pr/1',
                                    'rumkex',
                                    None,
                                    None,
                                    None,
                                ),
                                reason='something',
                                category=report_utils.CATEGORY_EXCLUDED_PR,
                            ),
                        ],
                    ),
                },
                slack_color=slack_tools.COLOR_GOOD,
            ),
            id='uservices telegram and slack report with pr warnings',
        ),
        pytest.param(
            Params(
                init_repo=dmp.init,
                branch='masters/ad_etl',
                chat_id='777',
                build_type='custom-unstable',
                build_id='312',
                build_problem='merge failed',
                users='alberist',
                staff_calls=['alberist'],
                telegram_messages=[
                    'backend [Custom ad_etl]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=312) (unstable) FAILED:\n'
                    'merge failed\n\n'
                    '@tg\\_alberist',
                ],
            ),
            id='branch_name_with_underlining',
        ),
    ],
)
def test_telegram_report(
        tmpdir,
        monkeypatch,
        github,
        staff_persons_mock,
        telegram,
        patch_requests,
        params: Params,
):
    if params.chat_id is not None:
        monkeypatch.setenv('REPORT_CHAT_ID', params.chat_id)
    monkeypatch.setenv('TEAMCITY_TOKEN', 'secret_token')
    monkeypatch.setenv('TEAMCITY_BUILD_TYPE', params.build_type)
    monkeypatch.setenv('BUILD_ID', params.build_id)
    if params.build_problem is not None:
        monkeypatch.setenv('BUILD_PROBLEM', params.build_problem)
    if params.conductor_ticket is not None:
        monkeypatch.setenv('CONDUCTOR_TICKET', params.conductor_ticket)
    if params.nanny_deploy_link is not None:
        monkeypatch.setenv('NANNY_DEPLOY_LINK', params.nanny_deploy_link)
    if params.users is not None:
        monkeypatch.setenv('AFFECTED_USERS', params.users)
    if params.build_status is not None:
        monkeypatch.setenv('BUILD_STATUS', params.build_status)
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'some_token')
    monkeypatch.setenv('SLACK_CHANNEL', params.slack_channel)

    if params.extra_environment:
        for key, value in params.extra_environment.items():
            monkeypatch.setenv(key, value)

    @patch_requests('https://teamcity.taxi.yandex-team.ru/app/rest')
    def teamcity_status(method, url, **kwargs):
        assert method.upper() == 'GET'
        return patch_requests.response(content=params.teamcity_status_response)

    @patch_requests(SLACK_POST_URL)
    def slack_send_message(method, url, **kwargs):
        assert method.upper() == 'POST'
        assert kwargs['json']['username'] == 'Teamcity'
        assert kwargs['json']['channel'] == params.slack_channel
        assert kwargs['json']['parse'] == 'full'
        color = kwargs['json']['attachments'][0]['color']
        assert color == params.slack_color
        blocks = kwargs['json']['attachments'][0]['blocks']
        assert len(blocks) == 1
        assert blocks[0]['fields'][0] == {
            'type': 'mrkdwn',
            'text': params.slack_message,
        }
        return patch_requests.response(json={'ok': True})

    repo = params.init_repo(tmpdir)
    repo.git.checkout(params.branch)
    monkeypatch.chdir(repo.working_tree_dir)
    github.init_repo('taxi', 'backend', next(repo.remotes[0].urls))

    telegram_report.main(params.args)

    if not params.disable_telegram:
        assert telegram.calls == [
            {
                'chat_id': params.chat_id,
                'disable_notification': False,
                'parse_mode': 'markdown',
                'text': text,
                'disable_web_page_preview': True,
            }
            for text in params.telegram_messages
        ]

        fetched_users = set(user['login'] for user in staff_persons_mock.calls)
        assert not fetched_users.symmetric_difference(params.staff_calls)
    else:
        assert telegram.calls == []

    if params.teamcity_status_response:
        assert len(teamcity_status.calls) == 1

    if params.slack_channel:
        assert len(slack_send_message.calls) == 1


class StaffParams(typing.NamedTuple):
    response: typing.List[typing.Dict[str, typing.Any]]
    logins: typing.Dict[str, str] = {}


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            StaffParams(
                response=[{'login': 'bad_guy', 'accounts': [{'type': 'vk'}]}],
            ),
            id='without_tg_login',
        ),
        pytest.param(
            StaffParams(
                response=[
                    {
                        'login': 'bad_guy',
                        'accounts': [
                            {'type': 'vk'},
                            {
                                'type': 'telegram',
                                'value': 'ok_login',
                                'private': False,
                            },
                        ],
                    },
                ],
                logins={'bad_guy': 'ok_login'},
            ),
            id='with_work_login',
        ),
        pytest.param(
            StaffParams(
                response=[
                    {
                        'login': 'bad_guy',
                        'accounts': [
                            {'type': 'vk'},
                            {
                                'type': 'telegram',
                                'value': 'login_bot',
                                'private': False,
                            },
                            {
                                'type': 'telegram',
                                'value': 'private_login',
                                'private': True,
                            },
                        ],
                    },
                ],
                logins={'bad_guy': 'private_login'},
            ),
            id='private_above_bot',
        ),
        pytest.param(
            StaffParams(
                response=[
                    {
                        'login': 'bad_guy',
                        'accounts': [
                            {
                                'type': 'telegram',
                                'value': 'login_bot',
                                'private': False,
                            },
                            {'type': 'vk'},
                            {
                                'type': 'telegram',
                                'value': 'private_login',
                                'private': True,
                            },
                            {
                                'type': 'telegram',
                                'value': 'ok_login',
                                'private': False,
                            },
                        ],
                    },
                ],
                logins={'bad_guy': 'ok_login'},
            ),
            id='work_login_above_all',
        ),
        pytest.param(
            StaffParams(
                response=[
                    {
                        'login': 'bad_guy',
                        'accounts': [
                            {'type': 'vk'},
                            {
                                'type': 'telegram',
                                'value': 'private_bot',
                                'private': True,
                            },
                            {
                                'type': 'telegram',
                                'value': 'private_bot',
                                'private': True,
                            },
                        ],
                    },
                    {
                        'login': 'ok_guy',
                        'accounts': [
                            {
                                'type': 'telegram',
                                'value': 'ok_guy',
                                'private': False,
                            },
                        ],
                    },
                ],
                logins={'bad_guy': 'private_bot', 'ok_guy': 'ok_guy'},
            ),
            id='two_logins',
        ),
    ],
)
def test_get_telegram_accounts_for(params, monkeypatch, patch_requests):
    monkeypatch.setenv('STAFF_TOKEN', 'staff-token')

    @patch_requests('https://staff-api.yandex-team.ru/v3/persons')
    def _persons(method, url, **kwargs):
        return patch_requests.response(json={'result': params.response})

    assert params.logins == staff.get_telegram_accounts_for([])
