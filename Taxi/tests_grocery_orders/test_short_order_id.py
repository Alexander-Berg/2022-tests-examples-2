import re

import pytest

from . import consts
from . import headers
from . import models
from . import order_v2_submit_consts

GET_SEQINCREMENT = """
SELECT
    seqincrement
FROM
    pg_catalog.pg_sequence
WHERE
    seqrelid = 'orders.short_order_id_seq'::regclass;
"""

GET_SEQLASTVALUE = """
SELECT
    last_value
FROM
    orders.short_order_id_seq;
"""


@pytest.mark.now(consts.NOW)
async def test_basic(
        taxi_grocery_orders,
        pgsql,
        now,
        testpoint,
        taxi_config,
        grocery_cart,
        grocery_depots,
):
    grocery_cart.set_payment_method(
        {'type': 'card', 'id': 'test_payment_method_id'},
    )
    grocery_cart.set_depot_id(depot_id=order_v2_submit_consts.DEPOT_ID)
    grocery_depots.add_depot(
        legacy_depot_id=order_v2_submit_consts.DEPOT_ID,
        region_id=order_v2_submit_consts.REGION_ID,
    )
    grocery_cart.set_grocery_flow_version(
        order_v2_submit_consts.PROCESSING_FLOW_VERSION,
    )

    config_seq_params_name = 'GROCERY_ORDERS_SHORT_ORDER_ID_SEQ_PARAMS'
    config = taxi_config.get(config_seq_params_name)
    config['enabled'] = True
    taxi_config.set_values({config_seq_params_name: config})

    class Context:
        order_id = None
        short_order_id = None
        short_order_ids = []

    context = Context()

    cursor = pgsql['grocery_orders'].cursor()
    cursor.execute(GET_SEQINCREMENT)
    seqincrement = cursor.fetchone()[0]

    @testpoint('mock_short_order_id')
    def _mock_short_order_id(data):
        short_order_id = data['short_order_id']
        date = now.date().strftime('%y%m%d')
        assert re.fullmatch(date + '-\\d{3}-\\d{4}', short_order_id)
        assert short_order_id not in context.short_order_ids
        context.short_order_ids.append(short_order_id)
        return {}

    async def _submit(first_call=False):
        response = await taxi_grocery_orders.post(
            '/lavka/v1/orders/v2/submit',
            json=order_v2_submit_consts.SUBMIT_BODY,
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == 200

        if first_call:
            assert context.order_id is None
            context.order_id = response.json()['order_id']
        else:
            assert context.order_id == response.json()['order_id']

        order = models.Order(
            pgsql=pgsql, order_id=context.order_id, insert_in_pg=False,
        )
        order.update()

        if first_call:
            assert context.short_order_id is None
            context.short_order_id = order.short_order_id
        else:
            assert context.short_order_id == order.short_order_id

    for i in range(seqincrement):
        await _submit(first_call=(i == 0))
        assert _mock_short_order_id.times_called == i + 1
        cursor.execute(GET_SEQLASTVALUE)
        assert seqincrement == cursor.fetchone()[0]

    await _submit()
    assert _mock_short_order_id.times_called == seqincrement + 1
    cursor.execute(GET_SEQLASTVALUE)
    assert seqincrement * 2 == cursor.fetchone()[0]
