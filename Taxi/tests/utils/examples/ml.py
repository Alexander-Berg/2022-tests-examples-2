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
                    'taxi-plotva-ml/data',
                    'taxi-plotva-ml-deps/data',
                    'tools/data',
                ],
                submodules=[
                    (
                        'submodules/backend-py3',
                        [
                            repository.Commit(
                                'init submodule', ['file1', 'file2'],
                            ),
                            repository.Commit('second commit', ['file3']),
                        ],
                    ),
                ],
            ),
        ],
    )
    repository.commit_debian_dir(
        repo,
        'taxi-plotva-ml',
        path='taxi-plotva-ml',
        version='0.1.1',
        release_ticket='TAXIREL-1',
    )
    repository.commit_debian_dir(
        repo,
        'taxi-plotva-ml-deps',
        path='taxi-plotva-ml-deps',
        version='0.1.1',
        release_ticket='TAXIREL-2',
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
                    '  commits-from-submodules: no\n'
                ),
            ),
        ],
    )

    repo.git.checkout('-b', 'masters/taxi-plotva-ml')
    repo.git.checkout('-b', 'masters/taxi-plotva-ml-deps')
    repo.git.checkout('develop')

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    return repo
