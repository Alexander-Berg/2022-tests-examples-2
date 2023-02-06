# pylint: disable=too-many-lines
import pathlib
import shutil
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Sequence
from typing import Type

import git
import pytest

import get_changed_projects
from taxi_buildagent import dep_graph
from tests.plugins import arc
from tests.utils import repository
from tests.utils.examples import backend_cpp
from tests.utils.examples import backend_py3
from tests.utils.examples import uservices


class Params(NamedTuple):
    init_repo: Callable[[str], git.Repo]
    expected: str = ''
    develop: bool = False
    commits: Sequence[repository.Commit] = ()
    exception_class: Optional[Type[Exception]] = None
    os_name: Optional[str] = None
    ya_make_only: bool = False
    force_changed: Sequence[str] = ()
    force_changed_env: Optional[str] = None
    force_changed_all: bool = False
    exclude_projects: Optional[str] = None
    changes_count: int = 0


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(init_repo=backend_cpp.init, expected='_empty'),
            id='backend-cpp empty',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                develop=True,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
            ),
            id='backend-cpp develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[repository.Commit('a', ['a'])],
            ),
            id='backend-cpp all',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='main surger',
                changes_count=2,
                commits=[
                    repository.Commit(
                        'antifraud', ['common/clients/antifraud/file1'],
                    ),
                ],
            ),
            id='backend-cpp graph',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud graph main',
                changes_count=3,
                commits=[
                    repository.Commit(
                        'antifraud swagger', ['antifraud/docs/yaml/file1'],
                    ),
                ],
            ),
            id='backend-cpp swagger',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='main surger',
                changes_count=2,
                commits=[
                    repository.Commit(
                        'only surger', ['surger/docs/yaml/file1'],
                    ),
                ],
            ),
            id='backend-cpp only surger',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected=(
                    'File malformed (no project name): '
                    'common/clients/antifraud/service.yaml'
                ),
                commits=[
                    repository.Commit(
                        comment='antifraud',
                        files=['common/clients/antifraud/service.yaml'],
                        # Broken service.yaml -- no 'project-name' property.
                        files_content="""
project-type: static
link-targets:
  - yandex-taxi-common
""".lstrip(),
                    ),
                ],
                exception_class=dep_graph.DepGraphBuildException,
            ),
            id='backend-cpp exception malformed (no project name)',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected=(
                    'File malformed (no short name): antifraud/service.yaml'
                ),
                commits=[
                    repository.Commit(
                        comment='antifraud',
                        files=['antifraud/service.yaml'],
                        # Broken service.yaml -- no 'short-name' property.
                        files_content="""
project-name: yandex-taxi-antifraud
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
has-swagger-client: true
""".lstrip(),
                    ),
                ],
                exception_class=dep_graph.DepGraphBuildException,
            ),
            id='backend-cpp exception malformed (no short name)',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='Duplicate projects occurred: yandex-taxi-surger',
                commits=[
                    repository.Commit(
                        comment='antifraud',
                        files=['common/clients/antifraud/service.yaml'],
                        files_content="""
project-name: yandex-taxi-surger
project-type: static
link-targets:
  - yandex-taxi-common
""".lstrip(),
                    ),
                ],
                exception_class=dep_graph.DepGraphBuildException,
            ),
            id='backend-cpp exception duplicate',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud',
                changes_count=1,
                commits=[repository.Commit('a', ['antifraud/fl'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='surger',
                changes_count=1,
                commits=[repository.Commit('a', ['surger/filey'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='main',
                changes_count=1,
                commits=[repository.Commit('a', ['tracker/123'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud surger',
                changes_count=2,
                commits=[
                    repository.Commit('a', ['antifraud/xx', 'surger/yy']),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud main',
                changes_count=2,
                commits=[
                    repository.Commit('a', ['antifraud/xx', 'tracker/yy']),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud main surger',
                changes_count=3,
                commits=[
                    repository.Commit(
                        'a', ['antifraud/xx', 'surger/yy', 'tracker/zz'],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[
                    repository.Commit(
                        'a',
                        [
                            'antifraud/xx',
                            'surger/yy',
                            'tracker/zz',
                            'common/src/aa',
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'a',
                        [
                            'antifraud/3',
                            'common/config/templates/config_fallback.json.tpl',
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='main',
                changes_count=1,
                commits=[repository.Commit('a', ['testsuite/tests/chat/ff'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[repository.Commit('a', ['testsuite/tests/ff'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[repository.Commit('a', ['testsuite/ss'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='_empty',
                commits=[
                    repository.Commit(
                        'a', ['common/config/templates/config.json.tpl'],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='main',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'a',
                        [
                            'tracker/a',
                            'common/config/templates/config_fallback.json.tpl',
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[
                    repository.Commit(
                        'a',
                        [
                            'a',
                            'common/config/templates/config_fallback.json.tpl',
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[repository.Commit('a', ['antifraud2'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[repository.Commit('a', ['tracker2'])],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[
                    repository.Commit(
                        'a',
                        [],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [repository.Commit('a', 'file')],
                            ),
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[
                    repository.Commit(
                        'a',
                        ['antifraud/1'],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [repository.Commit('a', 'file')],
                            ),
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(
                init_repo=backend_cpp.init,
                expected='antifraud driver-protocol graph protocol '
                'reposition surger',
                changes_count=6,
                commits=[
                    repository.Commit(
                        'a',
                        ['tracker/1'],
                        submodules=[
                            (
                                'submodules/testsuite',
                                [repository.Commit('a', 'file')],
                            ),
                        ],
                    ),
                ],
            ),
            id='backend-cpp',
        ),
        pytest.param(
            Params(init_repo=uservices.init, expected='_empty'),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[
                    repository.Commit(
                        'a',
                        [],
                        submodules=[
                            ('userver', [repository.Commit('a', ['file'])]),
                        ],
                    ),
                ],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                develop=True,
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[repository.Commit('a', ['Makefile'])],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[repository.Commit('a', ['service'])],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[repository.Commit('a', ['services/new/123'])],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer',
                changes_count=1,
                commits=[
                    repository.Commit('a', ['services/driver-authorizer/1']),
                ],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer2',
                changes_count=1,
                commits=[
                    repository.Commit('a', ['services/driver-authorizer2/2']),
                ],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[
                    repository.Commit(
                        'a', ['services/driver-authorizer/1', 'b'],
                    ),
                ],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[
                    repository.Commit('a', ['services/driver-authorizer22/1']),
                ],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[repository.Commit('a', ['services2'])],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[
                    repository.Commit(
                        'a',
                        ['services/driver-authorizer/1'],
                        submodules=[
                            ('userver', [repository.Commit('a', 'file')]),
                        ],
                    ),
                ],
            ),
            id='uservices',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='device-notify',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='device-notify',
                        files=['services/device-notify/service.yaml'],
                        files_content="""
project-name: yandex-taxi-device-notify
short-name: device-notify
""".lstrip(),
                    ),
                    repository.Commit(
                        'a',
                        [
                            'services/device-notify/debian/changelog',
                            'services/device-notify/'
                            'local-files-dependencies.txt',
                        ],
                    ),
                ],
            ),
            id='uservices new service (with changelog)',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    '(\'some services does not have service.yaml and/or '
                    'local-files-dependencies.txt, please add them: '
                    'services/device-notify\', None)'
                ),
                changes_count=1,
                commits=[
                    repository.Commit(
                        'a', ['services/device-notify/debian/changelog'],
                    ),
                ],
                exception_class=get_changed_projects.GetChangedProjectsExc,
            ),
            id='uservices new service without yaml file (for compatibility)',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer3',
                changes_count=1,
                commits=[repository.Commit('a', ['libraries/some-library/1'])],
            ),
            id='uservices library changes',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='_empty',
                commits=[
                    repository.Commit('a', ['libraries/unused-library/1']),
                    repository.Commit(
                        'a', ['libraries/one-file-library/library.yaml'],
                    ),
                ],
            ),
            id='uservices unused-library changes',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
                commits=[
                    repository.Commit('a', ['libraries/unused-library/1']),
                    repository.Commit('a', ['libraries/one-file-library']),
                ],
                changes_count=4,
            ),
            id='uservices one_file_library',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
                commits=[
                    repository.Commit('a', ['services/one-file-service']),
                ],
                changes_count=4,
            ),
            id='uservices one_file_service',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='driver-authorizer',
                        files=['services/driver-authorizer/service.yaml'],
                        files_content="""
project-name: yandex-taxi-driver-authorizer
short-name: driver-authorizer
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
""".lstrip(),
                    ),
                ],
            ),
            id='uservices xenial',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                os_name='xenial',
                expected='driver-authorizer3',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='driver-authorizer',
                        files=['services/driver-authorizer3/service.yaml'],
                        files_content="""
project-name: yandex-taxi-driver-authorizer3
short-name: driver-authorizer3
target-os:
  - xenial
  - bionic
""".lstrip(),
                    ),
                ],
            ),
            id='uservices xenial and bionic',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                os_name='bionic',
                expected='driver-authorizer',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='driver-authorizer',
                        files=['services/driver-authorizer/service.yaml'],
                        files_content="""
project-name: yandex-taxi-driver-authorizer
short-name: driver-authorizer
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - bionic
""".lstrip(),
                    ),
                ],
            ),
            id='uservices bionic',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                os_name='xenial',
                expected='driver-authorizer pilorama',
                changes_count=2,
                commits=[
                    repository.Commit(
                        comment='driver-authorizer',
                        files=['services/driver-authorizer/service.yaml'],
                        files_content="""
project-name: yandex-taxi-driver-authorizer
short-name: driver-authorizer
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
""".lstrip(),
                    ),
                    repository.Commit(
                        comment='pilorama',
                        files=['services/pilorama/service.yaml'],
                        files_content="""
project-name: yandex-taxi-pilorama
short-name: pilorama
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
  - bionic
""".lstrip(),
                    ),
                ],
            ),
            id='uservices several services (xenial)',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                os_name='bionic',
                expected='pilorama',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='driver-authorizer',
                        files=['services/driver-authorizer/service.yaml'],
                        files_content="""
project-name: yandex-taxi-driver-authorizer
short-name: driver-authorizer
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
""".lstrip(),
                    ),
                    repository.Commit(
                        comment='pilorama',
                        files=['services/pilorama/service.yaml'],
                        files_content="""
project-name: yandex-taxi-pilorama
short-name: pilorama
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
  - bionic
""".lstrip(),
                    ),
                ],
            ),
            id='uservices several services (bionic)',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                ya_make_only=True,
                expected='driver-authorizer',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='move to tier0',
                        files=[
                            'services/driver-authorizer/service.yaml',
                            'services/driver-authorizer/gen/ya.make',
                        ],
                        files_content="""
project-name: yandex-taxi-driver-authorizer
short-name: driver-authorizer
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - bionic
ya-make:
  enabled: maybe
""".lstrip(),
                    ),
                    repository.Commit(
                        comment='pilorama',
                        files=['services/pilorama/service.yaml'],
                        files_content="""
project-name: yandex-taxi-pilorama
short-name: pilorama
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
  - bionic
""".lstrip(),
                    ),
                ],
            ),
            id='uservices only ya make',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                os_name='bionic',
                expected='pilorama',
                changes_count=1,
                commits=[
                    repository.Commit(
                        comment='move to tier0',
                        files=[
                            'services/driver-authorizer/service.yaml',
                            'services/driver-authorizer/gen/ya.make',
                        ],
                        files_content="""
project-name: yandex-taxi-driver-authorizer
short-name: driver-authorizer
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - bionic
ya-make:
  enabled: maybe
""".lstrip(),
                    ),
                    repository.Commit(
                        comment='pilorama',
                        files=['services/pilorama/service.yaml'],
                        files_content="""
project-name: yandex-taxi-pilorama
short-name: pilorama
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
target-os:
  - xenial
  - bionic
""".lstrip(),
                    ),
                ],
            ),
            id='uservices exclude ya make',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2 '
                'driver-authorizer3 pilorama',
                changes_count=4,
                commits=[repository.Commit('a', ['service'])],
            ),
            id='uservices all',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='_empty',
                commits=[
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
            ),
            id='uservices add orphaned config',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='_empty',
                commits=[
                    repository.Commit(
                        'add orphaned config',
                        ['schemas/configs/declarations/some.yaml'],
                    ),
                ],
            ),
            id='uservices add orphaned config',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),  # all services
                changes_count=4,
                commits=[
                    repository.Commit(
                        'add orphaned config',
                        ['schemas/configs/something-else'],
                    ),
                ],
            ),
            id='uservices add orphaned config',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='_empty',
                force_changed=['.github/CODEOWNERS'],
            ),
            id='uservices force_changed ignored',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer3',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'comment', files=['services/driver-authorizer/'],
                    ),
                ],
                force_changed=['services/driver-authorizer3'],
            ),
            id='uservices force_changed service ignore_develop',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer3',
                changes_count=1,
                force_changed=['services/driver-authorizer3'],
            ),
            id='uservices force_changed service',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer3',
                changes_count=1,
                force_changed=['libraries/some-library'],
            ),
            id='uservices force_changed library',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2'
                ' driver-authorizer3 pilorama',
                changes_count=4,
                force_changed=['libraries/rock-and-roll'],
            ),
            id='uservices force_changed unknown_path rebuild_all',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2'
                ' driver-authorizer3 pilorama',
                changes_count=4,
                force_changed=['services/rock-and-roll'],
            ),
            id='uservices force_changed unknown_path rebuild_all',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                develop=True,
                force_changed_env='.github/CODEOWNERS',
                expected='_empty',
                changes_count=0,
            ),
            id='uservices force_changed_env empty',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                develop=True,
                force_changed_env='services/driver-authorizer3',
                expected='driver-authorizer3',
                changes_count=1,
            ),
            id='uservices force_changed service directory',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                develop=True,
                force_changed_env='libraries/some-library',
                expected='driver-authorizer3',
                changes_count=1,
            ),
            id='uservices force_changed_env library dicrectory',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                develop=True,
                force_changed_env=(
                    'services/driver-authorizer3/file with space\n'
                    'services/driver-authorizer2/file2\n'
                    'services/driver-authorizer/file3\n'
                ),
                expected=(
                    'driver-authorizer driver-authorizer2 driver-authorizer3'
                ),
                changes_count=3,
            ),
            id='uservices force_changed_env multiple',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                develop=True,
                force_changed_env='new-file.sh',
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
                changes_count=4,
            ),
            id='uservices force_changed_env new-file',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                develop=True,
                force_changed_env='',
                expected='_empty',
            ),
            id='uservices force_changed_env empty',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                force_changed_env='tax',
            ),
            id='backend-py3 force_changed_env common',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                force_changed_env='tax\nservices/taxi-adjust/a/b/c',
            ),
            id='backend-py3 force_changed_env common service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                expected='services/taxi-adjust',
                changes_count=1,
                force_changed_env='services/taxi-adjust/1',
            ),
            id='backend-py3 force_changed_env service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                expected='services/taxi-adjust services/taxi-corp-data',
                changes_count=2,
                force_changed_env=(
                    'services/taxi-adjust/file with space\n'
                    'services/taxi-corp-data/file with space\n'
                ),
            ),
            id='backend-py3 force_changed_env services',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                force_changed_env='taxi/db.py',
            ),
            id='backend-py3 force_changed_env taxi',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                expected=(
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust'
                ),
                changes_count=3,
                force_changed_env='libraries/very-common-library/a.py',
            ),
            id='backend-py3 force_changed_env library',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                develop=True,
                force_changed_env='',
                expected='_empty',
            ),
            id='backend-py3 force_changed_env empty',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
                changes_count=4,
                commits=[
                    repository.Commit(
                        'a',
                        ['services/driver-authorizer/1'],
                        submodules=[
                            ('userver', [repository.Commit('a', 'file')]),
                        ],
                    ),
                ],
                exclude_projects='',
            ),
            id='uservices exclude no',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='driver-authorizer driver-authorizer2',
                changes_count=2,
                commits=[
                    repository.Commit(
                        'a',
                        ['services/driver-authorizer/1'],
                        submodules=[
                            ('userver', [repository.Commit('a', 'file')]),
                        ],
                    ),
                ],
                exclude_projects='driver-authorizer3, pilorama',
            ),
            id='uservices exclude comma services',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected='_empty',
                commits=[
                    repository.Commit(
                        'a',
                        ['services/driver-authorizer/1'],
                        submodules=[
                            ('userver', [repository.Commit('a', 'file')]),
                        ],
                    ),
                ],
                exclude_projects=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
            ),
            id='uservices exclude all services',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
                changes_count=4,
                commits=[
                    repository.Commit(
                        'change some rand deps', ['some-deps/SomeDeps2.yaml'],
                    ),
                ],
            ),
            id='uservices change some_random_dependant',
        ),
        pytest.param(
            Params(
                init_repo=uservices.init,
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
                changes_count=4,
                commits=[
                    repository.Commit(
                        'remove some rand deps',
                        ['some-deps/SomeDeps2.yaml'],
                        do_delete=True,
                    ),
                ],
            ),
            id='uservices remove some_random_dependant',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library '
                    'services/taxi-adjust '
                    'services/taxi-fleet'
                ),
                changes_count=3,
                commits=[
                    repository.Commit('a', ['libraries/another-library/a']),
                ],
            ),
            id='backend-py3 library change',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init, expected='_empty', develop=False,
            ),
            id='backend-py3 empty',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                develop=True,
            ),
            id='backend-py3 develop',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                commits=[repository.Commit('a', ['tax'])],
            ),
            id='backend-py3 common',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                commits=[
                    repository.Commit(
                        'a', ['tax', 'services/taxi-adjust/a/b/c'],
                    ),
                ],
            ),
            id='backend-py3 common service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-adjust',
                changes_count=1,
                commits=[repository.Commit('a', ['services/taxi-adjust/1'])],
            ),
            id='backend-py3 service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-corp',
                changes_count=1,
                commits=[repository.Commit('a', ['services/taxi-corp/2'])],
            ),
            id='backend-py3 service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taximeter',
                changes_count=1,
                commits=[repository.Commit('a', ['services/taximeter/aa'])],
            ),
            id='backend-py3 service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-adjust services/taxi-corp-data',
                changes_count=2,
                commits=[
                    repository.Commit(
                        'a',
                        [
                            'services/taxi-adjust/1',
                            'services/taxi-corp-data/2',
                        ],
                    ),
                ],
            ),
            id='backend-py3 services',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library '
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust '
                    'services/taxi-corp '
                    'services/taxi-corp-data '
                    'services/taxi-fleet '
                    'services/taximeter '
                    'taxi plugins '
                    'tests'
                ),
                changes_count=10,  # must be 11
                commits=[repository.Commit('db', ['taxi/db.py'])],
            ),
            id='backend-py3 common',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust'
                ),
                changes_count=3,
                commits=[
                    repository.Commit(
                        'very-common-library',
                        ['libraries/very-common-library/a.py'],
                    ),
                ],
            ),
            id='backend-py3 library',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='libraries/some-library services/taxi-adjust',
                changes_count=2,
                commits=[
                    repository.Commit(
                        'some-library', ['libraries/some-library/a.py'],
                    ),
                ],
            ),
            id='backend-py3 library',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='libraries/new-library',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'new-library', ['libraries/new-library/123'],
                    ),
                    repository.Commit(
                        'new-library',
                        ['libraries/new-library/library.yaml'],
                        files_content='description: new library, no one uses',
                    ),
                ],
            ),
            id='backend-py3 new-library',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-adjust',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'add config',
                        [
                            'schemas/configs/declarations/'
                            + 'taxi-adjust/ADJUST_RETRIES.yaml',
                        ],
                    ),
                ],
            ),
            id='backend-py3 add-config',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='_empty',
                commits=[
                    repository.Commit(
                        'add config',
                        [
                            'schemas/configs/declarations/'
                            + 'taxi-adjust/SOMETHING.yaml',
                        ],
                    ),
                ],
            ),
            id='backend-py3 add-config orphan',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/some-library '
                    'services/taxi-adjust '
                    'services/taxi-fleet'
                ),
                changes_count=3,
                commits=[
                    repository.Commit(
                        'add new api',
                        ['schemas/services/protocol/api_2.yaml'],
                    ),
                ],
            ),
            id='backend-py3 library add-service-schema',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='_empty',
                commits=[
                    repository.Commit(
                        'add unused schema',
                        ['schemas/services/driver-protocol/api.yaml'],
                    ),
                ],
            ),
            id='backend-py3 library add-service-schema',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/some-library services/taxi-adjust '
                    'services/taxi-corp tests'
                ),
                changes_count=4,
                commits=[
                    repository.Commit(
                        'update geoareas', ['schemas/mongo/geoareas.yaml'],
                    ),
                ],
            ),
            id='backend-py3 library add-mongo-schema',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-corp tests',
                changes_count=2,
                commits=[
                    repository.Commit(
                        'add new schema', ['schemas/mongo/new_colletion.yaml'],
                    ),
                ],
            ),
            id='backend-py3 add-mongo-schema common',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-adjust services/taxi-corp tests',
                changes_count=3,
                commits=[
                    repository.Commit(
                        'update schema', ['schemas/mongo/adjust_events.yaml'],
                    ),
                ],
            ),
            id='backend-py3 add-mongo-schema service',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust services/taxi-corp '
                    'services/taxi-corp-data services/taxi-fleet '
                    'services/taximeter taxi plugins tests'
                ),
                changes_count=10,  # must be 11
                commits=[
                    repository.Commit(
                        'new schemas type', ['schemas/redis/baobab.yaml'],
                    ),
                ],
            ),
            id='backend-py3 orphaned',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust services/taxi-corp '
                    'services/taxi-corp-data services/taxi-fleet '
                    'services/taximeter taxi plugins tests'
                ),
                changes_count=10,  # must be 11
                commits=[
                    repository.Commit('new schemas type', ['schemas/redis']),
                ],
            ),
            id='backend-py3 orphaned',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust services/taxi-corp '
                    'services/taxi-corp-data services/taxi-fleet '
                    'services/taximeter taxi plugins tests'
                ),
                changes_count=10,  # must be 11
                commits=[repository.Commit('new dir', ['dir'])],
            ),
            id='backend-py3 new-dir',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected=(
                    'libraries/another-library libraries/some-library '
                    'libraries/very-common-library '
                    'services/taxi-adjust services/taxi-corp '
                    'services/taxi-corp-data services/taxi-fleet '
                    'services/taximeter taxi plugins tests'
                ),
                changes_count=10,  # must be 11
                commits=[
                    repository.Commit(
                        'new plugin', ['plugins/hello/plugin.py'],
                    ),
                ],
            ),
            id='backend-py3 new-plugin',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='services/taxi-adjust',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'remove config',
                        [
                            'schemas/configs/declarations/'
                            + 'taxi-adjust/ADJUST_TIMEOUT.yaml',
                        ],
                        do_delete=True,
                    ),
                ],
            ),
            id='backend-py3 remove config',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='tests',
                changes_count=1,
                commits=[
                    repository.Commit(
                        'remove config', ['tests/data'], do_delete=True,
                    ),
                ],
            ),
            id='backend-py3 remove test data',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='libraries/another-library libraries/some-library '
                'libraries/very-common-library services/taxi-adjust '
                'services/taxi-corp services/taxi-corp-data '
                'services/taxi-fleet services/taximeter '
                'taxi plugins tests',
                changes_count=10,  # must be 11
                commits=[repository.Commit('change all', ['tools/some'])],
            ),
            id='backend-py3 change tools',
        ),
        pytest.param(
            Params(
                init_repo=backend_py3.init,
                expected='libraries/another-library libraries/some-library '
                'libraries/very-common-library services/taxi-adjust '
                'services/taxi-corp services/taxi-corp-data '
                'services/taxi-fleet services/taximeter '
                'taxi plugins tests',
                changes_count=10,  # must be 11
                commits=[
                    repository.Commit(
                        'remove config', ['tests/data'], do_delete=True,
                    ),
                ],
                force_changed_all=True,
            ),
            id='backend-py3 force changed all',
        ),
    ],
)
def test_main(
        monkeypatch,
        tmpdir,
        teamcity_set_parameters,
        teamcity_report_statistic,
        params: Params,
) -> None:
    repo = params.init_repo(tmpdir)
    if params.develop:
        assert not params.commits
    else:
        repo.git.checkout('-b', 'pr')
        repository.apply_commits(repo, params.commits)
        repo.git.checkout(repo.head.commit)

    args = [repo.working_tree_dir]
    if params.os_name is not None:
        args.extend(['--os', params.os_name])
    if params.ya_make_only:
        args.extend(['--ya-make-only'])
    for path in params.force_changed:
        args.extend(['--force-changed', path])
    if params.force_changed_all:
        args.extend(['--force-changed-all'])
    if params.force_changed_env is not None:
        monkeypatch.setenv(
            'GET_CHANGED_PROJECTS_FORCE_CHANGED', params.force_changed_env,
        )
    if params.exclude_projects is not None:
        args.extend(['--exclude-projects', params.exclude_projects])

    if params.exception_class:
        with pytest.raises(params.exception_class) as exc_info:
            get_changed_projects.main(args)
        assert params.expected == str(exc_info.value)
        assert teamcity_set_parameters.calls == []
        assert teamcity_report_statistic.calls == []
    else:
        get_changed_projects.main(args)
        assert teamcity_set_parameters.calls == [
            {'name': 'env.CHANGED_PROJECTS', 'value': params.expected},
        ]
        assert teamcity_report_statistic.calls == [
            {'key': 'changed_projects', 'value': params.changes_count},
        ]


