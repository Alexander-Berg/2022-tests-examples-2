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
                [
                    'services/taxi-adjust/data',
                    'services/taxi-adjust/Dockerfile',
                    'services/taxi-corp/data',
                    'services/taxi-corp-data/data',
                    'services/taxi-fleet/data',
                    'taxi/data',
                    'services/taximeter/data',
                    'tests/data',
                    'tools/pep8',
                    'libraries/very-common-library/code',
                    'libraries/some-library/code',
                    'libraries/another-library/code',
                    'schemas/services/protocol/api.yaml',
                    'schemas/configs/declarations/'
                    + 'taxi-adjust/ADJUST_TIMEOUT.yaml',
                    'schemas/mongo/dborders.yaml',
                ],
                submodules=[
                    repository.SubmoduleCommits(
                        'submodules/codegen',
                        [repository.Commit('init repo', ['file1', 'file2'])],
                    ),
                ],
            ),
        ],
    )
    repository.commit_debian_dir(
        repo,
        'taxi-adjust',
        path='services/taxi-adjust',
        version='0.1.1',
        release_ticket='TAXIREL-1',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-corp',
        path='services/taxi-corp',
        version='0.1.2',
        release_ticket='TAXIREL-2',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-corp-data',
        path='services/taxi-corp-data',
        version='0.1.3',
        release_ticket='TAXIREL-3',
    )
    repository.commit_debian_dir(
        repo,
        'taximeter',
        path='services/taximeter',
        version='0.1.4',
        release_ticket='TAXIREL-4',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-fleet',
        path='services/taxi-fleet',
        version='0.1.5',
        release_ticket='TAXIREL-5',
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'service',
                ['services.yaml'],
                files_content=(
                    'services:\n'
                    '  directory: services\n'
                    'lang: python\n'
                    'force-common-changes:\n'
                    '    - services/*/local-files-dependencies.txt\n'
                    '    - services/*/debian-dev-dependencies.txt\n'
                    'common:\n'
                    '  followers: no\n'
                    '  shared-dirs:\n'
                    '    - schemas/services\n'
                    '    - schemas/configs/declarations\n'
                    '    - schemas/mongo\n'
                    '  extra-projects:\n'
                    '    - name: tests\n'
                    '      deps:\n'
                    '        - schemas/mongo\n'
                    '    - name: taxi plugins\n'
                ),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='taxi-fleet service yaml',
                files=['services/taxi-fleet/service.yaml'],
                files_content="""
teamcity:
  conductor-disabled: yes
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='taxi-adjust service yaml',
                files=['services/taxi-adjust/service.yaml'],
                files_content="""
deps-py3:
  docker-image: some-image
  path: some/path/to/
""".lstrip(),
            ),
            repository.Commit(
                comment='taxi-corp service yaml',
                files=['services/taxi-corp/service.yaml'],
                files_content='{}',
            ),
            repository.Commit(
                comment='taxi-corp-data service yaml',
                files=['services/taxi-corp-data/service.yaml'],
                files_content='{}',
            ),
            repository.Commit(
                comment='taximeter service yaml',
                files=['services/taximeter/service.yaml'],
                files_content='{}',
            ),
            repository.Commit(
                comment='example-service yaml',
                files=['services/example-service/service.yaml'],
                files_content="""
clients:
    services:
      - example-service
""".lstrip(),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='taxi-adjust local deps',
                files=['services/taxi-adjust/local-files-dependencies.txt'],
                files_content="""
libraries/very-common-library
libraries/some-library
libraries/another-library
schemas/configs/declarations/taxi-adjust/ADJUST_TIMEOUT.yaml
schemas/configs/declarations/taxi-adjust/ADJUST_RETRIES.yaml
schemas/mongo/adjust_events.yaml
""".lstrip(),
            ),
            repository.Commit(
                comment='taxi-corp local deps',
                files=['services/taxi-corp/local-files-dependencies.txt'],
                files_content='schemas/mongo',
            ),
            repository.Commit(
                comment='taxi-corp-data local deps',
                files=['services/taxi-corp-data/local-files-dependencies.txt'],
                files_content='',
            ),
            repository.Commit(
                comment='taxi-corp-data local deps',
                files=['services/taximeter/local-files-dependencies.txt'],
                files_content='',
            ),
            repository.Commit(
                comment='taxi-fleet local deps',
                files=['services/taxi-fleet/local-files-dependencies.txt'],
                files_content="""
libraries/another-library
schemas/services/protocol
""".lstrip(),
            ),
            repository.Commit(
                comment='very-common-library library.yaml',
                files=['libraries/very-common-library/library.yaml'],
                files_content='description: library',
            ),
            repository.Commit(
                comment='some-library library.yaml',
                files=['libraries/some-library/library.yaml'],
                files_content='description: library',
            ),
            repository.Commit(
                comment='another-library library.yaml',
                files=['libraries/another-library/library.yaml'],
                files_content='description: library',
            ),
            repository.Commit(
                comment='very-common-library local deps',
                files=[
                    'libraries/very-common-library/'
                    'local-files-dependencies.txt',
                ],
                files_content='',
            ),
            repository.Commit(
                comment='some-library local deps',
                files=['libraries/some-library/local-files-dependencies.txt'],
                files_content="""
libraries/very-common-library
schemas/services/protocol
schemas/mongo/geoareas.yaml
""".lstrip(),
            ),
            repository.Commit(
                comment='another-library local deps',
                files=[
                    'libraries/another-library/local-files-dependencies.txt',
                ],
                files_content='',
            ),
        ],
    )

    repo.git.checkout('-b', 'masters/taxi-adjust')
    repo.git.checkout('-b', 'masters/taxi-corp')
    repo.git.checkout('-b', 'masters/taxi-corp-data')
    repo.git.checkout('-b', 'masters/taxi-fleet')
    repo.git.checkout('-b', 'masters/taximeter')
    repo.git.checkout('-b', 'masters/empty-service')
    repo.git.checkout('-b', 'origin/masters/taxi-adjust')
    repo.git.checkout('-b', 'origin/masters/taxi-corp')
    repo.git.checkout('-b', 'origin/masters/taxi-corp-data')
    repo.git.checkout('-b', 'origin/masters/taxi-fleet')
    repo.git.checkout('-b', 'origin/masters/taximeter')
    repo.git.checkout('-b', 'origin/masters/empty-service')
    repo.git.checkout('develop')

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    return repo
