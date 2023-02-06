import asyncio
import json

import jsonschema
import pytest

import tests_driver_orders_app_api.redis_helpers as rh


CONTENT_HEADER = {'Content-Type': 'application/json'}


@pytest.mark.parametrize(
    'exp3_json_file_name, match_enabled',
    [
        ('exp3_use_contractor_order_setcar_false.json', False),
        ('exp3_use_contractor_order_setcar_true.json', True),
    ],
)
@pytest.mark.parametrize(
    'body, code',
    [
        (
            {
                'order_id': 'order_id',
                'driver_cancel_infos': [
                    {
                        'cancel_reason': 'shown',
                        'driver': {
                            'park_id': 'park_id',
                            'driver_profile_id': 'driver_profile_id',
                            'alias_id': 'order_id_0',
                        },
                    },
                ],
            },
            200,
        ),
        ({'alias_id': 'alias_id'}, 400),
    ],
)
async def test_valid_request(
        taxi_driver_orders_app_api,
        body,
        code,
        fleet_parks,
        load_json,
        exp3_json_file_name,
        experiments3,
        match_enabled,
        contractor_order_setcar,
):
    experiments3.add_experiments_json(load_json(exp3_json_file_name))
    await taxi_driver_orders_app_api.invalidate_caches()

    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/cancel/user',
        headers={**CONTENT_HEADER},
        data=json.dumps(body),
    )
    if match_enabled and response.status_code == 200:
        assert contractor_order_setcar.cancel_handler.has_calls
    else:
        assert not contractor_order_setcar.cancel_handler.has_calls

    assert response.status_code == code


@pytest.mark.parametrize('completed_order', [False, True])
@pytest.mark.config(DRIVER_ORDERS_APP_API_CHECK_COMBO_ORDERS_DISCOUNT=True)
async def test_remove_combo_order(
        taxi_driver_orders_app_api,
        fleet_parks,
        load_json,
        redis_store,
        completed_order,
):
    driver_id = 'driver_profile_id'
    combo_order_id = 'order_id_0'
    body = {
        'order_id': 'order_id',
        'driver_cancel_infos': [
            {
                'cancel_reason': 'shown',
                'driver': {
                    'alias_id': 'order_id_0',
                    'driver_profile_id': driver_id,
                    'park_id': 'park_id',
                },
            },
        ],
    }

    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    combo_order_status = {
        'order_id': combo_order_id,
        'is_outer_reason': False,
        'status': 50 if completed_order else 20,
    }
    rh.add_combo_orders_status_item(
        redis_store, driver_id, combo_order_id, combo_order_status,
    )
    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/cancel/user',
        headers={**CONTENT_HEADER},
        data=json.dumps(body),
    )
    assert response.status_code == 200

    combo_orders_statuses = rh.get_combo_orders_status_items(
        redis_store, driver_id,
    )
    if completed_order:
        # do not delete terminated orders
        assert combo_orders_statuses == {combo_order_id: combo_order_status}
    else:
        # order should be deleted
        assert not combo_orders_statuses


PAYLOAD_SETCAR_STATUSES = [
    {'setcar_id': 'Order1', 'status': 'completed'},
    {'setcar_id': 'Order2', 'status': 'completed'},
    {
        'setcar_id': 'Order3',
        'status': 'cancelled',
        'reason': {
            'category': 'assigned_to_other_driver',
            'message': 'assigned_to_other_driver_mes',
        },
    },
    {
        'setcar_id': 'Order4',
        'status': 'cancelled',
        'reason': {
            'category': 'unknown',
            'message': 'Заказ отменен',
        },  # Default message when translation not found
    },
]


@pytest.fixture(name='get_push_schema')
def _get_setcar_statuses(load_yaml):
    schema = load_yaml('setcar_statuses.yaml')
    return schema


