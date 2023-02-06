import pytest


@pytest.mark.parametrize(
    'request_params, expected_notifications, staff_data',
    [
        pytest.param(
            {'name': 'superapp', 'include_meta': 'true'},
            None,
            {
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
            },
            marks=pytest.mark.pgsql(
                'taxi_exp', files=['exists_experiment_with_lost_owners.sql'],
            ),
            id='owners_without_lost',
        ),
        pytest.param(
            {'name': 'superapp', 'include_meta': 'true'},
            [
                {
                    'message': (
                        'Dismissed owners found: another_login. '
                        'Exclude them and resave.'
                    ),
                    'notification_type': 'lost_logins_warning',
                },
            ],
            {
                'another_login': {
                    'login': 'another_login',
                    'work_email': 'work_email@yandex-team.ru',
                    'official': {'is_dismissed': True},
                    'id': 0,
                },
                'first-login': {
                    'login': 'first-login',
                    'work_email': 'team-t@yandex-team.ru',
                    'official': {'is_dismissed': False},
                    'id': 1,
                },
            },
            marks=pytest.mark.pgsql(
                'taxi_exp', files=['exists_experiment_with_lost_owners.sql'],
            ),
            id='with_lost_owners',
        ),
        pytest.param(
            {'name': 'superapp', 'include_meta': 'true'},
            None,
            {
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
            },
            marks=pytest.mark.pgsql(
                'taxi_exp', files=['exists_experiment_with_lost_watcher.sql'],
            ),
            id='watchers_without_lost',
        ),
        pytest.param(
            {'name': 'superapp', 'include_meta': 'true'},
            [
                {
                    'message': (
                        'Dismissed watchers found: another_login. '
                        'Exclude them and resave.'
                    ),
                    'notification_type': 'lost_logins_warning',
                },
            ],
            {
                'another_login': {
                    'login': 'another_login',
                    'work_email': 'work_email@yandex-team.ru',
                    'official': {'is_dismissed': True},
                    'id': 0,
                },
                'first-login': {
                    'login': 'first-login',
                    'work_email': 'team-t@yandex-team.ru',
                    'official': {'is_dismissed': False},
                    'id': 1,
                },
            },
            marks=pytest.mark.pgsql(
                'taxi_exp', files=['exists_experiment_with_lost_watcher.sql'],
            ),
            id='with_lost_watchers',
        ),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {
            'common': {
                'fill_notifications': True,
                'check_logins_is_dismissed': True,
                'enable_owners_is_dismissed': True,
                'enable_watchers_is_dismissed': True,
            },
        },
        'settings': {'common': {'in_set_max_elements_count': 100}},
    },
)
async def test(
        taxi_exp_client,
        patch_staff,
        request_params,
        expected_notifications,
        staff_data,
):
    patch_staff.fill(staff_data)

    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params=request_params,
    )
    assert response.status == 200, await response.text()
    get_body = await response.json()

    assert get_body.get('notifications') == expected_notifications
