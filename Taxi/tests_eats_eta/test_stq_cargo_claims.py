import datetime

import pytest

from . import utils


@utils.eats_eta_settings_config3()
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize(
    'route_points, order_update',
    [
        [None, {}],
        [
            [
                {'point_id': 1000, 'visit_order': 1001, 'type': 'source'},
                {'point_id': 1002, 'visit_order': 1003, 'type': 'destination'},
            ],
            {
                'place_point_id': 1000,
                'place_visit_order': 1001,
                'customer_point_id': 1002,
                'customer_visit_order': 1003,
            },
        ],
    ],
)
@pytest.mark.parametrize(
    'corp_client_type',
    ['unknown', utils.EDA_CORP_CLIENT, utils.RETAIL_CORP_CLIENT],
)
async def test_stq_cargo_claims(
        stq_runner,
        make_order,
        db_insert_order,
        db_select_orders,
        now_utc,
        route_points,
        order_update,
        corp_client_type,
        cargo,
        check_redis_value,
):
    order_nr = 'order-nr'
    claim_id = 'claim-id'
    claim_status = 'pickuped'
    claim_created_at = now_utc

    fields_to_reset = {
        'place_point_id': 123,
        'place_visit_status': 'pending',
        'place_visit_order': 123,
        'place_visited_at': now_utc,
        'place_cargo_waiting_time': datetime.timedelta(seconds=123),
        'customer_point_id': 123,
        'customer_visit_status': 'pending',
        'customer_visit_order': 123,
        'customer_visited_at': now_utc,
        'customer_cargo_waiting_time': datetime.timedelta(seconds=123),
        'courier_transport_type': 'pedestrian',
        'courier_position': '(1.2,2.3)',
        'courier_position_updated_at': now_utc,
        'courier_speed': 123,
        'courier_direction': 123,
        'place_point_eta_updated_at': now_utc,
        'customer_point_eta_updated_at': now_utc,
        'batch_info': {},
        'batch_info_updated_at': now_utc,
    }

    order = make_order(
        order_nr=order_nr,
        claim_id=claim_id,
        claim_status=claim_status,
        claim_created_at=claim_created_at,
        **fields_to_reset,
    )
    db_insert_order(order)

    stq_claim_id = 'stq-claim-id'
    stq_created_at = now_utc - datetime.timedelta(seconds=123)

    await stq_runner.eats_cargo_claims.call(
        task_id=order_nr,
        kwargs={
            'eats_id': order_nr,
            'claim_id': stq_claim_id,
            'corp_client_type': corp_client_type,
            'created_at': utils.to_string(stq_created_at),
            'route_points': route_points,
        },
    )

    order['claim_id'] = stq_claim_id
    order['claim_created_at'] = stq_created_at
    order['claim_status'] = 'new'
    order['corp_client_type'] = corp_client_type
    for field in fields_to_reset:
        order[field] = None
    order.update(order_update)

    assert db_select_orders(order_nr=order_nr)[0] == order

    for redis_key in utils.ORDER_CREATED_REDIS_KEYS:
        check_redis_value(order_nr, redis_key, order[redis_key])
    check_redis_value(
        order_nr,
        'courier_arrival_duration',
        utils.FALLBACKS['courier_arrival_duration'],
    )
