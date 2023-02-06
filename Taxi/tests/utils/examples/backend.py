from tests.utils import repository

from . import yamls_content


def init(tmpdir):
    path = str(tmpdir.mkdir('repo'))
    repo = repository.init_repo(
        path,
        'alberist',
        'alberist@yandex-team.ru',
        [
            repository.Commit(
                'init repo', ['taxi/data', 'doc/data', 'taxi-utils/data'],
            ),
        ],
    )
    repository.commit_debian_dir(
        repo, 'taxi-backend', version='3.0.224', release_ticket='TAXIREL-123',
    )
    repo.git.checkout('-b', 'master')
    repo.git.checkout('develop')

    origin_dir = str(tmpdir.mkdir('origin'))
    origin = repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    fork_dir = str(tmpdir.mkdir('fork'))
    fork = origin.clone(fork_dir)
    repository.set_current_user(fork, 'alberist', 'alberist@yandex-team.ru')
    fork.git.checkout('develop')

    repository.apply_commits(
        fork,
        [
            repository.Commit(
                'something',
                ['something.py'],
                files_content='content for some file\n',
            ),
            repository.Commit(
                'order_events',
                ['taxi/core/order-events.yaml'],
                files_content='content for some yaml file\n',
            ),
            repository.Commit(
                'config',
                ['taxi/configs/config.txt'],
                files_content='yet another content for config file\n',
            ),
            repository.Commit(
                'some schema',
                ['taxi/somefile.yaml'],
                files_content='schema info of some file\n',
            ),
            repository.Commit(
                'fill db_settings',
                ['taxi/core/db_settings.yaml'],
                files_content=yamls_content.DB_SETTINGS_YAML_CONTENT,
            ),
            repository.Commit(
                'adjust declarations',
                ['taxi/config/declarations/adjust/ADJUST_CONFIG.yaml'],
                files_content=yamls_content.ADJUST_CONFIG_YAML_CONTENT,
            ),
            repository.Commit(
                'zendesk declarations',
                ['taxi/config/declarations/zendesk/ZENDESK_VERIFY_CERT.yaml'],
                files_content=yamls_content.ZENDESK_VERIFY_CERT_YAML_CONTENT,
            ),
            repository.Commit(
                'some_service yaml',
                ['schemas/services/some_service/service.yaml'],
                files_content='some content',
            ),
            repository.Commit(
                'some_service yaml',
                ['schemas/services/debts/api/service.yaml'],
                files_content=yamls_content.DEBTS_API_YAML_CONTENT,
            ),
            repository.Commit(
                'some_service yaml',
                ['schemas/services/debts/client.yaml'],
                files_content=yamls_content.DEBTS_CLIENT_YAML_CONTENT,
            ),
        ],
    )

    fork.git.push('--set-upstream', 'origin', 'develop')
    fork.git.checkout('master')
    fork.git.merge('--no-ff', 'develop')
    fork.git.push('--set-upstream', 'origin', 'master')
    repo.git.pull('origin', 'develop')

    return repo
