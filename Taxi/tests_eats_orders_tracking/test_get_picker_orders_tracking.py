import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'

MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'
ORDER_NR = '000000-000000'

ALWAYS_MATCH = {'predicate': {'type': 'true'}, 'enabled': True}

CALL_PICKER = 'Call picker'
ORDER_ASSIGNED = 'Order assigned'
ORDER_PICKING = 'Order picking'
ORDER_PICKED_UP = 'Order picked up'
ORDER_PAID = 'Order paid'


def make_clause(title, arg_name):
    return {
        'title': 'something',
        'value': {
            'default': {
                'title_key': title,
                'short_title_key': 'short_title',
                'show_car_info': False,
                'show_courier': False,
                'icons': [],
                'buttons': [],
            },
        },
        'predicate': {'type': 'bool', 'init': {'arg_name': arg_name}},
    }


LAYER_AB = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS_MATCH,
    name='eats_orders_tracking_dm_layer_ab',
    consumers=['eats-orders-tracking/display_matcher'],
    clauses=[
        {
            'title': 'Always match',
            'value': {
                'experiment_layer_order_type_name': (
                    'eats_orders_tracking_dm_layer_order_type_default'
                ),
            },
            'predicate': {'type': 'true'},
        },
    ],
)

LAYER_ORDER_TYPE = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS_MATCH,
    name='eats_orders_tracking_dm_layer_order_type_default',
    consumers=['eats-orders-tracking/display_matcher'],
    clauses=[
        {
            'title': 'Always match',
            'value': {
                'experiment_layer_order_status_name': (
                    'eats_orders_tracking_dm_layer_order_status_native'
                ),
            },
            'predicate': {'type': 'true'},
        },
    ],
)

LAYER_ORDER_STATUS = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS_MATCH,
    name='eats_orders_tracking_dm_layer_order_status_native',
    consumers=['eats-orders-tracking/display_matcher'],
    clauses=[
        make_clause(CALL_PICKER, 'picker_has_phone'),
        make_clause(ORDER_PAID, 'has_picker_paid_the_order'),
        make_clause(ORDER_PICKED_UP, 'is_order_picked_up'),
        make_clause(ORDER_PICKING, 'is_order_picking_started'),
        make_clause(ORDER_ASSIGNED, 'is_picker_assigned'),
    ],
    default_value={
        'default': {
            'title_key': 'Default key',
            'short_title_key': 'Default short key',
            'show_car_info': False,
            'show_courier': False,
            'icons': [],
            'buttons': [],
        },
    },
)


def add_picker_phone(
        pgsql,
        picker_id,
        phone_id,
        extension=None,
        ttl='2050-12-28T18:15:43.51+00:00',
):
    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""
        insert into eats_orders_tracking.picker_phones
        (picker_id, personal_phone_id, extension, ttl)
        values (%s, %s, %s, %s);
        """,
        [picker_id, phone_id, extension, ttl],
    )


def update_status_history(
        pgsql, order_nr, status, value='2120-12-28T18:15:43.51+00:00',
):
    cursor = pgsql['eats_orders_tracking'].cursor()
    payload = f"""{{"picker_id":"picker_1", "status":"new",
        "status_history":{{"{status}":"{value}"}}}}"""
    cursor.execute(
        f"""
        insert into eats_orders_tracking.picker_orders (order_nr, payload)
        values (%s, %s) on conflict (order_nr) do update set
        payload = EXCLUDED.payload;
        """,
        [order_nr, payload],
    )


@pytest.mark.parametrize(
    ['status', 'expected_title'],
    [
        ('assigned_at', ORDER_ASSIGNED),
        ('picking_at', ORDER_PICKING),
        ('picked_up_at', ORDER_PICKED_UP),
        ('paid_at', ORDER_PAID),
    ],
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@LAYER_AB
@LAYER_ORDER_TYPE
@LAYER_ORDER_STATUS
async def test_picker_statuses(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eats_personal,
        pgsql,
        status,
        expected_title,
):
    # Checking that right picker statuses are passed to experiments
    # Based on those statuses experiment value is returned
    update_status_history(pgsql, ORDER_NR, status)
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    tracked_orders = response.json()['payload']['trackedOrders']
    assert tracked_orders[0]['title'] == expected_title


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@LAYER_AB
@LAYER_ORDER_TYPE
@LAYER_ORDER_STATUS
async def test_picker_phone(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eats_personal,
        pgsql,
):
    # Checking that picker_has_phone == true flag is passed to experiments
    add_picker_phone(pgsql, picker_id='picker_1', phone_id='asdassfa')
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    tracked_orders = response.json()['payload']['trackedOrders']
    assert tracked_orders[0]['title'] == CALL_PICKER


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@LAYER_AB
@LAYER_ORDER_TYPE
@LAYER_ORDER_STATUS
async def test_picker_phone_expired(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eats_personal,
        pgsql,
):
    # Checking that if picker phone is expired
    # picker_has_phone is false in experiment
    add_picker_phone(
        pgsql,
        picker_id='picker_1',
        phone_id='asdassfa',
        ttl='2020-10-28T17:20:00.00+00:00',
    )
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    tracked_orders = response.json()['payload']['trackedOrders']
    assert tracked_orders[0]['title'] == 'Default key'
