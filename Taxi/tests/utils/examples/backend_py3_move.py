import os

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
                    'taxi-adjust/data',
                    'taxi-adjust/Dockerfile',
                    'taxi-corp/data',
                    'taxi-corp-data/data',
                    'taxi-fleet/data',
                    'taxi/data',
                    'taximeter/data',
                    'tests/data',
                    'tools/pep8',
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
        path='taxi-adjust',
        version='0.1.1',
        release_ticket='TAXIREL-1',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-corp',
        path='taxi-corp',
        version='0.1.2',
        release_ticket='TAXIREL-2',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-corp-data',
        path='taxi-corp-data',
        version='0.1.3',
        release_ticket='TAXIREL-3',
    )
    repository.commit_debian_dir(
        repo,
        'taximeter',
        path='taximeter',
        version='0.1.4',
        release_ticket='TAXIREL-4',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-fleet',
        path='taxi-fleet',
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
                    'lang: python\n'
                    'common:\n'
                    '  followers: no\n'
                    '  project-sources:\n'
                    '    - taxi\n'
                    '    - tests\n'
                    '    - plugins\n'
                ),
            ),
        ],
    )
    repository.apply_commits(
        repo,
        [
            repository.Commit(
                comment='taxi-fleet service yaml',
                files=['taxi-fleet/service.yaml'],
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
                files=['taxi-adjust/service.yaml'],
                files_content="""
    deps-py3:
      docker-image: some-image
      path: some/path/to/
        """.lstrip(),
            ),
        ],
    )

    repo.git.checkout('-b', 'masters/taxi-adjust')
    repo.git.checkout('-b', 'masters/taxi-corp')
    repo.git.checkout('-b', 'masters/taxi-corp-data')
    repo.git.checkout('-b', 'masters/taxi-fleet')
    repo.git.checkout('-b', 'masters/taximeter')
    repo.git.checkout('develop')

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)
    repository.apply_commits(
        repo,
        [
            repository.Commit('before-corp-only', ['taxi-corp/s1']),
            repository.Commit(
                'before-corp-adjust', ['taxi-corp/s2', 'taxi-adjust/s2'],
            ),
            repository.Commit('before-taxi', ['taxi/s3']),
            repository.Commit('before-fleet', ['taxi-fleet/s4']),
            repository.Commit('before-corp-taxi', ['taxi/s5', 'taxi-corp/s5']),
        ],
    )

    os.mkdir(os.path.join(path, 'services'))
    repo.git.mv('taxi-adjust', 'services/taxi-adjust')
    repo.git.mv('taxi-corp', 'services/taxi-corp')
    repo.git.mv('taxi-corp-data', 'services/taxi-corp-data')
    repo.git.mv('taxi-fleet', 'services/taxi-fleet')
    repo.git.mv('taximeter', 'services/taximeter')
    services_yaml = os.path.join(path, 'services.yaml')
    with open(services_yaml, 'a') as yaml_file:
        yaml_file.write('services:\n  directory: services\n')
    repo.git.add(services_yaml)
    repo.index.commit('move-services')

    repository.apply_commits(
        repo,
        [
            repository.Commit('after-corp-only', ['services/taxi-corp/s1']),
            repository.Commit(
                'after-corp-adjust',
                ['services/taxi-corp/s2', 'services/taxi-adjust/s2'],
            ),
            repository.Commit('after-taxi', ['taxi/s3']),
            repository.Commit('after-fleet', ['services/taxi-fleet/s4']),
            repository.Commit(
                'after-corp-taxi', ['taxi/s5', 'services/taxi-corp/s5'],
            ),
        ],
    )

    repo.git.push('origin', 'develop')
    return repo
