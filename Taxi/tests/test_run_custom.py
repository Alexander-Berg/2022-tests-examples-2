# pylint: disable=too-many-lines
import os
import typing

import freezegun
import git
import pytest

import git_checkout
import run_custom
from taxi_buildagent.tools.vcs import git_repo
from tests.utils import repository
from tests.utils.examples import backend
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import backend_py3_move
from tests.utils.examples import dmp
from tests.utils.examples import schemas
from tests.utils.examples import uservices


class Params(typing.NamedTuple):
    init_repo: typing.Callable[[str], git.Repo]
    branch: str
    version: str
    path: str = ''
    develop_changes: typing.Sequence[repository.Commit] = ()
    add_all_prs: bool = False
    master_branch: typing.Optional[str] = None
    changes: str = '  (same as master)'
    pull_requests: typing.Sequence[dict] = ()
    fail_message: typing.Optional[dict] = None
    telegram_messages: typing.Sequence[str] = ()
    staff_calls: typing.Sequence[str] = ()
    check_status: str = ''
    test_contexts: typing.Optional[str] = None
    staff_error: bool = False
    teamcity_set_parameters: typing.Dict[str, str] = {}
    disable_changelog: str = ''
    disable_single_service_check: typing.Optional[str] = None
    allow_failed_prs_flag: bool = False


