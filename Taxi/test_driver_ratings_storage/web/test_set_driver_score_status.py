import pytest

HEADERS = {'X-Yandex-Login': 'login', 'X-Yandex-UID': '1234567890'}
CHECK_QUERY = """SELECT is_ignored
FROM driver_ratings_storage.driver_score_status_history
WHERE order_id='aabbccdd1234' AND login='login'
ORDER BY event_at ASC"""
BODY_403 = {
    'code': 'LIMIT_EXCEEDED',
    'message': 'You\'ve reached the limit of allowed operations number',
}


async def test_ok(taxi_driver_ratings_storage_web, mockserver, pgsql):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return {
            'fields': {'_id': 'aabbccdd1234'},
            'order_id': 'aabbccdd1234',
            'replica': 'archive',
            'version': '12345',
        }

    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        json={'is_ignored': True, 'description': 'Some comment'},
        headers=HEADERS,
    )
    assert response.status == 200

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(CHECK_QUERY)
        assert cursor.fetchall() == [(True,)]

    # and again to check idempotency
    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        json={'is_ignored': True, 'description': 'Some comment'},
        headers=HEADERS,
    )
    assert response.status == 200

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(CHECK_QUERY)
        assert cursor.fetchall() == [(True,)]

    # another description doesn't make a new record
    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        json={'is_ignored': True, 'description': 'Another comment'},
        headers=HEADERS,
    )
    assert response.status == 200

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(CHECK_QUERY)
        assert cursor.fetchall() == [(True,)]

    # change status
    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        json={'is_ignored': False, 'description': 'Another comment'},
        headers=HEADERS,
    )
    assert response.status == 200

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(CHECK_QUERY)
        assert cursor.fetchall() == [(True,), (False,)]


@pytest.mark.config(DRIVER_SCORE_STATUS_DESCRIPTION_MIN_LENGTH=10)
async def test_short_comment(taxi_driver_ratings_storage_web):
    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        json={'is_ignored': True, 'description': '11'},
        headers=HEADERS,
    )
    assert response.status == 400

    content = await response.json()
    assert content == {
        'code': 'BAD_REQUEST',
        'message': 'Expected minimum 10 symbols in comment',
    }


async def test_invalid_order_core(taxi_driver_ratings_storage_web, mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Not found'},
        )

    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'another_order'},
        json={'is_ignored': True, 'description': 'Some comment'},
        headers=HEADERS,
    )
    assert response.status == 404

    content = await response.json()
    assert content == {'code': 'NOT_FOUND', 'message': 'Order not found'}


async def test_invalid_order_db(taxi_driver_ratings_storage_web, mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': ''},
        )

    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'yet_another_order'},
        json={'is_ignored': True, 'description': 'Some comment'},
        headers=HEADERS,
    )
    assert response.status == 500

    content = await response.json()
    assert content == {
        'code': 'INTERNAL_SERVER_ERROR',
        'message': 'Internal server error',
        'details': {'reason': 'Failed to check order_id'},
    }


@pytest.mark.parametrize(
    'is_supersupport,usual_limit,expected_code,expected_body',
    [
        (True, 1, 200, None),
        (False, 1, 403, BODY_403),
        (False, 5, 403, BODY_403),
        (False, 10, 200, None),
    ],
)
@pytest.mark.pgsql('driver_ratings_storage', files=['make_many_actions.sql'])
async def test_limit_exceeded(
        taxi_driver_ratings_storage_web,
        mockserver,
        taxi_config,
        is_supersupport,
        usual_limit,
        expected_code,
        expected_body,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return {
            'fields': {'_id': 'aabbccdd1234'},
            'order_id': 'aabbccdd1234',
            'replica': 'archive',
            'version': '12345',
        }

    taxi_config.set_values(
        {
            'DRIVER_SCORE_STATUS_SUPPORT_SETTINGS': {
                'supersupports': ['login'] if is_supersupport else [],
                'settings': {'period_days': 1, 'limit': usual_limit},
            },
        },
    )

    response = await taxi_driver_ratings_storage_web.put(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        json={'is_ignored': True, 'description': 'Some comment'},
        headers=HEADERS,
    )
    assert response.status == expected_code

    if expected_body:
        content = await response.json()
        assert content == expected_body
