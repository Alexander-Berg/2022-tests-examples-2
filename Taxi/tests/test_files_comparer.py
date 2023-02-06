# pylint: disable=too-many-lines
import os
import pathlib
from typing import Dict
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Tuple

import pytest

import files_comparer
from tests.plugins import arc
from tests.utils import repository
from tests.utils.examples import arcadia
from tests.utils.examples import backend
from tests.utils.examples import schemas


class Params(NamedTuple):
    argv: Sequence[str]
    teamcity_build_fail: Sequence[dict]
    info_changed_by_format: Sequence[Tuple[str, str]] = ()
    teamcity_error_report: Optional[Dict[str, str]] = None
    develop_changes: Sequence[repository.Commit] = ()


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                argv=['--error-message', 'Format checking is failed'],
                teamcity_build_fail=[],
            ),
            id='check_format_correctness empty',
        ),
        pytest.param(
            Params(
                argv=['--error-message', 'Format checking is failed'],
                info_changed_by_format=[
                    ('something.py', 'gif with cats is the best\n'),
                ],
                teamcity_error_report={
                    'files-comparer:something.py': (
                        'diff --git a/something.py b/something.py\n'
                        'index 05498ea..49db071 100644\n'
                        '--- a/something.py\n'
                        '+++ b/something.py\n'
                        '@@ -1 +1,2 @@\n'
                        ' content for some file\n'
                        '+gif with cats is the best'
                    ),
                },
                teamcity_build_fail=[
                    {
                        'description': 'Format checking is failed',
                        'identity': None,
                    },
                ],
            ),
            id='check_format_correctness single file',
        ),
        pytest.param(
            Params(
                info_changed_by_format=[
                    ('taxi/core/order-events.yaml', 'python code\n'),
                    (
                        'taxi/configs/config.txt',
                        'some another text\noriginal text\n',
                    ),
                    (
                        'taxi/somefile.yaml',
                        'inequal wrong string\nyet another text\n',
                    ),
                ],
                teamcity_error_report={
                    'files-comparer:taxi/core/order-events.yaml': (
                        'diff --git a/taxi/core/order-events.yaml '
                        'b/taxi/core/order-events.yaml\n'
                        'index 20093c9..26dab4f 100644\n'
                        '--- a/taxi/core/order-events.yaml\n'
                        '+++ b/taxi/core/order-events.yaml\n'
                        '@@ -1 +1,2 @@\n'
                        ' content for some yaml file\n'
                        '+python code'
                    ),
                    'files-comparer:taxi/configs/config.txt': (
                        'diff --git a/taxi/configs/config.txt '
                        'b/taxi/configs/config.txt\n'
                        'index fa9215b..ed6cb3f 100644\n'
                        '--- a/taxi/configs/config.txt\n'
                        '+++ b/taxi/configs/config.txt\n'
                        '@@ -1 +1,3 @@\n'
                        ' yet another content for config file\n'
                        '+some another text\n'
                        '+original text'
                    ),
                    'files-comparer:taxi/somefile.yaml': (
                        'diff --git a/taxi/somefile.yaml b/taxi/'
                        'somefile.yaml\n'
                        'index 2ac9bf7..5af92fc 100644\n'
                        '--- a/taxi/somefile.yaml\n'
                        '+++ b/taxi/somefile.yaml\n'
                        '@@ -1 +1,3 @@\n'
                        ' schema info of some file\n'
                        '+inequal wrong string\n'
                        '+yet another text'
                    ),
                },
                teamcity_build_fail=[
                    {'description': 'Checking is failed', 'identity': None},
                ],
                argv=['--error-message', 'Checking is failed'],
            ),
            id='check_format_correctness multiple files',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Config declaration check is failed',
                    'taxi/config/declarations/',
                    'schemas_repo/schemas/configs/declarations',
                ],
                develop_changes=[
                    repository.Commit(
                        'adjust declarations',
                        ['taxi/config/declarations/adjust/ADJUST_CONFIG.yaml'],
                        files_content="""
default:
  __default__: true
  child_tariff_events_enabled: true
  enabled: true
  vip_events_enabled: true
description: adjust.com
tags: []
validators:
- $dictionary_of:
    required_keys:
    - __default__
    - enabled
""".lstrip(),
                    ),
                    repository.Commit(
                        'zendesk declarations',
                        [
                            'taxi/config/declarations/zendesk/'
                            'ZENDESK_VERIFY_CERT.yaml',
                        ],
                        files_content="""
default: false
description: zendesk
tags: []
validators:
- $boolean
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': 'Config declaration check is failed',
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:taxi/config/declarations/adjust/'
                    'ADJUST_CONFIG.yaml': (
                        '--- '
                        'schemas_repo/schemas/configs/declarations/adjust/'
                        'ADJUST_CONFIG.yaml\n'
                        '+++ taxi/config/declarations/adjust/'
                        'ADJUST_CONFIG.yaml\n'
                        '@@ -1,12 +1,12 @@\n'
                        ' default:\n'
                        '-  __default__: false\n'
                        '-  child_tariff_events_enabled: false\n'
                        '+  __default__: true\n'
                        '+  child_tariff_events_enabled: true\n'
                        '   enabled: true\n'
                        '-  vip_events_enabled: false\n'
                        '-description: new_adjust.com\n'
                        '-tags: [\'new tag\']\n'
                        '+  vip_events_enabled: true\n'
                        '+description: adjust.com\n'
                        '+tags: []\n'
                        ' validators:\n'
                        ' - $dictionary_of:\n'
                        '     required_keys:\n'
                        '     - __default__\n'
                        '-    - disabled\n'
                        '+    - enabled\n'
                    ),
                    'files-comparer:taxi/config/declarations/zendesk/'
                    'ZENDESK_VERIFY_CERT.yaml': (
                        '--- '
                        'schemas_repo/schemas/configs/declarations/zendesk/'
                        'ZENDESK_VERIFY_CERT.yaml\n'
                        '+++ taxi/config/declarations/zendesk/'
                        'ZENDESK_VERIFY_CERT.yaml\n'
                        '@@ -0,0 +1,5 @@\n'
                        '+default: false\n'
                        '+description: zendesk\n'
                        '+tags: []\n'
                        '+validators:\n'
                        '+- $boolean\n'
                    ),
                },
            ),
            id='check config_declarations_path',
        ),
        pytest.param(
            Params(
                teamcity_build_fail=[],
                develop_changes=[
                    repository.Commit(
                        'adjust declarations',
                        ['taxi/config/declarations/adjust/ADJUST_CONFIG.yaml'],
                        do_delete=True,
                    ),
                ],
                argv=[
                    '--error-message',
                    'Config declaration check is failed',
                    'taxi/config/declarations/',
                    'schemas_repo/schemas/configs/declarations',
                ],
            ),
            id='check config_declarations_path deleted',
        ),
        pytest.param(
            Params(
                teamcity_build_fail=[],
                develop_changes=[
                    repository.Commit(
                        'parks declarations',
                        [
                            'taxi/config/declarations/parks/'
                            'PARKS_ENABLE_PHOTO_VALIDITY_CHECK.yaml',
                        ],
                        files_content="""
default: true
description: driver-profiles/photo
""".lstrip(),
                    ),
                ],
                argv=[
                    '--error-message',
                    'Config declaration check is failed',
                    'taxi/config/declarations/',
                    'schemas_repo/schemas/configs/declarations',
                ],
            ),
            id='check config_declarations_path changed origin',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Config declaration check is failed',
                    'taxi/config/declarations/',
                    'schemas_repo/schemas/configs/declarations',
                ],
                develop_changes=[
                    repository.Commit(
                        'adjust declarations',
                        ['taxi/config/declarations/adjust/ADJUST_CONFIG.yaml'],
                        rename_to='NEW_ADJUST_CONFIG.yaml',
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': 'Config declaration check is failed',
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:taxi/config/declarations/adjust/'
                    'NEW_ADJUST_CONFIG.yaml': (
                        '--- '
                        'schemas_repo/schemas/configs/declarations/adjust/'
                        'NEW_ADJUST_CONFIG.yaml\n'
                        '+++ taxi/config/declarations/adjust/'
                        'NEW_ADJUST_CONFIG.yaml\n'
                        '@@ -0,0 +1,12 @@\n'
                        '+default:\n'
                        '+  __default__: false\n'
                        '+  child_tariff_events_enabled: false\n'
                        '+  enabled: true\n'
                        '+  vip_events_enabled: false\n'
                        '+description: new_adjust.com\n'
                        '+tags: [\'new tag\']\n'
                        '+validators:\n'
                        '+- $dictionary_of:\n'
                        '+    required_keys:\n'
                        '+    - __default__\n'
                        '+    - disabled\n'
                    ),
                },
            ),
            id='check config_declarations_path rename',
        ),
        pytest.param(
            Params(
                argv=[
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--error-message',
                    'Services schemas does not match schemas master',
                    '--match-subdirs',
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs no files',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'social service yaml',
                        ['schemas/services/social/service.yaml'],
                        files_content="""
host:
    production: api.social.yandex.ru
    testing: api.social - test.yandex.ru
    unstable: api.social - test.yandex.ru
middlewares:
tvm: social
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs one service',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'social service yaml',
                        ['schemas/services/social/service.yaml'],
                        files_content="""
host:
    production: api.social.yandex.ru
    testing: api.social - test.yandex.ru
    unstable: api.social - test.yandex.ru
middlewares:
tvm: social
""".lstrip(),
                    ),
                    repository.Commit(
                        'driver-authorizer-external yaml',
                        [
                            'schemas/services/driver-authorizer-external/'
                            'service.yaml',
                        ],
                        files_content="""
host:
  production: driver-authorizer.taxi.yandex.net
  testing: driver-authorizer.taxi.tst.yandex.net
  unstable: driver-authorizer.taxi.dev.yandex.net
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': (
                            'Services schemas does not match schemas master'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:schemas/services/'
                    'driver-authorizer-external/api/api.yaml': (
                        '--- '
                        'schemas_repo/schemas/services/'
                        'driver-authorizer-external'
                        '/api/api.yaml\n'
                        '+++ '
                        'schemas/services/driver-authorizer-external/api/'
                        'api.yaml\n'
                        '@@ -1,5 +0,0 @@\n'
                        '-swagger: \'2.0\'\n'
                        '-info:\n'
                        '-  description: '
                        'Yandex Taxi Driver Authorizer Protocol\n'
                        '-  title: Yandex Taxi Driver Authorizer Protocol\n'
                        '-  version: \'1.0\'\n'
                    ),
                },
            ),
            id='match_subdirs two services',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'social service yaml',
                        ['schemas/services/social/service.yaml'],
                        files_content="""
host:
    production: api.social.yandex.ru
    testing: api.social - test.yandex.ru
    unstable: api.social - test.yandex.ru
middlewares:
tvm: social
""".lstrip(),
                    ),
                    repository.Commit(
                        'driver-authorizer-external yaml',
                        [
                            'schemas/services/driver-authorizer-external/'
                            'service.yaml',
                        ],
                        files_content="""
host:
  production: driver-authorizer.taxi.yandex.net
  testing: driver-authorizer.taxi.tst.yandex.net
  unstable: driver-authorizer.taxi.dev.yandex.net
""".lstrip(),
                    ),
                    repository.Commit(
                        'driver-authorizer-external api.yaml',
                        [
                            'schemas/services/driver-authorizer-external/api/'
                            'api.yaml',
                        ],
                        files_content="""
swagger: '2.0'
info:
  description: Yandex Taxi Driver Authorizer Protocol
  title: Yandex Taxi Driver Authorizer Protocol
  version: '1.0'
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs correct',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'social service yaml',
                        ['schemas/services/social/service.yaml'],
                        files_content="""
host:
    production: api.social.yandex.ru
    testing: api.social - test.yandex.ru
    unstable: api.social - test.yandex.ru
middlewares:
tvm: social
""".lstrip(),
                    ),
                    repository.Commit(
                        'driver-authorizer-external yaml',
                        [
                            'schemas/services/driver-authorizer-external/'
                            'service.yaml',
                        ],
                        files_content="""
host:
  production: driver-authorizer.taxi.yandex.net
  testing: driver-authorizer.taxi.tst.yandex.net
  unstable: driver-authorizer.taxi.dev.yandex.net
""".lstrip(),
                    ),
                    repository.Commit(
                        'social api yaml',
                        ['schemas/services/social/api/api.yaml'],
                        files_content="""
swagger: '2.0'
info:
    description: Yandex Passport API
    title: Yandex Passport API
    version: '1.0'
host: api.social.yandex.ru
""".lstrip(),
                    ),
                    repository.Commit(
                        'driver-authorizer-external api.yaml',
                        [
                            'schemas/services/driver-authorizer-external/api/'
                            'api.yaml',
                        ],
                        files_content="""
swagger: '2.0'
info:
  description: Yandex Taxi Driver Authorizer Protocol
  title: Yandex Taxi Driver Authorizer Protocol
  version: '1.0'
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': (
                            'Services schemas does not match schemas master'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:schemas/services/social/api/api.yaml': (
                        '--- '
                        'schemas_repo/schemas/services/social/api/api.yaml\n'
                        '+++ '
                        'schemas/services/social/api/api.yaml\n'
                        '@@ -0,0 +1,6 @@\n'
                        '+swagger: \'2.0\'\n'
                        '+info:\n'
                        '+    description: Yandex Passport '
                        'API\n'
                        '+    title: Yandex Passport API\n'
                        '+    version: \'1.0\'\n'
                        '+host: api.social.yandex.ru\n'
                    ),
                },
            ),
            id='match_subdirs additional files',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'social another service yaml',
                        ['schemas/services/coupons/service.yaml'],
                        files_content="""
host:
    production: api.coupons.yandex.ru
    testing: api.coupons - test.yandex.ru
    unstable: api.coupons - test.yandex.ru
middlewares:
tvm: coupons
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': (
                            'Services schemas does not match schemas master'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:schemas/services/coupons/service.yaml': (
                        '--- '
                        'schemas_repo/schemas/services/coupons/service.yaml\n'
                        '+++ '
                        'schemas/services/coupons/service.yaml\n'
                        '@@ -0,0 +1,6 @@\n'
                        '+host:\n'
                        '+    production: '
                        'api.coupons.yandex.ru\n'
                        '+    testing: api.coupons - '
                        'test.yandex.ru\n'
                        '+    unstable: api.coupons - '
                        'test.yandex.ru\n'
                        '+middlewares:\n'
                        '+tvm: coupons\n'
                    ),
                },
            ),
            id='match_subdirs new service',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'driver-map service yaml',
                        ['schemas/services/driver-map/api/api/service.yaml'],
                        files_content="""
host:
  unstable: driver-map.taxi.dev.yandex.net
""".lstrip(),
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': (
                            'Services schemas does not match schemas master'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:schemas/services/driver-map/api/'
                    'service.yaml': (
                        '--- '
                        'schemas_repo/schemas/services/driver-map/api/'
                        'service.yaml\n'
                        '+++ '
                        'schemas/services/driver-map/api/service.yaml\n'
                        '@@ -1,2 +0,0 @@\n'
                        '-host:\n'
                        '-  unstable: '
                        'driver-map.taxi.dev.yandex.net\n'
                    ),
                },
            ),
            id='match_subdirs longpath',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'driver-map service yaml',
                        ['schemas/services/service.yaml'],
                        files_content='some file content',
                    ),
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs rootdir',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'delete some_service yaml',
                        ['schemas/services/some_service/service.yaml'],
                        do_delete=True,
                    ),
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs delete repo service',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'delete some_service yaml',
                        ['schemas/services/debts/client.yaml'],
                        do_delete=True,
                    ),
                ],
                teamcity_build_fail=[
                    {
                        'description': (
                            'Services schemas does not match schemas master'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:schemas/services/debts/client.yaml': (
                        '--- '
                        'schemas_repo/schemas/services/debts/client.yaml\n'
                        '+++ '
                        'schemas/services/debts/client.yaml\n'
                        '@@ -1,6 +0,0 @@\n'
                        '-host:\n'
                        '-  production: debts.taxi.yandex.net\n'
                        '-  testing: debts.taxi.tst.yandex.net\n'
                        '-  unstable: debts.taxi.dev.yandex.net\n'
                        '-middlewares:\n'
                        '-  tvm: debts\n'
                    ),
                },
            ),
            id='match_subdirs delete one file',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'delete some_service yaml',
                        [
                            'schemas/services/debts/api/service.yaml',
                            'schemas/services/debts/client.yaml',
                        ],
                        do_delete=True,
                    ),
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs delete service content',
        ),
        pytest.param(
            Params(
                argv=[
                    '--error-message',
                    'Services schemas does not match schemas master',
                    'schemas/services/',
                    'schemas_repo/schemas/services/',
                    '--match-subdirs',
                ],
                develop_changes=[
                    repository.Commit(
                        'delete some_service yaml',
                        ['schemas/services/debts/'],
                        do_delete=True,
                    ),
                ],
                teamcity_build_fail=[],
            ),
            id='match_subdirs delete service',
        ),
    ],
)
def test_check_files_format(
        tmpdir,
        chdir,
        teamcity_report_test_problem,
        teamcity_report_problems,
        params: Params,
):
    repo = backend.init(tmpdir)
    if params.develop_changes:
        repository.apply_commits(repo, params.develop_changes)

    repo_dir = tmpdir.join('repo')
    schemas.init(repo_dir)

    chdir(repo.working_tree_dir)

    for diff_pair in params.info_changed_by_format:
        file_path = os.path.join(repo.working_tree_dir, diff_pair[0])
        with open(file_path, 'a') as fout:
            fout.write(diff_pair[1])

    files_comparer.main(params.argv)

    assert teamcity_report_problems.calls == params.teamcity_build_fail

    teamcity_error_report = params.teamcity_error_report or {}
    assert teamcity_error_report == {
        call['test_name']: call['problem_message']
        for call in teamcity_report_test_problem.calls
    }


