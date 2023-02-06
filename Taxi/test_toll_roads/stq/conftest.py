import pytest

from test_toll_roads import db_helper


@pytest.fixture
def db(stq3_context):
    return db_helper.DbHelper(stq3_context)


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):  # pylint: disable=W0621
    simple_secdist['settings_override'].update(
        {
            'SKOLKOVO_LOGIN': 'yandex_taxi_login',
            'SKOLKOVO_PASSWORD': 'yaxndex_taxi_password',
        },
    )
    return simple_secdist
