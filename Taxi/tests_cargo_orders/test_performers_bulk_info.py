import json
import operator

import pytest


def _get_orders_with_performers(
        default_order_id,
        load_json,
        yt_enabled,
        with_error=False,
        with_performer_cancel=False,
        with_cargo_performer_cancel_flow=False,
):
    result = [
        {
            'order': {
                'order_id': default_order_id,
                'provider_order_id': 'taxi-order',
                'use_cargo_pricing': False,
            },
            'performer_info': {
                'car_id': 'car',
                'car_model': 'car_model',
                'car_number': 'car_number',
                'driver_id': 'driver',
                'is_deaf': False,
                'lookup_version': 1,
                'name': 'abc',
                'order_alias_id': '1234',
                'order_id': default_order_id,
                'park_id': 'park',
                'park_clid': 'clid',
                'phone_pd_id': '7930a74c2aa64f71b96dff9a91ea0b81',
                'revision': 1,
            },
        },
    ]
    if yt_enabled:
        result.extend(load_json('expected_orders_from_yt_with_error.json'))
    if with_error:
        orders_with_error = [
            'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
            'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
            '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
        ]
        for order in result:
            if order['order']['order_id'] in orders_with_error:
                order['order']['order_error'] = {
                    'message': 'UNKNOWN_CARD',
                    'cargo_order_id': order['order']['order_id'],
                    'reason': 'COMMIT_ERROR',
                    'updated_ts': '2021-06-30T11:08:43.070017+00:00',
                }
    if with_performer_cancel:
        orders_with_cancel = [
            default_order_id,
            'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
        ]
        for order in result:
            if order['order']['order_id'] in orders_with_cancel:
                order['order']['order_cancel_performer_reason_list'] = [
                    {
                        'taxi_order_id': order['order']['provider_order_id'],
                        'park_id': 'park',
                        'driver_id': 'driver',
                        'cargo_cancel_reason': 'cargo_reason',
                        'taxi_cancel_reason': 'taxi_reason',
                        'created_ts': '2020-02-03T13:33:54.827958+00:00',
                        'completed': False,
                        'guilty': True,
                        'need_reorder': True,
                        'free_cancellations_limit_exceeded': False,
                        'request_id': 3,
                        'fine_completed': False,
                    },
                    {
                        'taxi_order_id': order['order']['provider_order_id'],
                        'park_id': 'park',
                        'driver_id': 'driver',
                        'cargo_cancel_reason': 'cargo_reason',
                        'taxi_cancel_reason': 'taxi_reason',
                        'created_ts': '2020-02-03T13:33:54.827958+00:00',
                        'completed': True,
                        'guilty': True,
                        'need_reorder': True,
                        'free_cancellations_limit_exceeded': False,
                        'request_id': 4,
                        'fine_completed': False,
                    },
                ]
    if with_cargo_performer_cancel_flow:
        orders_with_cancel = [
            default_order_id,
            'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
        ]
        for order in result:
            if order['order']['order_id'] in orders_with_cancel:
                order['order']['order_cancel_performer_reason_list'] = [
                    {
                        'taxi_order_id': order['order']['provider_order_id'],
                        'park_id': 'park',
                        'driver_id': 'driver',
                        'cargo_cancel_reason': 'cargo_reason',
                        'taxi_cancel_reason': 'taxi_reason',
                        'created_ts': '2020-02-03T13:33:54.827958+00:00',
                        'completed': False,
                        'guilty': False,
                        'need_reorder': True,
                        'free_cancellations_limit_exceeded': False,
                        'request_id': 3,
                        'fine_completed': True,
                    },
                    {
                        'taxi_order_id': order['order']['provider_order_id'],
                        'park_id': 'park',
                        'driver_id': 'driver',
                        'cargo_cancel_reason': 'cargo_reason',
                        'taxi_cancel_reason': 'taxi_reason',
                        'created_ts': '2020-02-03T13:33:54.827958+00:00',
                        'completed': True,
                        'guilty': True,
                        'need_reorder': True,
                        'free_cancellations_limit_exceeded': True,
                        'request_id': 4,
                        'fine_completed': True,
                    },
                ]

    return result


@pytest.mark.pgsql('cargo_orders', files=['orders_performers.sql'])
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            True, marks=pytest.mark.config(CARGO_ORDERS_ENABLE_YT=True),
        ),
        False,
    ],
)
async def test_performers_bulk_info(
        taxi_cargo_orders, yt_apply, load_json, default_order_id, yt_enabled,
):
    response = await taxi_cargo_orders.post(
        '/v1/performers/bulk-info',
        json={
            'orders_ids': [
                default_order_id,
                'b1fe01dd-c302-4727-9f80-6e6c5e210a91',  # no performer
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
            ],
        },
    )
    assert response.status_code == 200
    response_performers = sorted(
        response.json()['performers'], key=operator.itemgetter('order_id'),
    )
    expected_performers = [
        info['performer_info']
        for info in _get_orders_with_performers(
            default_order_id, load_json, yt_enabled,
        )
        if info.get('performer_info') is not None
    ]
    assert response_performers == expected_performers


