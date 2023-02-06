import pytest

from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

STAFF_DATA = {
    'another_login': {
        'login': 'another_login',
        'work_email': 'work_email@yandex-team.ru',
        'official': {'is_dismissed': False},
        'id': 0,
    },
    'first-login': {
        'login': 'first-login',
        'work_email': 'team-t@yandex-team.ru',
        'official': {'is_dismissed': False},
        'id': 1,
    },
    'dismissed-login': {
        'login': 'dismissed-login',
        'work_email': 'dismissed-accaunt@yandex-team.ru',
        'official': {'is_dismissed': True},
        'id': 2,
    },
}
LOGINS = list(STAFF_DATA)


@pytest.mark.parametrize(
    'owners,watchers,expected_response',
    [
        (
            [login for login in LOGINS if login != 'dismissed-login'],
            [login for login in LOGINS if login == 'dismissed-login'],
            {
                'message': (
                    'Dismissed watchers found: dismissed-login. '
                    'Exclude them and resave.'
                ),
                'code': 'DISMISSED_LOGINS',
            },
        ),
        (
            [login for login in LOGINS if login == 'dismissed-login'],
            [login for login in LOGINS if login != 'dismissed-login'],
            {
                'message': (
                    'Dismissed owners found: dismissed-login. '
                    'Exclude them and resave.'
                ),
                'code': 'DISMISSED_LOGINS',
            },
        ),
        ([LOGINS[0]], [LOGINS[1]], {'name': 'NAME'}),
    ],
)
@pytest.mark.pgsql(
    'taxi_exp',
    files=['owners_and_experiments.sql'],
    queries=[db.ADD_CONSUMER.format('test_consumer')],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'check_logins_is_dismissed': True,
                'enable_owners_is_dismissed': True,
                'enable_watchers_is_dismissed': True,
            },
        },
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
async def test(
        taxi_exp_client, patch_staff, owners, watchers, expected_response,
):
    patch_staff.fill(STAFF_DATA)

    body = experiment.generate(name='NAME', owners=owners, watchers=watchers)
    response = await helpers.verbose_init_exp_by_draft(taxi_exp_client, body)
    clean_response = {
        key: value
        for key, value in response.items()
        if key in {'name', 'code', 'message'}
    }
    assert clean_response == expected_response
