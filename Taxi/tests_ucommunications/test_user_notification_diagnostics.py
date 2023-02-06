import pytest


NOW = '2020-01-01T02:03:00+00:00'
DEFAULT_DATE = '1970-01-01T00:00:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [],
    },
)
async def test_empty_conditions(taxi_ucommunications, mock_xiva, mockserver):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': 'user1'}

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': 'user1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_notifications_available': 'yes',
        'features': {
            'is_delivery_reports_supported': {
                'updated_at': NOW,
                'value': 'unknown',
            },
            'is_notifications_enabled_by_system': {
                'updated_at': NOW,
                'value': 'yes',
            },
            'is_subscribed': {'updated_at': NOW, 'value': False},
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_APPLICATIONS_SUPPORT_ACK_MIN_VERSION={
        'android': [1, 2, 3],
    },
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [
            {
                'feature': 'is_notifications_enabled_by_system',
                'expected_values': ['yes'],
                'max_age': 3600,
            },
            {
                'feature': 'is_delivery_reports_supported',
                'expected_values': ['yes'],
                'max_age': 3600,
            },
            {
                'feature': 'is_subscribed',
                'expected_values': [True],
                'max_age': 3600,
            },
        ],
    },
)
async def test_all_features_ok(taxi_ucommunications, mockserver, mongodb):
    @mockserver.json_handler('/xiva/v2/list')
    def _xiva_list(request):
        return [{'id': 'user1', 'platform': 'fcm', 'session': 'session'}]

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {
            'id': 'user1',
            'application': 'android',
            'application_version': '1.2.3',
        }

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': 'user1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'is_notifications_available': 'yes',
        'features': {
            'is_delivery_reports_supported': {
                'updated_at': NOW,
                'value': 'yes',
            },
            'is_notifications_enabled_by_system': {
                'updated_at': NOW,
                'value': 'yes',
            },
            'is_subscribed': {'updated_at': NOW, 'value': True},
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [
            {
                'feature': 'is_notifications_enabled_by_system',
                'expected_values': ['yes'],
            },
        ],
    },
)
@pytest.mark.parametrize(
    'user_id,feature_result,common_result',
    [('user1', 'yes', 'yes'), ('user3', 'no', 'no')],
)
async def test_features_declined_by_value(
        taxi_ucommunications,
        mockserver,
        mock_xiva,
        user_id,
        feature_result,
        common_result,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': user_id}

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': user_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['is_notifications_available'] == common_result
    assert (
        body['features']['is_notifications_enabled_by_system']['value']
        == feature_result
    )


@pytest.mark.now(NOW)
@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [
            {
                'feature': 'is_notifications_enabled_by_system',
                'expected_values': ['yes', 'no', 'unknown'],
                'max_age': 1,
            },
        ],
    },
)
@pytest.mark.parametrize(
    'user_id,feature_result,common_result',
    [('user1', 'yes', 'yes'), ('user3', 'no', 'no')],
)
async def test_features_declined_by_age(
        taxi_ucommunications,
        mockserver,
        mock_xiva,
        user_id,
        feature_result,
        common_result,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': user_id}

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': user_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['is_notifications_available'] == common_result
    assert (
        body['features']['is_notifications_enabled_by_system']['value']
        == feature_result
    )


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [],
    },
)
@pytest.mark.parametrize(
    'user_id,expected_result', [('user1', 'yes'), ('user2', 'no')],
)
async def test_features_is_notifications_enabled_by_system(
        taxi_ucommunications, mockserver, mock_xiva, user_id, expected_result,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': user_id}

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': user_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert (
        body['features']['is_notifications_enabled_by_system']['value']
        == expected_result
    )


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [],
    },
)
@pytest.mark.parametrize(
    'user_id,has_subscription', [('user1', True), ('user2', False)],
)
async def test_features_is_subscribed(
        taxi_ucommunications, mockserver, user_id, has_subscription,
):
    @mockserver.json_handler('/xiva/v2/list')
    def _list(request):
        return [{'id': user_id}] if has_subscription else []

    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {'id': user_id}

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': user_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body['features']['is_subscribed']['value'] == has_subscription


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_APPLICATIONS_SUPPORT_ACK_MIN_VERSION={
        'android': [1, 2, 3],
        'iphone': [3, 2, 1],
    },
    COMMUNICATIONS_USER_NOTIFICATION_DIAGNOSTICS={
        'notifications_allowed_conditions': [],
    },
)
@pytest.mark.parametrize(
    'application,version,expected_result',
    [
        ('android', '1.2.3', 'yes'),
        ('iphone', '1.1.1', 'no'),
        ('lavka', '1.1.1', 'unknown'),
        (None, None, 'unknown'),
    ],
)
async def test_features_is_delivery_reports_supported(
        taxi_ucommunications,
        mockserver,
        mock_xiva,
        application,
        version,
        expected_result,
):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        return {
            'id': 'user',
            'application': application,
            'application_version': version,
        }

    response = await taxi_ucommunications.post(
        'user/notification/diagnostics', json={'user_id': 'user'},
    )
    assert response.status_code == 200
    body = response.json()
    assert (
        body['features']['is_delivery_reports_supported']['value']
        == expected_result
    )
