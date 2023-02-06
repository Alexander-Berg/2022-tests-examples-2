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
        'con1': {
            'uri': mongo_connection_info.get_uri(dbname='dbcon1'),
        },
        'con2': {
            'uri': mongo_connection_info.get_uri(dbname='dbcon2'),
        },
        'con3': {
            'uri': mongo_connection_info.get_uri(dbname='dbcon3'),
        },
        'geoareas': {
            'uri': mongo_connection_info.get_uri(dbname='dbgeoareas'),
        },
        'phone_history': {
            'uri': mongo_connection_info.get_uri(dbname='dbphone_history'),
        },
        'tariffs': {
            'uri': mongo_connection_info.get_uri(dbname='dbtariffs'),
        },
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
