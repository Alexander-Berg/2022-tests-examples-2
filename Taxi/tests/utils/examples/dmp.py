from tests.utils import repository


def init(tmpdir):
    path = str(tmpdir.mkdir('repo'))
    repo = repository.init_repo(
        path=path, username='alberist', email='alberist@yandex-team.ru',
    )
    repository.commit_debian_dir(
        repo, 'ad_etl', path='ad_etl', version='1.1.1',
    )

    repo.git.checkout('-b', 'masters/ad_etl')
    repo.git.checkout('develop')

    bare_dir = str(tmpdir.mkdir('origin'))
    repo.clone(bare_dir, bare=True)
    repo.git.remote('add', 'origin', bare_dir)

    return repo
