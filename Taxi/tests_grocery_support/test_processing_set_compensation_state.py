import json
import uuid

import pytest

from . import active_orders_models
from . import common
from . import experiments
from . import models

ORDER_ID = 'test_id'

COMPENSATION_EVENT_POLICY = {
    'error_after': models.ONE_MINUTE_FROM_NOW,
    'retry_interval': 10,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}

SAVE_INFORMER_EVENT_POLICY = {
    'error_after': models.THREE_MINUTES_FROM_NOW,
    'retry_interval': 30,
    'stop_retry_after': models.SIX_MINUTES_FROM_NOW,
    'retry_count': 1,
}


@pytest.mark.now(models.NOW)
@experiments.GROCERY_PROCESSING_EVENTS_POLICY
@pytest.mark.parametrize(
    'state, payload', [(True, 'test_promo'), (True, None), (False, None)],
)
@pytest.mark.parametrize(
    'compensation_source, cancel_reason',
    [('admin_cancellation', 'dispatch_failed'), ('admin_compensation', None)],
)
async def test_set_compensation_state(
        taxi_grocery_support,
        state,
        payload,
        compensation_source,
        cancel_reason,
        pgsql,
        now,
        processing,
        grocery_orders,
):
    compensation_uid = str(uuid.uuid4())
    situation_uid_1 = str(uuid.uuid4())
    situation_uid_2 = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_one_maas_id = 14

    customer = common.create_default_customer(pgsql, now)

    compensation_info = {'compensation_value': 15, 'status': 'in_progress'}
    compensation = common.create_compensation_v2(
        pgsql=pgsql,
        comp_id=compensation_uid,
        maas_id=compensation_maas_id,
        user=customer,
        situations=[situation_uid_1, situation_uid_2],
        main_situation_id=situation_one_maas_id,
        compensation_info=compensation_info,
        source=compensation_source,
        cancel_reason=cancel_reason,
        main_situation_code='some_code',
    )
    compensation.update_db()

    active_orders_models.ActiveOrder(
        pgsql, order_id=ORDER_ID, order_state='delivering',
    )
    grocery_orders.add_order(order_id=ORDER_ID)

    situation = common.create_situation_v2(
        pgsql, situation_one_maas_id, compensation_uid, situation_uid_1,
    )
    situation.update_db()

    request_json = {
        'compensation_id': compensation_uid,
        'order_id': ORDER_ID,
        'state': state,
        'payload': payload,
    }

    response = await taxi_grocery_support.post(
        '/processing/v1/set-compensation-state', json=request_json,
    )
    assert response.status_code == 200

    if state:
        compensation_info['status'] = 'success'
    else:
        compensation_info['status'] = 'error'

    if payload:
        compensation_info['generated_promo'] = payload

    compensation.raw_compensation_info = json.dumps(compensation_info)
    compensation.compare_with_db()

    if compensation_source == 'admin_cancellation':
        cancel_events = list(
            processing.events(scope='grocery', queue='processing'),
        )
        cancel_event = cancel_events[0]
        assert cancel_event.payload['order_id'] == ORDER_ID
        assert cancel_event.payload['reason'] == 'cancel_and_push'
        assert cancel_event.payload['cancel_reason_type'] == 'admin_request'
        assert cancel_event.payload['cancel_reason_message'] == cancel_reason
        assert not cancel_event.payload['need_send_notification']
        assert cancel_event.payload['compensation_id'] == compensation_uid
        assert cancel_event.payload['compensation_info'] == compensation_info
        assert (
            cancel_event.payload['compensation_type']
            == compensation.compensation_type
        )
        assert (
            cancel_event.payload['situation_code'] == situation.situation_code
        )
        assert 'event_policy' not in cancel_event.payload

    elif state:
        events = list(
            processing.events(scope='grocery', queue='compensations'),
        )
        event = events[0]
        assert event.payload['reason'] == 'compensation_notification'
        assert event.payload['order_id'] == ORDER_ID
        assert event.payload['compensation_id'] == compensation_uid
        assert event.payload['compensation_info'] == compensation_info
        assert (
            event.payload['compensation_type']
            == compensation.compensation_type
        )
        assert event.payload['situation_code'] == situation.situation_code
        assert event.payload['event_policy'] == COMPENSATION_EVENT_POLICY

        events = list(
            processing.events(
                scope='grocery', queue='processing_non_critical',
            ),
        )
        event = events[0]
        assert event.payload['reason'] == 'save_informer'
        assert event.payload['order_id'] == ORDER_ID
        assert event.payload['compensation_info'] == compensation_info
        assert (
            event.payload['compensation_type']
            == compensation.compensation_type
        )
        assert event.payload['situation_code'] == situation.situation_code
        assert not event.payload['cancel_reason']
        assert event.payload['event_policy'] == SAVE_INFORMER_EVENT_POLICY


@pytest.mark.now(models.NOW)
async def test_set_compensation_state_404(taxi_grocery_support):
    request_json = {
        'compensation_id': 'test_id',
        'order_id': ORDER_ID,
        'state': True,
    }

    response = await taxi_grocery_support.post(
        '/processing/v1/set-compensation-state', json=request_json,
    )
    assert response.status_code == 404


@pytest.mark.now(models.NOW)
async def test_set_compensation_state_409(taxi_grocery_support, pgsql, now):
    compensation_uid = str(uuid.uuid4())
    situation_uid = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_one_maas_id = 14

    customer = common.create_default_customer(pgsql, now)

    compensation_info = {'compensation_value': 15, 'status': 'success'}
    compensation = common.create_compensation_v2(
        pgsql,
        compensation_uid,
        compensation_maas_id,
        customer,
        [situation_uid],
        situation_one_maas_id,
        compensation_info,
    )
    compensation.update_db()

    request_json = {
        'compensation_id': compensation_uid,
        'order_id': ORDER_ID,
        'state': False,
    }

    response = await taxi_grocery_support.post(
        '/processing/v1/set-compensation-state', json=request_json,
    )
    assert response.status_code == 409


async def test_informer_not_sent_for_inactive_order(
        taxi_grocery_support, pgsql, now, processing,
):
    compensation_uid = str(uuid.uuid4())
    situation_uid_1 = str(uuid.uuid4())
    situation_uid_2 = str(uuid.uuid4())
    compensation_maas_id = 11
    situation_one_maas_id = 14

    customer = common.create_default_customer(pgsql, now)

    compensation_info = {'compensation_value': 15, 'status': 'in_progress'}
    compensation = common.create_compensation_v2(
        pgsql=pgsql,
        comp_id=compensation_uid,
        maas_id=compensation_maas_id,
        user=customer,
        situations=[situation_uid_1, situation_uid_2],
        main_situation_id=situation_one_maas_id,
        compensation_info=compensation_info,
        source='admin_compensation',
        main_situation_code='some_code',
    )
    compensation.update_db()

    situation = common.create_situation_v2(
        pgsql, situation_one_maas_id, compensation_uid, situation_uid_1,
    )
    situation.update_db()

    request_json = {
        'compensation_id': compensation_uid,
        'order_id': ORDER_ID,
        'state': True,
    }

    response = await taxi_grocery_support.post(
        '/processing/v1/set-compensation-state', json=request_json,
    )
    assert response.status_code == 200

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events