@pytest.mark.pgsql('cargo_orders', files=['order_with_error.sql'])
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            True, marks=pytest.mark.config(CARGO_ORDERS_ENABLE_YT=True),
        ),
        False,
    ],
)
async def test_order_with_error(
        taxi_cargo_orders, yt_apply, load_json, default_order_id, yt_enabled,
):
    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info',
        json={
            'cargo_orders_ids': [
                default_order_id,
                'b1fe01dd-c302-4727-9f80-6e6c5e210a91',  # no performer
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
            ],
        },
    )
    assert response.status_code == 200
    orders = sorted(
        response.json()['orders'], key=lambda doc: doc['order']['order_id'],
    )
    for order in orders:
        order.pop('order_updated', None)
        order['order'].pop('order_cancel_performer_reason_list', None)
    assert orders == _get_orders_with_performers(
        default_order_id, load_json, yt_enabled, True,
    )


@pytest.mark.pgsql('cargo_orders', files=['orders_performers.sql'])
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            True, marks=pytest.mark.config(CARGO_ORDERS_ENABLE_YT=True),
        ),
        False,
    ],
)
async def test_orders_bulk_info(
        taxi_cargo_orders, yt_apply, load_json, default_order_id, yt_enabled,
):
    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info',
        json={
            'cargo_orders_ids': [
                default_order_id,
                'b1fe01dd-c302-4727-9f80-6e6c5e210a91',  # no performer
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
            ],
        },
    )
    assert response.status_code == 200
    orders = sorted(
        response.json()['orders'], key=lambda doc: doc['order']['order_id'],
    )
    for order in orders:
        order.pop('order_updated', None)
        order['order'].pop('order_cancel_performer_reason_list', None)
    assert orders == _get_orders_with_performers(
        default_order_id, load_json, yt_enabled,
    )


@pytest.mark.pgsql('cargo_orders', files=['orders_performers.sql'])
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.now('2020-06-01T06:35:00+0000')
@pytest.mark.config(CARGO_ORDERS_ENABLE_YT_FORCE_ORDERS=True)
async def test_orders_bulk_info_yt_force(
        taxi_cargo_orders, yt_apply, load_json, default_order_id, testpoint,
):
    @testpoint('cargo_orders_enable_yt_force_orders_callback')
    def _testpoint_callback(data):
        return {'enable': True}

    @testpoint('cargo_orders_enable_yt_force_orders_check')
    def _testpoint_check(data):
        pass

    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info', json={'cargo_orders_ids': [default_order_id]},
    )
    assert response.status_code == 200

    assert _testpoint_callback.next_call()['data'] is None
    assert _testpoint_check.next_call()['data'] is None


@pytest.mark.pgsql('cargo_orders', files=['order_with_performer_cancel.sql'])
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            True, marks=pytest.mark.config(CARGO_ORDERS_ENABLE_YT=True),
        ),
        False,
    ],
)
async def test_order_with_order_cancel_performer_reason(
        taxi_cargo_orders, yt_apply, load_json, default_order_id, yt_enabled,
):
    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info',
        json={
            'cargo_orders_ids': [
                default_order_id,
                'b1fe01dd-c302-4727-9f80-6e6c5e210a91',  # no performer
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
            ],
        },
    )
    assert response.status_code == 200
    orders = sorted(
        response.json()['orders'], key=lambda doc: doc['order']['order_id'],
    )
    for order in orders:
        order.pop('order_updated', None)
    assert orders == _get_orders_with_performers(
        default_order_id, load_json, yt_enabled, False, True,
    )


@pytest.mark.pgsql('cargo_orders', files=['orders_performers.sql'])
async def test_performers_bulk_info_cached(
        taxi_cargo_orders, load_json, default_order_id, pgsql,
):
    driver_loyalty = (
        {
            'matched_driver_rewards': {
                'point_b': {'show_point_b': False, 'lock_reasons': {}},
            },
        },
    )

    cursor = pgsql['cargo_orders'].cursor()
    cursor.execute(
        """
        UPDATE cargo_orders.orders_performers
        SET loyalty_rewards = %s
        """,
        (json.dumps(driver_loyalty),),
    )
    response = await taxi_cargo_orders.post(
        '/v1/performers/bulk-info-cached',
        json={
            'orders_ids': [
                default_order_id,
                'b1fe01dd-c302-4727-9f80-6e6c5e210a91',  # no performer
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
            ],
        },
    )
    assert response.status_code == 200
    response_performers = sorted(
        response.json()['performers'], key=operator.itemgetter('order_id'),
    )
    expected_performers = [
        {
            'loyalty_rewards': [
                {
                    'matched_driver_rewards': {
                        'point_b': {'lock_reasons': {}, 'show_point_b': False},
                    },
                },
            ],
            **info['performer_info'],
        }
        for info in _get_orders_with_performers(
            default_order_id, load_json, False,
        )
        if info.get('performer_info') is not None
    ]
    assert response_performers == expected_performers


