import datetime

import pytest


POSTGRES_KEY_TO_REDIS_KEY = {
    'order_type': 'order:{order_nr}:type',
    'shipping_type': 'order:{order_nr}:shipping-type',
    'delivery_type': 'order:{order_nr}:delivery-type',
    'order_status': 'order:{order_nr}:status',
    'picking_status': 'order:{order_nr}:picking:status',
    'claim_status': 'order:{order_nr}:claim:status',
    'place_visit_status': 'order:{order_nr}:place:visit-status',
    'customer_visit_status': 'order:{order_nr}:customer:visit-status',
    'courier_arrival_duration': 'order:{order_nr}:courier-arrival:duration',
    'cooking_duration': 'order:{order_nr}:cooking:duration',
    'picking_duration': 'order:{order_nr}:picking:duration',
    'place_waiting_duration': 'order:{order_nr}:place:waiting-duration',
    'delivery_duration': 'order:{order_nr}:delivery:duration',
    'courier_arrival_at': 'order:{order_nr}:courier-arrival:eta',
    'cooking_finishes_at': 'order:{order_nr}:cooking:eta',
    'picked_up_at': 'order:{order_nr}:picking:eta',
    'delivery_starts_at': 'order:{order_nr}:delivery:starts-at',
    'delivery_at': 'order:{order_nr}:delivery:eta',
    'complete_at': 'order:{order_nr}:complete:eta',
    'created_at': 'order:{order_nr}:created-at',
    'courier_arrival_started_at': (
        'order:{order_nr}:courier-arrival:started-at'
    ),
    'picking_started_at': 'order:{order_nr}:picking:started-at',
    'delivery_started_at': 'order:{order_nr}:delivery:started-at',
}

ORDER_CREATED_REDIS_KEYS = (
    'order_type',
    'shipping_type',
    'order_status',
    'created_at',
    'delivery_started_at',
)

ESTIMATION_KEYS = {
    'courier_arrival_duration',
    'cooking_duration',
    'picking_duration',
    'courier_arrival_at',
    'cooking_finishes_at',
    'picked_up_at',
    'place_waiting_duration',
    'delivery_starts_at',
    'delivery_duration',
    'delivery_at',
    'complete_at',
}

REDIS_KEYS_TTL = {
    '__default__': 60,
    'courier_arrival_duration': 100,
    'cooking_duration': 200,
    'picking_duration': 300,
    'picked_up_at': 400,
    'delivery_duration': 500,
}
MAGNIT_BRAND_IDS = [54321]
MAGNIT_CORP_CLIENT = 'magnit'
API_CARGO_TOKEN_MAGNIT = 'testsuite-api-cargo-token-magnit'

RETAIL_CORP_CLIENT = 'retail'
API_CARGO_TOKEN_RETAIL = 'testsuite-api-cargo-token-retail'

BELARUS_COUNTRY_ID = 14
BELARUS_CORP_CLIENT = 'eats_by'
API_CARGO_TOKEN_BY = 'testsuite-api-cargo-token-by'

KAZAKHSTAN_COUNTRY_ID = 5
KAZAKHSTAN_CORP_CLIENT = 'eats_kz'
API_CARGO_TOKEN_KZ = 'testsuite-api-cargo-token-kz'

EDA_CORP_CLIENT = 'eats'
API_CARGO_TOKEN_EDA = 'testsuite-api-cargo-token'

CARGO_AUTH_HEADER_TO_CORP_CLIENT = {
    f'Bearer {token}': corp_client
    for corp_client, token in (
        (MAGNIT_CORP_CLIENT, API_CARGO_TOKEN_MAGNIT),
        (RETAIL_CORP_CLIENT, API_CARGO_TOKEN_RETAIL),
        (BELARUS_CORP_CLIENT, API_CARGO_TOKEN_BY),
        (KAZAKHSTAN_CORP_CLIENT, API_CARGO_TOKEN_KZ),
        (EDA_CORP_CLIENT, API_CARGO_TOKEN_EDA),
    )
}

