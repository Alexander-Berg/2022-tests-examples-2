# pylint: disable=import-error
import copy
import datetime

from geobus_tools.channels import timelefts


DRIVER_ETA_HANDLER = '/driver-eta/driver-eta/v2/eta'


async def publish_etas(
        redis_store,
        redis_eta_payload_processed,
        now,
        num_etas,
        time_left=302,
        distance_left=50000,
        delta_time=0,
        position=None,
        driver_id='00000000000000000000000000000000'
        '_11111111111111111111111111111111',
        order_ids=('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',),
        cache_is_empty=True,
        service_id='processing:driving',
):
    return await publish_timelefts_only(
        redis_store,
        redis_eta_payload_processed,
        now,
        num_etas,
        time_left,
        distance_left,
        delta_time,
        position,
        driver_id,
        order_ids,
        cache_is_empty,
        service_id,
    )


async def publish_timelefts_only(
        redis_store,
        redis_eta_payload_processed,
        now,
        num_etas,
        time_left=302,
        distance_left=50000,
        delta_time=0,
        position=None,
        driver_id='00000000000000000000000000000000'
        '_11111111111111111111111111111111',
        order_ids=('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',),
        cache_is_empty=True,
        service_id='processing:driving',
):
    if position is None:
        position = [37.65, 55.73]
    timestamp = copy.deepcopy(now).replace(
        tzinfo=datetime.timezone.utc,
    ) - datetime.timedelta(seconds=delta_time)
    cache = {}
    for order_id in order_ids:
        etas = {
            'payload': [
                {
                    'contractor_id': driver_id,
                    'route_id': order_id,
                    'timestamp': timestamp,
                    'adjusted_pos': position,
                    'tracking_type': 'RouteTracking',
                    'adjusted_segment_index': 0,
                    'update_timestamp': timestamp,
                    'timeleft_data': [
                        {
                            'destination_position': [37.66, 55.71],
                            'time_left': time_left,
                            'distance_left': distance_left,
                            'service_id': service_id,
                            'order_id': order_id,
                        },
                    ],
                }
                for i in range(num_etas)
            ],
        }
        redis_store.publish(
            'channel:drw:timelefts', timelefts.serialize_message(etas, now),
        )
        cache.update((await redis_eta_payload_processed.wait_call())['cache'])

    if cache_is_empty:
        assert len(cache) == len(order_ids)

    return cache


def get_all_order_ids_in_database(pgsql):
    cursor = pgsql['eta_autoreorder'].cursor()
    cursor.execute('SELECT * from eta_autoreorder.orders')
    return sorted([row[0] for row in cursor])


def get_sorted_testpoint_calls(testpoint_name, testpoint_key, sort_key=None):
    return sorted(
        [
            testpoint_name.next_call()[testpoint_key]
            for _ in range(testpoint_name.times_called)
        ],
        key=lambda x: x[sort_key] if sort_key else x,
    )


async def initialize_geobus_from_database(
        pgsql, redis_store, redis_eta_payload_processed, now,
):
    cursor = pgsql['eta_autoreorder'].cursor()
    cursor.execute('SELECT * from eta_autoreorder.orders')
    for row in cursor:
        await publish_etas(
            redis_store,
            redis_eta_payload_processed,
            now,
            1,
            driver_id=str(row[5]),
            time_left=row[7].seconds,
            distance_left=row[8],
            order_ids=[str(row[0])],
            cache_is_empty=False,
        )
