import uuid

import pytest

from tests_grocery_orders_tracking import consts
from tests_grocery_orders_tracking import models


@pytest.mark.parametrize(
    'informer_type',
    [
        'long_courier_search',
        'long_courier_search_promocode',
        'long_delivery',
        'long_delivery_promocode',
        'late_order_promocode',
        'compensation',
        'custom',
    ],
)
async def test_basic(taxi_grocery_orders_tracking, pgsql, informer_type):
    order_id = str(uuid.uuid4())

    informer = models.Informer(
        pgsql=pgsql,
        order_id=order_id,
        informer_type=informer_type,
        compensation_type=consts.DEFAULT_COMPENSATION_TYPE,
        situation_code=consts.DEFAULT_SITUATION_CODE,
        cancel_reason=consts.DEFAULT_CANCEL_REASON,
        raw_compensation_info=consts.DEFAULT_COMPENSATION_INFO,
        insert_in_pg=False,
    )

    request_json = {
        'order_id': informer.order_id,
        'informer_type': informer.informer_type,
        'compensation_type': informer.compensation_type,
        'situation_code': informer.situation_code,
        'cancel_reason': informer.cancel_reason,
        'compensation_info': consts.DEFAULT_COMPENSATION_INFO,
    }

    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/save-informer', json=request_json,
    )
    assert response.status_code == 200
    informer.compare_with_db()


async def test_idempotency(taxi_grocery_orders_tracking, pgsql):
    order_id = str(uuid.uuid4())

    informer_1 = models.Informer(
        pgsql=pgsql,
        order_id=order_id,
        informer_type=consts.DEFAULT_INFORMER_TYPE,
        compensation_type='voucher',
        cancel_reason='some_cancel_reason',
        insert_in_pg=False,
    )
    informer_2 = models.Informer(
        pgsql=pgsql,
        order_id=order_id,
        informer_type=consts.DEFAULT_INFORMER_TYPE,
        compensation_type='refund',
        situation_code='test_code',
        insert_in_pg=False,
    )

    request_json = {
        'order_id': informer_1.order_id,
        'informer_type': informer_1.informer_type,
        'compensation_type': informer_1.compensation_type,
        'cancel_reason': informer_1.cancel_reason,
    }
    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/save-informer', json=request_json,
    )
    assert response.status_code == 200

    informer_1.compare_with_db()

    request_json = {
        'order_id': informer_2.order_id,
        'informer_type': informer_2.informer_type,
        'compensation_type': informer_2.compensation_type,
        'situation_code': informer_2.situation_code,
    }
    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/save-informer', json=request_json,
    )
    assert response.status_code == 200

    # Check that first informer was updated with info from second
    informer_1.situation_code = informer_2.situation_code
    informer_1.compensation_type = informer_2.compensation_type
    informer_1.compare_with_db()