CORP_CLIENT_TO_API_TOKEN = {
    MAGNIT_CORP_CLIENT: API_CARGO_TOKEN_MAGNIT,
    RETAIL_CORP_CLIENT: API_CARGO_TOKEN_RETAIL,
    BELARUS_CORP_CLIENT: API_CARGO_TOKEN_BY,
    KAZAKHSTAN_CORP_CLIENT: API_CARGO_TOKEN_KZ,
    EDA_CORP_CLIENT: API_CARGO_TOKEN_EDA,
}

FALLBACKS = {
    'router_type': 'car',
    'router_mode': 'best',
    'router_jams': 'jams',
    'router_tolls': 'tolls',
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
    'minimal_remaining_duration': 60,
}


def trunc_timedelta(timedelta):
    return datetime.timedelta(seconds=int(timedelta.total_seconds()))


def picking_started(picking_status):
    return picking_status not in (
        None,
        'new',
        'dispatching',
        'waiting_dispatch',
        'dispatch_failed',
        'assigned',
        'cancelled',
    )


def make_corp_client(order_type=None, brand_id=None, country_id=None):
    if brand_id in MAGNIT_BRAND_IDS:
        return MAGNIT_CORP_CLIENT
    if order_type in ('retail', 'shop'):
        return RETAIL_CORP_CLIENT
    if country_id == BELARUS_COUNTRY_ID:
        return BELARUS_CORP_CLIENT
    if country_id == KAZAKHSTAN_COUNTRY_ID:
        return KAZAKHSTAN_CORP_CLIENT
    return EDA_CORP_CLIENT


def make_cargo_authorization_header(
        order_type=None, brand_id=None, country_id=None,
):
    corp_client = make_corp_client(
        order_type=order_type, brand_id=brand_id, country_id=country_id,
    )
    api_token = CORP_CLIENT_TO_API_TOKEN[corp_client]
    return f'Bearer {api_token}'


def make_redis_key(postgres_key, order_nr):
    if postgres_key not in POSTGRES_KEY_TO_REDIS_KEY:
        raise Exception('Invalid redis key')
    return POSTGRES_KEY_TO_REDIS_KEY[postgres_key].format(order_nr=order_nr)


def make_redis_updated_at_key(postgres_key, order_nr):
    if postgres_key not in ESTIMATION_KEYS:
        return None
    return (
        POSTGRES_KEY_TO_REDIS_KEY[postgres_key].format(order_nr=order_nr)
        + ':updated-at'
    )


# pylint: disable=invalid-name
def make_redis_estimation_source_key(postgres_key, order_nr):
    if postgres_key not in ESTIMATION_KEYS:
        return None
    return (
        POSTGRES_KEY_TO_REDIS_KEY[postgres_key].format(order_nr=order_nr)
        + ':source'
    )


def to_string(whatever):
    if whatever is None:
        return None
    if isinstance(whatever, datetime.datetime):
        return whatever.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return str(whatever)


