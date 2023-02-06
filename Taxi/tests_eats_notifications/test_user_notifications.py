import pytest


USER_NOTIFICATIONS_EXPERIMENT = pytest.mark.experiments3(
    name='eats_notifications_user_notifications',
    consumers=['eats-notifications/user-notifications'],
    is_config=True,
    default_value={
        'enabled': True,
        'config': {
            'deeplink': 'deeplink_1',
            'dark_theme_icon': 'icon_dark',
            'light_theme_icon': 'icon_light',
        },
    },
    clauses=[],
)


def build_selection_config(
        enabled_templates, is_enabled=True, max_count=100, max_age_days=365,
):
    return {
        'is_feature_enabled': is_enabled,
        'enabled_templates': enabled_templates,
        'maximal_notifications_count': max_count,
        'maximal_notification_age_days': max_age_days,
    }


def build_expected_block(title, body, notified_at):
    return {
        'title': title,
        'body': body,
        'deeplink': 'deeplink_1',
        'themed_icon': [
            {'icon': 'icon_dark', 'theme': 'dark'},
            {'icon': 'icon_light', 'theme': 'light'},
        ],
        'notified_at': notified_at,
    }


@pytest.mark.now('2020-01-02T00:00:00+00:00')
@pytest.mark.config(
    EATS_NOTIFICATIONS_USER_NOTIFICATIONS_SELECTION=build_selection_config(
        [{'project_key': 'project_key_1', 'template_key': 'template_key_1'}],
    ),
)
@USER_NOTIFICATIONS_EXPERIMENT
@pytest.mark.pgsql('eats_notifications', files=['init_test_db.sql'])
async def test_user_ids(taxi_eats_notifications):
    response = await taxi_eats_notifications.post(
        '/v1/user-notifications',
        headers={
            'X-Eats-User': 'user_id=eater_id_1,eater_uuid=eater_uuid_1',
            'X-Yandex-UID': 'yandex_uid_1',
        },
    )
    assert response.status_code == 200
    assert response.json() == [
        build_expected_block('title_3', 'body_3', '2020-01-01T00:00:03+00:00'),
        build_expected_block('title_2', 'body_2', '2020-01-01T00:00:02+00:00'),
        build_expected_block('title_1', 'body_1', '2020-01-01T00:00:01+00:00'),
    ]


@pytest.mark.now('2020-01-02T00:00:00+00:00')
@pytest.mark.config(
    EATS_NOTIFICATIONS_USER_NOTIFICATIONS_SELECTION=build_selection_config(
        [{'project_key': 'project_key_1', 'template_key': 'template_key_1'}],
        is_enabled=False,
    ),
)
@USER_NOTIFICATIONS_EXPERIMENT
@pytest.mark.pgsql('eats_notifications', files=['init_test_db.sql'])
async def test_disabled_by_config(taxi_eats_notifications):
    response = await taxi_eats_notifications.post(
        '/v1/user-notifications',
        headers={
            'X-Eats-User': 'user_id=eater_id_1,eater_uuid=eater_uuid_1',
            'X-Yandex-UID': 'yandex_uid_1',
        },
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.now('2020-01-02T00:00:00+00:00')
@pytest.mark.config(
    EATS_NOTIFICATIONS_USER_NOTIFICATIONS_SELECTION=build_selection_config(
        [
            {'project_key': 'project_key_1', 'template_key': 'template_key_1'},
            {'project_key': 'project_key_1', 'template_key': 'template_key_2'},
            {'project_key': 'project_key_2', 'template_key': 'template_key_1'},
        ],
    ),
)
@USER_NOTIFICATIONS_EXPERIMENT
@pytest.mark.pgsql('eats_notifications', files=['init_test_db.sql'])
async def test_filter_keys(taxi_eats_notifications):
    response = await taxi_eats_notifications.post(
        '/v1/user-notifications',
        headers={'X-Eats-User': 'user_id=eater_id_2'},
    )
    assert response.status_code == 200
    assert response.json() == [
        build_expected_block('title_7', 'body_7', '2020-01-01T00:00:07+00:00'),
        build_expected_block('title_5', 'body_5', '2020-01-01T00:00:05+00:00'),
        build_expected_block('title_4', 'body_4', '2020-01-01T00:00:04+00:00'),
    ]


@pytest.mark.now('2020-01-02T00:00:00+00:00')
@pytest.mark.config(
    EATS_NOTIFICATIONS_USER_NOTIFICATIONS_SELECTION=build_selection_config(
        [{'project_key': 'project_key_1', 'template_key': 'template_key_1'}],
    ),
)
@USER_NOTIFICATIONS_EXPERIMENT
@pytest.mark.pgsql('eats_notifications', files=['init_test_db.sql'])
async def test_filter_status(taxi_eats_notifications):
    response = await taxi_eats_notifications.post(
        '/v1/user-notifications',
        headers={'X-Eats-User': 'user_id=eater_id_3'},
    )
    assert response.status_code == 200
    assert response.json() == [
        build_expected_block(
            'title_10', 'body_10', '2020-01-01T00:00:10+00:00',
        ),
    ]


def build_mark_selection_config(max_count=100, max_age_days=365):
    return pytest.mark.config(
        EATS_NOTIFICATIONS_USER_NOTIFICATIONS_SELECTION=build_selection_config(
            [
                {
                    'project_key': 'project_key_1',
                    'template_key': 'template_key_1',
                },
            ],
            max_count=max_count,
            max_age_days=max_age_days,
        ),
    )


@pytest.mark.now('2020-01-02T00:00:13+00:00')
@USER_NOTIFICATIONS_EXPERIMENT
@pytest.mark.pgsql('eats_notifications', files=['init_test_db.sql'])
@pytest.mark.parametrize(
    ['expected_response'],
    [
        pytest.param(
            [
                build_expected_block(
                    'title_14', 'body_14', '2020-01-01T00:00:14+00:00',
                ),
                build_expected_block(
                    'title_13', 'body_13', '2020-01-01T00:00:13+00:00',
                ),
                build_expected_block(
                    'title_12', 'body_12', '2020-01-01T00:00:12+00:00',
                ),
            ],
            marks=[build_mark_selection_config()],
            id='all_notifications',
        ),
        pytest.param(
            [
                build_expected_block(
                    'title_14', 'body_14', '2020-01-01T00:00:14+00:00',
                ),
                build_expected_block(
                    'title_13', 'body_13', '2020-01-01T00:00:13+00:00',
                ),
            ],
            marks=[build_mark_selection_config(max_age_days=1)],
            id='limit_by_age',
        ),
        pytest.param(
            [
                build_expected_block(
                    'title_14', 'body_14', '2020-01-01T00:00:14+00:00',
                ),
            ],
            marks=[build_mark_selection_config(max_count=1)],
            id='limit_by_count',
        ),
    ],
)
async def test_limits(taxi_eats_notifications, expected_response):
    response = await taxi_eats_notifications.post(
        '/v1/user-notifications',
        headers={'X-Eats-User': 'user_id=eater_id_4'},
    )
    assert response.status_code == 200
    assert response.json() == expected_response
