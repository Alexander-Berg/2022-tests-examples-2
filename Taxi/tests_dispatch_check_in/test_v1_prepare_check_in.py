import copy
import datetime

import bson
import pytest

import tests_dispatch_check_in.utils as utils

BODY = {
    'user_id': 'some_user',
    'user_phone_id': 'some_phone',
    'user_locale': 'some_locale',
    'order_request': {
        'pickup_point_uri': 'pickup_point_uri1',
        'point_a': [37.62, 55.75],
        'requirements': {},
        'classes': ['econom'],
        'is_delayed': False,
    },
    'tariff_zone': 'some_tariff_zone',
    'created': 1622801162.803,
    'revision': {'order.version': 1, 'processing.version': 2},
}


async def insert_to_db_test_impl(
        taxi_dispatch_check_in,
        pgsql,
        mocked_time,
        expected_terminal_id='svo1',
):
    now = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    mocked_time.set(now)

    # Check prepare-check-in idempotency, only first call writes to db
    for i in range(0, 2):
        request_body = copy.deepcopy(BODY)
        request_body['created'] = request_body['created'] + i
        response = await taxi_dispatch_check_in.put(
            '/v1/prepare-check-in',
            params={'order_id': 'order_id1'},
            json=request_body,
        )
        assert response.status == 200
        assert response.json() == {
            'order_proc_set_fields': {
                'dispatch_check_in': {
                    'check_in_time': None,
                    'pickup_line': None,
                },
                'order.request.lookup_ttl': 1200,
            },
        }

        etalon = {
            'order_id1': {
                'updated_ts': now,
                'created_ts': datetime.datetime.fromtimestamp(
                    1622801162, tz=datetime.timezone.utc,
                ),
                'check_in_ts': None,
                'terminal_id': expected_terminal_id,
                'pickup_line': None,
                'tariff_zone': 'some_tariff_zone',
                'classes': ['econom'],
                'user_id': 'some_user',
                'user_phone_id': 'some_phone',
                'user_locale': 'some_locale',
            },
        }

        db = pgsql['dispatch_check_in']
        assert etalon == utils.get_all_orders(db, ['user_phone_id'])

        mocked_time.set(now + datetime.timedelta(seconds=15))
        await taxi_dispatch_check_in.tests_control(invalidate_caches=False)


