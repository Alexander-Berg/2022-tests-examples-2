# pylint: disable=too-many-lines, too-many-statements, too-many-locals
import dataclasses
import os
import re
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

import freezegun
import git
import pytest

import git_checkout
import run_release
from taxi_buildagent import slack_tools
from taxi_buildagent import utils
from taxi_buildagent.tools import vcs
from taxi_buildagent.tools.vcs import git_repo
from tests.plugins import arc
import tests.plugins.startrek as plugin_startrek
from tests.utils import pytest_wraps
from tests.utils import repository
from tests.utils.examples import arcadia
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import backend_py3_move
from tests.utils.examples import llvm_toolchain
from tests.utils.examples import ml
from tests.utils.examples import uservices

HASH_COMMIT_REGEX = re.compile(r'\(hash commit ([a-z0-9]*)\)')


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    branch: str
    commits: Sequence[repository.Commit]
    git_race_commits: Sequence[repository.Commit] = ()
    # push order below: develop -> master -> tags
    git_any_push_responses: Sequence[Tuple[int, bool]] = tuple()
    git_relates_hook: bool = False
    fail: Optional[dict] = None
    version: Optional[str] = None
    release_tag: str = ''
    component_name: Optional[str] = None
    component_prefix: Optional[str] = None
    component_opened: dict = {}
    ticket_summary: str = 'Backend'
    created_ticket: Optional[dict] = None
    created_comment: Optional[dict] = {
        'text': (
            '====Для следующих тикетов не было обнаружено '
            'отчётов о тестировании:\n'
            'TAXITOOLS-1\n\n'
            '====Следующие тикеты находятся в статусе '
            '"Открыт":\n'
            'TAXITOOLS-1\n\n'
            '====Следующие тикеты не имеют исполнителя:\n'
            'TAXITOOLS-1'
        ),
    }
    extra_comments: Sequence[dict] = ()
    telegram_message: str = ''
    slack_message: str = ''
    changes: str = ''
    add_followers: str = '1'
    staff_calls: Sequence[str] = ()
    path: str = ''
    release_ticket: Optional[str] = None
    startrek_disabled: str = ''
    telegram_disabled: str = ''
    slack_disabled: str = ''
    ticket_status: str = ''
    ticket_components: List[Dict[str, Union[str, int]]] = []
    changelog_release_ticket: str = (
        '  Release ticket https://st.yandex-team.ru/TAXIREL-222\n\n'
    )
    get_ticket: Sequence[Dict[str, str]] = []
    update_ticket: Optional[dict] = None
    no_changes_enabled: str = ''
    allow_empty_release_ticket: str = ''
    staff_error: bool = False
    increase_last_number_of_version: str = ''
    teamcity_set_parameters: Dict[str, str] = {}
    freeze_hash: str = '1234'
    migration_tickets: List[str] = []
    tickets_comments: Dict[str, plugin_startrek.TicketComments] = {}
    ticket_assignee: str = ''
    disable_test_ticket_checks: str = ''
    master_commits: List[repository.Commit] = []
    disable_update_changelog: bool = False
    deploy_type: str = ''


