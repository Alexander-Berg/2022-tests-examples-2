import pytest

NOW = '2020-09-21T12:30:00.000+00:00'
THR_SECONDS_1DAY = 86400
THR_SECONDS_1HOUR = 3600

PERIOD_BEGIN = '2020-09-20T10:00:00.000000+00:00'
PERIOD_END = '2020-09-20T13:00:00.000000+00:00'
UPDATED_1 = '2020-09-20T12:31:00.799672+00:00'
UPDATED_2 = '2020-09-20T11:00:00.799672+00:00'

LEGACY_DEPOT_ID = '100'
ORDER_ID_1 = 'test_order_id_0'
PERFORMER_ID_1 = 'dbid0_uuid0'
ORDER_ID_2 = 'test_order_id_1'
PERFORMER_ID_2 = 'dbid1_uuid1'


def generate_performer(performer_id: str):
    return {'courier_dbid_uuid': performer_id, 'performer_status': 'idle'}


def generate_order(order_id: str):
    return {
        'order_id': order_id,
        'order_status': 'delivering',
        'delivery_type': 'courier',
        'assembly_started': '2021-08-12T07:22:40.721471+00:00',
        'assembly_finished': '2021-08-12T07:22:40.721471+00:00',
        'courier_dbid_uuid': 'dbid0_uuid0',
    }


EXPECTED_RESPONSE_1 = {
    'depot_states': [
        {
            'depot_id': LEGACY_DEPOT_ID,
            'depot_state': {
                'orders': [generate_order(ORDER_ID_1)],
                'performers': [generate_performer(PERFORMER_ID_1)],
            },
            'updated': UPDATED_1,
        },
    ],
}

EXPECTED_RESPONSE_2 = {
    'depot_states': [
        {
            'depot_id': LEGACY_DEPOT_ID,
            'depot_state': {
                'orders': [generate_order(ORDER_ID_1)],
                'performers': [generate_performer(PERFORMER_ID_1)],
            },
            'updated': UPDATED_1,
        },
        {
            'depot_id': LEGACY_DEPOT_ID,
            'depot_state': {
                'orders': [generate_order(ORDER_ID_2)],
                'performers': [generate_performer(PERFORMER_ID_2)],
            },
            'updated': UPDATED_2,
        },
    ],
}


@pytest.mark.now(NOW)
@pytest.mark.config(
    GROCERY_DISPATCH_TRACKING_DEPOT_STATE_THR_SECONDS=THR_SECONDS_1DAY,
)
async def test_admin_depot_state_all_from_db(
        taxi_grocery_dispatch_tracking,
        grocery_cold_storage,
        insert_depot_state,
):
    insert_depot_state(
        depot_id=LEGACY_DEPOT_ID,
        orders=[generate_order(ORDER_ID_1)],
        performers=[generate_performer(PERFORMER_ID_1)],
        updated=UPDATED_1,
    )

    response = await taxi_grocery_dispatch_tracking.post(
        '/admin/grocery-dispatch-tracking/v1/depot-state',
        json={
            'depot_id': LEGACY_DEPOT_ID,
            'period_begin': PERIOD_BEGIN,
            'period_end': PERIOD_END,
        },
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE_1


@pytest.mark.now(NOW)
@pytest.mark.config(
    GROCERY_DISPATCH_TRACKING_DEPOT_STATE_THR_SECONDS=THR_SECONDS_1HOUR,
)
async def test_admin_depot_state_all_from_yt(
        taxi_grocery_dispatch_tracking, grocery_cold_storage,
):
    grocery_cold_storage.set_depot_state_response(
        items=[
            {
                'depot_id': LEGACY_DEPOT_ID,
                'item_id': LEGACY_DEPOT_ID,
                'orders': [generate_order(ORDER_ID_1)],
                'performers': [generate_performer(PERFORMER_ID_1)],
                'updated': UPDATED_1[:-6],
            },
        ],
    )

    response = await taxi_grocery_dispatch_tracking.post(
        '/admin/grocery-dispatch-tracking/v1/depot-state',
        json={
            'depot_id': LEGACY_DEPOT_ID,
            'period_begin': PERIOD_BEGIN,
            'period_end': PERIOD_END,
        },
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE_1


@pytest.mark.now(NOW)
@pytest.mark.config(
    GROCERY_DISPATCH_TRACKING_DEPOT_STATE_THR_SECONDS=THR_SECONDS_1DAY,
)
async def test_admin_depot_state_from_db_and_yt(
        taxi_grocery_dispatch_tracking,
        grocery_cold_storage,
        insert_depot_state,
):
    insert_depot_state(
        depot_id=LEGACY_DEPOT_ID,
        orders=[generate_order(ORDER_ID_1)],
        performers=[generate_performer(PERFORMER_ID_1)],
        updated=UPDATED_1,
    )

    grocery_cold_storage.set_depot_state_response(
        items=[
            {
                'depot_id': LEGACY_DEPOT_ID,
                'item_id': LEGACY_DEPOT_ID,
                'orders': [generate_order(ORDER_ID_2)],
                'performers': [generate_performer(PERFORMER_ID_2)],
                'updated': UPDATED_2[:-6],
            },
        ],
    )

    response = await taxi_grocery_dispatch_tracking.post(
        '/admin/grocery-dispatch-tracking/v1/depot-state',
        json={
            'depot_id': LEGACY_DEPOT_ID,
            'period_begin': PERIOD_BEGIN,
            'period_end': PERIOD_END,
        },
    )

    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE_2