MISSING_ORDER_ID = '88888888-4444-4444-4444-ccccccccccc1'


def _insert_performer_missing_in_cache(pgsql):
    cursor = pgsql['cargo_orders'].cursor()
    cursor.execute(
        f"""
    INSERT INTO cargo_orders.orders (
        order_id,
        waybill_ref,
        provider_order_id,
        provider_user_id,
        updated
    ) VALUES (
        '{MISSING_ORDER_ID}',
        'waybill-ref-missing',
        'taxi-order',
        'taxi_user_id_1',
        '2020-02-03 16:33:54.827958+03'
    );
    """,
    )
    cursor.execute(
        f"""
        INSERT INTO cargo_orders.orders_performers (
            order_id,
            order_alias_id,
            phone_pd_id,
            name,
            driver_id,
            park_id,
            park_clid,
            car_id,
            car_number,
            car_model,
            lookup_version
        ) VALUES (
            '{MISSING_ORDER_ID}',
            '1234',
            '7930a74c2aa64f71b96dff9a91ea0b81',
            'abc',
            'almost_incident',
            'baby_dont_crash_me',
            'clid',
            'car',
            'car_number',
            'car_model',
            1
        );
    """,
    )


@pytest.mark.config(
    USERVER_CACHES={
        'performer-info-cache': {
            'full-update-interval-ms': 1,
            'update-interval-ms': 50,
            'update-jitter-ms': 5,
            'updates-enabled': True,
        },
    },
)
@pytest.mark.pgsql('cargo_orders', files=['orders_performers.sql'])
async def test_performers_bulk_info_cached_cache_miss(
        taxi_cargo_orders, load_json, default_order_id, pgsql,
):
    driver_loyalty = (
        {
            'matched_driver_rewards': {
                'point_b': {'show_point_b': False, 'lock_reasons': {}},
            },
        },
    )

    cursor = pgsql['cargo_orders'].cursor()

    await taxi_cargo_orders.invalidate_caches()
    _insert_performer_missing_in_cache(pgsql)
    cursor.execute(
        """
        UPDATE cargo_orders.orders_performers
        SET loyalty_rewards = %s
        """,
        (json.dumps(driver_loyalty),),
    )
    response = await taxi_cargo_orders.post(
        '/v1/performers/bulk-info-cached',
        json={
            'orders_ids': [
                default_order_id,
                'b1fe01dd-c302-4727-9f80-6e6c5e210a91',  # no performer
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
                'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
                MISSING_ORDER_ID,
            ],
        },
    )
    assert response.status_code == 200
    missing_performer = filter(
        lambda p: p['order_id'] == MISSING_ORDER_ID,
        response.json()['performers'],
    )
    assert missing_performer is not None


@pytest.mark.pgsql('cargo_orders', files=['order_with_performer_cancel.sql'])
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            True, marks=pytest.mark.config(CARGO_ORDERS_ENABLE_YT=True),
        ),
        False,
    ],
)
async def test_use_performer_fines_flow(
        mockserver,
        taxi_cargo_orders,
        yt_apply,
        load_json,
        default_order_id,
        yt_enabled,
        exp_cargo_orders_use_performer_fines_service,
):
    cargo_order_ids = [
        default_order_id,
        'b1fe01dd-c302-4727-9f80-6e6c5e210a91',
        'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
        'b1fe01dd-c302-4727-9f80-6e6c5e210a9e',
    ]

    @mockserver.json_handler('/cargo-performer-fines/order/cancel/info')
    def _performer_fines(request):
        assert request.query['cargo_order_id'] in [
            default_order_id,
            'b1fe01dd-c302-4727-9f80-6e6c5e210a9f',
        ]

        cancellations = load_json('cargo_performer_fines_flow.json')
        for cancellation in cancellations:
            cancellation['cargo_order_id'] = request.query['cargo_order_id']
        return {'cancellations': cancellations}

    response = await taxi_cargo_orders.post(
        '/v1/orders/bulk-info', json={'cargo_orders_ids': cargo_order_ids},
    )
    assert response.status_code == 200
    orders = sorted(
        response.json()['orders'], key=lambda doc: doc['order']['order_id'],
    )
    for order in orders:
        order.pop('order_updated', None)
    assert orders == _get_orders_with_performers(
        default_order_id, load_json, yt_enabled, False, False, True,
    )
