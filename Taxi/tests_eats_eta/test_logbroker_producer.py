import datetime
import json

import pytest

from . import utils


PERIODIC_NAME = 'eta-periodic-updater'
LOGBROKER_PRODUCER_TASK = 'eta-updater-logbroker-producer'
CLEAN_LOGBROKER_PRODUCER_QUEUE = 'clean-logbroker-producer-queue'
DB_ORDERS_UPDATE_OFFSET = 5
EATS_ETA_FALLBACKS = {
    'router_type': 'car',
    'courier_speed': 10,
    'courier_arrival_duration': 1000,
    'place_cargo_waiting_time': 300,
    'delivery_duration': 1200,
    'cooking_duration': 300,
    'estimated_picking_time': 1200,
    'picking_duration': 1800,
    'picking_queue_length': 600,
    'place_waiting_duration': 300,
    'customer_waiting_duration': 300,
    'picker_waiting_time': 100,
    'picker_dispatching_time': 100,
}


@utils.eats_eta_settings_config3(
    db_orders_update_offset=DB_ORDERS_UPDATE_OFFSET,
    logbroker_producer_period=1000,
)
@utils.eats_eta_fallbacks_config3()
@pytest.mark.parametrize('send_to_logbroker', [None, False, True])
async def test_message(
        experiments3,
        now_utc,
        taxi_eats_eta,
        testpoint,
        make_order,
        db_insert_order,
        db_insert_place,
        make_place,
        send_to_logbroker,
):
    if send_to_logbroker is not None:
        experiments3.add_experiment3_from_marker(
            utils.eats_eta_send_to_logbroker_config3(send_to_logbroker), None,
        )

    await taxi_eats_eta.run_task(CLEAN_LOGBROKER_PRODUCER_QUEUE)

    total_time = datetime.timedelta(seconds=1500)
    order_created_at = now_utc - datetime.timedelta(seconds=3000)

    delivery_started_at = now_utc
    delivery_duration = datetime.timedelta(
        seconds=EATS_ETA_FALLBACKS['delivery_duration'],
    )
    delivery_at = delivery_started_at + delivery_duration
    complete_at = delivery_at + datetime.timedelta(
        seconds=EATS_ETA_FALLBACKS['customer_waiting_duration'],
    )
    order_status = 'taken'
    place_id = 1234
    brand_id = 5678
    eater_id = 'vpupkin'

    @testpoint('logbroker_publish')
    def commit(data):
        assert data['name'] == 'eta-updater-logbroker-producer'
        the_data = {
            'order_nr': 'order_nr-1',
            'order_status': order_status,
            'place_id': place_id,
            'brand_id': brand_id,
            'eater_id': eater_id,
            'courier_arrival_duration': datetime.timedelta(),
            'picking_duration': datetime.timedelta(),
            'picked_up_at': now_utc,
            'cooking_duration': None,
            'cooking_finishes_at': None,
            'delivery_duration': delivery_duration,
            'place_waiting_duration': datetime.timedelta(),
            'courier_arrival_at': now_utc,
            'delivery_starts_at': now_utc,
            'delivery_at': delivery_at,
            'complete_at': complete_at,
            'promise': total_time,
            'promise_at': order_created_at + total_time,
        }

        for key, val in json.loads(data['data']).items():
            if isinstance(val, str) and (
                    key not in {'order_nr', 'order_status', 'eater_id'}
            ):
                val = utils.parse_datetime(val)
            elif isinstance(val, int) and (
                key not in {'place_id', 'brand_id'}
            ):
                val = datetime.timedelta(seconds=val)
            assert (key, val) == (key, the_data[key])

    @testpoint('eats-eta::message-pushed')
    def after_push(data):
        pass

    @testpoint(f'{PERIODIC_NAME}::eta-updated')
    def after_update(data):
        pass

    db_insert_order(
        make_order(
            place_id=place_id,
            eater_id=eater_id,
            shipping_type='delivery',
            order_status=order_status,
            delivery_started_at=delivery_started_at,
            delivery_type='native',
            order_type='retail',
            total_time=total_time,
            created_at=order_created_at,
        ),
    )
    db_insert_place(make_place(id=place_id, brand_id=brand_id))

    await taxi_eats_eta.run_distlock_task(PERIODIC_NAME)
    await after_update.wait_call()
    assert after_push.times_called == int(bool(send_to_logbroker))
    await taxi_eats_eta.run_task(LOGBROKER_PRODUCER_TASK)
    if send_to_logbroker:
        await commit.wait_call()
