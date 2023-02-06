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
                    'services/driver-authorizer/data',
                    'services/driver-authorizer/Dockerfile',
                    'services/driver-authorizer2/data',
                    'services/driver-authorizer3/data',
                    'services/pilorama/data',
                    'libraries/some-library/data',
                    'libraries/another-library/data',
                    'libraries/unused-library/data',
                    'testsuite/data',
                    'some-deps/SomeDeps2.yaml',
                    'Makefile',
                ],
                submodules=[
                    (
                        'userver',
                        [repository.Commit('init repo', ['file1', 'file2'])],
                    ),
                ],
            ),
        ],
    )
    repository.commit_debian_dir(
        repo,
        'driver-authorizer',
        path='services/driver-authorizer',
        release_ticket='TAXIREL-1',
        version='1.1.1',
    )
    repository.commit_debian_dir(
        repo,
        'driver-authorizer2',
        path='services/driver-authorizer2',
        release_ticket='TAXIREL-2',
        version='2.2.2',
    )
    repository.commit_debian_dir(
        repo,
        'pilorama',
        path='services/pilorama',
        release_ticket='TAXIREL-3',
        version='1.1.1',
    )
    repository.commit_debian_dir(
        repo,
        'driver-authorizer3',
        path='services/driver-authorizer3',
        release_ticket='TAXIREL-4',
        version='1.1.1',
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'service',
                ['services.yaml'],
                files_content="""
services:
  directory: services
common:
  ignore:
    - .github/CODEOWNERS
    - README.md
    - configs/declarations
  shared-dirs:
    - schemas/configs/declarations
    - schemas/postgresql
    - ../ml
    - ../schemas/schemas/mongo
force-common-changes:
    - services/*/local-files-dependencies.txt
    - services/*/build-dependencies-debian.txt
lang: cpp
arcadia-additional-projects:
    - ml
    - schemas/schemas
""".lstrip(),
            ),
        ],
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'driver-authorizer',
                ['services/driver-authorizer/service.yaml'],
                files_content='project-name: driver-authorizer',
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'driver-authorizer2',
                ['services/driver-authorizer2/service.yaml'],
                files_content="""
project-name: yandex-taxi-driver-authorizer2
teamcity:
  release:
    deploy-branch: driver-authorizer2-deploy-branch
docker-deploy:
    os-name: trusty
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'driver-authorizer3',
                ['services/driver-authorizer3/service.yaml'],
                files_content="""
project-name: yandex-taxi-driver-authorizer3
teamcity:
  release:
    deploy-branch: driver-authorizer3-deploy-branch
""".lstrip(),
            ),
        ],
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'userver-sample',
                ['services/uservice-template/service.yaml'],
                files_content="""
project-name: userver-sample
""".lstrip(),
            ),
        ],
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'pilorama',
                ['services/pilorama/service.yaml'],
                files_content="""
project-name: yandex-taxi-pilorama
teamcity:
  release:
    deploy-branch: my-deploy-branch
""".lstrip(),
            ),
        ],
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'some-library',
                ['libraries/some-library/library.yaml'],
                files_content="""
project-name: yandex-taxi-some-library
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'another-library',
                ['libraries/another-library/library.yaml'],
                files_content="""
project-name: yandex-taxi-another-library
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'unused-library',
                ['libraries/unused-library/library.yaml'],
                files_content="""
project-name: yandex-taxi-unused-library
""".lstrip(),
            ),
        ],
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'local-files-dependencies2',
                ['services/driver-authorizer2/local-files-dependencies.txt'],
                files_content="""
libraries/another-library
../schemas/schemas/mongo
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'local-files-dependencies3',
                ['services/driver-authorizer3/local-files-dependencies.txt'],
                files_content="""
libraries/some-library
some-deps/SomeDeps2.yaml
../ml/taxi_ml_cxx
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'local-files-dependencies',
                [
                    'services/pilorama/local-files-dependencies.txt',
                    'services/driver-authorizer/local-files-dependencies.txt',
                ],
                files_content='',
            ),
        ],
    )

    repo.git.checkout('-b', 'masters/driver-authorizer')
    repo.git.checkout('-b', 'masters/driver-authorizer2')
    repo.git.checkout('-b', 'masters/driver-authorizer3')
    repo.git.checkout('-b', 'masters/pilorama')
    repo.git.checkout('-b', 'origin/masters/driver-authorizer')
    repo.git.checkout('-b', 'origin/masters/driver-authorizer2')
    repo.git.checkout('-b', 'origin/masters/driver-authorizer3')
    repo.git.checkout('-b', 'origin/masters/pilorama')
    repo.git.checkout('develop')

    bare_dir = str(tmpdir.mkdir('origin'))
    repo.clone(bare_dir, bare=True)
    repo.git.remote('add', 'origin', bare_dir)

    return repo