class AnotherParams(NamedTuple):
    argv: Sequence[str]
    untracked_files: Sequence[pathlib.Path] = ()
    deleted_files: Sequence[pathlib.Path] = ()
    renamed_files: Mapping[pathlib.Path, pathlib.Path] = {}
    changed_files: Mapping[pathlib.Path, str] = {}
    untracked_files_in_submodules: Mapping[
        pathlib.Path, Sequence[pathlib.Path],
    ] = {}
    teamcity_build_fail: Optional[Sequence[dict]] = None
    teamcity_error_report: Optional[Mapping[str, str]] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            AnotherParams(
                argv=[
                    '--unstaged-changes-check',
                    '--error-message',
                    'Generated changes are not committed. Please, run '
                    '"make gen" for this project and commit generated files',
                ],
                untracked_files=[pathlib.Path('untracked_file')],
                deleted_files=[
                    pathlib.Path('schemas/services/social/service.yaml'),
                ],
                renamed_files={
                    pathlib.Path(
                        'schemas/services/driver-authorizer-external/'
                        'service.yaml',
                    ): (
                        pathlib.Path(
                            'schemas/services/driver-authorizer-external/'
                            'service2.yaml',
                        )
                    ),
                },
                changed_files={
                    pathlib.Path(
                        'schemas/services/driver-map/api/service.yaml',
                    ): 'this new data is in surger/data\n',
                },
                untracked_files_in_submodules={
                    pathlib.Path('submodules/testsuite'): [
                        pathlib.Path('testsuite_untracked'),
                    ],
                },
                teamcity_build_fail=[
                    {
                        'description': (
                            'Generated changes are not committed. '
                            'Please, run "make gen" '
                            'for this project and commit generated files'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:untracked_file': (
                        '--- /dev/null\n'
                        '+++ untracked_file\n'
                        '@@ -0,0 +1 @@\n'
                        '+untracked_file\n'
                    ),
                    'files-comparer:schemas/services/social/service.yaml': (
                        'diff --git '
                        'a/schemas/services/social/service.yaml '
                        'b/schemas/services/social/service.yaml\n'
                        'deleted file mode 100644\n'
                        'index 072b863..0000000\n'
                        '--- a/schemas/services/social/service.yaml\n'
                        '+++ /dev/null\n'
                        '@@ -1,6 +0,0 @@\n'
                        '-host:\n'
                        '-    production: api.social.yandex.ru\n'
                        '-    testing: api.social - test.yandex.ru\n'
                        '-    unstable: api.social - test.yandex.ru\n'
                        '-middlewares:\n'
                        '-tvm: social'
                    ),
                    'files-comparer:schemas/services/'
                    'driver-authorizer-external/service.yaml': (
                        'diff --git '
                        'a/schemas/services/driver-authorizer-external/'
                        'service.yaml '
                        'b/schemas/services/driver-authorizer-external/'
                        'service.yaml\n'
                        'deleted file mode 100644\n'
                        'index 91e2dbf..0000000\n'
                        '--- '
                        'a/schemas/services/driver-authorizer-external/'
                        'service.yaml\n'
                        '+++ /dev/null\n'
                        '@@ -1,4 +0,0 @@\n'
                        '-host:\n'
                        '-  production: driver-authorizer.taxi.yandex.net\n'
                        '-  testing: driver-authorizer.taxi.tst.yandex.net\n'
                        '-  unstable: driver-authorizer.taxi.dev.yandex.net'
                    ),
                    'files-comparer:schemas/services/'
                    'driver-authorizer-external/'
                    'service2.yaml': (
                        '--- /dev/null\n'
                        '+++ '
                        'schemas/services/driver-authorizer-external/'
                        'service2.yaml\n'
                        '@@ -0,0 +1,4 @@\n'
                        '+host:\n'
                        '+  production: driver-authorizer.taxi.yandex.net\n'
                        '+  testing: driver-authorizer.taxi.tst.yandex.net\n'
                        '+  unstable: driver-authorizer.taxi.dev.yandex.net\n'
                    ),
                    'files-comparer:schemas/services/driver-map/api/'
                    'service.yaml': (
                        'diff --git '
                        'a/schemas/services/driver-map/api/service.yaml '
                        'b/schemas/services/driver-map/api/service.yaml\n'
                        'index b29371d..7340a83 100644\n'
                        '--- a/schemas/services/driver-map/api/service.yaml\n'
                        '+++ b/schemas/services/driver-map/api/service.yaml\n'
                        '@@ -1,2 +1 @@\n'
                        '-host:\n'
                        '-  unstable: driver-map.taxi.dev.yandex.net\n'
                        '+this new data is in surger/data'
                    ),
                },
            ),
            id='all possible changes after codegen',
        ),
        pytest.param(
            AnotherParams(
                argv=[
                    '--unstaged-changes-check',
                    '--error-message',
                    'Generated changes are not committed. Please, run '
                    '"make gen" for this project and commit generated files',
                ],
                untracked_files_in_submodules={
                    pathlib.Path('submodules/testsuite'): [
                        pathlib.Path('testsuite_untracked'),
                    ],
                },
                teamcity_build_fail=[],
                teamcity_error_report={},
            ),
            id='no changes after codegen (submodules are ignored)',
        ),
        pytest.param(
            AnotherParams(
                argv=[
                    '--unstaged-changes-check',
                    '--error-message',
                    'Generated changes are not committed. Please, run '
                    '"make gen" for this project and commit generated files',
                ],
                untracked_files=[pathlib.Path('untracked_dir/untracked_file')],
                untracked_files_in_submodules={},
                teamcity_build_fail=[
                    {
                        'description': (
                            'Generated changes are not committed. '
                            'Please, run "make gen" '
                            'for this project and commit generated files'
                        ),
                        'identity': None,
                    },
                ],
                teamcity_error_report={
                    'files-comparer:untracked_dir/untracked_file': (
                        '--- /dev/null\n'
                        '+++ untracked_dir/untracked_file\n'
                        '@@ -0,0 +1 @@\n'
                        '+untracked_file\n'
                    ),
                },
            ),
            id='untracked dir after codegen (submodules are ignored)',
        ),
    ],
)
def test_untracked_changes(
        tmpdir,
        chdir,
        teamcity_report_problems,
        teamcity_report_test_problem,
        params: AnotherParams,
):
    repo = schemas.init(tmpdir)

    chdir(repo.working_tree_dir)

    # create some "code generated" files
    for path in params.untracked_files:
        path.parent.mkdir(exist_ok=True)
        path.touch()
        path.write_text(path.name + '\n')

    for path in params.deleted_files:
        path.unlink()

    for path_from, path_to in params.renamed_files.items():
        path_from.rename(path_to)

    for path, new_file_data in params.changed_files.items():
        path.write_text(new_file_data)

    for path, untracked_files in params.untracked_files_in_submodules.items():
        for untracked_file in untracked_files:
            untracked_file = path / untracked_file
            untracked_file.touch()
            untracked_file.write_text(untracked_file.name + '\n')

    files_comparer.main(params.argv)

    assert teamcity_report_problems.calls == params.teamcity_build_fail

    teamcity_error_report = params.teamcity_error_report or {}
    assert teamcity_error_report == {
        call['test_name']: call['problem_message']
        for call in teamcity_report_test_problem.calls
    }


