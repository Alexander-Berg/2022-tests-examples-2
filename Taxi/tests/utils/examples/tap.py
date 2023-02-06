from tests.utils import repository


def init(tmpdir):
    path = str(tmpdir.mkdir('repo'))
    repo = repository.init_repo(
        path,
        'dteterin',
        'dteterin@yandex-team.ru',
        [
            repository.Commit(
                'init repo',
                files=['libyandex-taxi-graph2.rb', 'persqueue-wrapper.rb'],
            ),
        ],
    )

    repo.git.checkout('-b', 'master')

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'graph content',
                ['libyandex-taxi-graph2.rb'],
                files_content="""
VERSION = "1234567"
RESOURCES_ID = "999111"

Some code
blah-blah-blah
""".lstrip(),
            ),
            repository.Commit(
                'pw content',
                ['persqueue-wrapper.rb'],
                files_content="""
VERSION = "7654321"

Some code too
blah-blah-blah
""".lstrip(),
            ),
            repository.Commit(
                'graph content too',
                ['libyandex-taxi-graph.rb'],
                files_content="""
VERSION = "1234567"
RESOURCES_ID = "999;111;45"

Some code
blah-blah-blah
ololo
""".lstrip(),
            ),
        ],
    )

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    return repo