@freezegun.freeze_time('2018-04-23 14:22:56', tz_offset=3)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
            ),
            id='empty backend',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
                develop_changes=[
                    repository.Commit('change1', ['file1', 'file2']),
                    repository.Commit('change2', ['taxi/asdf']),
                ],
                changes='  * alberist | change2\n  * alberist | change1',
            ),
            id='backend develop changes on master',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                version='taxi-backend (3.0.224untesting123)',
                develop_changes=[
                    repository.Commit('change1', ['file1', 'file2']),
                    repository.Commit('change2', ['taxi/asdf']),
                ],
                changes='  * alberist | change2\n  * alberist | change1',
            ),
            id='backend develop changes',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
                develop_changes=[],
                changes='  (same as master)\n\n  PR vitja@ "fix all (#1)":\n\n'
                '  * User vitja | change2\n  * User vitja | change1',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='fix all',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file1', 'file2']),
                            repository.Commit('change2', ['taxi/asdf']),
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix2',
                        labels=['deploy:unstable'],  # Ignore by label
                        commits=[repository.Commit('change1', ['file3'])],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix3',
                        labels=['deploy:custom'],
                        commits=[],  # No commits
                    ),
                ],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'vitja'},
            ),
            id='backend ignore by label',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
                develop_changes=[
                    repository.Commit('change1', ['file1', 'file2']),
                    repository.Commit('change2', ['taxi/asdf']),
                ],
                changes='  * alberist | change2\n'
                '  * alberist | change1\n\n'
                '  PR vitja@ "feat nothing: add files (#1)":\n\n'
                '  * User vitja | change2\n'
                '  * User vitja | change1',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat nothing: add files',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file3', 'file4']),
                            repository.Commit('change2', ['taxi/asd']),
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix2',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file5', 'file6']),
                            repository.Commit('change2', ['taxi/asdf']),
                        ],
                    ),
                ],
                staff_calls=['vitja'],
                telegram_messages=[
                    'backend [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\n@tg\\_vitja '
                    '[#2](https://github.yandex-team.ru/taxi/backend/pull/2)'
                    ' - conflict with develop',
                ],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'vitja'},
            ),
            id='backend not merged with develop',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
                develop_changes=[
                    repository.Commit('change1', ['file1', 'file2']),
                    repository.Commit('change2', ['taxi/asdf']),
                ],
                changes='  * alberist | change2\n'
                '  * alberist | change1\n\n'
                '  PR vitja@ "cc all: asdf (#1)":\n\n'
                '  * User vitja | change2\n'
                '  * User vitja | change1',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='cc all: asdf',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file3', 'file4']),
                            repository.Commit('change2', ['taxi/asd']),
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix2',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file5', 'file6']),
                            repository.Commit('change2', ['taxi/asdf']),
                        ],
                    ),
                ],
                staff_calls=[],
                telegram_messages=[
                    'backend [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\nvitja '
                    '[#2](https://github.yandex-team.ru/taxi/backend/pull/2)'
                    ' - conflict with develop',
                ],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'vitja'},
                staff_error=True,
            ),
            id='backend not merged with develop broken staff',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file3', 'file4']),
                            repository.Commit('change2', ['taxi/asd']),
                        ],
                    ),
                    dict(
                        login='alberist',
                        branch='feat/fix1',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit('change1', ['file4', 'file6']),
                        ],
                    ),
                ],
                staff_calls=['alberist', 'vitja'],
                telegram_messages=[
                    'backend [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123) '
                    '(untesting)\nMerge conflicts:\n@tg\\_alberist '
                    '[#2](https://github.yandex-team.ru/taxi/backend/pull/2)'
                    ' - conflict with PR '
                    '[#1](https://github.yandex-team.ru/taxi/backend/pull/1)'
                    ' @tg\\_vitja',
                ],
                fail_message={
                    'description': 'Failed to merge pr #2',
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist vitja',
                    'env.BUILD_PROBLEM': 'Failed to merge pr #2',
                },
            ),
            id='merge conflict',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='master',
                version='taxi-backend (3.0.224untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='fix all',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change1', ['file1'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/vitja/1',
                                'state': 'success',
                                'context': 'tests',
                            },
                            {
                                'target_url': 'http://teamcity/vitja/1',
                                'state': 'pending',
                                'context': 'tests',
                            },
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix2',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change2', ['file2'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/vitja/2',
                                'state': 'pending',
                                'context': 'tests',
                            },
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix3',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change3', ['file3'])],
                        statuses=[],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix4',
                        title='fix nothing',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change4', ['file4'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/vitja/4',
                                'state': 'success',
                                'context': 'tests',
                            },
                            {
                                'target_url': 'http://teamcity/vitja/4',
                                'state': 'failed',
                                'context': 'default',
                            },
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix5',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change5', ['file5'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/vitja/5',
                                'state': 'success',
                                'context': 'default',
                            },
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix6',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change6', ['file6'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/vitja/7',
                                'state': 'failed',
                                'context': 'default',
                            },
                            {
                                'target_url': 'http://teamcity/vitja/6',
                                'state': 'success',
                                'context': 'default',
                            },
                        ],
                    ),
                    dict(
                        login='vitja',
                        branch='feat/fix7',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change5', ['file7'])],
                        updated='2018-04-21T14:49:14Z',
                        statuses=[
                            {
                                'target_url': 'http://teamcity/vitja/7',
                                'state': 'success',
                                'context': 'tests',
                            },
                        ],
                    ),
                ],
                changes='  (same as master)\n\n'
                '  PR vitja@ "fix all (#1)":\n\n'
                '  * User vitja | change1\n\n'
                '  PR vitja@ "fix nothing (#4)":\n\n'
                '  * User vitja | change4',
                staff_calls=['vitja', 'vitja', 'vitja', 'vitja', 'vitja'],
                telegram_messages=[
                    'backend [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\n@tg\\_vitja '
                    '[#2](https://github.yandex-team.ru/taxi/backend/pull/2)'
                    ' - tests [pending](http://teamcity/vitja/2)\n'
                    '@tg\\_vitja '
                    '[#3](https://github.yandex-team.ru/taxi/backend/pull/3)'
                    ' - tests missing\n@tg\\_vitja '
                    '[#5](https://github.yandex-team.ru/taxi/backend/pull/5)'
                    ' - tests missing\n@tg\\_vitja '
                    '[#6](https://github.yandex-team.ru/taxi/backend/pull/6)'
                    ' - tests missing\n'
                    'Label removed due to exceeding TTL:\n'
                    '@tg\\_vitja '
                    '[#7](https://github.yandex-team.ru/taxi/backend/pull/7)'
                    ' - last updated at 2018-04-21T14:49:14UTC',
                ],
                check_status='1',
                test_contexts='tests',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'vitja'},
            ),
            id='check pr status',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                version='taxi-backend-cpp (2.1.1untesting123)',
            ),
            id='empty backend_cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                version='taxi-backend-cpp (2.1.1untesting123)',
                develop_changes=[
                    repository.Commit('antifraud fix', ['antifraud/lib/123']),
                    repository.Commit(
                        'surger fix', ['surger/lib/123', 'common/fx'],
                    ),
                    repository.Commit(
                        'antisurge fix', ['antifraud/f1', 'surger/f2'],
                    ),
                    repository.Commit('protofix', ['tracker/f']),
                    repository.Commit(
                        'main test', ['testsuite/tests/chat/ff'],
                    ),
                    repository.Commit(
                        'not main test', ['testsuite/tests/ttt'],
                    ),
                ],
                changes='  * alberist | not main test\n'
                '  * alberist | main test\n'
                '  * alberist | protofix\n'
                '  * alberist | surger fix',
            ),
            id='backend_cpp develop changes',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='master',
                version='taxi-backend-cpp (2.1.1untesting123)',
                develop_changes=[
                    repository.Commit('antifraud fix', ['antifraud/lib/123']),
                    repository.Commit('surger fix', ['surger/lib/123']),
                    repository.Commit(
                        'new_sub',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit', ['test3'],
                                    ),
                                ],
                            ),
                            (
                                'new_sub',
                                [repository.Commit('init sub', ['f1'])],
                            ),
                        ],
                    ),
                ],
                changes='  * alberist | new_sub\n'
                '  * alberist | testsuite commit | submodules/testsuite',
            ),
            id='backend_cpp develop submodule update',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                version='taxi-antifraud (3.0.0hotfix25untesting123)',
            ),
            id='backend_cpp empty antifraud',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                branch='masters/antifraud',
                path='antifraud',
                version='taxi-antifraud (3.0.0hotfix25untesting123)',
                develop_changes=[
                    repository.Commit('antifix', ['antifraud/lib/123']),
                    repository.Commit(
                        'surger fix', ['surger/lib/123', 'common/fx'],
                    ),
                    repository.Commit('protofix', ['protocol/f']),
                    repository.Commit(
                        'config',
                        ['common/config/templates/config_fallback.json.tpl'],
                    ),
                    repository.Commit(
                        'main test', ['testsuite/tests/chat/ff'],
                    ),
                    repository.Commit(
                        'not main test', ['testsuite/tests/ttt'],
                    ),
                ],
                changes='  * alberist | not main test\n'
                '  * alberist | surger fix\n'
                '  * alberist | antifix',
            ),
            id='backend_cpp antifraud pr filters',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.1.1untesting123)',
            ),
            id='backend_py3 empty adjust',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='develop',
                path='services/taxi-adjust',
                version='taxi-adjust (0.1.1untesting123)',
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Custom should be built '
                        'from \'masters/PROJECT\' branch. '
                        'Current branch: \'develop\''
                    ),
                },
                fail_message={
                    'description': (
                        'Custom should be built '
                        'from \'masters/PROJECT\' branch. '
                        'Current branch: \'develop\''
                    ),
                    'identity': None,
                },
            ),
            id='backend_py3 from develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.1.1untesting123)',
                develop_changes=[
                    repository.Commit(
                        'adjust fix', ['services/taxi-adjust/f1'],
                    ),
                    repository.Commit('corp1', ['services/taxi-corp/f2']),
                    repository.Commit(
                        'corp2',
                        ['services/taxi-corp/f2', 'services/taxi/corp'],
                    ),
                ],
                changes='  * alberist | adjust fix\n\n'
                '  Common changes:\n'
                '  * alberist | corp2',
            ),
            id='backend_py3 adjust develop changes',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='orangevl',
                        branch='feat/fix1',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'change1', ['services/taxi-corp/file'],
                            ),
                        ],
                    ),
                ],
            ),
            id='backend_py3 test filter pr',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.1.1untesting123)',
                develop_changes=[
                    repository.Commit('corp1', ['services/taxi-corp/f2']),
                    repository.Commit('adjust1', ['services/taxi-adjust/f1']),
                    repository.Commit(
                        'testsuite update',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [
                                    repository.Commit(
                                        'testsuite commit 1', ['test3'],
                                    ),
                                ],
                            ),
                        ],
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
                changes='  * alberist | adjust1\n\n'
                '  Common changes:\n'
                '  * alberist | new testsuite update\n'
                '  * alberist | new testsuite 2.0\n'
                '  * alberist | testsuite update',
            ),
            id='backend_py3 develop submodule new_submodule_url',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3_move.init,
                branch='masters/taxi-corp',
                path='services/taxi-corp',
                version='taxi-corp (0.1.2untesting123)',
                pull_requests=[
                    dict(
                        login='me',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'fix1', ['services/taxi-corp/z3'],
                            ),
                        ],
                    ),
                ],
                changes=(
                    '  * alberist | after-corp-taxi\n'
                    '  * alberist | after-corp-adjust\n'
                    '  * alberist | after-corp-only\n'
                    '  * alberist | move-services\n'
                    '  * alberist | before-corp-taxi\n'
                    '  * alberist | before-corp-adjust\n\n'
                    '  Common changes:\n'
                    '  * alberist | after-taxi\n'
                    '  * alberist | before-taxi\n\n'
                    '  PR me@ "feat fix (#1)":\n\n'
                    '  * User me | fix1'
                ),
                teamcity_set_parameters={'env.AFFECTED_USERS': 'me'},
            ),
            id='backend_py3 move services corp',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3_move.init,
                branch='masters/taxi-adjust',
                path='services/taxi-adjust',
                version='taxi-adjust (0.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='me',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'fix1', ['services/taxi-corp/z3'],
                            ),
                        ],
                    ),
                ],
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
            ),
            id='backend_py3 move services adjust',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
            ),
            id='uservices empty driver-authorizer',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                develop_changes=[
                    repository.Commit('da', ['services/driver-authorizer/f1']),
                    repository.Commit(
                        'da2', ['services/driver-authorizer2/f1'],
                    ),
                    repository.Commit(
                        'common', ['services/driver-authorizer2/f1', 'Make'],
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
                changes='  * alberist | common\n' '  * alberist | da',
            ),
            id='uservices driver-authorizer filter',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                develop_changes=[
                    repository.Commit('da', ['services/driver-authorizer/f1']),
                    repository.Commit(
                        'add orphaned config',
                        [
                            'schemas/configs/declarations/orphaned_configs/'
                            'SOME_ORPHANED_CONFIG.yaml',
                        ],
                        files_content="""
default: true
description: Some orphaned config
tags: []
schema:
  type: boolean
""".lstrip(),
                    ),
                ],
                changes='  * alberist | da',
            ),
            id='uservices driver-authorizer orphaned',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'change1',
                                [],
                                submodules=[
                                    (
                                        'userver',
                                        [
                                            repository.Commit(
                                                'upd', ['file2', 'file3'],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='alberist',
                        branch='feat/unused',
                        title='feat unused',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'ignored commit',
                                [
                                    '.github/CODEOWNERS',
                                    'README.md',
                                    'configs/declarations/some/CONFIG.yaml',
                                ],
                            ),
                        ],
                    ),
                ],
                changes='  (same as master)\n\n'
                '  PR vitja@ "feat fix (#1)":\n\n'
                '  * User vitja | change1\n'
                '  * alberist | upd | userver',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'vitja'},
            ),
            id='uservices driver-authorizer submodule update',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='develop',
                master_branch='develop',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'change1',
                                [],
                                submodules=[
                                    (
                                        'userver',
                                        [
                                            repository.Commit(
                                                'upd', ['file2', 'file3'],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='alberist',
                        branch='feat/used',
                        title='feat unused',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'Not ignored commit',
                                [
                                    '.github/CODEOWNERS',
                                    'README.md',
                                    'configs/declarations/some/CONFIG.yaml',
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='tokhchukov',
                        branch='feat/used-anyway',
                        title='feat used anyway',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'ignored commit',
                                ['any/path', 'literally/any/path'],
                            ),
                        ],
                    ),
                ],
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist tokhchukov vitja',
                },
                disable_changelog='1',
                disable_single_service_check='1',
                add_all_prs=True,
            ),
            id='uservices driver-authorizer submodule update all_prs',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/pilorama',
                path='services/pilorama',
                version='pilorama (1.1.1untesting123)',
                develop_changes=[repository.Commit('change1', ['taxi/file'])],
                changes='  * alberist | change1',
                pull_requests=[
                    dict(
                        login='aselutin',
                        branch='feat/fix2',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change1', ['taxi/file'])],
                    ),
                ],
                staff_calls=['aselutin'],
                telegram_messages=[
                    'backend pilorama [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\n@tg\\_aselutin '
                    '[#1](https://github.yandex-team.ru/taxi/backend/pull/1)'
                    ' - conflict with develop',
                ],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'aselutin'},
            ),
            id='uservices driver-authorizer check service name',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='develop',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                disable_changelog='1',
                fail_message={
                    'description': (
                        'Custom should be built '
                        'from \'masters/PROJECT\' branch. '
                        'Current branch: \'develop\''
                    ),
                    'identity': None,
                },
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': (
                        'Custom should be built '
                        'from \'masters/PROJECT\' branch. '
                        'Current branch: \'develop\''
                    ),
                },
            ),
            id='uservices empty driver-authorizer custom-on-develop',
        ),
        pytest.param(
            Params(
                init_repo=schemas.init,
                branch='master',
                version='master (1.1.1unstable33)',
                develop_changes=[
                    repository.Commit(
                        'commit0',
                        [
                            'schemas/configs/declarations/tmp/file0.yaml',
                            'schemas/configs/declarations/tmp/file1.yaml',
                        ],
                    ),
                    repository.Commit('commit1', ['README.md']),
                ],
                disable_changelog='1',
            ),
            id='schemas with disabled changelog',
        ),
        pytest.param(
            Params(
                init_repo=schemas.init,
                branch='master',
                version='master (1.1.1unstable33)',
                develop_changes=[
                    repository.Commit(
                        'commit0',
                        [
                            'schemas/configs/declarations/tmp/file0.yaml',
                            'schemas/configs/declarations/tmp/file1.yaml',
                        ],
                    ),
                    repository.Commit('commit1', ['README.md']),
                ],
                teamcity_set_parameters={
                    'env.BUILD_PROBLEM': 'Changelog not found',
                },
                fail_message={
                    'description': 'Changelog not found',
                    'identity': None,
                },
            ),
            id='schemas with disabled changelog failed custom-on-master',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'change1',
                                [],
                                submodules=[
                                    repository.SubmoduleCommits(
                                        'userver',
                                        [
                                            repository.Commit(
                                                'upd1', ['file2', 'file3'],
                                            ),
                                            repository.Commit(
                                                'upd2', ['test4', 'test5'],
                                            ),
                                            repository.Commit(
                                                'upd3', ['test6', 'test7'],
                                            ),
                                        ],
                                        delete_after_update=True,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='alberist',
                        branch='feat/fix2',
                        title='feat fix2',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'change2',
                                [],
                                submodules=[
                                    repository.SubmoduleCommits(
                                        'userver',
                                        [
                                            repository.Commit(
                                                'upd2', ['test2', 'test3'],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                telegram_messages=[
                    'backend driver-authorizer [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\n@tg\\_vitja '
                    '[#1](https://github.yandex-team.ru/taxi/backend/pull/1)'
                    ' - incorrect submodule commit',
                ],
                staff_calls=['vitja'],
                changes='  (same as master)\n\n'
                '  PR alberist@ "feat fix2 (#2)":\n\n'
                '  * User alberist | change2\n'
                '  * alberist | upd2 | userver',
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'alberist vitja',
                },
            ),
            id='uservices driver-authorizer submodule several incorrect',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'change1',
                                [],
                                submodules=[
                                    repository.SubmoduleCommits(
                                        'userver',
                                        [
                                            repository.Commit(
                                                'upd1', ['alb2', 'alb3'],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='tokhchukov',
                        branch='feat/break',
                        title='feat break',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'break1',
                                [],
                                submodules=[
                                    repository.SubmoduleCommits(
                                        'external_repo',
                                        [
                                            repository.Commit(
                                                'init', ['README.txt'],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                changes='  (same as master)\n\n'
                '  PR vitja@ "feat fix (#1)":\n\n'
                '  * User vitja | change1\n'
                '  * alberist | upd1 | userver\n\n'
                '  PR tokhchukov@ "feat break (#2)":\n\n'
                '  * User tokhchukov | break1',
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'tokhchukov vitja',
                },
            ),
            id='uservices driver-authorizer external submodule',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                develop_changes=[
                    repository.Commit(
                        f'da{n}', ['services/driver-authorizer/f1'],
                    )
                    for n in range(20)
                ],
                changes='\n'.join(
                    [f'  * alberist | da{n}' for n in range(19, 9, -1)],
                ),
            ),
            id='uservices_driver_authorizer_filter_10_commits',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'st1\n\nRelates: TAXITOOLS-1',
                                [
                                    'services/driver-authorizer/build-'
                                    'dependencies-debian.txt',
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='tokhchukov',
                        branch='feat/fix2',
                        title='feat fix2',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'commit3',
                                [
                                    'services/driver-authorizer/local-files-'
                                    'dependencies.txt',
                                    'services/driver-authorizer2/2',
                                ],
                            ),
                        ],
                    ),
                ],
                changes='  (same as master)\n\n'
                '  PR vitja@ "feat fix (#1)":\n\n'
                '  * User vitja | st1\n\n'
                '  PR tokhchukov@ "feat fix2 (#2)":\n\n'
                '  * User tokhchukov | commit3',
                teamcity_set_parameters={
                    'env.AFFECTED_USERS': 'tokhchukov vitja',
                },
            ),
            id='uservices force_common_changes',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                branch='masters/driver-authorizer',
                path='services/driver-authorizer',
                version='driver-authorizer (1.1.1untesting123)',
                staff_calls=['tokhchukov'],
                pull_requests=[
                    dict(
                        login='vitja',
                        branch='feat/fix1',
                        title='feat fix',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'st1\n\nRelates: TAXITOOLS-1',
                                [
                                    'services/driver-authorizer/build-'
                                    'dependencies-debian.txt',
                                ],
                            ),
                        ],
                    ),
                    dict(
                        login='tokhchukov',
                        branch='feat/fix2',
                        title='feat fix2',
                        labels=['deploy:custom'],
                        commits=[
                            repository.Commit(
                                'commit3',
                                [
                                    'services/driver-authorizer/local-files-'
                                    'dependencies.txt',
                                    'services/driver-authorizer2/2',
                                ],
                            ),
                        ],
                        fetchable=False,
                    ),
                ],
                changes='  (same as master)\n\n'
                '  PR vitja@ "feat fix (#1)":\n\n'
                '  * User vitja | st1',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'vitja'},
                telegram_messages=[
                    'backend driver-authorizer '
                    '[Custom](https://teamcity.taxi.yandex-team.ru/'
                    'viewLog.html?buildId=123123) '
                    '(untesting)\n'
                    'Excluded Pull-Requests:\n'
                    '@tg\\_tokhchukov '
                    '[#2](https://github.yandex-team.ru/'
                    'taxi/backend/pull/2)'
                    ' - failed to fetch pr',
                ],
            ),
            id='uservices failed-to-fetch',
        ),
        pytest.param(
            Params(
                init_repo=dmp.init,
                branch='masters/ad_etl',
                path='ad_etl',
                version='ad_etl (1.1.1untesting123)',
                develop_changes=[repository.Commit('change1', ['taxi/file'])],
                changes='  * alberist | change1',
                pull_requests=[
                    dict(
                        login='aselutin',
                        branch='feat/fix2',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change1', ['taxi/file'])],
                    ),
                ],
                staff_calls=['aselutin'],
                telegram_messages=[
                    'backend ad\\_etl [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\n@tg\\_aselutin '
                    '[#1](https://github.yandex-team.ru/taxi/backend/pull/1)'
                    ' - conflict with develop',
                ],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'aselutin'},
            ),
            id='branch_name_with_underlining',
        ),
        pytest.param(
            Params(
                init_repo=dmp.init,
                branch='masters/ad_etl',
                path='ad_etl',
                version='ad_etl (1.1.1untesting123)',
                pull_requests=[
                    dict(
                        login='aselutin',
                        branch='feat/fix1',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change1', ['taxi/file'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/aselutin/1',
                                'state': 'pending',
                                'context': 'some_tests',
                            },
                        ],
                    ),
                ],
                check_status='1',
                test_contexts='some_tests',
                staff_calls=['aselutin'],
                telegram_messages=[
                    'backend ad\\_etl [Custom]'
                    '(https://teamcity.taxi.yandex-team.ru/viewLog.html?'
                    'buildId=123123) '
                    '(untesting)\nExcluded Pull-Requests:\n@tg\\_aselutin '
                    '[#1](https://github.yandex-team.ru/taxi/backend/pull/1)'
                    ' - some\\_tests [pending](http://teamcity/aselutin/1)',
                ],
                teamcity_set_parameters={'env.AFFECTED_USERS': 'aselutin'},
            ),
            id='test_name_with_underlining',
        ),
        pytest.param(
            Params(
                init_repo=backend.init,
                branch='develop',
                version='taxi-backend (3.0.224untesting123)',
                pull_requests=[
                    dict(
                        login='eugenyegorov',
                        branch='feat/fix1',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change1', ['file1'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/eugenyegorov/1',
                                'state': 'success',
                                'context': 'tests',
                            },
                        ],
                    ),
                    dict(
                        login='eugenyegorov',
                        branch='feat/fix2',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change2', ['file2'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/eugenyegorov/2',
                                'state': 'failed',
                                'context': 'tests',
                            },
                        ],
                    ),
                    dict(
                        login='eugenyegorov',
                        branch='feat/fix3',
                        labels=['deploy:custom'],
                        commits=[repository.Commit('change3', ['file3'])],
                        statuses=[
                            {
                                'target_url': 'http://teamcity/eugenyegorov/3',
                                'state': 'pending',
                                'context': 'tests',
                            },
                        ],
                    ),
                ],
                changes='  (same as master)\n\n'
                '  PR eugenyegorov@ "feat all: make good (#1)":\n\n'
                '  * User eugenyegorov | change1\n\n'
                '  PR eugenyegorov@ "feat all: make good (#2)":\n\n'
                '  * User eugenyegorov | change2\n\n'
                '  PR eugenyegorov@ "feat all: make good (#3)":\n\n'
                '  * User eugenyegorov | change3',
                check_status='1',
                test_contexts='tests',
                teamcity_set_parameters={'env.AFFECTED_USERS': 'eugenyegorov'},
                allow_failed_prs_flag=True,
            ),
            id='pass_prs_to_custom_by_flag',
        ),
    ],
)
def test_custom(
        github,
        home_dir,
        monkeypatch,
        patch,
        patch_requests,
        repos_dir,
        staff_persons_mock,
        teamcity_report_problems,
        teamcity_set_parameters,
        telegram,
        tmpdir,
        params: Params,
):
    monkeypatch.setenv('GITHUB_LABEL', 'deploy:custom')
    monkeypatch.setenv('DEPLOY_BRANCH', 'untesting')
    monkeypatch.setenv('BUILD_NUMBER', '123')
    monkeypatch.setenv('CUSTOM_REPORTS_CHAT_ID', 'tchatid')
    monkeypatch.setenv('CHECK_STATUS', params.check_status)
    monkeypatch.setenv('LABEL_TTL_DAYS', '1')
    monkeypatch.setenv('BUILD_ID', '123123')
    monkeypatch.setenv('PR_WHITE_LIST', '')
    monkeypatch.setenv('DISABLE_UPDATE_CHANGELOG', params.disable_changelog)
    if params.disable_single_service_check is not None:
        monkeypatch.setenv(
            'DISABLE_SINGLE_SERVICE_CHECK',
            params.disable_single_service_check,
        )
    if params.master_branch:
        monkeypatch.setenv('MASTER_BRANCH', params.master_branch)

    if params.add_all_prs:
        monkeypatch.setenv('ADD_ALL_PULL_REQUESTS_TO_CUSTOM', '1')

    if params.allow_failed_prs_flag:
        monkeypatch.setenv('CUSTOM_IGNORE_PR_STATUS_CHECK', '1')

    squash_merges = []
    merge_calls = []
    _origin_merge_branch = git_repo.Repo.merge_branch

    def merge_branch(self, source, *args):
        if '--squash' in args:
            squash_merges.append(source)
        merge_calls.append(source)
        return _origin_merge_branch(self, source, *args)

    monkeypatch.setattr(
        'taxi_buildagent.tools.vcs.git_repo.Repo.merge_branch', merge_branch,
    )

    if params.staff_error:

        @patch_requests('https://staff-api.yandex-team.ru/v3/persons')
        def _persons(method, url, **kwargs):
            return patch_requests.response(
                status_code=500,
                text='Emulating broken staff. Internal error.',
            )

    if params.test_contexts is not None:
        monkeypatch.setenv('TEST_CONTEXTS', params.test_contexts)

    repo = params.init_repo(tmpdir)
    origin_url = next(repo.remotes[0].urls)
    github_repo = github.init_repo('taxi', 'backend', origin_url)

    for prq in params.pull_requests:
        github_repo.create_pr(repo, **prq)

    if params.develop_changes:
        repository.apply_commits(repo, params.develop_changes)
        repo.git.push('origin', 'develop')

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
        without_sub_path,
    ]
    git_checkout.main(args)

    repo_without_submodules = git.Repo(without_sub_path)

    branches = repo_without_submodules.git.branch().split()
    branches = {branch for branch in branches}
    if params.branch != 'develop' and 'develop' in branches:
        repo_without_submodules.git.branch('-d', 'develop')

    repo_without_submodules.git.remote('set-url', 'origin', origin_url)

    repo_without_submodules.git.checkout(params.branch)
    monkeypatch.chdir(repo_without_submodules.working_tree_dir)
    run_custom.main()

    if params.add_all_prs:
        expected_calls = ['origin/develop']
        pr_num_range = range(1, len(params.pull_requests) + 1)
        expected_calls.extend(
            [f'refs/pull/{num}/head' for num in pr_num_range],
        )
        assert len(squash_merges) == len(params.pull_requests)
        assert expected_calls == merge_calls

    assert set(user['login'] for user in staff_persons_mock.calls) == set(
        params.staff_calls,
    )

    assert telegram.calls == [
        {
            'chat_id': 'tchatid',
            'disable_notification': False,
            'parse_mode': 'markdown',
            'text': text,
            'disable_web_page_preview': True,
        }
        for text in params.telegram_messages
    ]

    assert (params.teamcity_set_parameters or {}) == {
        call['name']: call['value'] for call in teamcity_set_parameters.calls
    }

    if params.fail_message is not None:
        assert teamcity_report_problems.calls == [params.fail_message]
        return

    if not params.disable_changelog:
        with open(os.path.join(params.path, 'debian/changelog')) as fp:
            changelog = fp.readline()
            for line in fp:
                if line.startswith(' ') or line == '\n':
                    changelog += line
                else:
                    break
        assert changelog == (
            '%s unstable; urgency=low\n\n  CURRENT DEVELOP:\n\n%s\n\n '
            '-- buildfarm <buildfarm@yandex-team.ru>  '
            'Mon, 23 Apr 2018 17:22:56 +0300\n\n'
        ) % (params.version, params.changes)
    if params.branch != 'develop':
        assert repo_without_submodules.active_branch.name == params.branch
    current_commit = repo_without_submodules.head.commit
    repo_without_submodules.git.merge('origin/develop')
    assert repo_without_submodules.head.commit == current_commit