class ArcParams(NamedTuple):
    changed_files: Sequence[str]
    arc_calls: Sequence[dict]
    tc_problems_calls: Sequence[dict] = []
    tc_test_problems_calls: Sequence[dict] = []
    unstaged_changes: bool = False
    source_dir: Optional[str] = None
    compare_dir: Optional[str] = None


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ArcParams(
                changed_files=[],
                arc_calls=[
                    {
                        'args': ['arc', 'diff', '$workdir', '--name-only'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
            ),
            id='no_changes',
        ),
        pytest.param(
            ArcParams(
                changed_files=['taxi/services.yaml'],
                arc_calls=[
                    {
                        'args': ['arc', 'diff', '$workdir', '--name-only'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'diff', 'services.yaml'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
                tc_problems_calls=[
                    {'description': 'Some error message', 'identity': None},
                ],
                tc_test_problems_calls=[
                    {
                        'problem_message': 'Some diff of services.yaml',
                        'test_name': 'files-comparer:services.yaml',
                    },
                ],
            ),
            id='one_changes',
        ),
        pytest.param(
            ArcParams(
                changed_files=[
                    'taxi/services.yaml',
                    'taxi/services/driver-authorizer/service.yaml',
                    'taxi/services/pilorama/src/main.cpp',
                ],
                arc_calls=[
                    {
                        'args': ['arc', 'diff', '$workdir', '--name-only'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'diff', 'services.yaml'],
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
                            'services/driver-authorizer/service.yaml',
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
                            'services/pilorama/src/main.cpp',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
                tc_problems_calls=[
                    {'description': 'Some error message', 'identity': None},
                ],
                tc_test_problems_calls=[
                    {
                        'problem_message': 'Some diff of services.yaml',
                        'test_name': 'files-comparer:services.yaml',
                    },
                    {
                        'problem_message': (
                            'Some diff of services/driver-authorizer'
                            '/service.yaml'
                        ),
                        'test_name': (
                            'files-comparer:services/driver-authorizer'
                            '/service.yaml'
                        ),
                    },
                    {
                        'problem_message': (
                            'Some diff of services/pilorama/src/main.cpp'
                        ),
                        'test_name': (
                            'files-comparer:services/pilorama/src/main.cpp'
                        ),
                    },
                ],
            ),
            id='multiple_changes',
        ),
        pytest.param(
            ArcParams(
                unstaged_changes=True,
                changed_files=[],
                arc_calls=[
                    {
                        'args': ['arc', 'status', '--short', '-u', 'all'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
            ),
            id='unstaged_no_changes',
        ),
        pytest.param(
            ArcParams(
                unstaged_changes=True,
                changed_files=['tests-pytest/conftest.py', 'services.yaml'],
                arc_calls=[
                    {
                        'args': ['arc', 'status', '--short', '-u', 'all'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'diff', 'tests-pytest/conftest.py'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'diff', 'services.yaml'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
                tc_problems_calls=[
                    {'description': 'Some error message', 'identity': None},
                ],
                tc_test_problems_calls=[
                    {
                        'problem_message': (
                            'Some diff of tests-pytest/conftest.py'
                        ),
                        'test_name': 'files-comparer:tests-pytest/conftest.py',
                    },
                    {
                        'problem_message': 'Some diff of services.yaml',
                        'test_name': 'files-comparer:services.yaml',
                    },
                ],
            ),
            id='unstaged_some_changes',
        ),
        pytest.param(
            ArcParams(
                unstaged_changes=True,
                changed_files=['tests-pytest/__init__.py', '__init__.py'],
                arc_calls=[
                    {
                        'args': ['arc', 'status', '--short', '-u', 'all'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'diff', 'tests-pytest/__init__.py'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                    {
                        'args': ['arc', 'diff', '__init__.py'],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
                tc_problems_calls=[
                    {'description': 'Some error message', 'identity': None},
                ],
                tc_test_problems_calls=[
                    {
                        'problem_message': (
                            'File tests-pytest/__init__.py is missing'
                        ),
                        'test_name': 'files-comparer:tests-pytest/__init__.py',
                    },
                    {
                        'problem_message': 'File __init__.py is missing',
                        'test_name': 'files-comparer:__init__.py',
                    },
                ],
            ),
            id='check_missed_init',
        ),
        pytest.param(
            ArcParams(
                changed_files=[],
                arc_calls=[
                    {
                        'args': ['arc', 'merge-base', 'HEAD', 'trunk'],
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
                            'HEAD',
                            'a123abc',
                            'uservices',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
                source_dir='uservices',
                compare_dir='schemas',
            ),
            id='matching_no_changes',
        ),
        pytest.param(
            ArcParams(
                changed_files=[
                    'taxi/uservices/services.yaml',
                    'taxi/uservices/services/driver-authorizer/service.yaml',
                ],
                arc_calls=[
                    {
                        'args': ['arc', 'merge-base', 'HEAD', 'trunk'],
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
                            'HEAD',
                            'a123abc',
                            'uservices',
                            '--name-only',
                        ],
                        'kwargs': {
                            'cwd': '$workdir',
                            'env': None,
                            'stderr': -1,
                            'stdout': -1,
                        },
                    },
                ],
                source_dir='uservices',
                compare_dir='schemas',
            ),
            id='matching_some_changes_no_files',
        ),
    ],
)
def test_arc(
        params,
        commands_mock,
        tmpdir,
        monkeypatch,
        teamcity_report_problems,
        teamcity_report_test_problem,
):
    work_dir = arcadia.init_dummy(tmpdir)
    monkeypatch.chdir(work_dir)

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'diff':
            if args[-1] == '--name-only':
                return '\n'.join(params.changed_files)
            if args[-1].endswith('__init__.py'):
                return ''
            return 'Some diff of ' + args[2]
        if command == 'status':
            return '\n'.join(('M  ' + file for file in params.changed_files))
        if command == 'merge-base':
            return 'a123abc'
        return 1  # unsupported command

    arc.substitute_paths(params.arc_calls, {'workdir': work_dir})

    argv = ['--error-message', 'Some error message']
    if params.source_dir:
        argv.append(params.source_dir)
    else:
        argv.append(str(work_dir))
    if params.compare_dir:
        argv.append(params.compare_dir)
    if params.unstaged_changes:
        argv.append('--unstaged-changes-check')

    files_comparer.main(argv)

    assert arc_mock.calls == params.arc_calls
    assert teamcity_report_problems.calls == params.tc_problems_calls
    assert teamcity_report_test_problem.calls == params.tc_test_problems_calls
