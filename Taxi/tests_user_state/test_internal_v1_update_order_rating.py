import pytest

TEST_ORDER_ID = 'test_order_id'

DB_NAME = 'user_state'
GET_UPGRADED_CLASS_ORDER_BY_ID_SQL = """
SELECT
  order_id,
  upgraded_to,
  yandex_uid,
  zone_name,
  brand,
  rating
FROM user_state.upgraded_class_orders
WHERE order_id = '{order_id}'
;
"""

DEFAULT_SETTINGS_CONFIG = {
    'high_order_rating': 5,
    'update_for_classes': ['some_class'],
    'max_upgrade_count_per_user': 100,
}

CONFIG_FOR_THRS_TESTS = {
    'high_order_rating': 5,
    'update_for_classes': ['some_class', 'some_class_2', 'some_class_3'],
    'max_upgrade_count_per_user': 2,
}


def get_personal_state(mongodb, yandex_uid, zone, brand):
    result = mongodb.personal_state.find(
        {'yandex_uid': yandex_uid, 'nearest_zone': zone, 'brand': brand},
    )
    return result[0] if result else None


def get_order(pgsql, order_id):
    db = pgsql[DB_NAME].cursor()
    query = GET_UPGRADED_CLASS_ORDER_BY_ID_SQL.format(order_id=order_id)
    db.execute(query)
    rows = [row for row in db]

    if rows:
        fields = [column.name for column in db.description]
        return dict(zip(fields, rows[0]))

    return None


def get_request(order_id=TEST_ORDER_ID, rating=5, is_order_completed=True):
    return {
        'order_id': order_id,
        'rating': rating,
        'is_order_completed': is_order_completed,
    }


@pytest.mark.config(
    USER_STATE_UPGRADED_CLASS_SELECT_SETTINGS=DEFAULT_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_ok(taxi_user_state, pgsql, mongodb):
    order_id = TEST_ORDER_ID
    expected_rating = 5
    expected_class = 'some_class'

    request = get_request(order_id=order_id, rating=expected_rating)
    response = await taxi_user_state.post(
        '/internal/user-state/v1/update-order-rating', json=request,
    )
    assert response.status == 200

    order = get_order(pgsql, order_id)
    personalstate = get_personal_state(
        mongodb, order['yandex_uid'], order['zone_name'], order['brand'],
    )

    assert order['rating'] == expected_rating
    assert personalstate['selected_class'] == expected_class


@pytest.mark.config(
    USER_STATE_UPGRADED_CLASS_SELECT_SETTINGS=DEFAULT_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
@pytest.mark.parametrize(
    'order_id,rating, should_change',
    [
        pytest.param(TEST_ORDER_ID, 5, True, id='Ok'),
        pytest.param(
            'not_in_db_order_id', 5, False, id='Order was not upgraded',
        ),
        pytest.param(TEST_ORDER_ID, 3, False, id='Low rating'),
        pytest.param(
            'processed_order_id', 5, False, id='Order already processed',
        ),
        pytest.param(
            'bad_class_order_id',
            5,
            False,
            id='Order was upgraded to class that is not in config',
        ),
        pytest.param('rated_order_id', 5, True, id='Order already rated'),
    ],
)
async def test_selected_class_change(
        taxi_user_state, pgsql, mongodb, order_id, rating, should_change,
):
    yandex_uid = 'test_yandex_uid'
    zone = 'moscow'
    brand = 'yataxibrand'

    personalstate_before = get_personal_state(mongodb, yandex_uid, zone, brand)
    class_before = personalstate_before['selected_class']

    request = {
        'order_id': order_id,
        'rating': rating,
        'is_order_completed': True,
    }
    response = await taxi_user_state.post(
        '/internal/user-state/v1/update-order-rating', json=request,
    )
    assert response.status == 200

    personalstate_after = get_personal_state(mongodb, yandex_uid, zone, brand)
    class_after = personalstate_after['selected_class']

    has_changed = class_after != class_before
    assert has_changed == should_change


@pytest.mark.config(
    USER_STATE_UPGRADED_CLASS_SELECT_SETTINGS=CONFIG_FOR_THRS_TESTS,
)
@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_selected_class_change_threshold(taxi_user_state, mongodb):
    yandex_uid = 'test_yandex_uid'
    zone = 'moscow'
    brand = 'yataxibrand'

    for order_id in ['test_order_id', 'test_order_id_2', 'test_order_id_3']:
        personalstate_before = get_personal_state(
            mongodb, yandex_uid, zone, brand,
        )
        class_before = personalstate_before['selected_class']

        request = {
            'order_id': order_id,
            'rating': 5,
            'is_order_completed': True,
        }
        response = await taxi_user_state.post(
            '/internal/user-state/v1/update-order-rating', json=request,
        )
        assert response.status == 200

        personalstate_after = get_personal_state(
            mongodb, yandex_uid, zone, brand,
        )
        class_after = personalstate_after['selected_class']

        has_changed = class_after != class_before
        if order_id != 'test_order_id_3':
            assert has_changed
        else:
            assert not has_changed


@pytest.mark.config(
    USER_STATE_UPGRADED_CLASS_SELECT_SETTINGS=CONFIG_FOR_THRS_TESTS,
)
@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_selected_class_change_update_race(
        taxi_user_state, pgsql, testpoint,
):
    @testpoint('update_race_testpoint')
    def mark_processed(data):
        cursor = pgsql['user_state'].cursor()
        cursor.execute(
            'UPDATE user_state.upgraded_class_orders SET '
            'was_processed = true, rating = 1 '
            'WHERE order_id = \'test_order_id\'',
        )

    request = {
        'order_id': 'test_order_id',
        'rating': 5,
        'is_order_completed': True,
    }
    response = await taxi_user_state.post(
        '/internal/user-state/v1/update-order-rating', json=request,
    )
    assert response.status == 200

    cursor = pgsql['user_state'].cursor()
    cursor.execute(
        'SELECT was_processed, rating FROM '
        'user_state.upgraded_class_orders WHERE order_id = \'test_order_id\'',
    )
    for row in cursor:
        assert row[0]
        assert row[1] == 1  # updated manually at testpoint

    cursor.execute(
        'SELECT possible_upgrade_count FROM '
        'user_state.upgraded_class_count '
        'WHERE yandex_uid = \'test_yandex_uid\'',
    )
    for row in cursor:
        assert row[0] == 3

    assert mark_processed.times_called == 1


@pytest.mark.config(
    USER_STATE_UPGRADED_CLASS_SELECT_SETTINGS=DEFAULT_SETTINGS_CONFIG,
)
@pytest.mark.pgsql(DB_NAME, files=['upgraded_class_orders.sql'])
async def test_metrics_exist(taxi_user_state, taxi_user_state_monitor):

    request = get_request()
    response = await taxi_user_state.post(
        '/internal/user-state/v1/update-order-rating', json=request,
    )
    assert response.status == 200

    metrics_name = 'user_state_upgraded_order_statistics'
    metrics = await taxi_user_state_monitor.get_metrics(metrics_name)
    assert metrics_name in metrics.keys()
