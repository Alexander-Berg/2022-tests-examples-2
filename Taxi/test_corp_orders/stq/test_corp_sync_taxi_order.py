# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import copy
import uuid

from taxi.stq import async_worker_ng

from corp_orders.stq import corp_sync_taxi_order


ORDER_ID = '6fa63ed97114326a97ca669c1be74506'
NOT_CORP_ORDER_ID = '394f07ff9e0e49aa82a15de17b0e8fe9'

ORDER_DOC = {
    '_id': ORDER_ID,
    'payment_tech': {
        'without_vat_to_pay': {'ride': 3480000, 'tips': 0},
        'user_to_pay': {'ride': 4176000, 'tips': 0},
    },
}

TASK_META_INFO = async_worker_ng.TaskInfo(
    id=uuid.uuid4().hex,
    exec_tries=0,
    reschedule_counter=0,
    queue='corp_sync_taxi_order',
)


async def test_sync(stq3_context, db):
    await corp_sync_taxi_order.task(stq3_context, TASK_META_INFO, ORDER_DOC)
    corp_order = await db.corp_orders.find_one({'_id': ORDER_ID})
    assert corp_order['without_vat_to_pay'] == {'ride': 3480000}
    assert corp_order['user_to_pay'] == {'ride': 4176000}


async def test_sync_not_dbcorp_order(stq3_context, db):
    order_doc = copy.deepcopy(ORDER_DOC)
    order_doc['_id'] = NOT_CORP_ORDER_ID

    await corp_sync_taxi_order.task(stq3_context, TASK_META_INFO, order_doc)

    corp_order = await db.corp_orders.find_one({'_id': NOT_CORP_ORDER_ID})
    assert corp_order is None