@pytest.mark.parametrize(
    'body, code',
    [
        (
            {
                'order_id': 'order_id',
                'driver_cancel_infos': [
                    {
                        'cancel_reason': 'shown',
                        'driver': {
                            'park_id': 'park_id_0',
                            'driver_profile_id': 'driver_profile_id',
                            'alias_id': 'order_id_0',
                        },
                    },
                ],
            },
            200,
        ),
    ],
)
@pytest.mark.redis_store(
    [
        'rpush',
        'Order:Driver:CompleteRequest:Items:park_id_0:driver_profile_id',
        'Order1',
        'Order2',
    ],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:park_id_0:driver_profile_id',
        json.dumps(
            {
                'alias_id': 'Order3',
                'message': 'assigned_to_other_driver_mes',
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'Order4',
                'message': 'missed translate',
                'category': 'unknown',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'is_enabled_client_events_experiment, client_events_fields',
    [(False, []), (True, ['setcar_statuses'])],
)
async def test_valid_push(
        taxi_driver_orders_app_api,
        body,
        code,
        fleet_parks,
        load_json,
        experiments3,
        stq,
        redis_store,
        is_enabled_client_events_experiment,
        client_events_fields,
        get_push_schema,
):

    experiments3.add_config(
        match={
            'predicate': {'type': 'true'},
            'enabled': is_enabled_client_events_experiment,
        },
        name='driver_orders_common_use_client_events_for_send_fields',
        consumers=['driver-orders-common/contractor_park'],
        clauses=[],
        default_value={
            'enabled': is_enabled_client_events_experiment,
            'fields': client_events_fields,
        },
    )
    await taxi_driver_orders_app_api.invalidate_caches()
    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/cancel/user',
        headers={**CONTENT_HEADER},
        data=json.dumps(body),
    )

    expected_setcar_statuses = PAYLOAD_SETCAR_STATUSES
    expected_setcar_statuses.append(
        {
            'setcar_id': 'order_id_0',
            'status': 'cancelled',
            'reason': {'category': 'cancelled', 'message': 'Заказ отменен'},
        },
    )

    assert response.status_code == code
    assert (
        stq.driver_orders_send_communications_notifications.times_called == 1
    )
    kwargs = stq.driver_orders_send_communications_notifications.next_call()[
        'kwargs'
    ]
    assert 'data' in kwargs
    assert 'order' in kwargs['data']
    if not is_enabled_client_events_experiment:
        setcar_statuses = kwargs['data']['setcar_statuses']
        jsonschema.validate(setcar_statuses, get_push_schema)
        assert 'setcar_statuses' in kwargs['data']

        def _sort_statuses(x):
            return x['setcar_id']

        def _statuses_are_equal(left, right):
            return left.sort(key=_sort_statuses) == right.sort(
                key=_sort_statuses,
            )

        assert _statuses_are_equal(expected_setcar_statuses, setcar_statuses)


@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Items:park_id_0',
        {'alias_id_0': json.dumps({'date_view': '2018-07-14T02:40:00Z'})},
    ],
    [
        'rpush',
        'Order:Driver:CancelReason:Items:park_id_0:driver_profile_id_0',
        '{"alias_id": "Hello", "message": "some text", "category": "unknown"}',
    ],
)
@pytest.mark.config(DRIVER_ORDERS_APP_API_CHECK_COMBO_ORDERS_DISCOUNT=True)
async def test_parallell_multioffer_cancel(
        taxi_driver_orders_app_api,
        fleet_parks,
        load_json,
        redis_store,
        mockserver,
        testpoint,
):
    count_driver = 20
    driver_cancel_infos = []
    for i in range(count_driver):
        num = str(i)
        driver_cancel_infos.append(
            {
                'cancel_reason': 'some_reason',
                'driver': {
                    'park_id': 'park_id_' + num,
                    'driver_profile_id': 'driver_profile_id_' + num,
                    'alias_id': 'alias_id_' + num,
                },
            },
        )
    body = {'order_id': 'order_id', 'driver_cancel_infos': driver_cancel_infos}

    cond = asyncio.Condition()
    times_called = 0

    @testpoint('cancel_request')
    async def _tp(data):
        nonlocal times_called
        times_called = times_called + 1
        async with cond:
            cond.notify()
        async with cond:
            await cond.wait_for(
                lambda: times_called >= count_driver / 2,
            )  # I'll be happy to do it better. But now i don't understand how.

    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    response = await taxi_driver_orders_app_api.post(
        '/internal/v2/order/cancel/multioffer',
        headers={**CONTENT_HEADER},
        data=json.dumps(body),
    )
    assert response.status_code == 200

    assert rh.get_setcar_item(redis_store, 'park_id_0', 'alias_id_0') is None
    reasons_content = redis_store.lrange(
        'Order:Driver:CancelReason:Items:park_id_0:driver_profile_id_0', 0, -1,
    )
    assert len(reasons_content) == 2
    actually_inserted = json.loads(reasons_content[1])
    assert actually_inserted['alias_id'] == 'alias_id_0'
    assert actually_inserted['message'] == 'some_reason'