async def coords_not_matched_test_impl(taxi_dispatch_check_in, pgsql):
    request_body = copy.deepcopy(BODY)
    request_body['order_request']['point_a'] = [123, 123]

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in',
        params={'order_id': 'order_id1'},
        json=request_body,
    )
    assert response.status == 200
    assert response.json() == {}

    etalon = {}
    db = pgsql['dispatch_check_in']
    assert etalon == utils.get_all_orders(db)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_prepare_check_in_insert_to_db_no_queue_size_fallback(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        pgsql,
        mocked_time,
):
    await insert_to_db_test_impl(taxi_dispatch_check_in, pgsql, mocked_time)

    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'check_in_flow_orders',
        1,
        ['svo1', 'econom'],
    )
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'orders_queue_size_fallback_orders',
        None,
        ['svo1', 'econom'],
    )


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo_always_check_in_flow',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
@pytest.mark.experiments3(
    filename='experiments3_orders_queue_size_fallback.json',
)
async def test_v1_prepare_check_in_insert_to_db_disabled_fallback(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        pgsql,
        mocked_time,
):
    await insert_to_db_test_impl(
        taxi_dispatch_check_in,
        pgsql,
        mocked_time,
        expected_terminal_id='svo_always_check_in_flow',
    )

    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'check_in_flow_orders',
        1,
        ['svo_always_check_in_flow', 'econom'],
    )
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'orders_queue_size_fallback_orders',
        None,
        ['svo_always_check_in_flow', 'econom'],
    )


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
@pytest.mark.experiments3(
    filename='experiments3_orders_queue_size_fallback.json',
)
async def test_v1_prepare_check_in_insert_to_db_order_queue_is_not_overflow(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        pgsql,
        mocked_time,
):
    await insert_to_db_test_impl(taxi_dispatch_check_in, pgsql, mocked_time)

    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'check_in_flow_orders',
        1,
        ['svo1', 'econom'],
    )
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'orders_queue_size_fallback_orders',
        None,
        ['svo1', 'econom'],
    )


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo_test_order_queue_overflow',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
        'svo_line_2': {
            'enabled': True,
            'terminal_id': 'svo_test_order_queue_overflow',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
@pytest.mark.experiments3(
    filename='experiments3_orders_queue_size_fallback.json',
)
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
async def test_v1_prepare_check_in_order_queue_is_overflow(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        pgsql,
        mocked_time,
):
    db = pgsql['dispatch_check_in']
    orders_before = utils.get_all_orders(db)
    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in', params={'order_id': 'order_id100'}, json=BODY,
    )
    assert response.status == 200
    assert response.json() == {}
    orders_after = utils.get_all_orders(db)

    assert orders_before == orders_after

    mocked_time.sleep(10)
    await taxi_dispatch_check_in.tests_control(invalidate_caches=False)
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'check_in_flow_orders',
        None,
        ['svo_test_order_queue_overflow', 'econom'],
    )
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'orders_queue_size_fallback_orders',
        1,
        ['svo_test_order_queue_overflow', 'econom'],
    )


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        # Not suitable because of disabled
        'svo_line_1': {
            'enabled': False,
            'terminal_id': 'svo',
            'allowed_tariffs': ['econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
        # Not suitable because of allowed_tariffs = business
        'svo_line_2': {
            'enabled': True,
            'terminal_id': 'svo',
            'allowed_tariffs': ['business'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
        # Not suitable because of no order's pickup point
        'svo_line_3': {
            'enabled': True,
            'terminal_id': 'svo',
            'allowed_tariffs': ['econom'],
            'pickup_points': ['pickup_point_uri2', 'pickup_point_uri3'],
            'check_in_zone_coordinates': [10, 10],
        },
        # Not suitable because of allowed tariffs are empty
        'svo_line_4': {
            'enabled': True,
            'terminal_id': 'svo',
            'allowed_tariffs': [],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
        # Not suitable because of pickup points are empty
        'svo_line_5': {
            'enabled': True,
            'terminal_id': 'svo',
            'allowed_tariffs': ['econom'],
            'pickup_points': [],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_prepare_check_in_no_suitable_pickup_line(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, pgsql,
):
    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in', params={'order_id': 'order_id1'}, json=BODY,
    )
    assert response.status == 200
    assert response.json() == {}

    etalon = {}
    db = pgsql['dispatch_check_in']
    assert etalon == utils.get_all_orders(db)

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_prepare_check_in_pickup_point_coords_not_matched(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, pgsql,
):
    await coords_not_matched_test_impl(taxi_dispatch_check_in, pgsql)

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


# Oneshot, because we want to test pickup points coords cache in null state
@pytest.mark.uservice_oneshot
@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
    DISPATCH_CHECK_IN_ALLOWED_PICKUP_POINTS=[],
)
async def test_v1_prepare_check_in_pickup_point_coords_not_matched_empty_uris(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, pgsql,
):
    await taxi_dispatch_check_in.invalidate_caches()
    await coords_not_matched_test_impl(taxi_dispatch_check_in, pgsql)

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_prepare_check_in_multiple_classes(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, pgsql,
):
    request_body = copy.deepcopy(BODY)
    request_body['order_request']['classes'].append('business')

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in',
        params={'order_id': 'order_id1'},
        json=request_body,
    )
    assert response.status == 200
    assert response.json() == {}

    etalon = {}
    db = pgsql['dispatch_check_in']
    assert etalon == utils.get_all_orders(db)

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_prepare_check_is_delayed_by_flag(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, pgsql,
):
    request_body = copy.deepcopy(BODY)
    request_body['order_request']['is_delayed'] = True

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in',
        params={'order_id': 'order_id1'},
        json=request_body,
    )
    assert response.status == 200
    assert response.json() == {}

    etalon = {}
    db = pgsql['dispatch_check_in']
    assert etalon == utils.get_all_orders(db)

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
    DELAYED_ORDER_DETECTION_THRESHOLD_MIN=10,
)
async def test_v1_prepare_check_is_delayed_by_due(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, pgsql,
):
    request_body = copy.deepcopy(BODY)
    request_body['order_request']['due'] = request_body['created'] + 601

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in',
        params={'order_id': 'order_id1'},
        json=request_body,
    )
    assert response.status == 200
    assert response.json() == {}

    etalon = {}
    db = pgsql['dispatch_check_in']
    assert etalon == utils.get_all_orders(db)

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
@pytest.mark.parametrize(
    'allowed_requirements, etalon',
    [
        ({'svo1': {'econom': ['child_seat', 'air_conditioner']}}, 0),
        ({'svo1': {'econom': ['child_seat', 'yellow_cab']}}, 1),
        ({'svo1': {'__default__': ['child_seat', 'yellow_cab']}}, 1),
        ({'__default__': {'__default__': ['child_seat', 'yellow_cab']}}, 1),
    ],
)
async def test_v1_prepare_check_in_allowed_requirements(
        taxi_dispatch_check_in,
        pgsql,
        taxi_config,
        allowed_requirements,
        etalon,
):
    request_body = copy.deepcopy(BODY)
    request_body['order_request']['requirements'] = {
        'yellow_cab': True,
        'child_seat': [0, 3, 7],
    }

    taxi_config.set(
        DISPATCH_CHECK_IN_ALLOWED_REQUIREMENTS=allowed_requirements,
    )

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in',
        params={'order_id': 'order_id1'},
        json=request_body,
    )
    assert response.status == 200

    db = pgsql['dispatch_check_in']
    assert len(utils.get_all_orders(db)) == etalon


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
async def test_v1_prepare_check_in_negative(
        taxi_dispatch_check_in, taxi_dispatch_check_in_monitor, mockserver,
):
    status_code = 400

    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _mock_order_set_fields(request):
        nonlocal status_code
        return mockserver.make_response(
            status=status_code,
            content_type='application/json',
            json={'code': 'non_writable_field', 'message': 'any_message'},
        )

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in', params={'order_id': 'order_id1'}, json=BODY,
    )
    r_json = response.json()
    assert response.status == 400
    assert r_json == {
        'message': 'Failed to prepare check-in',
        'code': 'PREPARE_CHECK_IN_FAILED',
    }

    status_code = 404
    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in', params={'order_id': 'order_id1'}, json=BODY,
    )
    r_json = response.json()
    assert response.status == 404
    assert r_json == {'message': 'Order not found', 'code': 'ORDER_NOT_FOUND'}

    status_code = 409
    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in', params={'order_id': 'order_id1'}, json=BODY,
    )
    r_json = response.json()
    assert response.status == 409
    assert r_json == {
        'message': 'Revision mismatch',
        'code': 'REVISION_MISMATCH',
    }

    assert _mock_order_set_fields.times_called == 3

    await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.config(
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'svo_line_1': {
            'enabled': True,
            'terminal_id': 'svo1',
            'allowed_tariffs': ['business', 'econom'],
            'pickup_points': ['pickup_point_uri1', 'pickup_point_uri2'],
            'check_in_zone_coordinates': [10, 10],
        },
    },
)
@pytest.mark.experiments3(filename='lookup_ttl_experiments.json')
@pytest.mark.parametrize('force_totw', [True, False])
@pytest.mark.parametrize('use_set_fields', [True, False])
async def test_v1_prepare_check_in_positive(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        taxi_config,
        mockserver,
        mocked_time,
        force_totw,
        use_set_fields,
):
    @mockserver.handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def _mock_order_set_fields(request):
        body = bson.BSON.decode(request.get_data())
        assert body == {
            'filter': {'status': 'pending'},
            'revision': {'order.version': 1, 'processing.version': 2},
            'update': {
                '$set': {
                    'dispatch_check_in': {
                        'check_in_time': None,
                        'pickup_line': None,
                    },
                    'order.request.lookup_ttl': 456,
                },
            },
        }
        return mockserver.make_response('', 200)

    @mockserver.json_handler('/client-notify/v2/push')
    def _v2_push(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'prepare_check_in_force_totw_order_id1_0'
        )
        assert request.json == {
            'client_id': 'some_user',
            'intent': 'force_totw',
            'service': 'go',
            'data': {'order_id': 'order_id1'},
        }
        return {'notification_id': '1'}

    taxi_config.set_values(
        {
            'DISPATCH_CHECK_IN_FORCE_TOTW_PUSH_SETTINGS': {
                'enabled': force_totw,
            },
            'DISPATCH_CHECK_IN_USE_SET_FIELDS': use_set_fields,
        },
    )

    response = await taxi_dispatch_check_in.put(
        '/v1/prepare-check-in', params={'order_id': 'order_id1'}, json=BODY,
    )
    assert _mock_order_set_fields.times_called == (1 if use_set_fields else 0)
    assert response.status == 200
    assert response.json() == {
        'order_proc_set_fields': {
            'dispatch_check_in': {'check_in_time': None, 'pickup_line': None},
            'order.request.lookup_ttl': 456,
        },
    }

    mocked_time.sleep(10)
    await taxi_dispatch_check_in.tests_control(invalidate_caches=False)
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'check_in_flow_orders',
        1,
        ['svo1', 'econom'],
    )
    await utils.check_metric(
        taxi_dispatch_check_in_monitor,
        'orders_queue_size_fallback_orders',
        None,
        ['svo1', 'econom'],
    )

    if force_totw:
        await _v2_push.wait_call()
    else:
        assert _v2_push.times_called == 0