def _ls_tree(repo, commit):
    return sorted(repo.git.ls_tree('-r', commit).splitlines())


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[],
                fail={
                    'description': 'No changes to release',
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'No changes to release',
                },
                created_comment=None,
            ),
            id='backend empty release',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[repository.Commit('commit1', ['file1'])],
                fail={
                    'description': (
                        'https://st.yandex-team.ru/TAXIREL-123 is closed!'
                    ),
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'https://st.yandex-team.ru/TAXIREL-123 is closed!'
                    ),
                },
                get_ticket=[{'ticket': 'TAXIREL-123'}],
                ticket_status='closed',
                release_ticket='https://st.yandex-team.ru/TAXIREL-123',
                created_comment=None,
            ),
            id='env.RELEASE_TICKET is closed',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py1',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [100, 42],  # created with this id in mock
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend success without component',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                component_prefix='some-prefix',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [222, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend success with component prefix',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[repository.Commit('commit', ['taxi/123', 'file2'])],
                component_opened={22: [{'key': 'TAXIREL-9001'}]},
                fail={
                    'description': (
                        'Old release tickets are opened: '
                        '[https://st.yandex-team.ru/TAXIREL-9001]. '
                        'More information about new releases and '
                        'attachment to releases: '
                        'https://wiki.yandex-team.ru/taxi/backend/'
                        'basichowto/deploy/'
                    ),
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Old release tickets are opened: '
                        '[https://st.yandex-team.ru/TAXIREL-9001]. '
                        'More information about new releases and '
                        'attachment to releases: '
                        'https://wiki.yandex-team.ru/taxi/backend/'
                        'basichowto/deploy/'
                    ),
                },
                created_comment=None,
            ),
            id='backend last release opened',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend success',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend develop success',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                git_race_commits=[
                    repository.Commit('race_commit1', ['file1']),
                ],
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend develop git race error',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                git_race_commits=[
                    repository.Commit('race_commit1', ['file1']),
                ],
                git_relates_hook=True,
                fail={
                    'description': (
                        'Some problem with push `develop` branch. '
                        'See https://wiki.yandex-team.ru/taxi/backend/'
                        'automatization/faq/#hotfix-or-release-failed '
                        'for details\n'
                        'git exited with code 1: '
                        'remote: backend/check-style.sh: '
                        'failed with exit status 1\n'
                        'remote: [POLICY] Commit '
                        'a6477a67e873a8cde7dacadbee724ef8afe4da19 doesn\'t '
                        'contain a relates ticket:\n'
                        'remote: update\n'
                        'To github.yandex-team.ru:taxi/backend.git\n'
                        '! [remote rejected] develop -> develop '
                        '(pre-receive hook declined)\n'
                        'error: failed to push some refs to '
                        '\'git@github.yandex-team.ru:taxi/backend.git\''
                    ),
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Some problem with push `develop` branch. '
                        'See https://wiki.yandex-team.ru/taxi/backend/'
                        'automatization/faq/#hotfix-or-release-failed '
                        'for details\n'
                        'git exited with code 1: '
                        'remote: backend/check-style.sh: '
                        'failed with exit status 1\n'
                        'remote: [POLICY] Commit '
                        'a6477a67e873a8cde7dacadbee724ef8afe4da19 doesn\'t '
                        'contain a relates ticket:\n'
                        'remote: update\n'
                        'To github.yandex-team.ru:taxi/backend.git\n'
                        '! [remote rejected] develop -> develop '
                        '(pre-receive hook declined)\n'
                        'error: failed to push some refs to '
                        '\'git@github.yandex-team.ru:taxi/backend.git\''
                    ),
                },
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
                extra_comments=[
                    {
                        'text': (
                            'TeamCity auto-release 3.0.225 '
                            '((https://teamcity.taxi.yandex-team.ru/'
                            'viewLog.html?buildId=123 FAILED))\n'
                            '((https://wiki.yandex-team.ru/taxi/backend'
                            '/automatization/faq/#hotfix-or-release-failed '
                            'check the wiki))'
                        ),
                    },
                ],
            ),
            id='backend develop git relates hook',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changelog_release_ticket='',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`'
                ),
                slack_message=(
                    'New release started\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`'
                ),
                startrek_disabled='1',
                created_comment=None,
            ),
            id='backend startrek disabled',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                release_ticket='https://st.yandex-team.ru/TAXIREL-111',
                fail={
                    'description': (
                        'Updating not last project ticket: '
                        '`https://st.yandex-team.ru/TAXIREL-111` instead of'
                        ' `https://st.yandex-team.ru/TAXIREL-123`'
                    ),
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Updating not last project ticket: '
                        '`https://st.yandex-team.ru/TAXIREL-111` instead of'
                        ' `https://st.yandex-team.ru/TAXIREL-123`'
                    ),
                },
                created_comment=None,
            ),
            id='backend wrong ticket',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * Mister Twister | commit message\n\n'
                '  New release changes:\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                release_ticket='https://st.yandex-team.ru/TAXIREL-123',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-123'
                    '\n\n'
                ),
                update_ticket={
                    'ticket': 'TAXIREL-123',
                    'json': {
                        'summary': 'summary, 3.0.225',
                        'description': (
                            'some\ntext\n\n'
                            '3.0.225:\nTAXITOOLS-1\nalberist | commit1'
                        ),
                        'followers': {'add': ['alberist']},
                    },
                },
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend release ticket',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend telegram disabled',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[],
                no_changes_enabled='1',
                created_comment=None,
            ),
            id='backend no changes enabled',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit('commit1', ['file1']),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': 'TAXITOOLS-1\nalberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * alberist | commit2\n  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                no_changes_enabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend success no changes enabled',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[],
                created_ticket={
                    'assignee': None,
                    'components': [22, 42],
                    'description': '',
                    'followers': [],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 3.0.225',
                },
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changelog_release_ticket=(
                    '  Release ticket '
                    'https://st.yandex-team.ru/TAXIREL-222\n'
                ),
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`'
                ),
                allow_empty_release_ticket='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': ''},
                created_comment=None,
            ),
            id='backend empty ticket',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                component_name='backend-cpp',
                commits=[
                    repository.Commit(
                        'test chat', ['testsuite/tests/chat/ff'],
                    ),
                    repository.Commit(
                        'test common', ['testsuite/tests/common/ff'],
                    ),
                    repository.Commit('commit1', ['tracker/1']),
                    repository.Commit(
                        'commit0\n\nRelates: TAXITOOLS-1',
                        ['file0', 'tracker/1'],
                    ),
                    repository.Commit(
                        'commit3', ['common/config/f', 'tracker/1'],
                    ),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                    repository.Commit(
                        'sub update',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [repository.Commit('ts', ['file'])],
                            ),
                        ],
                    ),
                    repository.Commit(
                        'add new sub',
                        [],
                        submodules=[
                            (
                                'newsubmodule',
                                [repository.Commit('newsub', ['file'])],
                            ),
                        ],
                    ),
                    repository.Commit(
                        'commita', ['antifraud/1', 'common/config/2'],
                    ),
                    repository.Commit(
                        'commits', ['surger/1', 'common/config/3'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [33, 42],
                    'description': (
                        'TAXITOOLS-1\n'
                        'alberist | commit1\n'
                        'alberist | commit3\n'
                        'alberist | test chat\n\n'
                        'Common changes:\n'
                        'alberist | add new sub\n'
                        'alberist | sub update\n'
                        'alberist | test common\n'
                        'alberist | ts | submodules/testsuite'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 2.1.2',
                },
                version='taxi-backend-cpp (2.1.2)',
                release_tag='2.1.2',
                changes='  * alberist | add new sub\n'
                '  * alberist | sub update\n'
                '  * alberist | commit2\n'
                '  * alberist | commit3\n'
                '  * alberist | commit0\n'
                '  * alberist | commit1\n'
                '  * alberist | test common\n'
                '  * alberist | test chat\n'
                '  * alberist | ts | submodules/testsuite',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend_cpp success',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                component_name='backend-cpp',
                commits=[
                    repository.Commit(
                        'add new sub',
                        [],
                        submodules=[
                            (
                                'newsubmodule',
                                [repository.Commit('newsub', ['file'])],
                            ),
                        ],
                        author='fail',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [33, 42],
                    'description': 'Common changes:\nfail | add new sub',
                    'followers': ['fail'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend 2.1.2',
                },
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.2`\n'
                    '\n@fail'
                ),
                version='taxi-backend-cpp (2.1.2)',
                release_tag='2.1.2',
                changes='  * fail | add new sub',
                staff_error=True,
                teamcity_set_parameters={'env.AFFECTED_USERS': 'fail'},
                created_comment=None,
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Package: `taxi-backend-cpp`\n'
                    'Version: `2.1.2`\n'
                    '\nfail'
                ),
            ),
            id='backend_cpp broken staff success',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                commits=[
                    repository.Commit(
                        'test chat', ['testsuite/tests/chat/ff'],
                    ),
                    repository.Commit(
                        'test common', ['testsuite/tests/common/ff'],
                    ),
                    repository.Commit('commit1', ['tracker/1', 'tracker/2']),
                    repository.Commit(
                        'commit0\n\nRelates: TAXITOOLS-1',
                        ['file0', 'tracker/1'],
                    ),
                    repository.Commit(
                        'commit3', ['common/config/f', 'tracker/1'],
                    ),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-1', ['file2'],
                    ),
                    repository.Commit(
                        'commit4\n\nRelates: TAXITOOLS-2',
                        ['antifraud/3', 'tracker/2'],
                    ),
                    repository.Commit(
                        'commit5\n\nRelates: TAXITOOLS-3',
                        ['common/clients/123', 'antifraud/4'],
                    ),
                    repository.Commit(
                        'sub update',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [repository.Commit('ts', ['file'])],
                            ),
                        ],
                    ),
                    repository.Commit(
                        'add new sub',
                        [],
                        submodules=[
                            (
                                'newsubmodule',
                                [repository.Commit('newsub', ['file'])],
                            ),
                        ],
                    ),
                    repository.Commit(
                        'commita', ['antifraud/1', 'common/config/2'],
                    ),
                    repository.Commit(
                        'commits', ['surger/1', 'common/config/3'],
                    ),
                    repository.Commit('commitp', ['surger/2', 'protocol/5']),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [35, 42],
                    'description': (
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'alberist | commita\n\n'
                        'Common changes:\n'
                        'alberist | add new sub\n'
                        'alberist | sub update\n'
                        'alberist | test common\n'
                        'alberist | ts | submodules/testsuite\n'
                        'https://st.yandex-team.ru/TAXITOOLS-1'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend antifraud 3.0.1',
                },
                version='taxi-antifraud (3.0.1)',
                release_tag='antifraud/3.0.1',
                changes='  * alberist | commita\n'
                '  * alberist | add new sub\n'
                '  * alberist | sub update\n'
                '  * alberist | commit5\n'
                '  * alberist | commit4\n'
                '  * alberist | commit2\n'
                '  * alberist | commit0\n'
                '  * alberist | test common\n'
                '  * alberist | ts | submodules/testsuite',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[
                    {'ticket': 'TAXITOOLS-2'},
                    {'ticket': 'TAXITOOLS-3'},
                ],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n\n'
                        '====Следующие тикеты находятся в статусе '
                        '"Открыт":\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3'
                    ),
                },
            ),
            id='backend_cpp antifraud',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                commits=[
                    repository.Commit(
                        'commit1\n\nRelates: TAXITOOLS-2',
                        ['antifraud/3', 'protocol/2'],
                    ),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-3',
                        ['common/clients/123', 'protocol/4'],
                    ),
                ],
                version='taxi-antifraud (3.0.1)',
                release_tag='antifraud/3.0.1',
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-123'
                    '\n\n'
                ),
                changes='  * Mister Twister | commit message\n\n'
                '  New release changes:\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                release_ticket='https://st.yandex-team.ru/TAXIREL-123',
                update_ticket={
                    'ticket': 'TAXIREL-123',
                    'json': {
                        'summary': 'summary, 3.0.1',
                        'description': (
                            'some\ntext\n\n'
                            '3.0.1:\n'
                            'TAXITOOLS-2\n\n'
                            'Common changes:\n'
                            'https://st.yandex-team.ru/TAXITOOLS-3'
                        ),
                        'followers': {'add': ['alberist']},
                    },
                },
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-2'}],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты находятся в статусе '
                        '"Открыт":\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-2'
                    ),
                },
            ),
            id='backend_cpp antifraud update',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/surger',
                path='surger',
                commits=[
                    repository.Commit(
                        'commit1\n\nRelates: TAXITOOLS-2',
                        ['surger/docs/yaml/file1'],
                    ),
                ],
                version='taxi-surger (3.3.6)',
                release_tag='surger/3.3.6',
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-222'
                    '\n\n'
                ),
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `surger`\n'
                    'Package: `taxi-surger`\n'
                    'Version: `3.3.6`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `surger`\n'
                    'Package: `taxi-surger`\n'
                    'Version: `3.3.6`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend surger 3.3.6',
                    'queue': 'TAXIREL',
                    'description': 'TAXITOOLS-2',
                    'components': [36, 42],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                get_ticket=[{'ticket': 'TAXITOOLS-2'}],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты находятся в статусе '
                        '"Открыт":\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-2'
                    ),
                },
            ),
            id='backend_cpp only surger',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                commits=[
                    repository.Commit(
                        'commit1\n\nRelates: TAXITOOLS-2',
                        ['antifraud/3', 'protocol/2'],
                    ),
                    repository.Commit(
                        'commit2\n\nRelates: TAXITOOLS-4', ['some_lib/1'],
                    ),
                ],
                version='taxi-antifraud (3.0.1)',
                release_tag='antifraud/3.0.1',
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-123'
                    '\n\n'
                ),
                changes='  * Mister Twister | commit message\n\n'
                '  New release changes:\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                release_ticket='https://st.yandex-team.ru/TAXIREL-123',
                update_ticket={
                    'ticket': 'TAXIREL-123',
                    'json': {
                        'summary': 'summary, 3.0.1',
                        'description': (
                            'some\ntext\n\n'
                            '3.0.1:\n'
                            'TAXITOOLS-2\n\n'
                            'Common libraries changes:\n'
                            'TAXITOOLS-4'
                        ),
                        'followers': {'add': ['alberist']},
                    },
                },
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Service name: `antifraud`\n'
                    'Package: `taxi-antifraud`\n'
                    'Version: `3.0.1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-2'}],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты находятся в статусе '
                        '"Открыт":\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-2'
                    ),
                },
            ),
            id='backend_cpp library update',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/protocol',
                path='protocol',
                fail={
                    'description': 'Attach to release is disabled',
                    'identity': None,
                },
                commits=[
                    repository.Commit(
                        'test_commit\n\nRelates: TAXITOOLS-5',
                        ['antifraud/3', 'protocol/2'],
                    ),
                ],
                changes='  * Mister Twister | commit message\n\n'
                '  New release changes:\n'
                '  * alberist | commit2',
                release_ticket='https://st.yandex-team.ru/TAXIREL-125',
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'Attach to release is disabled',
                },
                created_comment=None,
            ),
            id='backend_cpp protocol with created ticket',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/surger',
                path='surger',
                fail={
                    'description': 'Attach to release is disabled',
                    'identity': None,
                },
                commits=[
                    repository.Commit(
                        'test_commit\n\nRelates: TAXITOOLS-84',
                        ['antifraud/3', 'surger/2'],
                    ),
                ],
                release_ticket='https://st.yandex-team.ru/TAXIREL-124',
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'Attach to release is disabled',
                },
                created_comment=None,
            ),
            id='backend_cpp surger attach disabled',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/driver-protocol',
                path='driver-protocol',
                commits=[
                    repository.Commit(
                        'add reposition service yaml',
                        ['reposition/docs/yaml/v1/types/mode_locations.yaml'],
                    ),
                ],
                version='driver-protocol (7.4.6)',
                release_tag='driver-protocol/7.4.6',
                changes='  * alberist | add reposition service yaml',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-protocol`\n'
                    'Package: `driver-protocol`\n'
                    'Version: `7.4.6`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-protocol`\n'
                    'Package: `driver-protocol`\n'
                    'Version: `7.4.6`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-protocol 7.4.6',
                    'queue': 'TAXIREL',
                    'description': (
                        'Common libraries changes:\n'
                        'alberist | add reposition service yaml'
                    ),
                    'components': [49, 42],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='backend_cpp driver_protocol swagger',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/driver-protocol',
                path='driver-protocol',
                commits=[
                    repository.Commit(
                        'add reposition service yaml',
                        [
                            'reposition/docs/yaml/v1/types/'
                            'mode_locations.yaml',
                            'testsuite/tests/default_fixtures/db_tariffs.json',
                        ],
                    ),
                ],
                version='driver-protocol (7.4.6)',
                release_tag='driver-protocol/7.4.6',
                changes='  * alberist | add reposition service yaml',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-protocol`\n'
                    'Package: `driver-protocol`\n'
                    'Version: `7.4.6`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-protocol`\n'
                    'Package: `driver-protocol`\n'
                    'Version: `7.4.6`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-protocol 7.4.6',
                    'queue': 'TAXIREL',
                    'description': (
                        'Common changes:\n'
                        'alberist | add reposition service yaml'
                    ),
                    'components': [49, 42],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='backend_cpp driver_protocol swagger common',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/driver-protocol',
                path='driver-protocol',
                commits=[
                    repository.Commit(
                        'add reposition files',
                        [
                            'reposition/docs/yaml/v1/types/'
                            'mode_locations.yaml',
                            'reposition/src/mode_locations.cpp',
                        ],
                    ),
                ],
                version='driver-protocol (7.4.6)',
                release_tag='driver-protocol/7.4.6',
                changes='  * alberist | add reposition files',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-protocol`\n'
                    'Package: `driver-protocol`\n'
                    'Version: `7.4.6`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-protocol`\n'
                    'Package: `driver-protocol`\n'
                    'Version: `7.4.6`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-protocol 7.4.6',
                    'queue': 'TAXIREL',
                    'description': (
                        'Common libraries changes:\n'
                        'alberist | add reposition files'
                    ),
                    'components': [49, 42],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='backend_cpp driver_protocol swagger reposition',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/reposition',
                path='reposition',
                commits=[
                    repository.Commit(
                        'add reposition service yaml',
                        ['reposition/docs/yaml/v1/types/mode_locations.yaml'],
                    ),
                ],
                version='reposition (8.3.3)',
                release_tag='reposition/8.3.3',
                changes='  * alberist | add reposition service yaml',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `reposition`\n'
                    'Package: `reposition`\n'
                    'Version: `8.3.3`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `reposition`\n'
                    'Package: `reposition`\n'
                    'Version: `8.3.3`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend reposition 8.3.3',
                    'queue': 'TAXIREL',
                    'description': 'alberist | add reposition service yaml',
                    'components': [58, 42],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='backend_cpp reposition swagger',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/surger',
                path='surger',
                commits=[
                    repository.Commit(
                        'add reposition service yaml',
                        ['reposition/docs/yaml/v1/types/mode_locations.yaml'],
                    ),
                ],
                fail={
                    'description': 'No changes to release',
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'No changes to release',
                },
                created_comment=None,
            ),
            id='backend_cpp surger swagger reposition',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/surger',
                path='surger',
                commits=[
                    repository.Commit(
                        'testsuite tariff\n\nRelates: TAXITOOLS-90',
                        [
                            'testsuite/tests/default_fixtures/db_tariffs.json',
                            'testsuite/tests/common/ff',
                            'reposition/docs/yaml/v1/types/'
                            'mode_locations.yaml',
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [36, 42],
                    'description': (
                        'Common changes:\n'
                        'https://st.yandex-team.ru/TAXITOOLS-90'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend surger 3.3.6',
                },
                version='taxi-surger (3.3.6)',
                release_tag='surger/3.3.6',
                changes='  * alberist | testsuite tariff',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `surger`\n'
                    'Package: `taxi-surger`\n'
                    'Version: `3.3.6`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `surger`\n'
                    'Package: `taxi-surger`\n'
                    'Version: `3.3.6`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_cpp surger common',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/protocol',
                path='protocol',
                commits=[
                    repository.Commit(
                        'commit0\n\nRelates: TAXITOOLS-1',
                        ['file0', 'protocol/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [75, 42],
                    'description': 'TAXITOOLS-1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend protocol 3.2.5',
                },
                version='taxi-protocol (3.2.5)',
                release_tag='protocol/3.2.5',
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-222'
                    '\n\n'
                ),
                changes='  * alberist | commit0',
                telegram_message='',
                slack_message='',
                staff_calls=[],
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
            ),
            id='backend_cpp protocol without created ticket',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/1', 'services/taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['services/taxi/2', 'services/taxi-corp/2'],
                        submodules=[
                            repository.SubmoduleCommits(
                                'submodules/codegen',
                                [
                                    repository.Commit(
                                        'edit changelog 0.59',
                                        ['ignore_me'],
                                        files_content='ignore_me',
                                        author='buildfarm buildfarm',
                                        email='buildfarm@yandex-team.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                    repository.Commit('commit3', ['taxi/3'], author='oyaso'),
                    repository.Commit(
                        'commit4',
                        ['services/taxi-corp/4', 'services/taximeter/4'],
                    ),
                    repository.Commit(
                        'new-service', ['services/taxix/debian/changelog'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'oyaso | commit3'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * oyaso | commit3\n'
                '  * alberist | commit2',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3_taxi-adjust',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                master_commits=[
                    repository.Commit(
                        'changelog_new',
                        ['services/taxi-adjust/debian/changelog'],
                        (
                            'taxi-adjust (0.0.3.hotfix1) unstable; urgency=low'
                            '\n\n  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/1', 'services/taxi/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.0.4',
                },
                version='taxi-adjust (0.0.4)',
                release_tag='taxi-adjust/0.0.4',
                changes='  * alberist | commit1',
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3_taxi_adjust_diverged_changelog',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                master_commits=[
                    repository.Commit(
                        'changelog_new',
                        ['services/taxi-adjust/debian/changelog'],
                        (
                            'taxi-adjust (0.0.3.hotfix1) unstable; urgency=low'
                            '\n\n  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/1', 'services/taxi/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.0.4',
                },
                version='taxi-adjust (0.0.4)',
                release_tag='taxi-adjust/0.0.4',
                changes='  * alberist | commit1',
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
                disable_update_changelog=True,
            ),
            id='backend_py3_taxi_adjust_not_update_changelog',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/service.yaml'],
                        'clownductor: {sandbox-resources: '
                        '[{source-path: bla, destination-path: bla1, '
                        'owner: gilfanovii}]}',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.1resources1',
                },
                version='taxi-adjust (0.1.1resources1)',
                release_tag='taxi-adjust/0.1.1resources1',
                changes='  deploy-type:resource\n  * alberist | commit1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                telegram_disabled='1',
                slack_disabled='1',
                created_comment=None,
                deploy_type='sandbox-resources',
            ),
            id='backend_py3_update_sandbox_resources',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/service.yaml'],
                        'clownductor: {default-deploy-type: sandbox-resources,'
                        ' sandbox-resources: [{source-path: bla, '
                        'destination-path: bla1, owner: gilfanovii}]}',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.1resources1',
                },
                version='taxi-adjust (0.1.1resources1)',
                release_tag='taxi-adjust/0.1.1resources1',
                changes='  deploy-type:resource\n  * alberist | commit1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                telegram_disabled='1',
                slack_disabled='1',
                created_comment=None,
            ),
            id='backend_py3_update_sandbox_resources_default',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                master_commits=[
                    repository.Commit(
                        'changelog_new',
                        ['services/taxi-adjust/debian/changelog'],
                        (
                            'taxi-adjust (0.0.3resources1) unstable; urgency='
                            'low\n\n  Release ticket https://st.yandex-team.ru'
                            '/TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/service.yaml'],
                        'clownductor: {default-deploy-type: service,'
                        ' sandbox-resources: [{source-path: bla, '
                        'ttl: 4, destination-path: bla1, owner: gilfanovii}]}',
                    ),
                ],
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-6'
                    '\n\n'
                ),
                update_ticket={
                    'ticket': 'TAXIREL-6',
                    'json': {
                        'summary': 'summary, 0.0.3resources2',
                        'description': (
                            'some\ntext\n\n'
                            '0.0.3resources2:\n'
                            'alberist | commit1'
                        ),
                        'followers': {'add': ['alberist']},
                    },
                },
                version='taxi-adjust (0.0.3resources2)',
                release_tag='taxi-adjust/0.0.3resources2',
                changes=(
                    '  deploy-type:resource\n'
                    '  * alberist | Ololo\n\n'
                    '  New release changes:\n'
                    '  * alberist | commit1'
                ),
                ticket_components=[{'id': 41}],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                telegram_disabled='1',
                slack_disabled='1',
                created_comment=None,
                deploy_type='sandbox-resources',
                ticket_status='open',
                release_ticket='https://st.yandex-team.ru/TAXIREL-6',
            ),
            id='backend_py3_attach_updating_sandbox_resources',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                master_commits=[
                    repository.Commit(
                        'changelog_new',
                        ['services/taxi-adjust/debian/changelog'],
                        (
                            'taxi-adjust (0.0.3) unstable; urgency=low\n\n'
                            '  Release ticket https://st.yandex-team.ru'
                            '/TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/service.yaml'],
                        'clownductor: {default-deploy-type: sandbox-resources,'
                        ' sandbox-resources: [{source-path: bla, '
                        'destination-path: bla1, owner: gilfanovii}]}',
                    ),
                ],
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-6'
                    '\n\n'
                ),
                update_ticket={
                    'ticket': 'TAXIREL-6',
                    'json': {
                        'summary': 'summary, 0.0.3resources1',
                        'description': (
                            'some\ntext\n\n'
                            '0.0.3resources1:\n'
                            'alberist | commit1'
                        ),
                        'followers': {'add': ['alberist']},
                    },
                },
                version='taxi-adjust (0.0.3resources1)',
                release_tag='taxi-adjust/0.0.3resources1',
                changes=(
                    '  deploy-type:resource\n'
                    '  * alberist | Ololo\n\n'
                    '  New release changes:\n'
                    '  * alberist | commit1'
                ),
                ticket_components=[{'id': 41}],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                telegram_disabled='1',
                slack_disabled='1',
                created_comment=None,
                ticket_status='open',
                release_ticket='https://st.yandex-team.ru/TAXIREL-6',
            ),
            id='backend_py3_attach_resources_after_service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/service.yaml'],
                        'clownductor: {sandbox-resources: '
                        '[{source-path: bla, destination-path: bla1, '
                        'owner: gilfanovii}]}',
                    ),
                ],
                master_commits=[
                    repository.Commit(
                        'changelog_resources',
                        ['services/taxi-adjust/debian/changelog'],
                        (
                            'taxi-adjust (0.0.1resources1) unstable;'
                            ' urgency=low\n\n'
                            '  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-1\n\n'
                            '  deploy-type:resource\n'
                            '  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2018 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                ticket_status='open',
                ticket_components=[],
                release_ticket='https://st.yandex-team.ru/TAXIREL-1',
                deploy_type='service',
                update_ticket={
                    'ticket': 'TAXIREL-1',
                    'json': {
                        'summary': 'summary, 0.0.2',
                        'description': (
                            'some\ntext\n\n' '0.0.2:\n' 'alberist | commit1'
                        ),
                        'followers': {'add': ['alberist']},
                    },
                },
                version='taxi-adjust (0.0.2)',
                release_tag='taxi-adjust/0.0.2',
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-1'
                    '\n\n'
                ),
                changes=(
                    '  * alberist | Ololo\n\n'
                    '  New release changes:\n'
                    '  * alberist | commit1'
                ),
                telegram_disabled='1',
                slack_disabled='1',
                created_comment=None,
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
            ),
            id='backend_py3_attach_service_after_resources',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[],
                fail={
                    'description': (
                        'Wrong schema in service.yaml for sandbox-resources: '
                        'required key not provided \'clownductor\''
                    ),
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Wrong schema in service.yaml for sandbox-resources: '
                        'required key not provided \'clownductor\''
                    ),
                },
                created_comment=None,
                deploy_type='sandbox-resources',
            ),
            id='backend_py3_sanbox_resources_no_clown_info',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                master_commits=[
                    repository.Commit(
                        'changelog_new',
                        ['services/taxi-adjust/debian/changelog'],
                        (
                            'taxi-adjust (0.0.3.hotfix1) unstable; urgency=low'
                            '\n\n  Release ticket https://st.yandex-team.ru/'
                            'TAXIREL-6\n\n  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n\n'
                        ),
                    ),
                ],
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/1', 'services/taxi/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.0.4',
                },
                version='taxi-adjust (0.0.4)',
                release_tag='taxi-adjust/0.0.4',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.0.4`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.0.4`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3_taxi_adjust_diverged_changelog',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1', ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2', ['taxi/2', 'services/taxi-corp/2'],
                    ),
                    repository.Commit('commit3', ['taxi/3'], author='oyaso'),
                    repository.Commit(
                        'commit4',
                        ['services/taxi-corp/4', 'services/taximeter/4'],
                    ),
                    repository.Commit(
                        'new-service', ['services/taxix/debian/changelog'],
                    ),
                    repository.Commit(
                        'new testsuite 2.0',
                        [],
                        submodules=[
                            repository.SubmoduleCommits(
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit 2', ['test4'],
                                    ),
                                ],
                                reinit_if_exists=True,
                                origin_dir='second_submodules_testsuite',
                            ),
                        ],
                    ),
                    repository.Commit(
                        'new testsuite update',
                        [],
                        submodules=[
                            repository.SubmoduleCommits(
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit 3', ['test5'],
                                    ),
                                ],
                                origin_dir='second_submodules_testsuite',
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | new testsuite 2.0\n'
                        'alberist | new testsuite update\n'
                        'oyaso | commit3'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * alberist | new testsuite update\n'
                '  * alberist | new testsuite 2.0\n'
                '  * oyaso | commit3\n'
                '  * alberist | commit2',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 taxi-adjust new_submodule_url',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/1', 'services/taxi/1'],
                    ),
                    repository.Commit(
                        'commit2', ['taxi/2', 'services/taxi-corp/2'],
                    ),
                    repository.Commit('commit3', ['taxi/3'], author='oyaso'),
                    repository.Commit(
                        'commit4',
                        ['services/taxi-corp/4', 'services/taximeter/4'],
                        author='ivanov',
                    ),
                    repository.Commit(
                        'commit5', ['services/taxi-adjust/5'], author='oyaso',
                    ),
                    repository.Commit(
                        'commit6', ['services/taxi-corp/6'], author='petrov',
                    ),
                    repository.Commit('commit7', ['taxi/7'], author='ivanov'),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'alberist | commit1\n'
                        'oyaso | commit5\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'ivanov | commit7\n'
                        'oyaso | commit3'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit5\n'
                '  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * ivanov | commit7\n'
                '  * oyaso | commit3\n'
                '  * alberist | commit2',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
                created_comment=None,
            ),
            id='backend_py3 audit simplify',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1', ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2', ['taxi/2', 'services/taxi-corp/2'],
                    ),
                    repository.Commit(
                        'commit3\n\n'
                        'Relates: TAXITOOLS-1\n\n'
                        'Testing: Проверял в unstable, покрыто автотестами.\n'
                        'А этот тест в автокоммент попасть не должен.',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit4',
                        ['services/taxi-corp/4', 'services/taximeter/4'],
                        author='ivanov',
                    ),
                    repository.Commit(
                        'commit5 (#1000)\n\n'
                        'Testing: На прод не влияет. Хотя могла бы!\n\n'
                        'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit6', ['services/taxi-corp/6'], author='petrov',
                    ),
                    repository.Commit('commit7', ['taxi/7'], author='ivanov'),
                    repository.Commit(
                        'commit8 (#1001)\n\n'
                        'Testing: Еще раз очень хорошо тестировал!\n'
                        'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit9 (#1002)\n\n'
                        'Tests: Последний раз очень хорошо тестировал!\n'
                        'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit10 (#1042)\n\n'
                        'Testing: Тестирование нескольких тасок!\n'
                        'Relates: TAXITOOLS-3, TAXITOOLS-4, TAXITOOLS-5',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit11 (#1005)\n\n'
                        'Testing: И еще одна перетестирована!\n'
                        'Relates: TAXITOOLS-5',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit12\n\n' 'Testing: Коммит без relates!\n',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit13 (#1006)\n\n'
                        'Testing: Первый тэг тестинга.\n'
                        'Testing: Второй тэг тестинга.\n'
                        'Relates: TAXITOOLS-6',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit14 (#1007)\n\n'
                        'Этот коммит никуда не попадет, потому что '
                        'тестирования нет.\n'
                        'Relates: TAXITOOLS-3',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit15 (#1008)\n\n'
                        'Этот коммит не попадет в комментарий о '
                        'тестировании.\n'
                        'Relates: TAXITOOLS-7',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit16 (#1009)\n\n'
                        'Этот коммит будет с пометкой, что тестирования нет.\n'
                        'Relates: TAXITOOLS-8',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit17 (#1010)\n\n'
                        'Tested: Проверено в unstable.\n'
                        'Relates: TAXITOOLS-8, TAXITOOLS-9',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit18 (#1011)\n\n'
                        'Testing: Общие изменения, никуда не попадет.\n'
                        'Relates: TAXITOOLS-8',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-6\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n'
                        'TAXITOOLS-9\n'
                        'alberist | commit1\n'
                        'oyaso | commit12\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'ivanov | commit7\n'
                        'https://st.yandex-team.ru/TAXITOOLS-4\n'
                        'https://st.yandex-team.ru/TAXITOOLS-5'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[
                    {'ticket': 'TAXITOOLS-1'},
                    {'ticket': 'TAXITOOLS-2'},
                    {'ticket': 'TAXITOOLS-3'},
                    {'ticket': 'TAXITOOLS-6'},
                    {'ticket': 'TAXITOOLS-7'},
                    {'ticket': 'TAXITOOLS-8'},
                    {'ticket': 'TAXITOOLS-9'},
                ],
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TAXITOOLS-1\n'
                        '""Pull Request (hash commit 1234): '
                        'Проверял в unstable, покрыто автотестами.""\n\n'
                        'TAXITOOLS-2\n'
                        '""Pull Request (#1000): '
                        'На прод не влияет. Хотя могла бы!""\n'
                        '""Pull Request (#1001): '
                        'Еще раз очень хорошо тестировал!""\n'
                        '""Pull Request (#1002): '
                        'Последний раз очень хорошо тестировал!""\n\n'
                        'TAXITOOLS-6\n'
                        '""Pull Request (#1006): '
                        'Первый тэг тестинга. Второй тэг тестинга.""\n\n'
                        'TAXITOOLS-8\n'
                        '""Pull Request (#1009): ""'
                        '\n'
                        '""Pull Request (#1010): '
                        'Проверено в unstable.""\n\n'
                        'TAXITOOLS-9\n'
                        '""Pull Request (#1010): '
                        'Проверено в unstable.""\n\n'
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-6\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n'
                        'TAXITOOLS-9\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-6\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n'
                        'TAXITOOLS-9'
                    ),
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit17 (#1010)\n'
                '  * oyaso | commit16 (#1009)\n'
                '  * oyaso | commit15 (#1008)\n'
                '  * oyaso | commit14 (#1007)\n'
                '  * oyaso | commit13 (#1006)\n'
                '  * oyaso | commit12\n'
                '  * oyaso | commit9 (#1002)\n'
                '  * oyaso | commit8 (#1001)\n'
                '  * oyaso | commit5 (#1000)\n'
                '  * oyaso | commit3\n'
                '  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * oyaso | commit18 (#1011)\n'
                '  * oyaso | commit11 (#1005)\n'
                '  * oyaso | commit10 (#1042)\n'
                '  * ivanov | commit7\n'
                '  * alberist | commit2',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
            ),
            id='backend_py3 with testing message',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1', ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2', ['taxi/2', 'services/taxi-corp/2'],
                    ),
                    repository.Commit(
                        'commit3\n\n'
                        'Relates: TAXITOOLS-1\n\n'
                        'Testing: Проверял в unstable, покрыто автотестами.\n'
                        'А этот тест в автокоммент попасть не должен.',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit4',
                        ['services/taxi-corp/4', 'services/taximeter/4'],
                        author='ivanov',
                    ),
                    repository.Commit(
                        'commit5 (#1000)\n\n'
                        'Testing: На прод не влияет. Хотя могла бы!\n\n'
                        'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit6', ['services/taxi-corp/6'], author='petrov',
                    ),
                    repository.Commit('commit7', ['taxi/7'], author='ivanov'),
                    repository.Commit(
                        'commit8 (#1001)\n\n'
                        'Testing: Еще раз очень хорошо тестировал!\n'
                        'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit9 (#1002)\n\n'
                        'Tests: Последний раз очень хорошо тестировал!\n'
                        'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit10 (#1042)\n\n'
                        'Testing: Тестирование нескольких тасок!\n'
                        'Relates: TAXITOOLS-3, TAXITOOLS-4, TAXITOOLS-5',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit11 (#1005)\n\n'
                        'Testing: И еще одна перетестирована!\n'
                        'Relates: TAXITOOLS-5',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit12\n\n' 'Testing: Коммит без relates!\n',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit13 (#1006)\n\n'
                        'Testing: Первый тэг тестинга.\n'
                        'Testing: Второй тэг тестинга.\n'
                        'Relates: TAXITOOLS-6',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit14 (#1007)\n\n'
                        'Этот коммит никуда не попадет, потому что '
                        'тестирования нет.\n'
                        'Relates: TAXITOOLS-3',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit15 (#1008)\n\n'
                        'Этот коммит не попадет в комментарий о '
                        'тестировании.\n'
                        'Relates: TAXITOOLS-7',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit16 (#1009)\n\n'
                        'Этот коммит будет с пометкой, что тестирования нет.\n'
                        'Relates: TAXITOOLS-8',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit17 (#1010)\n\n'
                        'Tested: Проверено в unstable.\n'
                        'Relates: TAXITOOLS-8, TAXITOOLS-9',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit18 (#1011)\n\n'
                        'Testing: Общие изменения, никуда не попадет.\n'
                        'Relates: TAXITOOLS-8',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit19 (#1100)\n\n'
                        'Testing: Тестирование многих тасок,'
                        ' чтобы было больше 3 тикетов в common changes!\n'
                        'Relates: https://st.yandex-team.ru/TAXITOOLS-15,'
                        ' https://st.yandex-team.ru/TAXITOOLS-16,'
                        ' https://st.yandex-team.ru/TAXITOOLS-17',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-6\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n'
                        'TAXITOOLS-9\n'
                        'alberist | commit1\n'
                        'oyaso | commit12\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'ivanov | commit7\n'
                        '<{Tickets\n'
                        'https://st.yandex-team.ru/TAXITOOLS-15\n'
                        'https://st.yandex-team.ru/TAXITOOLS-16\n'
                        'https://st.yandex-team.ru/TAXITOOLS-17\n'
                        'https://st.yandex-team.ru/TAXITOOLS-4\n'
                        'https://st.yandex-team.ru/TAXITOOLS-5\n'
                        '}>'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[
                    {'ticket': 'TAXITOOLS-1'},
                    {'ticket': 'TAXITOOLS-2'},
                    {'ticket': 'TAXITOOLS-3'},
                    {'ticket': 'TAXITOOLS-6'},
                    {'ticket': 'TAXITOOLS-7'},
                    {'ticket': 'TAXITOOLS-8'},
                    {'ticket': 'TAXITOOLS-9'},
                ],
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TAXITOOLS-1\n'
                        '""Pull Request (hash commit 1234): '
                        'Проверял в unstable, покрыто автотестами.""\n\n'
                        'TAXITOOLS-2\n'
                        '""Pull Request (#1000): '
                        'На прод не влияет. Хотя могла бы!""\n'
                        '""Pull Request (#1001): '
                        'Еще раз очень хорошо тестировал!""\n'
                        '""Pull Request (#1002): '
                        'Последний раз очень хорошо тестировал!""\n\n'
                        'TAXITOOLS-6\n'
                        '""Pull Request (#1006): '
                        'Первый тэг тестинга. Второй тэг тестинга.""\n\n'
                        'TAXITOOLS-8\n'
                        '""Pull Request (#1009): ""'
                        '\n'
                        '""Pull Request (#1010): '
                        'Проверено в unstable.""\n\n'
                        'TAXITOOLS-9\n'
                        '""Pull Request (#1010): '
                        'Проверено в unstable.""\n\n'
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-6\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n'
                        'TAXITOOLS-9\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n'
                        'TAXITOOLS-6\n'
                        'TAXITOOLS-7\n'
                        'TAXITOOLS-8\n'
                        'TAXITOOLS-9'
                    ),
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit17 (#1010)\n'
                '  * oyaso | commit16 (#1009)\n'
                '  * oyaso | commit15 (#1008)\n'
                '  * oyaso | commit14 (#1007)\n'
                '  * oyaso | commit13 (#1006)\n'
                '  * oyaso | commit12\n'
                '  * oyaso | commit9 (#1002)\n'
                '  * oyaso | commit8 (#1001)\n'
                '  * oyaso | commit5 (#1000)\n'
                '  * oyaso | commit3\n'
                '  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * oyaso | commit19 (#1100)\n'
                '  * oyaso | commit18 (#1011)\n'
                '  * oyaso | commit11 (#1005)\n'
                '  * oyaso | commit10 (#1042)\n'
                '  * ivanov | commit7\n'
                '  * alberist | commit2',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
            ),
            id='backend_py3 with testing message, collapsed common changes'
            ' and full ticket urls',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1\n\n' 'Relates: TAXITOOLS-1',
                        ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2\n\n' 'Relates: TAXITOOLS-2',
                        ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit3\n\n' 'Relates: TAXITOOLS-3',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit9 (#1002)\n\n' 'Relates: TAXITOOLS-9',
                        ['services/taxi-corp/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit10 (#1042)\n\n' 'Relates: TAXITOOLS-10',
                        ['taxi/2', 'services/taxi-adjust/23'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit12 (#1006)\n\n' 'Relates: TAXITOOLS-12',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-10\n'
                        'TAXITOOLS-12\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[
                    {'ticket': 'TAXITOOLS-1'},
                    {'ticket': 'TAXITOOLS-10'},
                    {'ticket': 'TAXITOOLS-12'},
                    {'ticket': 'TAXITOOLS-2'},
                    {'ticket': 'TAXITOOLS-3'},
                ],
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из тикетов:\n'
                        'TAXITOOLS-1\n'
                        'На прод не влияет\n'
                        'TAXITOOLS-10\n'
                        'протестировано локально тестсьютом\n'
                        'TAXITOOLS-12\n'
                        'на сервисы не влияет, проверялось локально\n'
                        '<{TAXITOOLS-2\n'
                        'Длинный комментарий, который должен\n'
                        'полностью уйти под кат}>\n'
                        '<{TAXITOOLS-3\n'
                        'Проверил в тимсити\n\n----\n\n'
                        'покрыл тестами, проверил локально}>\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-10\n'
                        'TAXITOOLS-12\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3'
                    ),
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit12 (#1006)\n'
                '  * oyaso | commit10 (#1042)\n'
                '  * oyaso | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
                tickets_comments={
                    'TAXITOOLS-1': plugin_startrek.TicketComments(
                        [
                            {
                                'text': (
                                    'ОТЧЕТ О ТЕСТИРОВАНИИ: '
                                    'На прод не влияет'
                                ),
                            },
                        ],
                    ),
                    'TAXITOOLS-2': plugin_startrek.TicketComments(
                        [
                            {'text': 'Несвязанный комментарий'},
                            {
                                'text': (
                                    'Отчёт о тестировании:\n'
                                    'Длинный комментарий, который должен\n'
                                    'полностью уйти под кат'
                                ),
                            },
                            {'text': 'Другой несвязанный комментарий'},
                        ],
                    ),
                    'TAXITOOLS-3': plugin_startrek.TicketComments(
                        [
                            {
                                'text': (
                                    '    Отчёт о тестировании:\n'
                                    'Проверил в тимсити'
                                ),
                            },
                            {
                                'text': (
                                    'Отчёт о тестировании: '
                                    'покрыл тестами, проверил локально'
                                ),
                            },
                        ],
                    ),
                    'TAXITOOLS-10': plugin_startrek.TicketComments(
                        [
                            {
                                'text': (
                                    '  Отчёт о тестировании:   \n'
                                    'протестировано локально тестсьютом'
                                ),
                            },
                        ],
                    ),
                    'TAXITOOLS-12': plugin_startrek.TicketComments(
                        [
                            {
                                'text': (
                                    'Отчёт о тестировании:\n'
                                    'на сервисы не влияет, '
                                    'проверялось локально'
                                ),
                            },
                        ],
                    ),
                },
                ticket_status='closed',
            ),
            id='backend_py3 ticket testing comment',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1\n\n'
                        'Testing: На прод не влияет\n'
                        'Relates: TAXITOOLS-1',
                        ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit5 (#1000)\n\n' 'Relates: TAXITOOLS-5\n',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit14 (#1008)\n\n' 'Relates: TAXITOOLS-14',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit18 (#1011)\n\n' 'Relates: TAXITOOLS-18',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-14\n'
                        'TAXITOOLS-5\n\n'
                        'Common changes:\n'
                        'https://st.yandex-team.ru/TAXITOOLS-18'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[
                    {'ticket': 'TAXITOOLS-1'},
                    {'ticket': 'TAXITOOLS-14'},
                    {'ticket': 'TAXITOOLS-5'},
                ],
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TAXITOOLS-1\n'
                        '""Pull Request (hash commit 1234): '
                        'На прод не влияет""\n\n'
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-14\n'
                        'TAXITOOLS-5\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-14\n'
                        'TAXITOOLS-5\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-14\n'
                        'TAXITOOLS-5'
                    ),
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit14 (#1008)\n'
                '  * oyaso | commit5 (#1000)\n'
                '  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * oyaso | commit18 (#1011)',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
                tickets_comments={
                    'TAXITOOLS-14': plugin_startrek.TicketComments(
                        comment_list=[
                            {
                                'text': (
                                    'Долгая история из жизни, когда '
                                    'не нужен был отчет о тестировании\n'
                                    'Отчет о тестировании: '
                                    'Проверено автотестами.'
                                ),
                            },
                        ],
                    ),
                },
            ),
            id='backend_py3 all cases testing comment',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1\n\n'
                        'Relates: https://st.yandex-team.ru/TAXITOOLS-1',
                        ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'TAXITOOLS-1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[{'ticket': 'TAXITOOLS-1'}],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-1\n\n'
                        '@oxcd8o отпишитесь о тестировании и/или '
                        'переведите тикеты из статуса "Открыт"'
                    ),
                    'summonees': ['oxcd8o'],
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                tickets_comments={},
                ticket_assignee='oxcd8o',
                ticket_status='closed',
            ),
            id='backend_py3 strange ticket testing comment',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1\n\n'
                        'Testing: На прод не влияет\n'
                        'Relates: TAXITOOLS-1',
                        ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit5 (#1000)\n\n' 'Relates: TAXITOOLS-5\n',
                        ['services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit14 (#1008)\n\n' 'Relates: TAXITOOLS-14',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit18 (#1011)\n\n' 'Relates: TAXITOOLS-18',
                        ['taxi/2', 'services/taxi-corp/2'],
                        author='oyaso',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-14\n'
                        'TAXITOOLS-5\n\n'
                        'Common changes:\n'
                        'https://st.yandex-team.ru/TAXITOOLS-18'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[
                    {'ticket': 'TAXITOOLS-1'},
                    {'ticket': 'TAXITOOLS-14'},
                    {'ticket': 'TAXITOOLS-5'},
                ],
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TAXITOOLS-1\n'
                        '""Pull Request (hash commit 1234): '
                        'На прод не влияет""\n\n'
                        '====Отчёты о тестировании из тикетов:\n'
                        'TAXITOOLS-14\n'
                        'Проверено автотестами.\n\n'
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'TAXITOOLS-5\n\n'
                        '@aselutin отпишитесь о тестировании и/или '
                        'переведите тикеты из статуса "Открыт"'
                    ),
                    'summonees': ['aselutin'],
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit14 (#1008)\n'
                '  * oyaso | commit5 (#1000)\n'
                '  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * oyaso | commit18 (#1011)',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
                tickets_comments={
                    'TAXITOOLS-14': plugin_startrek.TicketComments(
                        [
                            {
                                'text': (
                                    'Отчет о тестировании: '
                                    'Проверено автотестами.'
                                ),
                            },
                        ],
                    ),
                },
                ticket_assignee='aselutin',
                ticket_status='closed',
            ),
            id='backend_py3 testing comment summon',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit2 (#1002)\n\n' 'Relates: SECRET-1',
                        ['services/taxi-adjust/1', 'taxi/2'],
                        author='rumkex',
                    ),
                    repository.Commit(
                        'commit3 (#1003)\n\n' 'Relates: SECRET-2',
                        ['services/taxi-adjust/1', 'taxi/2'],
                        author='rumkex',
                    ),
                    repository.Commit(
                        'commit4 (#1004)\n\n' 'Relates: ANOTHER-1',
                        ['services/taxi-adjust/1', 'taxi/2'],
                        author='rumkex',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'ANOTHER-1\nSECRET-1\nSECRET-2',
                    'followers': ['rumkex'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                get_ticket=[
                    {'ticket': 'ANOTHER-1'},
                    {'ticket': 'SECRET-1'},
                    {'ticket': 'SECRET-2'},
                ],
                ticket_assignee='rumkex',
                created_comment={
                    'summonees': ['rumkex'],
                    'text': (
                        '====Для следующих тикетов не было обнаружено отчётов '
                        'о тестировании:\n'
                        'ANOTHER-1\nSECRET-1\nSECRET-2\n\n'
                        '====По следующим тикетам проверку выполнить '
                        'не удалось:\n'
                        'ANOTHER-1\nSECRET-1\nSECRET-2\n'
                        'Проверьте доступ робота к очередям\n\n'
                        '@rumkex отпишитесь о тестировании и/или переведите '
                        'тикеты из статуса "Открыт"'
                    ),
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * rumkex | commit4 (#1004)\n'
                '  * rumkex | commit3 (#1003)\n'
                '  * rumkex | commit2 (#1002)',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_rumkex'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@rumkex'
                ),
                staff_calls=['rumkex'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'rumkex'},
                tickets_comments={
                    'SECRET-1': plugin_startrek.TicketComments(
                        error_message='Нет доступа', status_code=403,
                    ),
                    'SECRET-2': plugin_startrek.TicketComments(
                        error_message='Нет доступа', status_code=403,
                    ),
                    'ANOTHER-1': plugin_startrek.TicketComments(
                        error_message='Нет доступа', status_code=403,
                    ),
                },
                ticket_status='closed',
            ),
            id='backend_py3 check autocomment with inaccessible tickets',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1\n\n'
                        'Testing: На прод не влияет\n'
                        'Relates: TAXITOOLS-1',
                        ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit14 (#1008)\n\n' 'Relates: TAXITOOLS-14',
                        ['taxi/2', 'services/taxi-adjust/5'],
                        author='oyaso',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': 'TAXITOOLS-1\nTAXITOOLS-14',
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TAXITOOLS-1\n'
                        '""Pull Request (hash commit 1234): '
                        'На прод не влияет""'
                    ),
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * oyaso | commit14 (#1008)\n'
                '  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
                tickets_comments={
                    'TAXITOOLS-14': plugin_startrek.TicketComments(
                        [
                            {
                                'text': (
                                    'Отчет о тестировании: '
                                    'Проверено автотестами.'
                                ),
                            },
                        ],
                    ),
                },
                ticket_assignee='aselutin',
                ticket_status='closed',
                disable_test_ticket_checks='yes',
            ),
            id='backend_py3 with test comment check disabled',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3_move.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'alberist | after-corp-adjust\n'
                        'alberist | before-corp-adjust\n'
                        'alberist | move-services\n\n'
                        'Common changes:\n'
                        'alberist | after-corp-taxi\n'
                        'alberist | after-taxi\n'
                        'alberist | before-corp-taxi\n'
                        'alberist | before-taxi'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                commits=[],
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes=(
                    '  * alberist | after-corp-adjust\n'
                    '  * alberist | move-services\n'
                    '  * alberist | before-corp-adjust\n\n'
                    '  Common changes:\n'
                    '  * alberist | after-corp-taxi\n'
                    '  * alberist | after-taxi\n'
                    '  * alberist | before-corp-taxi\n'
                    '  * alberist | before-taxi'
                ),
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 taxi-adjust move',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3_move.init,
                branch='masters/taxi-corp',
                path='services/taxi-corp',
                created_ticket={
                    'assignee': None,
                    'components': [100, 42],
                    'description': (
                        'alberist | after-corp-adjust\n'
                        'alberist | after-corp-only\n'
                        'alberist | after-corp-taxi\n'
                        'alberist | before-corp-adjust\n'
                        'alberist | before-corp-only\n'
                        'alberist | before-corp-taxi\n'
                        'alberist | move-services\n\n'
                        'Common changes:\n'
                        'alberist | after-taxi\n'
                        'alberist | before-taxi'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-corp 0.1.3',
                },
                commits=[],
                version='taxi-corp (0.1.3)',
                release_tag='taxi-corp/0.1.3',
                changes=(
                    '  * alberist | after-corp-taxi\n'
                    '  * alberist | after-corp-adjust\n'
                    '  * alberist | after-corp-only\n'
                    '  * alberist | move-services\n'
                    '  * alberist | before-corp-taxi\n'
                    '  * alberist | before-corp-adjust\n'
                    '  * alberist | before-corp-only\n\n'
                    '  Common changes:\n'
                    '  * alberist | after-taxi\n'
                    '  * alberist | before-taxi'
                ),
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 taxi-corp move',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                component_name='backend-py2',
                commits=[
                    repository.Commit(
                        'commit1\n\n'
                        'Relates: TAXITOOLS-2\n\n'
                        'Testing: Проверял в unstable, покрыто автотестами.\n'
                        'А этот тест в автокоммент попасть не должен.',
                        ['file1'],
                        author='oyaso',
                    ),
                    repository.Commit(
                        'commit2 (#42)\n\n'
                        'Testing: На прод не влияет. Хотя могла бы!\n\n'
                        'Relates: TAXITOOLS-3',
                        ['file2'],
                        author='oyaso',
                    ),
                    repository.Commit('commit3', ['file3']),
                ],
                version='taxi-backend (3.0.225)',
                release_tag='3.0.225',
                changes='  * Mister Twister | commit message\n\n'
                '  New release changes:\n'
                '  * alberist | commit3\n'
                '  * oyaso | commit2 (#42)\n'
                '  * oyaso | commit1',
                release_ticket='https://st.yandex-team.ru/TAXIREL-123',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-123]'
                    '(https://st.yandex-team.ru/TAXIREL-123)\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-123|'
                    'TAXIREL-123>\n'
                    'Package: `taxi-backend`\n'
                    'Version: `3.0.225`\n'
                    '\n@alberist @oyaso'
                ),
                changelog_release_ticket=(
                    '  Release ticket https://st.yandex-team.ru/TAXIREL-123'
                    '\n\n'
                ),
                update_ticket={
                    'ticket': 'TAXIREL-123',
                    'json': {
                        'summary': 'summary, 3.0.225',
                        'description': (
                            'some\ntext\n\n'
                            '3.0.225:\n'
                            'TAXITOOLS-2\n'
                            'TAXITOOLS-3\n'
                            'alberist | commit3'
                        ),
                        'followers': {'add': ['alberist', 'oyaso']},
                    },
                },
                get_ticket=[
                    {'ticket': 'TAXITOOLS-2'},
                    {'ticket': 'TAXITOOLS-3'},
                ],
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TAXITOOLS-2\n'
                        '""Pull Request (hash commit 1234): '
                        'Проверял в unstable, покрыто автотестами.""\n\n'
                        'TAXITOOLS-3\n'
                        '""Pull Request (#42): '
                        'На прод не влияет. Хотя могла бы!""\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-2\n'
                        'TAXITOOLS-3'
                    ),
                },
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
            ),
            id='backend release ticket with testing message',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1', ['services/taxi-adjust/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'add new submodule',
                        [],
                        submodules=[
                            (
                                'submodules/awesome-lib',
                                [
                                    repository.Commit(
                                        'awesome lib init', ['f1', 'f2'],
                                    ),
                                    repository.Commit(
                                        'awesome lib update', ['f3', 'f4'],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | add new submodule'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  * alberist | commit1\n\n'
                '  Common changes:\n'
                '  * alberist | add new submodule',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 new submodule',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                    ),
                    repository.Commit('commit3', ['common/3']),
                    repository.Commit(
                        'commit4',
                        [
                            'services/driver-authorizer2/2',
                            'services/driver-authorizer2/3',
                        ],
                    ),
                    repository.Commit(
                        'commit5',
                        [],
                        submodules=[
                            (
                                'userver',
                                [repository.Commit('usr', ['f1', 'f2'])],
                            ),
                        ],
                    ),
                    repository.Commit(
                        'ignored commit',
                        [
                            'libraries/some-library/src/main.cpp',
                            '.github/CODEOWNERS',
                            'README.md',
                            'configs/declarations/some/CONFIG.yaml',
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | commit3\n'
                        'alberist | commit5\n'
                        'alberist | usr | userver'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit5\n'
                '  * alberist | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1\n'
                '  * alberist | usr | userver',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices driver-authorizer',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                    ),
                    repository.Commit(
                        'commit5',
                        [],
                        submodules=[
                            (
                                'userver',
                                [
                                    repository.Commit(
                                        'third party commit',
                                        ['f1', 'f2'],
                                        author='Jack Daniels',
                                        email='jack_daniels@yandex.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                    repository.Commit(
                        'commit6',
                        [],
                        submodules=[
                            (
                                'userver',
                                [
                                    repository.Commit(
                                        'approved third party commit',
                                        ['f1', 'f2'],
                                        author='oyaso',
                                        email='oyaso@yandex-team.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | commit5\n'
                        'alberist | commit6\n'
                        'oyaso | approved third party commit | userver'
                    ),
                    'followers': ['alberist', 'oyaso'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit6\n'
                '  * alberist | commit5\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1\n'
                '  * oyaso | approved third party commit | userver',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist @tg\\_oyaso'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist @oyaso'
                ),
                staff_calls=['alberist', 'oyaso'],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist oyaso',
                },
                created_comment=None,
            ),
            id='uservices third party submodule',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer3',
                path='services/driver-authorizer3',
                commits=[
                    repository.Commit('commit1', ['libraries/some-library/1']),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [95, 42],
                    'description': (
                        'Common libraries changes:\n' 'alberist | commit1'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer3 1.1.2',
                },
                version='driver-authorizer3 (1.1.2)',
                release_tag='driver-authorizer3/1.1.2',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer3`\n'
                    'Package: `driver-authorizer3`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer3`\n'
                    'Package: `driver-authorizer3`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices library release',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer3',
                path='services/driver-authorizer3',
                commits=[
                    repository.Commit('commit1', ['libraries/some-library/1']),
                    repository.Commit(
                        'commit2', ['services/driver-authorizer2/2'],
                    ),
                    repository.Commit(
                        'commit3', ['libraries/another-library/1'],
                    ),
                    repository.Commit(
                        'commit4', ['libraries/unused-library/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [95, 42],
                    'description': (
                        'Common libraries changes:\n' 'alberist | commit1'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer3 1.1.2',
                },
                version='driver-authorizer3 (1.1.2)',
                release_tag='driver-authorizer3/1.1.2',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer3`\n'
                    'Package: `driver-authorizer3`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer3`\n'
                    'Package: `driver-authorizer3`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices not-only-library release',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path=os.path.join('services', 'pilorama'),
                commits=[
                    repository.Commit(
                        'commit1',
                        [
                            os.path.join('services', 'pilorama', '1'),
                            os.path.join('taxi', '1'),
                        ],
                    ),
                    repository.Commit(
                        'pilorama',
                        [os.path.join('services', 'pilorama', 'service.yaml')],
                        files_content="""
project-name: yandex-taxi-pilorama
startrek-ticket-disabled: yes
""".lstrip(),
                    ),
                ],
                version='pilorama (1.1.2)',
                release_tag='pilorama/1.1.2',
                created_ticket=None,
                changes='  * alberist | pilorama\n' '  * alberist | commit1',
                telegram_message='',
                slack_message='',
                staff_calls=[],
                telegram_disabled='1',
                slack_disabled='1',
                changelog_release_ticket='',
                created_comment=None,
            ),
            id='uservices pilorama',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'add docs commit',
                        ['services/driver-authorizer/docs/yaml/api/api.yaml'],
                    ),
                ],
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | add docs commit',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-authorizer 1.1.2',
                    'queue': 'TAXIREL',
                    'description': 'alberist | add docs commit',
                    'components': [93],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='uservices driver_authorizer docs',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'add docs commit',
                        ['services/driver-authorizer/docs/yaml/api/api.yaml'],
                    ),
                    repository.Commit('add taxi 1', ['taxi/tools/1']),
                ],
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | add taxi 1\n'
                '  * alberist | add docs commit',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-authorizer 1.1.2',
                    'queue': 'TAXIREL',
                    'description': (
                        'alberist | add docs commit\n\n'
                        'Common changes:\n'
                        'alberist | add taxi 1'
                    ),
                    'components': [93],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='uservices driver_authorizer docs common',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'add docs commit',
                        [
                            'services/driver-authorizer/docs/yaml/api/'
                            'api.yaml',
                            'taxi/tools/1',
                        ],
                        submodules=[
                            repository.SubmoduleCommits(
                                'userver',
                                [
                                    repository.Commit(
                                        'edit changelog 0.59',
                                        ['ignore_me'],
                                        author='buildfarm buildfarm',
                                        email='buildfarm@yandex-team.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | add docs commit',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-authorizer 1.1.2',
                    'queue': 'TAXIREL',
                    'description': 'alberist | add docs commit',
                    'components': [93],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='uservices_driver_authorizer_united_commit',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'add docs commit',
                        [
                            'services/driver-authorizer2/docs/yaml/api/'
                            'api.yaml',
                            'services/pilorama/docs/yaml/api/api.yaml',
                        ],
                    ),
                    repository.Commit(
                        'add services commit',
                        [
                            'services/driver-authorizer2/src/authorizer.cpp',
                            'services/pilorama/src/some.hpp',
                        ],
                    ),
                    repository.Commit('add taxi 1', ['taxi/tools/1']),
                ],
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | add taxi 1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_ticket={
                    'summary': 'Backend driver-authorizer 1.1.2',
                    'queue': 'TAXIREL',
                    'description': (
                        'Common changes:\n' 'alberist | add taxi 1'
                    ),
                    'components': [93],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                created_comment=None,
            ),
            id='uservices driver_authorizer common commit',
        ),
        pytest.param(
            Params(
                init_repo=ml.init,
                branch='masters/taxi-plotva-ml',
                path=os.path.join('taxi-plotva-ml'),
                commits=[
                    repository.Commit(
                        'second commit\n\n' 'Relates: TAXITOOLS-2',
                        files=['taxi-plotva-ml/data_new', 'tools/data_new'],
                        submodules=[
                            (
                                'submodules/backend-py3',
                                [
                                    repository.Commit(
                                        'update submodule', ['file3'],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                version='taxi-plotva-ml (0.1.2)',
                release_tag='taxi-plotva-ml/0.1.2',
                created_ticket={
                    'summary': 'Taxi Ml Backend taxi-plotva-ml 0.1.2',
                    'queue': 'TAXIREL',
                    'description': 'TAXITOOLS-2',
                    'components': [89, 42],
                    'followers': ['alberist'],
                    'assignee': None,
                },
                ticket_summary='Taxi Ml Backend',
                changes='  * alberist | second commit',
                telegram_message='',
                slack_message='',
                staff_calls=[],
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                get_ticket=[{'ticket': 'TAXITOOLS-2'}],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено отчётов'
                        ' о тестировании:\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-2'
                    ),
                },
            ),
            id='taxi-plotva-ml',
        ),
        pytest.param(
            Params(
                init_repo=llvm_toolchain.init,
                branch='master',
                commits=[repository.Commit('commit1', ['test/1'])],
                version=(
                    'taxi-toolchain '
                    '(1:7.1.0~svn3-1~exp1~20190408084827.60-taxi2)'
                ),
                release_tag='1-7.1.0-svn3-1-exp1-20190408084827.60-taxi2',
                changes='  * alberist | commit1',
                increase_last_number_of_version='1',
                startrek_disabled='1',
                telegram_disabled='1',
                slack_disabled='1',
                changelog_release_ticket='',
                created_comment=None,
            ),
            id='llvm-toolchain',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                    ),
                    repository.Commit('commit3', ['common/3']),
                    repository.Commit(
                        'commit4',
                        [
                            'services/driver-authorizer2/2',
                            'services/driver-authorizer2/3',
                        ],
                    ),
                    repository.Commit(
                        'commit5',
                        [],
                        submodules=[
                            (
                                'userver',
                                [repository.Commit('usr', ['f1', 'f2'])],
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | commit3\n'
                        'alberist | commit5\n'
                        'alberist | usr | userver'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit5\n'
                '  * alberist | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1\n'
                '  * alberist | usr | userver',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                git_any_push_responses=((1, True), (2, False), (1, True)),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices_driver-authorizer_push_fail_release_success',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                    ),
                    repository.Commit('commit3', ['common/3']),
                    repository.Commit(
                        'commit4',
                        [
                            'services/driver-authorizer2/2',
                            'services/driver-authorizer2/3',
                        ],
                    ),
                    repository.Commit(
                        'commit5',
                        [],
                        submodules=[
                            (
                                'userver',
                                [
                                    repository.Commit(
                                        'some autocommit\n\n'
                                        'Relates: TAXITOOLS-666',
                                        ['f1', 'f2'],
                                        author='buildfarm buildfarm',
                                        email='buildfarm@yandex-team.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | commit3\n'
                        'alberist | commit5'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit5\n'
                '  * alberist | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                git_any_push_responses=((1, True), (20, False), (1, True)),
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Push to masters/driver-authorizer failed'
                    ),
                },
                fail={
                    'description': 'Push to masters/driver-authorizer failed',
                    'identity': None,
                },
                created_comment={
                    'text': (
                        'TeamCity auto-release 1.1.2 '
                        '((https://teamcity.taxi.yandex-team.ru/'
                        'viewLog.html?buildId=123 FAILED))\n'
                        '((https://wiki.yandex-team.ru/taxi/backend'
                        '/automatization/faq/#hotfix-or-release-failed '
                        'check the wiki))'
                    ),
                },
            ),
            id='uservices_driver-authorizer_push_fail_release_fail',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                git_any_push_responses=(
                    (1, False),
                    (1, True),
                    (1, False),
                    (1, True),
                    (1, False),
                    (1, True),
                ),
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices_driver-authorizer_retry_all_pushes_and_release_ok',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                    ),
                    repository.Commit('commit3', ['common/3']),
                    repository.Commit(
                        'commit4',
                        [
                            'services/driver-authorizer2/2',
                            'services/driver-authorizer2/3',
                        ],
                    ),
                    repository.Commit(
                        'commit5',
                        [],
                        submodules=[
                            (
                                'userver',
                                [
                                    repository.Commit(
                                        'some autocommit\n\n'
                                        'Relates: TAXITOOLS-666',
                                        ['f1', 'f2'],
                                        author='buildfarm buildfarm',
                                        email='buildfarm@yandex-team.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | commit3\n'
                        'alberist | commit5'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit5\n'
                '  * alberist | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                git_any_push_responses=((20, False), (1, True)),
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Some problem with push `develop` branch. See '
                        'https://wiki.yandex-team.ru/taxi/'
                        'backend/automatization/faq/#hotfix-or-release-failed '
                        'for details'
                    ),
                },
                fail={
                    'description': (
                        'Some problem with push `develop` branch. See '
                        'https://wiki.yandex-team.ru/taxi/'
                        'backend/automatization/faq/#hotfix-or-release-failed '
                        'for details'
                    ),
                    'identity': None,
                },
                created_comment={
                    'text': (
                        'TeamCity auto-release 1.1.2 '
                        '((https://teamcity.taxi.yandex-team.ru/'
                        'viewLog.html?buildId=123 FAILED))\n'
                        '((https://wiki.yandex-team.ru/taxi/backend'
                        '/automatization/faq/#hotfix-or-release-failed '
                        'check the wiki))'
                    ),
                },
            ),
            id='uservices_driver-authorizer_fail_push_develop_n_fail_release',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                    ),
                    repository.Commit('commit3', ['common/3']),
                    repository.Commit(
                        'commit4',
                        [
                            'services/driver-authorizer2/2',
                            'services/driver-authorizer2/3',
                        ],
                    ),
                    repository.Commit(
                        'commit5',
                        [],
                        submodules=[
                            (
                                'userver',
                                [
                                    repository.Commit(
                                        'some autocommit\n\n'
                                        'Relates: TAXITOOLS-666',
                                        ['f1', 'f2'],
                                        author='buildfarm buildfarm',
                                        email='buildfarm@yandex-team.ru',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'alberist | commit2\n'
                        'alberist | commit3\n'
                        'alberist | commit5'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | commit5\n'
                '  * alberist | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                git_any_push_responses=((2, True), (20, False), (1, True)),
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'Push Tags failed',
                },
                fail={'description': 'Push Tags failed', 'identity': None},
                created_comment={
                    'text': (
                        'TeamCity auto-release 1.1.2 '
                        '((https://teamcity.taxi.yandex-team.ru/'
                        'viewLog.html?buildId=123 FAILED))\n'
                        '((https://wiki.yandex-team.ru/taxi/backend'
                        '/automatization/faq/#hotfix-or-release-failed '
                        'check the wiki))'
                    ),
                },
            ),
            id='uservices_driver-authorizer_fail_push_tags_and_fail_release',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'commit2',
                        ['common/2', 'services/driver-authorizer2/2'],
                        email='root@users.noreply.github.yandex-team.ru',
                        author='root',
                    ),
                    repository.Commit(
                        'commit3',
                        ['common/3'],
                        email='megaboss.yandex.ru',
                        author='megaboss',
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common changes:\n'
                        'megaboss | commit3\n'
                        'root | commit2'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * megaboss | commit3\n'
                '  * root | commit2\n'
                '  * alberist | commit1',
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices driver-authorizer followers-from-staff',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'use config',
                        [
                            'services/driver-authorizer/'
                            'local-files-dependencies.txt',
                        ],
                        files_content='schemas/configs/declarations/da/C.yaml',
                    ),
                    repository.Commit(
                        'commit1', ['services/driver-authorizer/1', 'taxi/1'],
                    ),
                    repository.Commit(
                        'config1',
                        [
                            'schemas/configs/declarations/orphaned_configs/'
                            'SOME_ORPHANED_CONFIG.yaml',
                        ],
                    ),
                    repository.Commit(
                        'config2', ['schemas/configs/declarations/da/C.yaml'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit1\n\n'
                        'Common libraries changes:\n'
                        'alberist | config2\n\n'
                        'Common changes:\n'
                        'alberist | use config'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes=(
                    '  * alberist | config2\n'
                    '  * alberist | commit1\n'
                    '  * alberist | use config'
                ),
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices driver-authorizer shared config',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer3',
                path='services/driver-authorizer3',
                commits=[
                    repository.Commit(
                        'commit1', ['libraries/some-library/fre', 'aaa'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [95, 42],
                    'description': (
                        'Common libraries changes:\n' 'alberist | commit1'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer3 1.1.2',
                },
                version='driver-authorizer3 (1.1.2)',
                release_tag='driver-authorizer3/1.1.2',
                changes='  * alberist | commit1',
                telegram_disabled='1',
                slack_disabled='1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices driver-authorizer order related_dep',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path='services/pilorama',
                commits=[
                    repository.Commit(
                        'local-files-dependencies.txt',
                        ['services/pilorama/local-files-dependencies.txt'],
                        'schemas/postgresql/somedir\n'
                        'schemas/postgresql/pilorama',
                    ),
                    repository.Commit(
                        'st1\n\nRelates: TAXITOOLS-1',
                        [
                            'services/pilorama/taxi_adjust/file.sql',
                            'services/pilorama/migrations/file2.sql',
                            'services/pilorama/dir/migrations/file3.sql',
                        ],
                    ),
                    repository.Commit(
                        'st2\n\nRelates: TAXITOOLS-2',
                        ['services/pilorama/dir/migrations/file.sql'],
                    ),
                    repository.Commit(
                        'st3\n\nRelates: TAXITOOLS-3',
                        ['schemas/postgresql/pilorama/migrations/file.sql'],
                    ),
                    repository.Commit(
                        'st\n\nRelates: TAXITOOLS-4',
                        [
                            'services/driver-authorizer/dir/migrations/f.sql',
                            'schemas/postgresql/driver-authorizer/'
                            'migrations/file.sql',
                        ],
                    ),
                ],
                migration_tickets=[
                    'TAXITOOLS-1',
                    'TAXITOOLS-2',
                    'TAXITOOLS-3',
                ],
                created_ticket={
                    'assignee': None,
                    'components': [100, 42],
                    'description': (
                        'TAXITOOLS-1\nTAXITOOLS-2\n\n'
                        'Common libraries changes:\n'
                        'TAXITOOLS-3\n\n'
                        'Common changes:\n'
                        'alberist | local-files-dependencies.txt'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend pilorama 1.1.2',
                },
                version='pilorama (1.1.2)',
                release_tag='pilorama/1.1.2',
                changes=(
                    '  * alberist | st3\n'
                    '  * alberist | st2\n'
                    '  * alberist | st1\n'
                    '  * alberist | local-files-dependencies.txt'
                ),
                telegram_disabled='1',
                slack_disabled='1',
                get_ticket=[
                    {'ticket': 'TAXITOOLS-1'},
                    {'ticket': 'TAXITOOLS-2'},
                ],
                created_comment={
                    'text': (
                        '====Для следующих тикетов не было обнаружено отчётов'
                        ' о тестировании:\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TAXITOOLS-1\n'
                        'TAXITOOLS-2'
                    ),
                },
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
            ),
            id='migration_tickets',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                commits=[
                    repository.Commit(
                        'commit1',
                        [
                            'services/driver-authorizer/local-files-'
                            'dependencies.txt',
                        ],
                    ),
                    repository.Commit(
                        'st2\n\nRelates: TAXITOOLS-2',
                        [
                            'services/driver-authorizer/build-dependencies-'
                            'debian.txt',
                        ],
                    ),
                    repository.Commit(
                        'commit3',
                        [
                            'services/driver-authorizer/local-files-'
                            'dependencies.txt',
                            'services/driver-authorizer/2',
                            'services/driver-authorizer/build-dependencies-'
                            'debian.txt',
                        ],
                    ),
                    repository.Commit(
                        'st4\n\nRelates: TAXITOOLS-4',
                        [
                            'services/driver-authorizer/local-files-'
                            'dependencies.txt',
                            'libraries/some-library/fre',
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [93],
                    'description': (
                        'alberist | commit3\n\n'
                        'Common libraries changes:\n'
                        'TAXITOOLS-4\n\n'
                        'Common changes:\n'
                        'alberist | commit1\n'
                        'https://st.yandex-team.ru/TAXITOOLS-2'
                    ),
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend driver-authorizer 1.1.2',
                },
                version='driver-authorizer (1.1.2)',
                release_tag='driver-authorizer/1.1.2',
                changes='  * alberist | st4\n'
                '  * alberist | commit3\n'
                '  * alberist | st2\n'
                '  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `driver-authorizer`\n'
                    'Package: `driver-authorizer`\n'
                    'Version: `1.1.2`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='uservices force_common_changes',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-adjust/local-files-dependencies.txt'],
                    ),
                    repository.Commit(
                        'commit2',
                        [
                            'services/taxi/2',
                            'services/taxi-adjust/debian-dev-dependencies.txt',
                        ],
                    ),
                    repository.Commit(
                        'commit3',
                        [
                            'services/taxi-corp/3',
                            'services/taxi-adjust/debian-dev-dependencies.txt',
                        ],
                    ),
                    repository.Commit(
                        'commit4',
                        [
                            'services/taxi-corp/4',
                            'services/taxi-corp/debian-dev-dependencies.txt',
                        ],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [78],
                    'description': (
                        'Common changes:\n'
                        'alberist | commit1\n'
                        'alberist | commit2\n'
                        'alberist | commit3'
                    ),
                    'followers': [],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-adjust 0.1.2',
                },
                version='taxi-adjust (0.1.2)',
                release_tag='taxi-adjust/0.1.2',
                changes='  Common changes:\n'
                '  * alberist | commit3\n'
                '  * alberist | commit2\n'
                '  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-adjust`\n'
                    'Package: `taxi-adjust`\n'
                    'Version: `0.1.2`'
                ),
                staff_calls=[],
                teamcity_set_parameters={'env.AFFECTED_USERS': ''},
                created_comment=None,
            ),
            id='backend_py3 force_common_changes',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-corp',
                path='services/taxi-corp',
                commits=[
                    repository.Commit(
                        'commit1',
                        ['services/taxi-corp/Dockerfile.some-service'],
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [100],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-corp 0.1.3',
                },
                version='taxi-corp (0.1.3)',
                release_tag='taxi-corp/0.1.3',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 taxi-corp no lxc',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-corp',
                path='services/taxi-corp',
                commits=[
                    repository.Commit(
                        comment='commit1',
                        files=['services/taxi-corp/service.yaml'],
                        files_content="""
docker-deploy: {}
""".lstrip(),
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [100],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-corp 0.1.3',
                },
                version='taxi-corp (0.1.3)',
                release_tag='taxi-corp/0.1.3',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 taxi-corp empty docker_deploy',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-corp',
                path='services/taxi-corp',
                commits=[
                    repository.Commit(
                        comment='commit1',
                        files=['services/taxi-corp/service.yaml'],
                        files_content="""
docker-deploy:
""".lstrip(),
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [100],
                    'description': 'alberist | commit1',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend taxi-corp 0.1.3',
                },
                version='taxi-corp (0.1.3)',
                release_tag='taxi-corp/0.1.3',
                changes='  * alberist | commit1',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `taxi-corp`\n'
                    'Package: `taxi-corp`\n'
                    'Version: `0.1.3`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='backend_py3 taxi-corp none docker_deploy',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/empty-service',
                path='services/empty-service',
                commits=[
                    repository.Commit(
                        'initial commit',
                        ['services/empty-service/debian/changelog'],
                        files_content=(
                            'empty-service (0.0.0) unstable; urgency=low\n\n'
                            '  * alberist | Ololo\n\n'
                            ' -- buildfarm <buildfarm@yandex-team.ru>  Wed, '
                            '19 May 2021 17:03:54 +0300\n'
                        ),
                    ),
                ],
                created_ticket={
                    'assignee': None,
                    'components': [100, 42],
                    'description': 'alberist | initial commit',
                    'followers': ['alberist'],
                    'queue': 'TAXIREL',
                    'summary': 'Backend empty-service 0.0.1',
                },
                version='empty-service (0.0.1)',
                release_tag='empty-service/0.0.1',
                changes='  * alberist | initial commit',
                telegram_message=(
                    'New release started\n'
                    'Ticket: [TAXIREL-222]'
                    '(https://st.yandex-team.ru/TAXIREL-222)\n'
                    'Service name: `empty-service`\n'
                    'Package: `empty-service`\n'
                    'Version: `0.0.1`\n'
                    '\n@tg\\_alberist'
                ),
                slack_message=(
                    'New release started\n'
                    'Ticket: <https://st.yandex-team.ru/TAXIREL-222|'
                    'TAXIREL-222>\n'
                    'Service name: `empty-service`\n'
                    'Package: `empty-service`\n'
                    'Version: `0.0.1`\n'
                    '\n@alberist'
                ),
                staff_calls=['alberist'],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'alberist'},
                created_comment=None,
            ),
            id='first_service_release',
        ),
    ],
)
def test_release(
        home_dir,
        monkeypatch,
        patch_requests,
        repos_dir,
        staff_persons_mock,
        startrek,
        teamcity_report_problems,
        teamcity_set_parameters,
        telegram,
        tmpdir,
        params: Params,
):
    # pylint: disable=too-many-branches
    if params.git_race_commits and params.git_any_push_responses:
        raise Exception('Race commits and push fails are mutually exclusive.')
    if params.component_name:
        monkeypatch.setenv('STARTREK_COMPONENT_NAME', params.component_name)
    if params.component_prefix:
        monkeypatch.setenv(
            'STARTREK_COMPONENT_PREFIX', params.component_prefix,
        )
    monkeypatch.setenv('BUILD_ID', '123')
    monkeypatch.setenv('RELEASE_TICKET_SUMMARY', params.ticket_summary)
    monkeypatch.setenv('TELEGRAM_BOT_CHAT_ID', 'tchatid')
    monkeypatch.setenv('SLACK_RELEASE_CHANNEL', 'some_channel')
    monkeypatch.setenv('ADD_FOLLOWERS', params.add_followers)
    monkeypatch.setenv('STARTREK_DISABLED', params.startrek_disabled)
    monkeypatch.setenv('TELEGRAM_DISABLED', params.telegram_disabled)
    monkeypatch.setenv('SLACK_DISABLED', params.slack_disabled)
    monkeypatch.setenv('NO_CHANGES_RELEASE_ENABLED', params.no_changes_enabled)
    monkeypatch.setenv(
        'ALLOW_EMPTY_RELEASE_TICKET', params.allow_empty_release_ticket,
    )
    monkeypatch.setenv(
        'INCREASE_LAST_NUMBER_OF_VERSION',
        params.increase_last_number_of_version,
    )
    if params.release_ticket is not None:
        monkeypatch.setenv('RELEASE_TICKET', params.release_ticket)

    # Force-enable autocomment feature in case it gets disabled in code
    monkeypatch.setenv(
        'DISABLE_TEST_COMMENT_CHECK', params.disable_test_ticket_checks,
    )
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'some_token')

    repo = params.init_repo(tmpdir)
    if params.master_commits:
        repo.git.checkout(params.branch)
        repository.apply_commits(repo, params.master_commits)
        repo.git.push('origin', params.branch)
        repo.git.checkout('develop')
    repository.apply_commits(repo, params.commits)
    repo.git.push('origin', 'develop')
    origin_url = next(repo.remotes[0].urls)

    git_config_file = home_dir / '.gitconfig'
    git_config = git.GitConfigParser(str(git_config_file), read_only=False)
    git_config.set_value('user', 'name', 'alberist')
    git_config.set_value('user', 'email', 'alberist@yandex-team.ru')

    git_config.set_value(
        'url "%s"' % repo.working_tree_dir,
        'insteadOf',
        'git@github.yandex-team.ru:taxi/backend.git',
    )

    without_sub_path = str(tmpdir.mkdir('repo_without_submodules'))
    args = [
        '--branch=' + params.branch,
        '--commit=' + params.branch,
        '--no-submodules',
        'git@github.yandex-team.ru:taxi/backend.git',
        str(without_sub_path),
    ]
    git_checkout.main(args)
    repo_without_submodules = git.Repo(without_sub_path)

    repo_without_submodules.git.remote('set-url', 'origin', origin_url)
    if params.component_opened:
        startrek.component_opened = params.component_opened
    if params.ticket_status:
        startrek.ticket_status = params.ticket_status
    if params.tickets_comments:
        startrek.comments = params.tickets_comments
    if params.ticket_assignee:
        startrek.ticket_assignee = params.ticket_assignee
    if params.ticket_components:
        startrek.ticket_components = params.ticket_components

    monkeypatch.chdir(repo_without_submodules.working_tree_dir)
    if params.version is None:
        with open(os.path.join(params.path, 'debian/changelog')) as fp:
            old_changelog = fp.read()

    if params.staff_error:

        @patch_requests('https://staff-api.yandex-team.ru/v3/persons')
        def _persons(method, url, **kwargs):
            return patch_requests.response(
                status_code=500,
                text='Emulating broken staff. Internal error.',
            )

    original_push_branch = git_repo.Repo.checkout_and_push_branch

    @patch_requests(slack_tools.SLACK_POST_URL)
    def slack_send_messages(method, url, **kwargs):
        return patch_requests.response(content='ok')

    def wrapper_push_branch(self, branch, **kwargs):
        if branch != 'develop':
            return original_push_branch(self, branch, **kwargs)

        if params.git_relates_hook:
            monkeypatch.setattr(
                'taxi_buildagent.utils._check_proc', wrapper_check_proc,
            )
        else:
            repository.add_commits_only_to_origin(
                repo_without_submodules, params.git_race_commits,
            )
        return original_push_branch(self, branch, **kwargs)

    def _is_push_successful_generator():
        for count, response in params.git_any_push_responses:
            for _ in range(count):
                yield response
        yield True

    generator = _is_push_successful_generator()

    def wrapper_push_branch_fail(self, branch, **kwargs):
        if not branch.startswith(('master', 'develop')):
            return original_push_branch(self, branch, **kwargs)
        if not next(generator):
            raise git_repo.GitRepoError('Push to %s failed' % branch)
        return original_push_branch(self, branch, **kwargs)

    def wrapper_push_tags_branch_fail(self, tag: str, remote: str = 'origin'):
        if not next(generator):
            raise git_repo.GitRepoError('Push Tags failed')

    def wrapper_check_proc(proc, output=None, error=None):
        raise utils.ShellError(
            'git exited with code 1: '
            'remote: backend/check-style.sh: '
            'failed with exit status 1\n'
            'remote: [POLICY] Commit '
            'a6477a67e873a8cde7dacadbee724ef8afe4da19 doesn\'t '
            'contain a relates ticket:\n'
            'remote: update\n'
            'To github.yandex-team.ru:taxi/backend.git\n'
            '! [remote rejected] develop -> develop '
            '(pre-receive hook declined)\n'
            'error: failed to push some refs to '
            '\'git@github.yandex-team.ru:taxi/backend.git\'',
        )

    if params.git_race_commits:
        monkeypatch.setattr(
            'taxi_buildagent.tools.vcs.git_repo.Repo.checkout_and_push_branch',
            wrapper_push_branch,
        )

    if params.git_any_push_responses:
        monkeypatch.setattr(
            'taxi_buildagent.tools.vcs.git_repo.Repo.checkout_and_push_branch',
            wrapper_push_branch_fail,
        )
        monkeypatch.setattr(
            'taxi_buildagent.tools.vcs.git_repo.Repo.push_tag',
            wrapper_push_tags_branch_fail,
        )

    args = []
    if params.disable_update_changelog:
        args = ['--changelog-disabled']
    args.extend(['--deploy-type', params.deploy_type])
    run_release.main(args)

    if params.created_ticket is None:
        assert startrek.create_ticket.calls == []
    else:
        assert startrek.create_ticket.calls == [
            {'json': params.created_ticket},
        ]

    if params.update_ticket is None:
        assert startrek.get_ticket.calls == params.get_ticket
        assert startrek.update_ticket.calls == []
    else:
        assert startrek.get_ticket.calls == [
            {'ticket': params.update_ticket['ticket']},
            *params.get_ticket,
        ]
        assert startrek.update_ticket.calls == [params.update_ticket]

    if params.created_comment is None:
        assert startrek.create_comment.calls == []
    else:
        calls = startrek.create_comment.calls
        for call in calls:
            call.get('json', {}).update(
                {
                    'text': HASH_COMMIT_REGEX.sub(
                        '(hash commit {})'.format(params.freeze_hash),
                        call.get('json', {}).get('text', ''),
                    ),
                },
            )

        expected_calls = [
            {'json': params.created_comment},
            *({'json': comment} for comment in params.extra_comments),
        ]

        assert calls == expected_calls

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

    calls = slack_send_messages.calls
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
        version = params.version.split('(')[-1].split(')')[0]
        if 'masters/' in params.branch:
            version = params.branch[len('masters/') :] + '/' + version
        migration_tickets = f'edit changelog {version}\n'
        if params.migration_tickets:
            migration_tickets += '\nMigration tickets:\n'
            migration_tickets += '\n'.join(params.migration_tickets) + '\n'
        commit_body = repo_without_submodules.git.log('-n1', '--format=%B')
        assert commit_body == migration_tickets
        with open(os.path.join(params.path, 'debian/changelog')) as fp:
            changelog = fp.readline()
            for line in fp:
                if line.startswith(' ') or line == '\n':
                    changelog += line
                else:
                    break
        assert changelog == (
            '%s unstable; urgency=low\n\n'
            '%s%s\n\n'
            ' -- buildfarm <buildfarm@yandex-team.ru>  '
            'Mon, 23 Apr 2018 17:22:56 +0300\n\n'
        ) % (params.version, params.changelog_release_ticket, params.changes)
    else:
        with open(os.path.join(params.path, 'debian/changelog')) as fp:
            changelog = fp.read()
        assert changelog == old_changelog

    assert (params.teamcity_set_parameters or {}) == {
        call['name']: call['value'] for call in teamcity_set_parameters.calls
    }
    assert repo_without_submodules.git.tag() == params.release_tag

    if params.fail:
        assert teamcity_report_problems.calls == [params.fail]
    else:
        if params.branch != 'develop':
            assert repo_without_submodules.active_branch.name == params.branch
            assert not repo_without_submodules.untracked_files
            if params.disable_update_changelog:
                assert repo_without_submodules.git.diff(
                    'develop', '--name-only',
                ) == os.path.join(params.path, 'debian', 'changelog')
            else:
                assert repo_without_submodules.git.diff('develop') == ''

            origin = git.Repo(next(repo_without_submodules.remotes[0].urls))
            assert _ls_tree(origin, params.branch) == _ls_tree(
                repo_without_submodules, params.branch,
            )


class ArcParams(NamedTuple):
    arc_calls: Sequence[Dict[str, Any]]
    tc_set_parameters_calls: Sequence[Dict[str, Any]]
    st_create_ticket_calls: Sequence[Dict[str, Any]]
    log_json: str
    changed_files_by_commit: Dict[str, Sequence[str]]
    exp_changelog: str
    no_changes_enabled: str = ''
    tc_report_problems_calls: Sequence[Dict[str, Any]] = []
    stable_branch: str = 'users/robot-taxi-teamcity/taxi/uservices/my-service'
    is_several_projects: bool = False
    revision: str = ''
    set_package_version_as_revision: bool = False
    tickets_comments: Dict[str, plugin_startrek.TicketComments] = {}
    ticket_status: Optional[str] = None
    ticket_assignee: Optional[str] = None
    created_comment: Optional[dict] = {
        'text': (
            '====Для следующих тикетов не было обнаружено отчётов о '
            'тестировании:\n'
            'TIKET-123\n\n'
            '====Следующие тикеты находятся в статусе "Открыт":\n'
            'TIKET-123\n\n'
            '====Следующие тикеты не имеют исполнителя:\n'
            'TIKET-123'
        ),
    }


@freezegun.freeze_time('2020-09-01 20:59:59', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ArcParams(
                arc_calls=[
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', '-b', 'tmp-lock', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'add', '--force', '$workdir/.lock'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'lock branch',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/lock/'
                            'release/taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service',
                            'trunk',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'rebase',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'r7777777'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/trunk',
                            'a141195',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            '-b',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'r7777777',
                            '-f',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service..arcadia/trunk',
                            '$workdir',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service..arcadia/trunk',
                            '$schemas_dir',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '45329c^',
                            '45329c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'add',
                            '$workdir/services/my-service/debian/changelog',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'edit changelog my-service/0.0.1',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            'releases/tplatform/taxi/services/'
                            'my-service/0.0.1',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'tag',
                            'taxi/uservices/my-service/0.0.1',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service/0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1:releases/tplatform/taxi/services/'
                            'my-service/0.0.1',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            '--delete',
                            'tags/users/robot-taxi-teamcity/lock/release/'
                            'taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                ],
                tc_set_parameters_calls=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                ],
                st_create_ticket_calls=[
                    {
                        'json': {
                            'assignee': None,
                            'components': [100, 42],
                            'description': (
                                'TIKET-123\n'
                                '\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TIKET-890'
                            ),
                            'followers': ['alberist', 'dteterin'],
                            'queue': 'TAXIREL',
                            'summary': 'uservices my-service 0.0.1',
                        },
                    },
                ],
                log_json='log1.json',
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/my-service/service.yaml',
                        'taxi/services/my-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/my-service/debian/changelog'],
                },
                exp_changelog='exp_changelog1.txt',
                revision='r7777777',
            ),
            id='with_revision',
        ),
        pytest.param(
            ArcParams(
                arc_calls=[
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', '-b', 'tmp-lock', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'add', '--force', '$workdir/.lock'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'lock branch',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/lock/release/'
                            'taxi/telematics',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/telematics',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'users/robot-taxi-teamcity/taxi/telematics',
                            'trunk',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'rebase',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            '-b',
                            'users/robot-taxi-teamcity/taxi/telematics',
                            'arcadia/trunk',
                            '-f',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics..arcadia/trunk',
                            '$workdir',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$graphdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$graphdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$graphdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics..arcadia/trunk',
                            '$graphdir',
                        ],
                        'kwargs': {
                            'cwd': '$graphdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$servicedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$servicedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$servicedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'telematics..arcadia/trunk',
                            '$servicedir',
                        ],
                        'kwargs': {
                            'cwd': '$servicedir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '7491ca^',
                            '7491ca',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            'bc4c6c^',
                            'bc4c6c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '45329c^',
                            '45329c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '7491ca^',
                            '7491ca',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            'bc4c6c^',
                            'bc4c6c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '7491ca^',
                            '7491ca',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            'bc4c6c^',
                            'bc4c6c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '7491ca^',
                            '7491ca',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            'bc4c6c^',
                            'bc4c6c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '7491ca^',
                            '7491ca',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            'bc4c6c^',
                            'bc4c6c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'releases/tplatform/taxi/telematics/0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'releases/tplatform/taxi/telematics/0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'add', '$workdir/debian/changelog'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'edit changelog 0.0.1',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/telematics',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            'releases/tplatform/taxi/telematics/0.0.1',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'tag',
                            'taxi/telematics/0.0.1',
                            'users/robot-taxi-teamcity/taxi/telematics',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'users/robot-taxi-teamcity/taxi/telematics',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/taxi/'
                            'telematics/0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'releases/tplatform/taxi/telematics/'
                            '0.0.1:releases/tplatform/taxi/telematics/0.0.1',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            '--delete',
                            'tags/users/robot-taxi-teamcity/lock/release/'
                            'taxi/telematics',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                ],
                tc_set_parameters_calls=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin seanchaidh',
                    },
                ],
                st_create_ticket_calls=[
                    {
                        'json': {
                            'assignee': None,
                            'components': [100, 42],
                            'description': (
                                'TICKET-9999\n'
                                'TIKET-123\n'
                                'TIKET-890\n'
                                'dteterin | Update uservices snapshot'
                                '(((https://a.yandex-team.ru/review/3845236 '
                                '3845236)))\n'
                                'dteterin | feat uservices: add .'
                                'arcignore(((https://a.yandex-team.ru/review/'
                                '8651573 8651573)))'
                            ),
                            'followers': [
                                'alberist',
                                'dteterin',
                                'seanchaidh',
                            ],
                            'queue': 'TAXIREL',
                            'summary': 'uservices 0.0.1',
                        },
                    },
                ],
                log_json='log1.json',
                changed_files_by_commit={
                    '12345a': [
                        'taxi/telematics/service.yaml',
                        'taxi/telematics/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/telematics/debian/changelog'],
                    'bc4c6c': ['taxi/services/aaa.yaml'],
                    '7491ca': ['taxi/graph/aaa.yaml'],
                },
                exp_changelog='exp_telematics_changelog.txt',
                stable_branch='users/robot-taxi-teamcity/taxi/telematics',
                is_several_projects=True,
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из пулл-реквестов:\n'
                        'TIKET-890\n'
                        '((https://a.yandex-team.ru/arc_vcs/commit/75757d '
                        'feat kek: kek)): '
                        'Вроде потестил\n\n'
                        '====Для следующих тикетов не было обнаружено отчётов '
                        'о тестировании:\n'
                        'TICKET-9999\n'
                        'TIKET-123\n\n'
                        '====Следующие тикеты находятся в статусе "Открыт":\n'
                        'TICKET-9999\n'
                        'TIKET-123\n'
                        'TIKET-890\n\n'
                        '====Следующие тикеты не имеют исполнителя:\n'
                        'TICKET-9999\n'
                        'TIKET-123\n'
                        'TIKET-890'
                    ),
                },
            ),
            id='additional_projects_case',
        ),
        pytest.param(
            ArcParams(
                arc_calls=[
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', '-b', 'tmp-lock', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'add', '--force', '$workdir/.lock'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'lock branch',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/lock/'
                            'release/taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'trunk',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'rebase',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            '-b',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                            '-f',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service..arcadia/trunk',
                            '$workdir',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service..arcadia/trunk',
                            '$schemas_dir',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '45329c^',
                            '45329c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'add',
                            '$workdir/services/my-service/debian/changelog',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'edit changelog my-service/0.0.1',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'tag',
                            'taxi/uservices/my-service/0.0.1',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service/0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1:releases/tplatform/taxi/services/'
                            'my-service/0.0.1',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            '--delete',
                            'tags/users/robot-taxi-teamcity/lock/release/'
                            'taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                ],
                tc_set_parameters_calls=[
                    {'name': 'env.AFFECTED_USERS', 'value': 'alberist'},
                ],
                st_create_ticket_calls=[
                    {
                        'json': {
                            'assignee': None,
                            'components': [100, 42],
                            'description': (
                                'TIKET-123\n'
                                '\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TIKET-890'
                            ),
                            'followers': ['alberist'],
                            'queue': 'TAXIREL',
                            'summary': 'uservices my-service 0.0.1',
                        },
                    },
                ],
                log_json='log3.json',
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/my-service/service.yaml',
                        'taxi/services/my-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/my-service/debian/changelog'],
                },
                exp_changelog='exp_changelog2.txt',
            ),
            id='arcadia_followers_blacklist_case',
        ),
        pytest.param(
            ArcParams(
                arc_calls=[
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', '-b', 'tmp-lock', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'add', '--force', '$workdir/.lock'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'lock branch',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/lock/'
                            'release/taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'trunk',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'rebase',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            '-b',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                            '-f',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service..arcadia/trunk',
                            '$workdir',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service..arcadia/trunk',
                            '$schemas_dir',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '45329c^',
                            '45329c',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '98989f^',
                            '98989f',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '12345a^',
                            '12345a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75757d^',
                            '75757d',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'releases/tplatform/taxi/services/my-service/'
                            '8380017',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'releases/tplatform/taxi/services/my-service/'
                            '8380017',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'add',
                            '$workdir/services/my-service/debian/changelog',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'edit changelog my-service/8380017',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            'releases/tplatform/taxi/services/my-service/'
                            '8380017',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'tag',
                            'taxi/uservices/my-service/8380017',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service/8380017',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'releases/tplatform/taxi/services/my-service/'
                            '8380017:releases/tplatform/taxi/services/'
                            'my-service/8380017',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            '--delete',
                            'tags/users/robot-taxi-teamcity/lock/release/'
                            'taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                ],
                tc_set_parameters_calls=[
                    {
                        'name': 'env.AFFECTED_USERS',
                        'value': 'alberist dteterin',
                    },
                ],
                st_create_ticket_calls=[
                    {
                        'json': {
                            'assignee': None,
                            'components': [100, 42],
                            'description': (
                                'TIKET-123\n'
                                '\n'
                                'Common changes:\n'
                                'https://st.yandex-team.ru/TIKET-890'
                            ),
                            'followers': ['alberist', 'dteterin'],
                            'queue': 'TAXIREL',
                            'summary': 'uservices my-service 8380017',
                        },
                    },
                ],
                log_json='log1.json',
                changed_files_by_commit={
                    '12345a': [
                        'taxi/services/my-service/service.yaml',
                        'taxi/services/my-service/src/main.cpp',
                    ],
                    '98989f': ['taxi/services/driver-authorizer/service.yaml'],
                    '75757d': ['taxi/services.yaml'],
                    '45329c': ['taxi/services/my-service/debian/changelog'],
                },
                exp_changelog='exp_revision_changelog.txt',
                set_package_version_as_revision=True,
            ),
            id='simple_revision_case',
        ),
        pytest.param(
            ArcParams(
                arc_calls=[
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', '-b', 'tmp-lock', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'add', '--force', '$workdir/.lock'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'lock branch',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/lock/'
                            'release/taxi/uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'trunk',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'rebase',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'checkout', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            '-b',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                            '-f',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service..arcadia/trunk',
                            '$workdir',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'merge-base',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            'arcadia/trunk',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'rev-parse', 'arcadia/trunk'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'log', '-n1', '--json', 'cbabc1'],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'log',
                            '--json',
                            'arcadia/users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service..arcadia/trunk',
                            '$schemas_dir',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$schemas_dir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$schemas_dir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '75fa4a^',
                            '75fa4a',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'diff',
                            '0417336^',
                            '0417336',
                            '$workdir',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'fetch',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'add',
                            '$workdir/services/my-service/debian/changelog',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'commit',
                            '--message',
                            'edit changelog my-service/0.0.1',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'checkout',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'reset',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1',
                            '--hard',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'tag',
                            'taxi/uservices/my-service/0.0.1',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'users/robot-taxi-teamcity/taxi/uservices/'
                            'my-service',
                            '--force',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'HEAD:tags/users/robot-taxi-teamcity/taxi/'
                            'uservices/my-service/0.0.1',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            'releases/tplatform/taxi/services/my-service/'
                            '0.0.1:releases/tplatform/taxi/services/'
                            'my-service/0.0.1',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'info', '--json'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': [
                            'arc',
                            'push',
                            '--delete',
                            'tags/users/robot-taxi-teamcity/lock/release/taxi/'
                            'uservices/my-service',
                        ],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                ],
                tc_set_parameters_calls=[
                    {'name': 'env.AFFECTED_USERS', 'value': 'nadya73'},
                ],
                tickets_comments={
                    'LAVKABACKEND-4653': plugin_startrek.TicketComments(
                        [{'text': 'Отчет о тестировании: testsuite'}],
                    ),
                    'LAVKABACKEND-4632': plugin_startrek.TicketComments(
                        [{'text': 'Отчет о тестировании: testsuite'}],
                    ),
                },
                created_comment={
                    'text': (
                        '====Отчёты о тестировании из тикетов:\n'
                        'LAVKABACKEND-4632\n'
                        'testsuite\n'
                        'LAVKABACKEND-4653\n'
                        'testsuite\n\n'
                        '====Для следующих тикетов не было обнаружено '
                        'отчётов о тестировании:\n'
                        'LAVKABACKEND-4631\n\n'
                        '@nadya73 отпишитесь о тестировании и/или '
                        'переведите тикеты из статуса "Открыт"'
                    ),
                    'summonees': ['nadya73'],
                },
                ticket_status='closed',
                ticket_assignee='nadya73',
                st_create_ticket_calls=[
                    {
                        'json': {
                            'assignee': None,
                            'components': [100, 42],
                            'description': (
                                'LAVKABACKEND-4631\n'
                                'LAVKABACKEND-4632\n'
                                'LAVKABACKEND-4653'
                            ),
                            'followers': ['nadya73'],
                            'queue': 'TAXIREL',
                            'summary': 'uservices my-service 0.0.1',
                        },
                    },
                ],
                log_json='log4.json',
                changed_files_by_commit={
                    '0417336': [
                        'taxi/services/my-service/service.yaml',
                        'taxi/services/my-service/src/main.cpp',
                    ],
                    '75fa4a': ['taxi/services/my-service/debian/changelog'],
                },
                exp_changelog='exp_changelog4.txt',
            ),
            id='attribute_ticket_case',
        ),
    ],
)
def test_arc_release(
        params: ArcParams,
        commands_mock,
        monkeypatch,
        tmpdir,
        load,
        startrek,
        teamcity_set_parameters,
        teamcity_report_problems,
):
    active_branch = params.stable_branch

    if params.is_several_projects:
        work_dir = arcadia.init_telematics(
            tmpdir, changelog_content=load('telematics_changelog.txt'),
        )
        arcadia.init_graph(
            tmpdir, changelog_content=load('base_changelog.txt'),
        )
        arcadia.init_uservices(
            tmpdir,
            main_service='my-new-service',
            changelog_content=load('base_changelog.txt'),
        )
        graph_dir = work_dir / '..' / 'graph'
        service_dir = work_dir / '..' / 'services' / 'driver-authorizer'
        substitute_dict = {
            'workdir': work_dir,
            'graphdir': graph_dir.resolve(),
            'servicedir': service_dir.resolve(),
        }
        changelog_path = work_dir / 'debian' / 'changelog'
        monkeypatch.setenv('MASTER_BRANCH', active_branch)
    else:
        work_dir = arcadia.init_uservices(
            tmpdir,
            main_service='my-service',
            changelog_content=load('base_changelog.txt'),
        )
        schemas_dir = (work_dir / '..' / 'schemas' / 'schemas').resolve()
        changelog_path = (
            work_dir / 'services' / 'my-service' / 'debian' / 'changelog'
        )
        substitute_dict = {'workdir': work_dir, 'schemas_dir': schemas_dir}

    monkeypatch.chdir(work_dir)
    arc.substitute_paths(params.arc_calls, substitute_dict)

    monkeypatch.setenv('RELEASE_TICKET_SUMMARY', 'uservices')
    monkeypatch.setenv('TELEGRAM_DISABLED', '1')
    monkeypatch.setenv('SLACK_DISABLED', '1')
    monkeypatch.setenv('ADD_FOLLOWERS', '1')
    monkeypatch.setenv('ARCADIA_RELEASE_REVISION', params.revision)
    monkeypatch.setenv('NO_CHANGES_RELEASE_ENABLED', params.no_changes_enabled)

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        nonlocal active_branch
        command = args[1]
        if command == 'info':
            return '{"branch": "%s"}' % active_branch
        if command == 'merge-base':
            return 'cbabc1'
        if command == 'rev-parse':
            return 'aaaaab'
        if command == 'log':
            if args[2] == '-n1':
                return """[{
"commit":"a141195",
"parents":["1","2"],
"author":"iegit",
"message":"some message",
"date":"2021-03-18T17:10:54+03:00",
"revision":8380017
}]
"""
            work_dir = args[-1]
            if 'graph' in work_dir:
                return load('graph.json')
            if 'driver-authorizer' in work_dir:
                return load('driver_authorizer.json')
            return load(params.log_json)
        if command == 'diff':
            commit = args[3]
            return '\n'.join(params.changed_files_by_commit[commit])
        if command == 'checkout':
            new_branch = args[2] if args[2] != '-b' else args[3]
            active_branch = new_branch
        if command == 'branch':
            return '[]'
        return 0

    @commands_mock('ya')
    def ya_mock(args, **kwargs):
        return 0

    if params.set_package_version_as_revision:
        (work_dir / 'services' / 'my-service' / 'service.yaml').write_text(
            """
project-name: yandex-taxi-my-service
versioning: revision
    """.strip(),
        )

    if params.ticket_status:
        startrek.ticket_status = params.ticket_status
    if params.tickets_comments:
        startrek.comments = params.tickets_comments
    if params.ticket_assignee:
        startrek.ticket_assignee = params.ticket_assignee

    run_release.main([])

    assert arc_mock.calls == params.arc_calls
    assert ya_mock.calls == []
    assert teamcity_set_parameters.calls == params.tc_set_parameters_calls
    assert teamcity_report_problems.calls == params.tc_report_problems_calls
    assert startrek.create_ticket.calls == params.st_create_ticket_calls
    assert changelog_path.read_text() == load(params.exp_changelog)

    if params.created_comment is None:
        assert startrek.create_comment.calls == []
    else:
        calls = startrek.create_comment.calls
        expected_calls = [{'json': params.created_comment}]
        assert calls == expected_calls


@dataclasses.dataclass
class BumpVersionParams(pytest_wraps.Params):
    version: str
    env_vars: Dict[str, str]
    expected_version: Optional[str]
    versioning: str = 'changelog'


@pytest_wraps.parametrize(
    [
        BumpVersionParams(
            version='0.10.1',
            env_vars={},
            expected_version='0.10.2',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='10.2hotfix3',
            env_vars={},
            expected_version='10.3',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='10.24hoxfix1hotfix1',
            env_vars={},
            expected_version='10.25',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='10',
            env_vars={},
            expected_version='11',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='hotfix',
            env_vars={},
            expected_version=None,
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1',
            env_vars={'VERSION': '1.0.0'},
            expected_version='1.0.0',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex1.1',
            env_vars={'INCREASE_LAST_NUMBER_OF_VERSION': '1'},
            expected_version='0.1.1-yandex1.2',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex1.1',
            env_vars={'INCREASE_LAST_NUMBER_OF_VERSION': ''},
            expected_version='0.1.2',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex1.1',
            env_vars={'VERSION': ''},
            expected_version='0.1.2',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex1',
            env_vars={'INCREASE_LAST_NUMBER_OF_VERSION': '1'},
            expected_version='0.1.1-yandex2',
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex',
            env_vars={'INCREASE_LAST_NUMBER_OF_VERSION': '1'},
            expected_version=None,
            pytest_id='simple_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex1.1',
            env_vars={},
            expected_version='0.1.1-yandex1.2',
            versioning='increase-last-number-of-version',
            pytest_id='versionig_increase_case',
        ),
        BumpVersionParams(
            version='0.1.1-yandex1.1',
            env_vars={},
            expected_version='8380017',
            versioning='revision',
            pytest_id='revision_case',
        ),
    ],
)
def test_bump_version(params, monkeypatch, tmpdir, load, commands_mock):
    work_dir = arcadia.init_uservices(
        tmpdir, 'my-service', load('base_changelog.txt'),
    )
    repo = vcs.open_repo(work_dir)

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        return """[{
"commit":"a141195",
"parents":["1","2"],
"author":"iegit",
"message":"some message",
"date":"2021-03-18T17:10:54+03:00",
"revision":8380017
}]
"""

    for key, val in params.env_vars.items():
        monkeypatch.setenv(key, val)
    if params.expected_version is None:
        with pytest.raises(run_release.BumpVersionError):
            run_release.get_bumped_version(
                params.version, params.versioning, repo, 'service',
            )
    else:
        assert (
            run_release.get_bumped_version(
                params.version, params.versioning, repo, 'service',
            )
            == params.expected_version
        )

    if params.versioning == 'revision':
        assert arc_mock.calls == [
            {
                'args': ['arc', 'log', '-n1', '--json'],
                'kwargs': {
                    'cwd': work_dir,
                    'env': None,
                    'stderr': -1,
                    'stdout': -1,
                },
            },
        ]
    else:
        assert arc_mock.calls == []
