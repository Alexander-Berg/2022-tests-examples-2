# pylint: disable=too-many-lines
import datetime

import pytest

from . import utils


PERIODIC_NAME = 'courier-estimations-updater'
DB_ORDERS_UPDATE_OFFSET = 5


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
async def test_courier_estimations_updater_empty_db(
        taxi_eats_eta, db_select_orders, redis_store,
):
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert db_select_orders() == []
    assert not redis_store.keys()


@pytest.mark.parametrize('order_status', ['paid'])
@pytest.mark.parametrize('order_type', ['retail'])
@pytest.mark.parametrize('brand_id', [1])
@pytest.mark.parametrize('country_id', [1])
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
@pytest.mark.parametrize(
    'corp_client_type',
    [None, utils.EDA_CORP_CLIENT, utils.RETAIL_CORP_CLIENT],
)
async def test_courier_estimations_updater_update_claims(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        make_place,
        db_insert_place,
        db_insert_order,
        db_select_orders,
        order_status,
        order_type,
        brand_id,
        country_id,
        corp_client_type,
        check_redis_value,
):
    orders = [
        make_order(
            id=i,
            claim_id=f'claim-{i}',
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            delivery_type='native',
            order_status=order_status,
            order_type=order_type,
            corp_client_type=corp_client_type,
            batch_info_updated_at=now_utc,
        )
        for i in range(3)
    ]
    place = make_place(brand_id=brand_id, country_id=country_id)
    db_insert_place(place)
    for order in orders:
        db_insert_order(order)

        claim_id = order['claim_id']

        cargo.add_claim(
            claim_id=claim_id,
            order_nr=order['order_nr'],
            order_type=order_type,
        )

        claim = load_json('claim.json')
        utils.update_cargo_claim(order, claim_id, claim)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def mock_cargo_points_eta(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_cargo_performer_position(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == len(orders)
    assert mock_cargo_points_eta.times_called == len(orders)
    assert mock_cargo_performer_position.times_called == len(orders)
    assert db_select_orders() == orders
    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'],
            'courier_arrival_duration',
            max(
                datetime.timedelta(
                    seconds=utils.FALLBACKS['courier_arrival_duration'],
                ),
                utils.trunc_timedelta(now_utc - order['claim_created_at'])
                + datetime.timedelta(
                    seconds=utils.FALLBACKS['minimal_remaining_duration'],
                ),
            ),
        )
        check_redis_value(
            order['order_nr'],
            'delivery_duration',
            utils.FALLBACKS['delivery_duration'],
        )


@pytest.mark.parametrize(
    'order_status', ['created', 'paid', 'confirmed', 'taken'],
)
@pytest.mark.parametrize(
    'order_type', ['retail', 'shop', 'fast_food', 'native'],
)
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
async def test_courier_estimations_updater_claim_changed(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        order_type,
        check_redis_value,
):
    claim_id = 'claim-0'
    order = make_order(
        id=1,
        claim_id=claim_id,
        order_nr='order_nr-1',
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        delivery_type='native',
        order_status=order_status,
        order_type=order_type,
        corp_client_type=utils.EDA_CORP_CLIENT,
        batch_info_updated_at=now_utc,
    )

    db_insert_order(order)

    cargo.add_claim(
        claim_id=claim_id, order_nr=order['order_nr'], order_type=order_type,
    )

    claim = load_json('claim.json')
    utils.update_cargo_claim(order, claim_id, claim)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def mock_cargo_points_eta(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_cargo_performer_position(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 1
    assert mock_cargo_points_eta.times_called == 1
    assert mock_cargo_performer_position.times_called == 1
    assert db_select_orders() == [order]
    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'],
        'courier_arrival_duration',
        max(
            datetime.timedelta(
                seconds=utils.FALLBACKS['courier_arrival_duration'],
            ),
            utils.trunc_timedelta(now_utc - order['claim_created_at'])
            + datetime.timedelta(
                seconds=utils.FALLBACKS['minimal_remaining_duration'],
            ),
        )
        if order_status != 'taken'
        else None,
    )
    check_redis_value(
        order['order_nr'],
        'delivery_duration',
        utils.FALLBACKS['delivery_duration'],
    )


@pytest.mark.parametrize(
    'order_status', ['created', 'paid', 'confirmed', 'taken'],
)
@pytest.mark.parametrize(
    'order_type', ['retail', 'shop', 'fast_food', 'native'],
)
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
async def test_courier_estimations_updater_order_has_claim_info(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        order_type,
        check_redis_value,
):
    order_nr = 'order_nr-1'
    claim_id = 'claim_1'
    cargo.add_claim(
        claim_id=claim_id, order_nr=order_nr, order_type=order_type,
    )
    order = make_order(
        id=1,
        order_nr=order_nr,
        status_changed_at=now_utc
        - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
        delivery_type='native',
        order_status=order_status,
        order_type=order_type,
        claim_id=claim_id,
        batch_info_updated_at=now_utc,
    )

    claim = load_json('claim.json')
    utils.update_cargo_claim(order, claim_id, claim)

    db_insert_order(order)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def mock_cargo_points_eta(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_cargo_performer_position(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 0
    assert mock_cargo_points_eta.times_called == 1
    assert mock_cargo_performer_position.times_called == 1
    assert db_select_orders() == [order]
    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'],
        'courier_arrival_duration',
        max(
            datetime.timedelta(
                seconds=utils.FALLBACKS['courier_arrival_duration'],
            ),
            utils.trunc_timedelta(now_utc - order['claim_created_at'])
            + datetime.timedelta(
                seconds=utils.FALLBACKS['minimal_remaining_duration'],
            ),
        )
        if order_status != 'taken'
        else None,
    )
    check_redis_value(
        order['order_nr'],
        'delivery_duration',
        utils.FALLBACKS['delivery_duration'],
    )


@pytest.mark.parametrize('order_status', ['confirmed', 'taken'])
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
@pytest.mark.parametrize(
    'cargo_info_update_offset',
    [datetime.timedelta(seconds=1), datetime.timedelta(days=1)],
)
async def test_courier_estimations_updater_update_points_eta(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        cargo_info_update_offset,
        check_redis_value,
):
    corp_client_type = utils.EDA_CORP_CLIENT
    orders = [
        make_order(
            id=i,
            claim_id=f'claim-{i}',
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            delivery_type='native',
            order_status=order_status,
            delivery_started_at=now_utc,
            corp_client_type=corp_client_type,
            courier_position='(11.22,33.44)',
            courier_position_updated_at=now_utc - cargo_info_update_offset,
            place_visit_status='visited',
            place_visited_at=now_utc,
            customer_visit_status='visited',
            customer_visited_at=now_utc,
            place_point_eta_updated_at=now_utc - cargo_info_update_offset,
            customer_point_eta_updated_at=now_utc - cargo_info_update_offset,
            batch_info_updated_at=now_utc,
        )
        for i in range(3)
    ]
    for order in orders:
        db_insert_order(order)

        claim_id = order['claim_id']
        cargo.add_claim(claim_id=claim_id, order_nr=order['order_nr'])

        claim = load_json('claim.json')
        utils.update_cargo_claim(order, claim_id, claim)

        points_eta = load_json('points_eta.json')
        utils.update_points_eta(order, now_utc, points_eta)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_cargo_performer_position(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 3
    assert cargo.mock_cargo_points_eta.times_called == 3
    assert mock_cargo_performer_position.times_called == 3
    assert db_select_orders() == orders
    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'],
            'courier_arrival_duration',
            utils.trunc_timedelta(
                max(
                    order['place_visited_at'],
                    now_utc
                    + datetime.timedelta(
                        seconds=utils.FALLBACKS['minimal_remaining_duration'],
                    ),
                )
                - order['claim_created_at'],
            )
            if order_status != 'taken'
            else None,
        )
        check_redis_value(
            order['order_nr'],
            'delivery_duration',
            utils.trunc_timedelta(
                max(
                    order['customer_visited_at']
                    - order['place_visited_at']
                    - order['place_cargo_waiting_time'],
                    datetime.timedelta(),
                )
                if order_status != 'taken'
                else max(
                    order['customer_visited_at'],
                    now_utc
                    + datetime.timedelta(
                        seconds=utils.FALLBACKS['minimal_remaining_duration'],
                    ),
                )
                - order['delivery_started_at'],
            ),
        )


@pytest.mark.now('2021-11-12T12:00:00+03:00')
@pytest.mark.parametrize(
    'place_visit_status, place_visited_at, '
    'customer_visit_status, customer_visited_at',
    [
        ['arrived', None, 'pending', '2021-11-12T13:00:00+03:00'],
        ['visited', '2021-11-12T12:00:00+03:00', 'arrived', None],
        [
            'visited',
            '2021-11-12T12:00:00+03:00',
            'pending',
            '2021-11-12T13:00:00+03:00',
        ],
    ],
)
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
async def test_courier_estimations_updater_missing_points_eta(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        place_visit_status,
        place_visited_at,
        customer_visit_status,
        customer_visited_at,
        check_redis_value,
):
    corp_client_type = utils.EDA_CORP_CLIENT
    order = make_order(
        id=1,
        claim_id='claim-1',
        order_nr='order_nr-1',
        status_changed_at=now_utc,
        delivery_type='native',
        order_status='confirmed',
        claim_status='performer_found',
        place_visit_status='pending',
        place_visited_at=now_utc - datetime.timedelta(minutes=1),
        customer_visit_status='pending',
        customer_visited_at=now_utc + datetime.timedelta(minutes=10),
        corp_client_type=corp_client_type,
        batch_info_updated_at=now_utc,
    )
    db_insert_order(order)

    claim_id = order['claim_id']
    cargo.add_claim(claim_id=claim_id, order_nr=order['order_nr'])

    claim = load_json('claim.json')
    order['claim_status'] = claim['status']
    utils.update_cargo_claim(order, claim_id, claim)

    points_eta = load_json('points_eta.json')
    for point in points_eta['route_points']:
        if point['type'] == 'source':
            point['visit_status'] = place_visit_status
            point['visited_at'] = {
                'actual': place_visited_at,
                'expected_waiting_time_sec': 100,
            }
        else:
            point['visit_status'] = customer_visit_status
            point['visited_at'] = {
                'actual': customer_visited_at,
                'expected_waiting_time_sec': 200,
            }
    order['place_visit_status'] = place_visit_status
    order['customer_visit_status'] = customer_visit_status
    if place_visited_at is not None:
        order['place_visited_at'] = utils.parse_datetime(place_visited_at)
        order['place_cargo_waiting_time'] = datetime.timedelta(seconds=100)
        order['place_point_eta_updated_at'] = now_utc
    if customer_visited_at is not None:
        order['customer_visited_at'] = utils.parse_datetime(
            customer_visited_at,
        )
        order['customer_cargo_waiting_time'] = datetime.timedelta(seconds=200)
        order['customer_point_eta_updated_at'] = now_utc

    cargo.points_eta = points_eta

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_cargo_performer_position(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 1
    assert cargo.mock_cargo_points_eta.times_called == 1
    assert mock_cargo_performer_position.times_called == 1
    assert db_select_orders() == [order]

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    if place_visited_at and customer_visited_at:
        courier_arrival_duration = utils.trunc_timedelta(
            order['place_visited_at'] - order['claim_created_at'],
        )
        delivery_duration = max(
            order['customer_visited_at']
            - order['place_visited_at']
            - (
                order['place_cargo_waiting_time']
                if place_visit_status != 'visited'
                else datetime.timedelta()
            ),
            datetime.timedelta(),
        )
    elif place_visit_status == 'visited' and place_visited_at is not None:
        courier_arrival_duration = (
            order['place_visited_at'] - order['claim_created_at']
        )
        delivery_duration = datetime.timedelta(
            seconds=utils.FALLBACKS['delivery_duration'],
        )
    else:
        courier_arrival_duration = max(
            datetime.timedelta(
                seconds=utils.FALLBACKS['courier_arrival_duration'],
            ),
            utils.trunc_timedelta(now_utc - order['claim_created_at'])
            + datetime.timedelta(
                seconds=utils.FALLBACKS['minimal_remaining_duration'],
            ),
        )
        delivery_duration = datetime.timedelta(
            seconds=utils.FALLBACKS['delivery_duration'],
        )
    check_redis_value(
        order['order_nr'],
        'courier_arrival_duration',
        courier_arrival_duration,
    )
    check_redis_value(
        order['order_nr'], 'delivery_duration', delivery_duration,
    )


@pytest.mark.parametrize('order_status', ['confirmed', 'taken'])
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
async def test_courier_estimations_updater_update_performer_position(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        check_redis_value,
):
    corp_client_type = utils.EDA_CORP_CLIENT
    orders = [
        make_order(
            id=i,
            claim_id=f'claim-{i}',
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            delivery_type='native',
            order_status=order_status,
            corp_client_type=corp_client_type,
            batch_info_updated_at=now_utc,
        )
        for i in range(3)
    ]
    for order in orders:
        db_insert_order(order)

        claim_id = order['claim_id']
        cargo.add_claim(claim_id=claim_id, order_nr=order['order_nr'])

        claim = load_json('claim.json')
        utils.update_cargo_claim(order, claim_id, claim)

        performer_position = load_json('performer_position.json')
        utils.update_performer_position(order, performer_position)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def mock_cargo_points_eta(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 3
    assert mock_cargo_points_eta.times_called == 3
    assert cargo.mock_cargo_performer_position.times_called == 3
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'],
            'courier_arrival_duration',
            max(
                utils.trunc_timedelta(now_utc - order['claim_created_at'])
                + datetime.timedelta(
                    seconds=utils.FALLBACKS['minimal_remaining_duration'],
                ),
                datetime.timedelta(
                    seconds=utils.FALLBACKS['courier_arrival_duration'],
                ),
            )
            if order_status != 'taken'
            else None,
        )
        check_redis_value(
            order['order_nr'],
            'delivery_duration',
            utils.FALLBACKS['delivery_duration'],
        )


@pytest.mark.parametrize('order_status', ['confirmed', 'taken'])
@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
async def test_courier_estimations_updater_update_orders_404(
        load_json,
        mockserver,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        order_status,
        check_redis_value,
):
    corp_client_type = utils.EDA_CORP_CLIENT
    orders = [
        make_order(
            id=i,
            claim_id=f'claim-{i}',
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET - 1 + i),
            delivery_type='native',
            order_status=order_status,
            corp_client_type=corp_client_type,
            batch_info_updated_at=now_utc,
        )
        for i in range(3)
    ]
    for order in orders:
        db_insert_order(order)

        claim_id = order['claim_id']
        cargo.add_claim(claim_id=claim_id, order_nr=order['order_nr'])
        claim = load_json('claim.json')
        utils.update_cargo_claim(order, claim_id, claim)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def mock_cargo_points_eta(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def mock_cargo_performer_position(_):
        return mockserver.make_response(
            status=404,
            json={'code': 'not_found', 'message': 'pretend the query failed'},
        )

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 3
    assert mock_cargo_points_eta.times_called == 3
    assert mock_cargo_performer_position.times_called == 3
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'],
            'courier_arrival_duration',
            max(
                utils.trunc_timedelta(now_utc - order['claim_created_at'])
                + datetime.timedelta(
                    seconds=utils.FALLBACKS['minimal_remaining_duration'],
                ),
                datetime.timedelta(
                    seconds=utils.FALLBACKS['courier_arrival_duration'],
                ),
            )
            if order_status != 'taken'
            else None,
        )
        check_redis_value(
            order['order_nr'],
            'delivery_duration',
            utils.FALLBACKS['delivery_duration'],
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@utils.eats_eta_corp_clients_config3()
async def test_courier_estimations_updater_no_update_for_claim_statuses(
        load_json,
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    corp_client_type = utils.EDA_CORP_CLIENT
    claim_statuses = [
        'new',
        'estimating',
        'estimating_failed',
        'ready_for_approval',
        'accepted',
        'performer_lookup',
        'performer_draft',
        'performer_not_found',
        'delivered',
        'delivered_finish',
        'failed',
        'cancelled',
        'cancelled_with_payment',
        'cancelled_by_taxi',
        'cancelled_with_items_on_hands',
        'returned',
        'returned_finish',
    ]
    orders = [
        make_order(
            id=i,
            claim_id=f'claim-{i}',
            order_nr='order_nr-{}'.format(i),
            status_changed_at=now_utc
            - datetime.timedelta(seconds=DB_ORDERS_UPDATE_OFFSET),
            delivery_type='native',
            order_status='confirmed',
            corp_client_type=corp_client_type,
            batch_info_updated_at=now_utc,
        )
        for i in range(len(claim_statuses))
    ]
    for i, order in enumerate(orders):
        db_insert_order(order)

        claim_id = order['claim_id']
        claim_status = claim_statuses[i]
        cargo.add_claim(
            claim_id=claim_id, order_nr=order['order_nr'], status=claim_status,
        )

        claim = load_json('claim.json')
        claim['status'] = claim_status
        utils.update_cargo_claim(order, claim_id, claim)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == len(claim_statuses)
    assert cargo.mock_cargo_points_eta.times_called == 0
    assert cargo.mock_cargo_performer_position.times_called == 0
    assert db_select_orders() == orders

    for order in orders:
        for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
            check_redis_value(order['order_nr'], redis_key, order[redis_key])
        check_redis_value(
            order['order_nr'],
            'courier_arrival_duration',
            max(
                utils.trunc_timedelta(now_utc - order['claim_created_at'])
                + datetime.timedelta(
                    seconds=utils.FALLBACKS['minimal_remaining_duration'],
                ),
                datetime.timedelta(
                    seconds=utils.FALLBACKS['courier_arrival_duration'],
                ),
            ),
        )
        check_redis_value(
            order['order_nr'],
            'delivery_duration',
            utils.FALLBACKS['delivery_duration'],
        )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_courier_estimations_updater_marketplace_ok(
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        check_redis_value,
):
    order = make_order(
        order_nr='order_nr-{}'.format(1),
        status_changed_at=now_utc,
        delivery_type='marketplace',
        shipping_type='delivery',
        order_status='confirmed',
    )
    order['id'] = db_insert_order(order)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 0
    assert cargo.mock_cargo_points_eta.times_called == 0
    assert cargo.mock_cargo_performer_position.times_called == 0
    assert db_select_orders() == [order]
    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'],
        'courier_arrival_duration',
        datetime.timedelta(
            seconds=utils.FALLBACKS['courier_arrival_duration'],
        ),
    )
    check_redis_value(
        order['order_nr'],
        'delivery_duration',
        utils.FALLBACKS['delivery_duration'],
    )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize('delivery_type', ['native', 'marketplace'])
async def test_courier_estimations_updater_get_ml_prediction(
        taxi_eats_eta,
        mockserver,
        cargo,
        now_utc,
        make_order,
        make_place,
        db_insert_order,
        db_insert_place,
        db_select_orders,
        check_redis_value,
        revisions,
        delivery_type,
):
    place_id = 1
    brand_id = 1
    cooking_time = 11
    delivery_time = 21
    total_time = 41
    ml_provider = 'ml'
    order = make_order(
        order_nr='order_nr-{}'.format(1),
        status_changed_at=now_utc,
        delivery_type=delivery_type,
        shipping_type='delivery',
        order_status='confirmed',
        place_id=place_id,
        delivery_coordinates='(11.22,33.44)',
    )
    db_insert_place(make_place(id=place_id, brand_id=brand_id))
    db_insert_order(order)

    revisions.set_default(order['order_nr'], str(order['place_id']))

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            status=500, content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def mock_umlaas(request):
        return utils.make_ml_response(
            place_id,
            cooking_time=cooking_time,
            delivery_time=delivery_time,
            total_time=total_time,
            request_id=request.query['request_id'],
            provider=ml_provider,
        )

    order['ml_provider'] = ml_provider
    order['cooking_time'] = datetime.timedelta(minutes=cooking_time)
    order['delivery_time'] = datetime.timedelta(minutes=delivery_time)
    order['total_time'] = datetime.timedelta(minutes=total_time)
    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 0
    assert cargo.mock_cargo_points_eta.times_called == 0
    assert cargo.mock_cargo_performer_position.times_called == 0
    assert mock_umlaas.times_called == 1
    assert db_select_orders() == [order]
    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order['order_nr'], redis_key, order[redis_key])
    check_redis_value(
        order['order_nr'],
        'courier_arrival_duration',
        datetime.timedelta(
            seconds=utils.FALLBACKS['courier_arrival_duration'],
        ),
    )
    check_redis_value(
        order['order_nr'], 'delivery_duration', order['delivery_time'],
    )


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
)
@utils.eats_eta_fallbacks_config3()
async def test_courier_estimations_updater_no_orders_to_update(
        taxi_eats_eta,
        cargo,
        now_utc,
        make_order,
        db_insert_order,
        db_select_orders,
        redis_store,
):
    orders = (
        [
            make_order(
                status_changed_at=now_utc,
                delivery_type='native',
                shipping_type='pickup',
                order_status='confirmed',
            ),
        ]
        + [
            make_order(
                status_changed_at=now_utc,
                delivery_type='native',
                shipping_type='delivery',
                order_status=order_status,
                claim_status='new',
            )
            for order_status in ('cancelled', 'complete')
        ]
        + [
            make_order(
                status_changed_at=now_utc,
                delivery_type='native',
                shipping_type='delivery',
                order_status='confirmed',
                claim_status=claim_status,
            )
            for claim_status in (
                'delivered',
                'delivered_finish',
                'failed',
                'cancelled',
                'cancelled_with_payment',
                'cancelled_by_taxi',
                'cancelled_with_items_on_hands',
                'returned',
                'returned_finish',
            )
        ]
    )
    for i, order in enumerate(orders):
        order['order_nr'] = f'order_nr-{i}'
        order['claim_id'] = f'claim_{i}'
        order['id'] = i
        db_insert_order(order)

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    assert cargo.mock_cargo_claims_info.times_called == 0
    assert cargo.mock_cargo_points_eta.times_called == 0
    assert cargo.mock_cargo_performer_position.times_called == 0
    assert db_select_orders() == orders
    assert not redis_store.keys()
