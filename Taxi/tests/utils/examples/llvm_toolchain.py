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
                files=['lib/data', 'clang/data', 'include/data', 'utils/data'],
            ),
        ],
    )
    repository.commit_debian_dir(
        repo,
        'taxi-toolchain',
        version='1:7.1.0~svn3-1~exp1~20190408084827.60-taxi1',
    )

    repo.git.checkout('-b', 'master')
    repo.git.checkout('develop')

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    return repo
