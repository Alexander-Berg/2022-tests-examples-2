import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        ' VALUES (1, \'eda_android\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (2, \'eda_android\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (2, \'eda_ios\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (2, \'magnit_android\')',
    ],
)
@pytest.mark.parametrize(
    'params, applications_config,' ' expected_applications',
    [
        pytest.param({'id': 0}, {}, [], id='empty applications list'),
        pytest.param(
            {'id': 1},
            {
                'eda_android': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            [
                {
                    'application': 'eda_android',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'go'},
                },
            ],
            id='one application',
        ),
        pytest.param(
            {'id': 2},
            {
                'eda_android': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'go'},
                    'user_identity_name': 'eater_id',
                },
                'eda_ios': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
                'magnit_android': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            [
                {
                    'application': 'eda_android',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                },
                {
                    'application': 'eda_ios',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                },
                {
                    'application': 'magnit_android',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                },
            ],
            id='multiple applications',
        ),
        pytest.param(
            {},
            {
                'eda_android': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
                'eda_ios': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
                'magnit_android': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
                'test': {
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            [
                {
                    'application': 'eda_android',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                },
                {
                    'application': 'magnit_android',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                },
                {
                    'application': 'test',
                    'type': 'test',
                    'settings': {'service': 'test', 'route': 'eda'},
                },
            ],
            id='without params',
        ),
    ],
)
async def test_applications_list(
        taxi_eats_notifications,
        taxi_config,
        params,
        applications_config,
        expected_applications,
):
    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
    )

    response = await taxi_eats_notifications.get(
        '/v1/admin/applications', params=params,
    )
    assert response.status_code == 200
    assert response.json()['applications'].sort(
        key=lambda x: x['application'],
    ) == expected_applications.sort(key=lambda x: x['application'])