def parse_datetime(date_string: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(
            date_string, '%Y-%m-%dT%H:%M:%S.%f%z',
        )
    except ValueError:
        return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')


def make_event(
        order_nr,
        event_time,
        order_event='created',
        created_at=None,
        order_type='native',
        delivery_type='native',
        shipping_type='delivery',
        eater_id='eater_id-1',
        eater_personal_phone_id='eater_personal_phone_id-1',
        promised_at='2022-03-03T19:30:00+03:00',
        application='web',
        place_id='1',
        payment_method='payment-method',
        meta=None,
        **kwargs,
):
    if isinstance(event_time, datetime.datetime):
        event_time = to_string(event_time)
    if created_at is None:
        created_at = event_time
    event = {
        'order_nr': order_nr,
        'order_event': order_event,
        'created_at': created_at,
        'order_type': order_type,
        'delivery_type': delivery_type,
        'shipping_type': shipping_type,
        'eater_id': eater_id,
        'eater_personal_phone_id': eater_personal_phone_id,
        'promised_at': promised_at,
        'application': application,
        'place_id': place_id,
        'payment_method': payment_method,
        f'{order_event}_at': event_time,
    }
    if meta:
        event['meta'] = meta

    for key, value in kwargs.items():
        if value is None:
            if key in event:
                del event[key]
        else:
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            if key == 'delivery_coordinates':
                if value.keys() == {'latitude', 'longitude'}:
                    value = {
                        'lat': value['latitude'],
                        'lon': value['longitude'],
                    }
            event[key] = value
    return event


def compare_db_with_expected_data(db_data, expected_data):
    for key, value in expected_data.items():
        if isinstance(db_data[key], datetime.datetime) and not isinstance(
                value, datetime.datetime,
        ):
            assert db_data[key] == parse_datetime(
                value,
            ), f'Key: {key}, value: {db_data[key]}, expected: {value}'
        else:
            assert (
                db_data[key] == value
            ), f'Key: {key}, value: {db_data[key]}, expected: {value}'


def eats_eta_settings_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_eta_settings',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-eta/settings'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {
                'db_orders_batch_size': 100,
                'db_places_batch_size': 100,
                'db_orders_update_offset': 3600,
                'db_orders_autocomplete_offset': 86400,
                'cargo_route_eta_ttl': 300,
                'cargo_courier_position_ttl': 300,
                'load_level_batch_size': 100,
                'update_status_offset': 3600,
                'places_batch_size': 100,
                'process_events': True,
                'process_event_retries': 3,
                'process_event_stq_retries': 3,
                'process_event_stq_timeout': 5,
                'stq_update_estimations_retries': 3,
                'stq_update_estimations_timeout': 5,
                'stq_update_estimations_initial_timeout': 2,
                'redis_keys_ttl': REDIS_KEYS_TTL,
                'logbroker_producer_period': 1000,
                'logbroker_producer_pop_batch_size': 100,
                'retail_info_ttl': 300,
                'bulk_handlers_tasks_count': 10,
                'batch_info_update_interval': 60,
                'segments_journal_tasks_count': 2,
            },
            **kwargs,
        ),
    )


# pylint: disable=invalid-name
def eats_eta_handlers_settings_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_eta_handlers_settings',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-eta/handlers-settings'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict({'force_first_update': False}, **kwargs),
    )


def eats_eta_corp_clients_config3():
    return pytest.mark.experiments3(
        name='eats_eta_corp_clients',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-eta/corp-clients'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'brand_id',
                        'set': list(map(str, MAGNIT_BRAND_IDS)),
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
                'value': {'corp_client': MAGNIT_CORP_CLIENT},
            },
            {
                'predicate': {
                    'init': {
                        'arg_name': 'order_type',
                        'set': ['retail', 'shop'],
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
                'value': {'corp_client': RETAIL_CORP_CLIENT},
            },
            {
                'predicate': {
                    'init': {
                        'arg_name': 'country_id',
                        'arg_type': 'string',
                        'value': str(BELARUS_COUNTRY_ID),
                    },
                    'type': 'eq',
                },
                'value': {'corp_client': BELARUS_CORP_CLIENT},
            },
            {
                'predicate': {
                    'init': {
                        'arg_name': 'country_id',
                        'arg_type': 'string',
                        'value': str(KAZAKHSTAN_COUNTRY_ID),
                    },
                    'type': 'eq',
                },
                'value': {'corp_client': KAZAKHSTAN_CORP_CLIENT},
            },
        ],
        default_value={'corp_client': EDA_CORP_CLIENT},
    )


# pylint: disable=invalid-name
def eats_eta_send_to_logbroker_config3(enabled):
    return pytest.mark.experiments3(
        name='eats_eta_send_to_logbroker',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-eta/send-to-logbroker'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={'enabled': enabled},
    )


