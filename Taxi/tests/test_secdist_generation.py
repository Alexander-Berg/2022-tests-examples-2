import pytest

from taxi_tests.utils import gensecdist


@pytest.mark.parametrize(
    (
        'source_dir, mongo_host_test, '
        'mongo_collections_settings_test, redis_sentinels_test, '
        'secdist_vars, result_secdist'
    ),
    [
        (
            # source_dir
            'test_source_dir',
            # mongo_host_test
            'mongodb://localhost:27217/',
            # mongo_collections_settings_test
            {
                'test_collections_alias': (
                    'test_collections',
                    'db_test_collections',
                    'test_collections_name',
                ),
            },
            # redis_sentinels_test
            [
                {'host': 'localhost', 'port': 26379},
            ],
            # secdist_vars
            {'test_var': 'test_var'},
            # result_secdist
            {
                'mongo_settings': {
                    'stq': {
                        'uri': 'mongodb://localhost:27217/dbstq',
                    },
                    'test_collections': {
                        'uri': 'mongodb://localhost:27217/db_test_collections',
                    },
                },
                'postgresql_settings': {
                    'composite_tables_count': 1,
                    'databases': {
                        'test': [
                            {
                                'master': (
                                    'host=/tmp/testsuite-postgresql '
                                    'user=testsuite dbname=reposition'
                                ),
                                'shard_number': 0,
                            },
                        ],
                    },
                },
                'redis_settings': {
                    'taxi-test': {
                        'command_control': {
                            'max_retries': 3,
                            'timeout_all_ms': 1000,
                            'timeout_single_ms': 1000,
                        },
                        'password': '',
                        'sentinels': [
                            {
                                'host': 'localhost',
                                'port': 26379,
                            },
                        ],
                        'shards': [
                            {
                                'name': 'test_master',
                            },
                        ],
                    },
                },
                'settings_override': {
                    'TEST_STORAGE_SETTINGS': {
                        'mds_bucket': '',
                        'mds_service_id': '',
                        'private_key_path': (
                            'test_source_dir/configs/tvm_private_key'
                        ),
                        'tvm_client_id': '',
                        'tvm_client_secret': '',
                        'tvm_login': '',
                    },
                    'TEST_LABELS': {
                        'login': 'web',
                        'password': 'web',
                        'token': 'test token',
                    },
                    'TEST_PARAM': {
                        'test': 'test',
                    },
                    'TEST_VARS': {
                        'test_var': 'test_var',
                    },
                },
            },
        ),
    ],
)
def test_create_secdist(source_dir,
                        mongo_host_test,
                        mongo_collections_settings_test,
                        redis_sentinels_test,
                        secdist_vars,
                        result_secdist,
                        get_file_path):
    secdist_dev = get_file_path('test_secdist_dev.json')
    secdist_template = get_file_path('test_secdist_template.json')
    generated_secdist = gensecdist.create_secdist(
        secdist_dev=secdist_dev,
        secdist_template=secdist_template,
        source_dir=source_dir,
        mongo_host=mongo_host_test,
        mongo_collections_settings=mongo_collections_settings_test,
        redis_sentinels=redis_sentinels_test,
        secdist_vars=secdist_vars,
    )
    assert generated_secdist == result_secdist
