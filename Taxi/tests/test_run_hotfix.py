# pylint: disable=too-many-lines
import dataclasses
import os
import pathlib
from typing import Callable
from typing import Optional
from typing import Sequence

import freezegun
import pytest

import run_hotfix
from taxi_buildagent import slack_tools
from taxi_buildagent.clients import vcs_base
from taxi_buildagent.tools.vcs import git_repo
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


@dataclasses.dataclass
class Params:
    init_repo: Callable
    branch: str
    pull_requests: Sequence[dict] = dataclasses.field(default_factory=list)
    fail: Optional[dict] = None
    version: Optional[str] = None
    telegram_message: str = ''
    slack_message: str = ''
    changes: str = ''
    add_followers: str = '1'
    staff_calls: Sequence[str] = ()
    path: str = ''
    update_ticket: Sequence[dict] = dataclasses.field(default_factory=list)
    ticket_comments: Sequence[str] = dataclasses.field(default_factory=list)
    ticket_components: Sequence[dict] = dataclasses.field(default_factory=list)
    telegram_disabled: str = ''
    slack_disabled: str = ''
    ticket_status: str = 'testing'
    changelog_release_ticket: Optional[str] = None
    fail_on_push: bool = False
    rollback_to_version: Optional[str] = None
    check_files_not_exist: Sequence[str] = dataclasses.field(
        default_factory=list,
    )
    master_commits: Sequence[repository.Commit] = dataclasses.field(
        default_factory=list,
    )
    disable_update_changelog: bool = False
    cherry_pick_twice: bool = False


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize('remote_backend', ('github', 'bitbucket'))
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                ticket_status='open',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                    ),
                ],
                fail={
                    'github': (
                        'Release ticket https://st.yandex-team.ru/TAXIREL-123'
                        ' is in a wrong status: `open` instead of `testing`'
                    ),
                    'bitbucket': (
                        'Release ticket https://st.yandex-team.ru/TAXIREL-123'
                        ' is in a wrong status: `open` instead of `testing`'
                    ),
                },
            ),
            id='bad ticket status',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='custom-master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                    ),
                ],
                fail={
                    'github': (
                        'https://github.yandex-team.ru/taxi/backend/pull/1'
                        ' must be based on master or develop,'
                        ' not on custom-master'
                    ),
                    'bitbucket': (
                        'https://bb.yandex-team.ru/projects/EDA/repos/core/'
                        'pull-requests/1 must be based on master or develop,'
                        ' not on custom-master'
                    ),
                },
            ),
            id='wrong base branch',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                        reviews=[vcs_base.Review('user1', 'commented')],
                    ),
                ],
                fail={
                    'github': (
                        'https://github.yandex-team.ru/taxi/backend/pull/1'
                        ' must be approved'
                    ),
                    'bitbucket': (
                        'https://bb.yandex-team.ru/projects/EDA/repos/core/'
                        'pull-requests/1 must be approved'
                    ),
                },
            ),
            id='no reviews',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                        reviews=[
                            vcs_base.Review('user1', 'commented'),
                            vcs_base.Review('user1', 'approved'),
                            vcs_base.Review('user1', 'rejected'),
                            vcs_base.Review('user2', 'approved'),
                        ],
                    ),
                ],
                fail={
                    'github': (
                        'https://github.yandex-team.ru/taxi/backend/pull/1'
                        ' must be approved'
                    ),
                    'bitbucket': (
                        'https://bb.yandex-team.ru/projects/EDA/repos/core/'
                        'pull-requests/1 must be approved'
                    ),
                },
            ),
            id='wrong reviewer',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                        reviews=[
                            vcs_base.Review('user1', 'rejected'),
                            vcs_base.Review('user1', 'approved'),
                            vcs_base.Review('user2', 'commented'),
                        ],
                    ),
                ],
                version='taxi-backend (3.0.224hotfix1)',
                changes='  * User alberist | commit\n',
                changelog_release_ticket='TAXIREL-123',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '3.0.224hotfix1:\n'
                                'User alberist | commit'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 3.0.224hotfix1',
                        },
                        'ticket': 'TAXIREL-123',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.224hotfix1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.224hotfix1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
            ),
            id='backend success',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='hotfix/my-hotfix',
                        target_branch='develop',
                        state='closed',
                        merge=True,
                        merge_message='hotfix: do stuff (#1)\n'
                        'Relates: TAXITOOLS-10',
                        login='rumkex',
                        commits=[repository.Commit('commit', ['file1'])],
                        reviews=[vcs_base.Review('oyaso', 'rejected')],
                    ),
                ],
                version='taxi-backend (3.0.224hotfix1)',
                changes=(
                    '  * User rumkex | hotfix: do stuff (#1) '
                    'Relates: TAXITOOLS-10\n'
                ),
                changelog_release_ticket='TAXIREL-123',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '3.0.224hotfix1:\n'
                                'User rumkex | hotfix: do stuff (#1) '
                                'Relates: TAXITOOLS-10'
                            ),
                            'followers': {'add': ['rumkex']},
                            'summary': 'summary, 3.0.224hotfix1',
                        },
                        'ticket': 'TAXIREL-123',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.224hotfix1`\n'
                    '\n@tg\\_rumkex'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.224hotfix1`\n'
                    '\n@rumkex'
                ),
                staff_calls=['rumkex'],
            ),
            id='backend hotfix from merged develop pr',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                pull_requests=[
                    dict(
                        branch='hotfix/my-hotfix',
                        target_branch='develop',
                        state='closed',
                        merge=True,
                        merge_message='hotfix: do stuff (#1)\n\n'
                        'Relates: TAXITOOLS-10',
                        login='rumkex',
                        commits=[
                            repository.Commit(
                                'commit', ['taxi-adjust/hotfix'],
                            ),
                        ],
                        reviews=[vcs_base.Review('oyaso', 'rejected')],
                    ),
                ],
                version='taxi-adjust (0.1.1hotfix1)',
                changes=(
                    '  Common changes:\n'
                    '  * User rumkex | hotfix: do stuff (#1)\n'
                ),
                changelog_release_ticket='TAXIREL-1',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '0.1.1hotfix1:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': []},
                            'summary': 'summary, 0.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-1',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-1]'
                    '(https://st.yandex-team.ru/TAXIREL-1)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.1hotfix1`'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-1|'
                    'TAXIREL-1>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.1hotfix1`'
                ),
            ),
            id='backend_py3 hotfix from merged develop pr',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='hotfix/my-hotfix',
                        target_branch='develop',
                        state='closed',
                        merge=False,
                        login='rumkex',
                        commits=[repository.Commit('commit', ['file1'])],
                        reviews=[],
                    ),
                ],
                fail={
                    'github': (
                        'https://github.yandex-team.ru/taxi/backend/pull/1'
                        ' should be merged into develop or rebased onto master'
                    ),
                    'bitbucket': (
                        'https://bb.yandex-team.ru/projects/EDA/repos/core/'
                        'pull-requests/1'
                        ' should be merged into develop or rebased onto master'
                    ),
                },
            ),
            id='backend hotfix from unmerged develop pr',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='hotfix/my-hotfix',
                        target_branch='develop',
                        state='closed',
                        merge=True,
                        merge_message='hotfix: do stuff (#1)\n'
                        'Relates: TAXITOOLS-1',
                        login='rumkex',
                        commits=[
                            # This commit alters a file that doesn't exist
                            # in master, hence breaking the cherry-pick
                            repository.Commit(
                                'commit', ['file'], 'overwritten',
                            ),
                        ],
                        reviews=[],
                    ),
                ],
                fail={
                    'github': (
                        'https://github.yandex-team.ru/taxi/backend/pull/1'
                        ' cannot be cherry-picked, aborted'
                    ),
                    'bitbucket': (
                        'https://bb.yandex-team.ru/projects/EDA/repos/core/'
                        'pull-requests/1'
                        ' cannot be cherry-picked, aborted'
                    ),
                },
            ),
            id='backend hotfix with failing cherrypick',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='hotfix/my-hotfix',
                        target_branch='develop',
                        state='closed',
                        merge=True,
                        merge_message='hotfix: do stuff (#1)\n'
                        'Relates: TAXITOOLS-2988',
                        login='sanyash',
                        commits=[repository.Commit('commit', ['file1'])],
                        reviews=[vcs_base.Review('rumkex', 'rejected')],
                    ),
                ],
                cherry_pick_twice=True,
                fail={
                    'github': (
                        'https://github.yandex-team.ru/taxi/backend/pull/1'
                        ' has been already merged into master'
                    ),
                    'bitbucket': (
                        'https://bb.yandex-team.ru/projects/EDA/repos/core/'
                        'pull-requests/1'
                        ' has been already merged into master'
                    ),
                },
            ),
            id='backend hotfix already merged',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '3.0.224hotfix1:\n'
                                'User alberist | commit'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 3.0.224hotfix1',
                        },
                        'ticket': 'TAXIREL-123',
                    },
                ],
                version='taxi-backend (3.0.224hotfix1)',
                changelog_release_ticket='TAXIREL-123',
                changes='  * User alberist | commit\n',
                ticket_comments=[
                    'TeamCity hotfix 3.0.224hotfix1 ((https://'
                    'teamcity.taxi.yandex-team.ru/viewLog.html?buildId=123 '
                    'FAILED))\n'
                    '((https://wiki.yandex-team.ru/taxi/backend/'
                    'automatization/faq/#hotfix-or-release-failed '
                    'check the wiki))',
                ],
                fail={
                    'github': (
                        'Some problem with push `develop` branch. See '
                        'https://wiki.yandex-team.ru/taxi/backend/'
                        'automatization/faq/#hotfix-or-release-failed '
                        'for details'
                    ),
                    'bitbucket': (
                        'Some problem with push `develop` branch. See '
                        'https://wiki.yandex-team.ru/taxi/backend/'
                        'automatization/faq/#hotfix-or-release-failed '
                        'for details'
                    ),
                },
                fail_on_push=True,
            ),
            id='backend hotfix with failing push',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit('commit', ['file1', 'file2']),
                        ],
                        reviews=[
                            vcs_base.Review('user1', 'approved'),
                            vcs_base.Review('user2', 'commented'),
                        ],
                    ),
                ],
                version='taxi-backend (3.0.224hotfix1)',
                changes='  * User alberist | commit\n',
                changelog_release_ticket='TAXIREL-123',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '3.0.224hotfix1:\n'
                                'User alberist | commit'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 3.0.224hotfix1',
                        },
                        'ticket': 'TAXIREL-123',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.224hotfix1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.224hotfix1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
            ),
            id='backend develop success',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[repository.Commit('commit', ['antifraud/1'])],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='taxi-backend-cpp (2.1.1hotfix1)',
                changelog_release_ticket='TAXIREL-100',
                update_ticket=[
                    {
                        'json': {
                            'description': 'some\ntext\n\n' '2.1.1hotfix1:\n',
                            'followers': {'add': []},
                            'summary': 'summary, 2.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-100',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-100]'
                    '(https://st.yandex-team.ru/TAXIREL-100)\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.1hotfix1`'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-100|'
                    'TAXIREL-100>\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.1hotfix1`'
                ),
            ),
            id='backend_cpp empty add',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit(
                                'commit\n\nRelates: TAXITOOLS-10',
                                ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='taxi-backend-cpp (2.1.1hotfix1)',
                changelog_release_ticket='TAXIREL-100',
                changes='  * User alberist | commit\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '2.1.1hotfix1:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 2.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-100',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-100]'
                    '(https://st.yandex-team.ru/TAXIREL-100)\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.1hotfix1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-100|'
                    'TAXIREL-100>\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.1hotfix1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
            ),
            id='backend_cpp success',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='master',
                        commits=[
                            repository.Commit(
                                'cc\n\nRelates: TAXITOOLS-10', ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                    dict(
                        branch='fix/data2',
                        target_branch='master',
                        commits=[
                            repository.Commit(
                                'cp\n\nRelates: TAXITOOLS-9', ['tracker/2'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='taxi-backend-cpp (2.1.1hotfix1)',
                changelog_release_ticket='TAXIREL-100',
                changes='  * User alberist | cc\n  * User alberist | cp\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '2.1.1hotfix1:\n'
                                'TAXITOOLS-9\n\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 2.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-100',
                    },
                ],
                ticket_comments=[
                    '====Для следующих тикетов не было обнаружено отчётов о '
                    'тестировании:\nTAXITOOLS-9\n\n'
                    '====Следующие тикеты не имеют исполнителя:\n'
                    'TAXITOOLS-9',
                ],
                telegram_disabled='1',
                slack_disabled='1',
            ),
            id='backend_cpp two pr',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='masters/antifraud',
                        commits=[
                            repository.Commit(
                                'commit\n\nRelates: TAXITOOLS-10',
                                ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='taxi-antifraud (3.0.0hotfix26)',
                changelog_release_ticket='TAXIREL-123',
                changes='  * User alberist | commit\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '3.0.0hotfix26:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 3.0.0hotfix26',
                        },
                        'ticket': 'TAXIREL-123',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.0hotfix26`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.0hotfix26`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
            ),
            id='backend_cpp antifraud',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='masters/taxi-adjust',
                        commits=[
                            repository.Commit(
                                'commit\n\nRelates: TAXITOOLS-10',
                                ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='taxi-adjust (0.1.1hotfix1)',
                changelog_release_ticket='TAXIREL-1',
                changes='  Common changes:\n' '  * User alberist | commit\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '0.1.1hotfix1:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': []},
                            'summary': 'summary, 0.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-1',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-1](https://st.yandex-team.ru/TAXIREL-1)'
                    '\nService name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.1hotfix1`'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-1|'
                    'TAXIREL-1>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.1hotfix1`'
                ),
            ),
            id='backend_py3 adjust',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='masters/driver-authorizer',
                        commits=[
                            repository.Commit(
                                'commit\n\nRelates: TAXITOOLS-10',
                                ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='driver-authorizer (1.1.1hotfix1)',
                changelog_release_ticket='TAXIREL-1',
                changes='  * User alberist | commit\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '1.1.1hotfix1:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': ['alberist']},
                            'summary': 'summary, 1.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-1',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-1](https://st.yandex-team.ru/TAXIREL-1)'
                    '\nService name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.1hotfix1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-1|'
                    'TAXIREL-1>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.1hotfix1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
            ),
            id='uservices driver-authorizer',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer2',
                path='services/driver-authorizer2',
                pull_requests=[
                    dict(
                        branch='feature/data',
                        target_branch='masters/driver-authorizer2',
                        commits=[
                            repository.Commit(
                                'commit0\n\nRelates: TAXITOOLS-11',
                                ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='driver-authorizer2 (2.2.2hotfix1)',
                changelog_release_ticket='TAXIREL-2',
                changes='  * User alberist | commit0\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '2.2.2hotfix1:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-11'
                            ),
                            'followers': {'add': []},
                            'summary': 'summary, 2.2.2hotfix1',
                        },
                        'ticket': 'TAXIREL-2',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-2](https://st.yandex-team.ru/TAXIREL-2)'
                    '\nService name: `driver-authorizer2`\n'
                    'Package: `driver-authorizer2`\n'
                    'Version: `2.2.2hotfix1`'
                ),
                slack_message=(
                    'New hotfix started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-2|'
                    'TAXIREL-2>\n'
                    'Service name: `driver-authorizer2`\n'
                    'Package: `driver-authorizer2`\n'
                    'Version: `2.2.2hotfix1`'
                ),
                add_followers='',
            ),
            id='uservices driver-authorizer2 without followers',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                slack_disabled='1',
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.0.3hotfix1)',
                changelog_release_ticket='TAXIREL-6',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '0.0.3hotfix1:\n'
                                'rollback to version 0.0.2'
                            ),
                            'followers': {'add': []},
                            'summary': (
                                'summary, 0.0.3hotfix1'
                                '(rollback to version 0.0.2)'
                            ),
                        },
                        'ticket': 'TAXIREL-6',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-6](https://st.yandex-team.ru/TAXIREL-6)'
                    '\nService name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.0.3hotfix1`'
                ),
                master_commits=[
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.2',
                        files=['services/taxi-adjust/debian/changelog'],
                    ),
                    repository.Commit(
                        comment='extra commit before 0.0.3',
                        files=['file3.py'],
                    ),
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.3',
                        files=['services/taxi-adjust/debian/changelog'],
                        files_content=(
                            'taxi-adjust (0.0.3) unstable; urgency=low\n\n'
                            '  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                check_files_not_exist=['file3.py'],
                rollback_to_version='0.0.2',
                disable_update_changelog=True,
            ),
            id='rollback_to_previous_release',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                rollback_to_version='0.0.1',
                disable_update_changelog=True,
                master_commits=[
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.2',
                        files=['services/taxi-adjust/debian/changelog'],
                    ),
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.3',
                        files=['services/taxi-adjust/debian/changelog'],
                        files_content=(
                            'taxi-adjust (0.0.3) unstable; urgency=low\n\n'
                            '  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                fail={
                    'github': 'Couldn\'t find version 0.0.1',
                    'bitbucket': 'Couldn\'t find version 0.0.1',
                },
            ),
            id='fail_rollback_to_wrong_version',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                slack_disabled='1',
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.0.4hotfix1)',
                changelog_release_ticket='TAXIREL-6',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '0.0.4hotfix1:\n'
                                'rollback to version 0.0.1'
                            ),
                            'followers': {'add': []},
                            'summary': (
                                'summary, 0.0.4hotfix1'
                                '(rollback to version 0.0.1)'
                            ),
                        },
                        'ticket': 'TAXIREL-6',
                    },
                ],
                telegram_message=(
                    'New hotfix started\n'
                    'Ticket: [TAXIREL-6](https://st.yandex-team.ru/TAXIREL-6)'
                    '\nService name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.0.4hotfix1`'
                ),
                master_commits=[
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.1',
                        files=['services/taxi-adjust/debian/changelog'],
                    ),
                    repository.Commit(
                        comment='extra commit before 0.0.3',
                        files=['file3.py'],
                    ),
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.3',
                        files=['services/taxi-adjust/debian/changelog'],
                    ),
                    repository.Commit(
                        comment='extra commit before 0.0.4',
                        files=['file4.py'],
                    ),
                    repository.Commit(
                        comment='edit changelog taxi-adjust/0.0.4',
                        files=['services/taxi-adjust/debian/changelog'],
                        files_content=(
                            'taxi-adjust (0.0.4) unstable; urgency=low\n\n'
                            '  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                check_files_not_exist=['file3.py', 'file4.py'],
                rollback_to_version='0.0.1',
                disable_update_changelog=True,
            ),
            id='rollback_to_old_version',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                slack_disabled='1',
                telegram_disabled='1',
                disable_update_changelog=True,
                pull_requests=[
                    dict(
                        branch='fix/data',
                        target_branch='masters/taxi-adjust',
                        commits=[
                            repository.Commit(
                                'commit\n\nRelates: TAXITOOLS-10',
                                ['common/1'],
                            ),
                        ],
                        reviews=[vcs_base.Review('user1', 'approved')],
                    ),
                ],
                version='taxi-adjust (0.1.1hotfix1)',
                changelog_release_ticket='TAXIREL-1',
                changes='  Common changes:\n' '  * User alberist | commit\n',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '0.1.1hotfix1:\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TAXITOOLS-10'
                            ),
                            'followers': {'add': []},
                            'summary': 'summary, 0.1.1hotfix1',
                        },
                        'ticket': 'TAXIREL-1',
                    },
                ],
            ),
            id='backend_py3_taxi_adjust_not_update_changelog',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                slack_disabled='1',
                telegram_disabled='1',
                version='yandex-taxi (0.0.3hotfix1)',
                changelog_release_ticket='TAXIREL-6',
                update_ticket=[
                    {
                        'json': {
                            'description': (
                                'some\ntext\n\n'
                                '0.0.3hotfix1:\n'
                                'rollback to version 0.0.2'
                            ),
                            'followers': {'add': []},
                            'summary': (
                                'summary, 0.0.3hotfix1'
                                '(rollback to version 0.0.2)'
                            ),
                        },
                        'ticket': 'TAXIREL-6',
                    },
                ],
                master_commits=[
                    repository.Commit(
                        comment='edit changelog 0.0.2',
                        files=['debian/changelog'],
                    ),
                    repository.Commit(
                        comment='extra commit before 0.0.3',
                        files=['file3.py'],
                    ),
                    repository.Commit(
                        comment='edit changelog 0.0.3',
                        files=['debian/changelog'],
                        files_content=(
                            'yandex-taxi (0.0.3) unstable; urgency=low\n\n'
                            '  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                check_files_not_exist=['file3.py'],
                rollback_to_version='0.0.2',
                disable_update_changelog=True,
            ),
            id='backend_rollback',
        ),
    ],
)
def test_hotfix(
        tmpdir,
        monkeypatch,
        chdir,
        teamcity_report_problems,
        startrek,
        staff_persons_mock,
        github,
        bitbucket_instance,
        telegram,
        patch_requests,
        params: Params,
        remote_backend: str,
):
    monkeypatch.setenv('BUILD_ID', '123')
    monkeypatch.setenv('TELEGRAM_BOT_CHAT_ID', 'tchatid')
    monkeypatch.setenv('SLACK_RELEASE_CHANNEL', 'some_channel')
    monkeypatch.setenv('ADD_FOLLOWERS', params.add_followers)
    monkeypatch.setenv('TELEGRAM_DISABLED', params.telegram_disabled)
    monkeypatch.setenv('SLACK_DISABLED', params.slack_disabled)
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'some_token')
    if params.rollback_to_version:
        monkeypatch.setenv('ROLLBACK_TO_VERSION', params.rollback_to_version)

    repo = params.init_repo(tmpdir)
    if params.master_commits:
        repo.git.checkout(params.branch)
        for commit in params.master_commits:
            repository.apply_commits(repo, [commit])
            if commit.comment.startswith('edit changelog'):
                repo.create_tag(commit.comment.split()[-1])
        repo.git.push('-f', 'origin', params.branch)
        repo.git.checkout('develop')
    repository.apply_commits(repo, [repository.Commit('commit', ['file'])])
    repo.git.push('origin', 'develop')
    repo.git.checkout(params.branch)

    for pull_request in params.pull_requests:
        target_branch = pull_request['target_branch']
        if target_branch in repo.branches:
            continue
        repo.git.branch(target_branch, 'develop')
        repo.git.push('origin', target_branch)

    chdir(repo.working_tree_dir)
    with open(os.path.join(params.path, 'debian/changelog')) as fp:
        old_changelog = fp.read()
    for _fle in params.check_files_not_exist:
        assert pathlib.Path(_fle).exists()

    startrek.ticket_status = params.ticket_status
    if params.ticket_components:
        startrek.ticket_components = params.ticket_components

    @patch_requests(slack_tools.SLACK_POST_URL)
    def slack_send_message(method, url, **kwargs):
        return patch_requests.response(json={'ok': True}, content='ok')

    urls = []

    if remote_backend == 'github':
        github_repo = github.init_repo(
            'taxi', 'backend', next(repo.remotes[0].urls),
        )
        for pull_request in params.pull_requests:
            urls.append(github_repo.create_pr(repo, **pull_request))
    elif remote_backend == 'bitbucket':
        monkeypatch.setenv('BITBUCKET_ORG', 'EDA')
        monkeypatch.setenv('BITBUCKET_REPO', 'core')
        for pull_request in params.pull_requests:
            pull_request_mock = bitbucket_instance.create_pr(
                repo, **pull_request,
            )
            urls.append(pull_request_mock.self_url)
    else:
        raise ValueError('Invalid backend')

    if params.cherry_pick_twice:
        urls.append(urls[-1])

    if params.fail_on_push:
        monkeypatch.setattr(
            'taxi_buildagent.tools.vcs.git_repo.Repo.checkout_and_push_branch',
            _fail_push_with_error,
        )

    args = []
    if params.disable_update_changelog:
        args = ['--changelog-disabled']
    run_hotfix.main(args + urls)

    assert startrek.update_ticket.calls == params.update_ticket
    assert startrek.create_comment.calls == [
        {'json': {'text': comment}} for comment in params.ticket_comments
    ]

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

    assert staff_persons_mock.calls == [
        {'login': login} for login in params.staff_calls
    ]

    if params.version is not None:
        with open(os.path.join(params.path, 'debian/changelog')) as fp:
            changelog = fp.readline()
            for line in fp:
                if line.startswith(' ') or line == '\n':
                    changelog += line
                else:
                    break
        if params.rollback_to_version:
            body = f'  Rollback to: {params.rollback_to_version}\n'
        else:
            body = (
                '  * Mister Twister | commit message\n\n'
                f'  New hotfix changes:\n{params.changes}'
            )
        assert changelog == (
            '%s unstable; urgency=low\n\n'
            '  Release ticket https://st.yandex-team.ru/%s\n\n%s\n'
            ' -- buildfarm <buildfarm@yandex-team.ru>  '
            'Mon, 23 Apr 2018 17:22:56 +0300\n\n'
        ) % (params.version, params.changelog_release_ticket, body)
    else:
        with open(os.path.join(params.path, 'debian/changelog')) as fp:
            changelog = fp.read()
        assert changelog == old_changelog

    if params.fail:
        calls = teamcity_report_problems.calls
        assert len(calls) == 1
        assert calls[0]['description'] == params.fail[remote_backend]
    else:
        if params.branch != 'develop':
            assert repo.active_branch.name == params.branch
            if params.disable_update_changelog or params.rollback_to_version:
                assert os.path.join(
                    params.path, 'debian', 'changelog',
                ) in repo.git.diff('develop', '--name-only')
            else:
                assert os.path.join(
                    params.path, 'debian', 'changelog',
                ) not in repo.git.diff('develop', '--name-only')
    for _fle in params.check_files_not_exist:
        assert not pathlib.Path(_fle).exists()


def _fail_push_with_error(_, branch, **kwargs):
    raise git_repo.GitRepoError('Push to %s failed' % branch)
