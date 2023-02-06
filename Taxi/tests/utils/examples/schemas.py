from tests.utils import repository

from . import yamls_content


def init(tmpdir):
    path = str(tmpdir.mkdir('schemas_repo'))
    repo = repository.init_repo(
        path,
        'aselutin',
        'aselutin@yandex-team.ru',
        [
            repository.Commit(
                'init repo',
                files=[
                    'schemas/configs/declarations/data',
                    'taxi-schemas/data',
                    'scripts/data',
                    'Makefile',
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
                ],
            ),
        ],
    )

    repository.apply_commits(
        repo,
        [
            repository.Commit(
                'add db_settings',
                ['db_settings.yaml'],
                files_content=yamls_content.DB_SETTINGS_YAML_CONTENT,
            ),
            repository.Commit(
                'adjust declarations',
                ['schemas/configs/declarations/adjust/ADJUST_CONFIG.yaml'],
                files_content=yamls_content.ADJUST_CONFIG_YAML_CONTENT,
            ),
            repository.Commit(
                'zendesk declarations',
                ['schemas/configs/declarations/ZENDESK_VERIFY_CERT.yaml'],
                files_content=yamls_content.ZENDESK_VERIFY_CERT_YAML_CONTENT,
            ),
            repository.Commit(
                'parks declarations',
                [
                    'schemas/configs/declarations/parks/'
                    'PARKS_ENABLE_PHOTO_VALIDITY_CHECK.yaml',
                ],
                files_content="""
default: true
description: driver-profiles/photo
""".lstrip(),
            ),
            repository.Commit(
                'driver-authorizer-external api.yaml',
                ['schemas/services/driver-authorizer-external/api/api.yaml'],
                files_content="""
swagger: '2.0'
info:
  description: Yandex Taxi Driver Authorizer Protocol
  title: Yandex Taxi Driver Authorizer Protocol
  version: '1.0'
""".lstrip(),
            ),
            repository.Commit(
                'social yaml',
                ['schemas/services/social/service.yaml'],
                files_content="""
host:
    production: api.social.yandex.ru
    testing: api.social - test.yandex.ru
    unstable: api.social - test.yandex.ru
middlewares:
tvm: social
""".lstrip(),
            ),
            repository.Commit(
                'driver-authorizer-external service yaml',
                ['schemas/services/driver-authorizer-external/service.yaml'],
                files_content="""
host:
  production: driver-authorizer.taxi.yandex.net
  testing: driver-authorizer.taxi.tst.yandex.net
  unstable: driver-authorizer.taxi.dev.yandex.net
""".lstrip(),
            ),
            repository.Commit(
                'driver-map service yaml',
                ['schemas/services/driver-map/api/api/service.yaml'],
                files_content="""
host:
  unstable: driver-map.taxi.dev.yandex.net
""".lstrip(),
            ),
            repository.Commit(
                'driver-map service yaml',
                ['schemas/services/driver-map/api/service.yaml'],
                files_content="""
host:
  unstable: driver-map.taxi.dev.yandex.net
""".lstrip(),
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
    repo.git.checkout('-b', 'gh-pages')
    repo.git.checkout('-b', 'ml_pins')
    repo.git.checkout('-b', 'master')

    origin_dir = str(tmpdir.mkdir('origin'))
    repo.clone(origin_dir, bare=True)
    repo.git.remote('add', 'origin', origin_dir)

    return repo
