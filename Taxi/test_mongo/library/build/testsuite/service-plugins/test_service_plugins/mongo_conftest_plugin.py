# pylint: skip-file
# flake8: noqa
import pytest

@pytest.fixture(scope='session')
def mongodb_collections():
    return [
        'cars',
        'drivers',
        'parks',
        'user_phones',
    ]


@pytest.fixture(scope='session')
def mongo_settings(mongo_connection_info):
    return {
        'taxi': {
            'uri': mongo_connection_info.get_uri(dbname='dbtaxi'),
        },
        'users': {
            'uri': mongo_connection_info.get_uri(dbname='dbusers'),
        },
    }


@pytest.fixture(scope='session')
def mongo_settings_substitute(mongo_settings):
    return {'mongo_settings': lambda _: mongo_settings}
