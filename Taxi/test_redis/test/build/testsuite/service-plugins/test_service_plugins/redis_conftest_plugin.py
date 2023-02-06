# pylint: skip-file
# flake8: noqa
import pytest


@pytest.fixture(scope='session')
def redis_settings(redis_sentinels):
    single_setting = {
        'password': '',
        'sentinels': redis_sentinels,
        'shards': [{
            'name': 'test_master0',
        }]
    }
    return {
        'db1': single_setting,
        'db2': single_setting,
        'db3': single_setting,
        'sdb1': single_setting,
        'sdb2': single_setting,
        'sdb3': single_setting,
    }


@pytest.fixture(scope='session')
def redis_settings_substitute(redis_settings):
    return {'redis_settings': lambda _: redis_settings}