class ArcParams(NamedTuple):
    changed_files: List[str]
    arc_calls: List[Dict[str, Any]]
    branch: str
    expected: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            ArcParams(
                changed_files=[],
                branch='users/dteterin/feature/driver-authorizer',
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
                        'args': ['arc', 'fetch', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'merge-base', 'trunk', 'HEAD'],
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
                            'c3b2a1',
                            'HEAD',
                            '.',
                            '$ml_path',
                            '$schemas_path',
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
                expected='_empty',
            ),
            id='empty_case',
        ),
        pytest.param(
            ArcParams(
                changed_files=['repo/services/driver-authorizer/service.yaml'],
                branch='users/dteterin/feature/some-branch',
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
                        'args': ['arc', 'fetch', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'merge-base', 'trunk', 'HEAD'],
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
                            'c3b2a1',
                            'HEAD',
                            '.',
                            '$ml_path',
                            '$schemas_path',
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
                expected='driver-authorizer',
            ),
            id='pr_branch',
        ),
        pytest.param(
            ArcParams(
                changed_files=[],
                branch='trunk',
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
                ],
                expected=(
                    'driver-authorizer driver-authorizer2 '
                    'driver-authorizer3 pilorama'
                ),
            ),
            id='trunk_branch',
        ),
        pytest.param(
            ArcParams(
                changed_files=['schemas/schemas/mongo/configs_meta.yaml'],
                branch='users/dteterin/feature/some-branch',
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
                        'args': ['arc', 'fetch', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'merge-base', 'trunk', 'HEAD'],
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
                            'c3b2a1',
                            'HEAD',
                            '.',
                            '$ml_path',
                            '$schemas_path',
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
                expected='driver-authorizer2',
            ),
            id='external_shared_dir',
        ),
        pytest.param(
            ArcParams(
                changed_files=['ml/taxi_ml_cxx/lib/src/example/objects.cpp'],
                branch='users/sanyash/feature/use_ml_from_arcadia',
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
                        'args': ['arc', 'fetch', 'trunk'],
                        'kwargs': {'cwd': '$workdir', 'env': None},
                    },
                    {
                        'args': ['arc', 'merge-base', 'trunk', 'HEAD'],
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
                            'c3b2a1',
                            'HEAD',
                            '.',
                            '$ml_path',
                            '$schemas_path',
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
                expected='driver-authorizer3',
            ),
            id='use_ml_from_arcadia',
        ),
    ],
)
def test_main_arc(
        params, commands_mock, tmpdir, teamcity_set_parameters, monkeypatch,
):
    root_dir = pathlib.Path(tmpdir)
    (root_dir / '.arc').mkdir(parents=True, exist_ok=True)
    uservices.init(tmpdir)
    workdir = pathlib.Path(tmpdir / 'repo')
    shutil.rmtree(workdir / '.git')  # it'll be arc repo
    schemas_path = tmpdir / 'schemas/schemas'
    ml_path = tmpdir / 'ml'

    arc.substitute_paths(
        params.arc_calls,
        {'workdir': workdir, 'schemas_path': schemas_path, 'ml_path': ml_path},
    )

    @commands_mock('arc')
    def arc_mock(args, **kwargs):
        command = args[1]
        if command == 'info':
            return '{"hash": "abc123", "branch": "%s"}' % params.branch
        if command == 'merge-base':
            return 'c3b2a1'
        if command == 'diff':
            return '\n'.join(params.changed_files)
        return 0

    get_changed_projects.main([str(workdir)])

    assert arc_mock.calls == params.arc_calls
    assert teamcity_set_parameters.calls == [
        {'name': 'env.CHANGED_PROJECTS', 'value': params.expected},
    ]
