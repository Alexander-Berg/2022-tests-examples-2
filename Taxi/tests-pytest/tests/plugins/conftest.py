import copy
import os
import pathlib
import shutil
from typing import Set

import pytest
from taxi_linters import taxi_yamlfmt
import yatest.common  # pylint: disable=import-error

from codegen.plugin_manager import v3 as plugin_manager
from util.codegen_utils import core_plugins

pytest_plugins = [
    'codegen.tests.plugins.ref_comparer',
    'codegen.tests.plugins.common',
]


COMMON_REPOSITORY = {
    '../../groups/taxi-automatization': '',
    '../../groups/taxi-common': '',
    'services/test-service/debian/changelog': (
        'package-name (0.0.12testing37243) unstable; urgency=low'
    ),
    'services/test-service/docs/yaml/api/api.yaml': {
        'swagger': '2.0',
        'info': {
            'description': 'Test Service Description',
            'title': 'Test Service Title',
            'version': 'v1.0',
        },
        'paths': {
            '/v1/run': {
                'post': {
                    'parameters': [
                        {
                            'in': 'body',
                            'name': 'body',
                            'required': True,
                            'schema': {'$ref': '#/definitions/Request'},
                        },
                    ],
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'schema': {
                                'type': 'object',
                                'required': ['discounts'],
                                'properties': {
                                    'discounts': {
                                        'type': 'array',
                                        'items': {
                                            '$ref': '#/definitions/Response',
                                        },
                                    },
                                },
                                'additionalProperties': False,
                            },
                        },
                        '400': {
                            'description': 'Bad Request',
                            'schema': {'$ref': '#/definitions/BadRequest'},
                        },
                    },
                },
            },
        },
        'definitions': {
            'Request': {
                'type': 'object',
                'required': ['id'],
                'properties': {
                    'id': {'type': 'number'},
                    'data': {'type': 'string'},
                },
                'additionalProperties': False,
            },
            'Response': {
                'type': 'array',
                'x-taxi-cpp-type': 'std::unordered_set',
                'items': {'type': 'string'},
            },
            'BadRequest': {
                'type': 'object',
                'properties': {'message': {'type': 'string'}},
                'additionalProperties': False,
            },
        },
    },
    'services/test-service/docs/yaml/api/openapi.yaml': {
        'openapi': '3.0.0',
        'info': {
            'description': 'Test Service Description',
            'title': 'Test Service Title',
            'version': 'v1.0',
        },
        'paths': {
            '/openapi/v1/run': {
                'post': {
                    'parameters': [],
                    'requestBody': {
                        'required': True,
                        'content': {
                            'application/json': {
                                'schema': {
                                    '$ref': (
                                        '#/components'
                                        '/schemas'
                                        '/OpenapiRequest'
                                    ),
                                },
                            },
                        },
                    },
                    'responses': {
                        '200': {
                            'description': 'OK',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'required': ['discounts'],
                                        'properties': {
                                            'discounts': {
                                                'type': 'array',
                                                'items': {
                                                    '$ref': (
                                                        '#/components'
                                                        '/schemas'
                                                        '/OpenapiResponse'
                                                    ),
                                                },
                                            },
                                        },
                                        'additionalProperties': False,
                                    },
                                },
                            },
                        },
                        '400': {
                            'description': 'Bad Request',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        '$ref': (
                                            '#/components'
                                            '/schemas'
                                            '/OpenapiBadRequest'
                                        ),
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        'components': {
            'schemas': {
                'OpenapiRequest': {
                    'type': 'object',
                    'required': ['id'],
                    'properties': {
                        'id': {'type': 'number'},
                        'data': {'type': 'string'},
                    },
                    'additionalProperties': False,
                },
                'OpenapiResponse': {
                    'type': 'array',
                    'x-taxi-cpp-type': 'std::unordered_set',
                    'items': {'type': 'string'},
                },
                'OpenapiBadRequest': {
                    'type': 'object',
                    'properties': {'message': {'type': 'string'}},
                    'additionalProperties': False,
                },
            },
        },
    },
    'userver/core/library.yaml': {
        'maintainers': ['user', 'ver'],
        'description': 'UserVer',
        'project-name': 'userver-core',
        'project-alt-names': ['yandex-userver-core'],
    },
    'userver/grpc/library.yaml': {
        'maintainers': ['user', 'ver'],
        'description': 'UserVer',
        'project-name': 'userver-grpc',
        'project-alt-names': ['yandex-userver-grpc'],
    },
    'libraries/codegen/library.yaml': {
        'maintainers': ['not me'],
        'description': 'C',
        'project-name': 'yandex-taxi-library-codegen',
    },
    'libraries/codegen/src/lib.cpp': 'c++ code',
    'libraries/codegen/src/dir/some.cpp': 'c++ code',
    'libraries/codegen/src/lib_test.cpp': 'c++ code',
    'libraries/codegen-clients/library.yaml': {
        'maintainers': ['not me'],
        'description': 'CC',
        'project-name': 'yandex-taxi-library-codegen-clients',
    },
    'libraries/passenger-authorizer-backend/library.yaml': {
        'maintainers': ['not me'],
        'description': 'CC',
        'project-name': 'yandex-taxi-library-passenger-authorizer-backend',
    },
    'libraries/user-agent-parser/library.yaml': {
        'maintainers': ['not me'],
        'description': 'CC',
        'project-name': 'yandex-taxi-library-user-agent-parser',
    },
    'libraries/driver-authproxy-backend/library.yaml': {
        'maintainers': ['not me'],
        'description': 'CC',
        'project-name': 'yandex-taxi-library-driver-authproxy-backend',
    },
    'libraries/client-statistics/library.yaml': {
        'maintainers': ['not me'],
        'description': 'CC',
        'project-name': 'yandex-taxi-library-client-statistics',
    },
    'libraries/basic-http-client/library.yaml': {
        'maintainers': ['some'],
        'description': 'BHC',
        'project-name': 'yandex-taxi-library-basic-http-client',
    },
    'libraries/yt-replica-reader/library.yaml': {
        'maintainers': ['some'],
        'description': 'data',
        'project-name': 'yandex-taxi-library-yt-replica-reader',
    },
    'libraries/db-adapter/library.yaml': {
        'maintainers': ['some'],
        'description': 'data',
        'project-name': 'yandex-taxi-library-db-adapter',
    },
    'external-deps/boost.yaml': {
        'common-name': 'Boost',
        'partials': [
            {
                'name': 'regex',
                'helper-prefix': False,
                'includes': {'find': [{'names': ['boost/regex/config.hpp']}]},
                'libraries': {'find': [{'names': ['boost_regex']}]},
                'debian-names': ['libboost-regex-dev'],
                'formula-name': 'boost',
            },
        ],
    },
    'external-deps/Flatbuffers.yaml': {
        'name': 'Flatbuffers',
        'package-name': 'libflatbuffers-dev',
        'debian-names': ['libflatbuffers-dev'],
        'formula-name': 'libflatbuffers-dev',
        'version': '5615811',
        'libraries': {'find': [{'names': ['libflatbuffers-dev']}]},
        'includes': {'find': [{'names': ['flatbuffers/flatbuffers.h']}]},
    },
    'external-deps/Protobuf.yaml': {
        'name': 'Protobuf',
        'package-name': 'libyandex-taxi-protobuf-dev',
        'debian-names': ['libyandex-taxi-protobuf-dev'],
        'formula-name': 'libyandex-taxi-protobuf-dev',
        'version': '5610011',
        'fail-message': (
            'Could not find `Protobuf` package.\nDebian: sudo'
            ' apt update && sudo apt install libyandex-taxi-protobuf-dev\n'
            'MacOS: brew install protobuf'
        ),
        'libraries': {'find': [{'names': ['libyandex-taxi-protobuf-dev']}]},
        'includes': {'find': [{'names': ['google/protobuf/port_def.inc']}]},
    },
    'userver/mongo/library.yaml': {
        'maintainers': ['mon-go'],
        'description': 'MonGo',
        'project-name': 'userver-mongo',
        'project-alt-names': ['yandex-userver-mongo'],
    },
    'libraries/mongo-collections/library.yaml': {
        'maintainers': ['mon-go-co'],
        'description': 'MonGoCo',
        'project-name': 'yandex-taxi-library-mongo-collections',
    },
    'libraries/yt-logger/library.yaml': {
        'maintainers': ['vYtja'],
        'description': 'YT logger',
        'project-name': 'yandex-taxi-library-yt-logger',
    },
    'libraries/solomon-stats/library.yaml': {
        'maintainers': ['common'],
        'description': 'Solomon adapters',
        'project-name': 'yandex-taxi-library-solomon-stats',
    },
    'libraries/stq/library.yaml': {
        'maintainers': ['vYtja'],
        'description': 'STQ client',
        'project-name': 'yandex-taxi-library-stq',
    },
    'libraries/stq-dispatcher/library.yaml': {
        'maintainers': ['vYtja'],
        'description': 'STQ dispatcher',
        'project-name': 'yandex-taxi-library-stq-dispatcher',
    },
    'libraries/client-stq-agent/library.yaml': {
        'maintainers': ['vYtja'],
        'description': 'STQ client',
        'project-name': 'yandex-taxi-library-client-stq-agent',
    },
    'libraries/json-converters/library.yaml': {
        'maintainers': ['that man'],
        'description': 'json-converter lib',
        'project-name': 'yandex-taxi-library-json-converters',
    },
    'libraries/tvm2/library.yaml': {
        'maintainers': ['twirl'],
        'description': 'TVM',
        'project-name': 'yandex-taxi-library-tvm2',
    },
    'libraries/tvm2-http-client/library.yaml': {
        'maintainers': ['twirl'],
        'description': 'TVM client',
        'project-name': 'yandex-taxi-library-tvm2-http-client',
    },
    'libraries/api-over-db/library.yaml': {
        'maintainers': ['victorshch'],
        'description': 'API over data library',
        'project-name': 'yandex-taxi-library-api-over-db',
    },
    'libraries/segmented-dict/library.yaml': {
        'maintainers': ['lukashevich84'],
        'description': 'library with coro safe segmented dict',
        'project-name': 'yandex-taxi-library-segmented-dict',
    },
    'libraries/set-rules-matcher/library.yaml': {
        'maintainers': ['alex-tsarkov'],
        'description': 'Library for matching logic rules.',
        'project-name': 'yandex-taxi-library-set-rules-matcher',
    },
    'libraries/market-spok-infra-monitoring/library.yaml': {
        'maintainers': ['d-korotin'],
        'description': 'Market monitoring handlers',
        'project-name': 'yandex-taxi-library-set-rules-matcher',
    },
    'libraries/market-spok-infra-deploy/library.yaml': {
        'maintainers': ['d-korotin'],
        'description': 'Market deploy settings',
        'project-name': 'yandex-taxi-library-set-rules-matcher',
    },
    'userver/redis/library.yaml': {
        'maintainers': ['common'],
        'description': 'redis',
        'project-name': 'userver-redis',
        'project-alt-names': ['yandex-userver-redis'],
    },
    'userver/postgresql/library.yaml': {
        'maintainers': ['common'],
        'description': 'postgres',
        'project-name': 'userver-postgresql',
        'project-alt-names': ['yandex-userver-postgresql'],
    },
}

DEFAULT_REPOSITORY = {
    'services/test-service/service.yaml': {
        'wiki': 'no wiki',
        'short-name': 'test-service',
        'project-name': 'yandex-taxi-test-service',
        'maintainers': ['me'],
        'uservice_unit': {
            'hostname': {
                'production': ['me.yandex.ru', 'second.yandex.ru'],
                'testing': ['me.tst.yandex.ru'],
            },
            'description': 'my service',
        },
        'debian': {
            'source_package_name': 'package-name',
            'maintainer_name': 'my name',
            'maintainer_login': 'my login',
        },
    },
    'services/test-service/configs/config_vars.user.default.yaml': {},
    'services/test-service/configs/config_vars.user.production.yaml': {},
    'services/test-service/configs/config_vars.user.testing.yaml': {},
    'services/test-service/configs/config_vars.user.stress.yaml': {},
    'services/test-service/configs/config_vars.user.unstable.yaml': {},
    'services/test-service/configs/config_vars.user.testsuite.yaml': {},
    'services/test-service/configs/config.user.yaml': {},
}

MULTI_UNIT_REPOSITORY = {
    'services/test-service/service.yaml': {
        'wiki': 'no wiki',
        'short-name': 'test-service',
        'project-name': 'yandex-taxi-test-service',
        'maintainers': ['me'],
        'units': [
            {
                'uservice_unit': {
                    'name': 'first-unit',
                    'hostname': {
                        'production': ['me.yandex.ru'],
                        'testing': ['me.tst.yandex.ru'],
                    },
                    'description': 'my first service',
                },
                'debian': {'binary_package_name': 'yandex-taxi-first-unit'},
            },
            {
                'uservice_unit': {
                    'name': 'second-unit',
                    'hostname': {
                        'production': ['me.yandex.ru'],
                        'testing': ['me.tst.yandex.ru'],
                    },
                    'description': 'my second service',
                },
                'debian': {'binary_package_name': 'yandex-taxi-second-unit'},
            },
        ],
        'debian': {
            'source_package_name': 'package-name',
            'maintainer_name': 'my name',
            'maintainer_login': 'my login',
        },
    },
    'services/test-service/configs/first-unit/'
    'config_vars.user.default.yaml': {},
    'services/test-service/configs/first-unit/'
    'config_vars.user.production.yaml': {},
    'services/test-service/configs/first-unit/'
    'config_vars.user.testing.yaml': {},
    'services/test-service/configs/first-unit/'
    'config_vars.user.stress.yaml': {},
    'services/test-service/configs/first-unit/'
    'config_vars.user.unstable.yaml': {},
    'services/test-service/configs/first-unit/'
    'config_vars.user.testsuite.yaml': {},
    'services/test-service/configs/first-unit/config.user.yaml': {},
    'services/test-service/configs/second-unit/'
    'config_vars.user.default.yaml': {},
    'services/test-service/configs/second-unit/'
    'config_vars.user.production.yaml': {},
    'services/test-service/configs/second-unit/'
    'config_vars.user.testing.yaml': {},
    'services/test-service/configs/second-unit/'
    'config_vars.user.stress.yaml': {},
    'services/test-service/configs/second-unit/'
    'config_vars.user.unstable.yaml': {},
    'services/test-service/configs/second-unit/'
    'config_vars.user.testsuite.yaml': {},
    'services/test-service/configs/second-unit/config.user.yaml': {},
    'services/test-service/testsuite/tests_test_service/'
    'first_unit/test_ping.py': {},
    'services/test-service/testsuite/tests_test_service/'
    'second_unit/test_ping.py': {},
}


@pytest.fixture
def default_repository():
    return _create_repository(COMMON_REPOSITORY, DEFAULT_REPOSITORY)


@pytest.fixture
def multi_unit_repository():
    return _create_repository(COMMON_REPOSITORY, MULTI_UNIT_REPOSITORY)


@pytest.fixture(scope='session')
def default_base(tmpdir_factory):
    repository = _create_repository(COMMON_REPOSITORY, DEFAULT_REPOSITORY)

    codegen_path = tmpdir_factory.mktemp('default_base')

    return generate_repository(repository, codegen_path)


@pytest.fixture(scope='session')
def multi_unit_base(tmpdir_factory):
    repository = _create_repository(COMMON_REPOSITORY, MULTI_UNIT_REPOSITORY)

    codegen_path = tmpdir_factory.mktemp('multi_unit_base')

    return generate_repository(repository, codegen_path)


def _create_repository(base, *updates):
    result = copy.deepcopy(base)
    for update in updates:
        result.update(copy.deepcopy(update))
    return result


@pytest.fixture(scope='session', name='uservices_path')
def _uservices_path() -> str:
    return yatest.common.source_path('taxi/uservices')


@pytest.fixture(name='codegen_root_path')
def _codegen_root_path(tmpdir):
    return tmpdir.mkdir('repo')


@pytest.fixture(name='codegen_uservices_path')
def _codegen_uservices_path(codegen_root_path):
    path = codegen_root_path / 'taxi' / 'uservices'
    os.makedirs(path)
    return path


@pytest.fixture(name='repo_comparator')
def _repo_comparator(dir_comparator):
    def compare(repository, generated_dir, *test_dirs, deleted=()):
        ignored = list(repository.keys())
        for deleted_file in deleted:
            assert not os.path.exists(
                os.path.join(generated_dir, deleted_file),
            )
            ignored.append(deleted_file)

        if yatest.common.get_param('create_generated_files'):
            os.environ['CREATE_GENERATED_FILES'] = 'yes'

        dir_comparator(
            generated_dir,
            *test_dirs,
            ignore=[
                'build/services/test-service/testsuite/'
                'yandex-taxi-test-service.service',
                'build/services/test-service/testsuite/configs/service.yaml',
                'build/services/test-service/units/'
                'first-unit/testsuite/configs/service.yaml',
                'build/services/test-service/units/'
                'second-unit/testsuite/configs/service.yaml',
                'build/services/test-service/units/test-service/'
                'testsuite/configs/service.yaml',
                'build/testsuite/ctest-runtests',
                'build/testsuite/runtests',
                'build/testsuite/taxi-env',
                *ignored,
            ],
        )

    return compare


@pytest.fixture(name='generate_services_and_libraries')
def generate_services_and_libraries(repo_comparator, codegen_root_path):
    def runner(repository, *test_dirs, deleted=(), sort_keys=True):
        uservices_path = generate_repository(
            repository, codegen_root_path, sort_keys=sort_keys,
        )

        repo_comparator(
            repository, uservices_path, *test_dirs, deleted=deleted,
        )

    return runner


def generate_repository(
        repository: dict, target_path: str, sort_keys=True,
) -> str:
    prepare_uservices(target_path)

    codegen_uservices_path = os.path.join(target_path, 'taxi', 'uservices')

    for path, content in repository.items():
        full_path = os.path.join(codegen_uservices_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if isinstance(content, str):
            with open(full_path, 'w', encoding='utf-8') as fout:
                fout.write(content)
        elif isinstance(content, bytes):
            with open(full_path, 'wb') as fout_binary:
                fout_binary.write(content)
        else:
            if isinstance(sort_keys, bool):
                file_sort_keys = sort_keys
            elif isinstance(sort_keys, dict):
                file_sort_keys = sort_keys.get(path, True)
            else:
                file_sort_keys = True
            write_yaml(full_path, content, sort_keys=file_sort_keys)

    repo = core_plugins.Repository(
        pathlib.Path(codegen_uservices_path),
        core_plugins.CodegenOptions.from_args(
            [
                '--generate-debian',
                '--log-level=DEBUG',
                '--build-dir',
                os.path.join(codegen_uservices_path, 'build'),
            ],
        ),
    )

    with pytest.MonkeyPatch.context() as monkeypatch:  # pylint: disable=E1101
        monkeypatch.chdir(target_path)
        monkeypatch.setenv('IS_TEAMCITY', '')
        monkeypatch.setenv('CODEGEN_CACHE_DISABLED', '1')
        monkeypatch.setenv('CLANG_FORMAT_DISABLED', '')

        manager = plugin_manager.PluginManager(repo, progress=False)
        manager.configure()
        manager.generate()

    for path in repo.generated_sources_dir.rglob('*'):
        if not path.is_file():
            continue
        actual_path = repo.arcadia_root_dir / path.relative_to(
            repo.generated_sources_dir,
        )
        if repo.arcadia_root_dir not in actual_path.resolve().parents:
            # Trying to write data outside of working directory
            continue
        actual_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, actual_path)
    shutil.rmtree(repo.generated_sources_dir)

    return codegen_uservices_path


def prepare_uservices(target_path: str) -> None:
    uservices_path = yatest.common.source_path('taxi/uservices')
    schemas_path = yatest.common.source_path('taxi/schemas')

    target_uservices_path = os.path.join(target_path, 'taxi', 'uservices')
    target_schemas_path = os.path.join(target_path, 'taxi', 'schemas')

    symlink_dir_content(uservices_path, target_uservices_path, {'userver'})
    # symlink userver plugins
    os.makedirs(os.path.join(target_uservices_path, 'userver'), exist_ok=True)
    os.symlink(
        os.path.join(uservices_path, 'userver', 'plugins'),
        os.path.join(target_uservices_path, 'userver', 'plugins'),
    )

    # symlink mongo schemas
    os.makedirs(os.path.join(target_schemas_path, 'schemas'), exist_ok=True)
    os.symlink(
        os.path.join(schemas_path, 'schemas', 'mongo'),
        os.path.join(target_schemas_path, 'schemas', 'mongo'),
    )

    os.makedirs(
        os.path.join(target_schemas_path, 'schemas', 'proto'), exist_ok=True,
    )


def symlink_dir_content(
        path_from: str, path_to: str, exclude_names: Set[str],
) -> None:
    os.makedirs(os.path.join(path_to), exist_ok=True)
    for fname in os.listdir(path_from):
        if not fname.startswith('.') and fname not in exclude_names:
            os.symlink(
                os.path.join(path_from, fname), os.path.join(path_to, fname),
            )


def write_yaml(path: str, yaml_contents: str, sort_keys) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fle:
        taxi_yamlfmt.dump(yaml_contents, fle, sort_keys=sort_keys)