def eats_eta_fallbacks_config3(**kwargs):
    default_value = dict(FALLBACKS, **kwargs)
    return pytest.mark.experiments3(
        name='eats_eta_fallbacks',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-eta/fallbacks'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'delivery_zone_courier_type',
                        'arg_type': 'string',
                        'value': 'pedestrian',
                    },
                    'type': 'eq',
                },
                'value': dict(default_value, router_type='pedestrian'),
            },
        ],
        default_value=default_value,
    )


def eats_eta_route_estimation_router_settings(redis_ttl):
    default_value = {
        'router_mode': 'best',
        'router_jams': 'jams',
        'router_tolls': 'no_tolls',
        'router_type': 'car',
        'redis_ttl': redis_ttl,
    }
    return pytest.mark.experiments3(
        name='eats_eta_route_estimation_router_settings',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-eta-route-estimation/router-settings'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[
            {
                'predicate': {
                    'init': {
                        'arg_name': 'courier_transport_type',
                        'arg_type': 'string',
                        'value': 'pedestrian',
                    },
                    'type': 'eq',
                },
                'value': dict(default_value, router_type='pedestrian'),
            },
        ],
        default_value=default_value,
    )


def eats_eta_route_estimation_estimation_settings(
        pickup_first=0,
        pickup_consequent=None,
        dropoff=0,
        parking=None,
        router_rate=None,
):
    return pytest.mark.experiments3(
        name='eats_eta_route_estimation_estimation_settings',
        is_config=True,
        match={
            'consumers': [
                {'name': 'eats-eta-route-estimation/estimation-settings'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={
            'collect_first': pickup_first,
            'collect_consequent': pickup_consequent or pickup_first,
            'deliver': dropoff,
            'parking': parking or {},
            'router_rate': router_rate or {'__default__': {}},
        },
    )


def update_cargo_claim(order, claim_id, claim):
    order['claim_id'] = claim_id
    order['claim_status'] = claim['status']
    order['claim_created_at'] = datetime.datetime.fromisoformat(
        claim['created_ts'],
    )
    order['place_point_id'] = claim['route_points'][0]['id']
    order['customer_point_id'] = claim['route_points'][1]['id']
    order['place_visit_order'] = claim['route_points'][0]['visit_order']
    order['customer_visit_order'] = claim['route_points'][1]['visit_order']
    order['courier_transport_type'] = claim['performer_info']['transport_type']


def update_performer_position(order, performer_position):
    order['courier_position'] = '({},{})'.format(
        performer_position['position']['lon'],
        performer_position['position']['lat'],
    )
    order['courier_position_updated_at'] = datetime.datetime.fromisoformat(
        '1970-01-01T00:00:00+00:00',
    ) + datetime.timedelta(seconds=performer_position['position']['timestamp'])
    order['courier_speed'] = performer_position['position']['speed']
    order['courier_direction'] = performer_position['position']['direction']


def update_points_eta(order, now_utc, points_eta):
    order['place_visit_status'] = points_eta['route_points'][0]['visit_status']
    order['customer_visit_status'] = points_eta['route_points'][1][
        'visit_status'
    ]
    order['place_visited_at'] = datetime.datetime.fromisoformat(
        points_eta['route_points'][0]['visited_at']['expected'],
    )
    order['place_cargo_waiting_time'] = datetime.timedelta(
        seconds=points_eta['route_points'][0]['visited_at'][
            'expected_waiting_time_sec'
        ],
    )
    order['customer_visited_at'] = datetime.datetime.fromisoformat(
        points_eta['route_points'][1]['visited_at']['expected'],
    )
    order['customer_cargo_waiting_time'] = datetime.timedelta(
        seconds=points_eta['route_points'][1]['visited_at'][
            'expected_waiting_time_sec'
        ],
    )
    order['place_point_eta_updated_at'] = now_utc
    order['customer_point_eta_updated_at'] = now_utc


def make_ml_response(
        place_id,
        request_id='request-id',
        provider='ml',
        cooking_time=20.0,
        delivery_time=25.0,
        total_time=60.0,
        min_time=10,
        max_time=120,
):
    return {
        'exp_list': [],
        'request_id': request_id,
        'provider': provider,
        'predicted_times': [
            {
                'id': place_id,
                'times': {
                    'cooking_time': cooking_time,
                    'delivery_time': delivery_time,
                    'total_time': total_time,
                    'boundaries': {'min': min_time, 'max': max_time},
                },
            },
        ],
    }


def make_remaining_duration(now_utc, order, expected_estimations, key, value):
    if key == 'courier_arrival_duration':
        if 'courier_arrival_at' in expected_estimations:
            return min(
                value,
                max(
                    expected_estimations['courier_arrival_at']['value']
                    - now_utc,
                    datetime.timedelta(),
                ),
            )
    elif key == 'cooking_duration':
        if 'cooking_finishes_at' in expected_estimations:
            return min(
                value,
                max(
                    expected_estimations['cooking_finishes_at']['value']
                    - now_utc,
                    datetime.timedelta(),
                ),
            )
    elif key == 'picking_duration':
        if picking_started(order['picking_status']):
            return max(
                order['picking_starts_at'] + value - now_utc,
                datetime.timedelta(),
            )
        return value
    elif key == 'place_waiting_duration':
        if 'courier_arrival_at' in expected_estimations:
            courier_arrival_at = expected_estimations['courier_arrival_at'][
                'value'
            ]
            if courier_arrival_at < now_utc:
                return max(
                    expected_estimations['courier_arrival_at']['value']
                    + value
                    - now_utc,
                    datetime.timedelta(),
                )
            return value
    elif key == 'delivery_duration':
        if (
                order['order_status'] == 'taken'
                and order.get('delivery_started_at', None) is not None
        ):
            return max(
                order['delivery_started_at'] + value - now_utc,
                datetime.timedelta(),
            )
        return value
    return None


def store_estimations_to_redis(
        redis_store,
        order_nr,
        redis_values,
        redis_updated_at=None,
        estimations_source=None,
):
    for key, value in redis_values.items():
        redis_key = make_redis_key(key, order_nr)
        if value is not None:
            redis_store.set(redis_key, to_string(value))
        else:
            redis_store.delete(redis_key)
        redis_value = redis_store.get(redis_key)
        try:
            if redis_value is not None:
                assert redis_value.decode() == to_string(value)
            else:
                assert value is None
        except AssertionError:
            raise Exception(order_nr, redis_key, value, redis_value)
        if redis_updated_at is not None:
            redis_updated_at_key = make_redis_updated_at_key(key, order_nr)
            if redis_updated_at_key is not None:
                redis_store.set(
                    redis_updated_at_key, to_string(redis_updated_at),
                )
                redis_value = redis_store.get(redis_updated_at_key)
                try:
                    assert (
                        redis_value is not None
                        and redis_value.decode() == to_string(redis_updated_at)
                    )
                except AssertionError:
                    raise Exception(order_nr, redis_key, value, redis_value)
        if estimations_source is not None:
            redis_estimation_source_key = make_redis_estimation_source_key(
                key, order_nr,
            )
            if redis_estimation_source_key is not None:
                redis_store.set(
                    redis_estimation_source_key, estimations_source,
                )
                redis_value = redis_store.get(redis_estimation_source_key)
                try:
                    assert (
                        redis_value is not None
                        and redis_value.decode() == estimations_source
                    )
                except AssertionError:
                    raise Exception(order_nr, redis_key, value, redis_value)


def _make_redis_key_with_suffix(data, suffix):
    return ':'.join(
        [f'{k}:{data[k]}' for k in ['user_id', 'place_id']] + [suffix],
    )


def make_redis_key_no_cart(data):
    return _make_redis_key_with_suffix(data, 'nocart')


def make_redis_key_with_cart(data):
    return _make_redis_key_with_suffix(data, 'cart')
