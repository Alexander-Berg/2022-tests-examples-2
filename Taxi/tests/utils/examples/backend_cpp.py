from tests.utils import repository


def init(tmpdir):
    path = str(tmpdir.mkdir('repo'))
    repo = repository.init_repo(
        path,
        'alberist',
        'alberist@yandex-team.ru',
        [
            repository.Commit(
                'init repo',
                files=[
                    'common/clients/antifraud/data',
                    'common/config/templates/config_fallback.json.tpl',
                    'common/src/data',
                    'antifraud/data',
                    'surger/data',
                    'protocol/data',
                    'tracker/data',
                    'docs/data',
                    'driver-protocol/data',
                    'reposition/data',
                ],
                submodules=[
                    (
                        'submodules/testsuite',
                        [
                            repository.Commit(
                                'init submodule', ['file1', 'file2'],
                            ),
                            repository.Commit('second commit', ['file3']),
                        ],
                    ),
                    (
                        'submodules/random_submodule',
                        [
                            repository.Commit(
                                'init_submodule', ['file_1', 'file_2'],
                            ),
                            repository.Commit('second_commit', ['file_3']),
                        ],
                    ),
                ],
            ),
        ],
    )
    repository.commit_debian_dir(
        repo,
        'taxi-antifraud',
        path='antifraud',
        version='3.0.0hotfix25',
        release_ticket='TAXIREL-123',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-surger',
        path='surger',
        version='3.3.5',
        release_ticket='TAXIREL-124',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-backend-cpp',
        version='2.1.1',
        release_ticket='TAXIREL-100',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-protocol',
        path='protocol',
        version='3.2.4',
        release_ticket='TAXIREL-125',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-backend-cpp',
        path='graph',
        version='2.1.1',
        release_ticket='TAXIREL-101',
    )
    repository.commit_debian_dir(
        repo,
        'driver-protocol',
        path='driver-protocol',
        version='7.4.5',
        release_ticket='TAXIREL-891',
    )
    repository.commit_debian_dir(
        repo,
        'reposition',
        path='reposition',
        version='8.3.2',
        release_ticket='TAXIREL-368',
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'service',
                ['services.yaml'],
                files_content="""
services:
  main:
    - tracker
    - testsuite/tests/chat
    - graph
lang: cpp
common:
  ignore:
    - common/config
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='antifraud client service yaml',
                files=['common/clients/antifraud/service.yaml'],
                files_content="""
project-name: yandex-taxi-client-antifraud
project-type: static
link-targets:
  - yandex-taxi-common
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='antifraud service yaml',
                files=['antifraud/lib/service.yaml'],
                files_content="""
project-name: yandex-taxi-antifraud
short-name: antifraud
link-targets:
  - yandex-taxi-common
  - yandex-taxi-some-lib
has-swagger-client: true
    """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='surger service yaml',
                files=['surger/service.yaml'],
                files_content="""
project-name: yandex-taxi-surger
teamcity:
    release-attach-disabled: yes
link-targets:
  - yandex-taxi-common
  - yandex-taxi-client-antifraud
    """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='some lib service yaml',
                files=['some_lib/service.yaml'],
                files_content="""
project-name: yandex-taxi-some-lib
    """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='protocol client service yaml',
                files=['protocol/lib/service.yaml'],
                files_content="""
project-name: taxi-protocol
teamcity:
    release-attach-disabled: yes
link-targets:
  - yandex-taxi-common
  - yandex-taxi-protocol
    """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='graph',
                files=['graph/service.yaml'],
                files_content="""
project-name: yandex-taxi-graph
link-targets:
  - antifraud_swagger_api
        """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='driver-protocol service yaml',
                files=['driver-protocol/service.yaml'],
                files_content="""
project-name: yandex-taxi-driver-protocol
description: taxi driver-protocol
short-name: driver-protocol
extended-name: taxi-driver-protocol
hostname:
  production: driver-protocol.taxi.yandex.net
link-targets:
  - yandex-taxi-client-geotracks
  - yandex-taxi-client-billing-accounts
  - Boost
  - yandex-taxi-reposition-client
  - yandex-taxi-reposition-models
  - tags_swagger_api
  - driver_metrics_swagger_api
            """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='reposition service yaml',
                files=['reposition/service.yaml'],
                files_content="""
project-name: yandex-taxi-reposition
description: Reposition description
short-name: reposition
extended-name: taxi-reposition
hostname:
  production: reposition.taxi.yandex.net
link-targets:
  - yandex-taxi-common
  - reposition_swagger_handlers
  - reposition_swagger_api
  - tags_swagger_api
has-swagger-client: true
        """.lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='client reposition service yaml',
                files=['common/reposition/client/service.yaml'],
                files_content="""
project-name: yandex-taxi-reposition-client
project-type: static
link-targets:
  - Boost
  - yandex-taxi-common
  - yandex-taxi-reposition-models
  - reposition_swagger_api
            """.lstrip(),
            ),
        ],
    )

    repo.git.checkout('-b', 'masters/antifraud')
    repo.git.checkout('-b', 'masters/protocol')
    repo.git.checkout('-b', 'masters/surger')
    repo.git.checkout('-b', 'masters/driver-protocol')
    repo.git.checkout('-b', 'masters/reposition')
    repo.git.checkout('-b', 'master')
    repo.git.checkout('develop')

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    return repo
