import collections
import datetime

import pytest
import pytz


DEFAULT_SLOTS = {
    'daily_slots': [
        {
            'day': d,
            'slots': [
                {'start': f'{h:02}:00', 'end': f'{h+1:02}:00'}
                for h in range(8, 20)
            ],
        }
        for d in range(2)
    ],
}
EMPTY_SLOTS: dict = {'daily_slots': []}  # annotation fixes mypy error
NEXT_DAY_SLOTS = {
    'daily_slots': [
        {
            'day': 1,
            'slots': [
                {'start': f'{x:02}:00', 'end': f'{(x+1)%24:02}:00'}
                for x in range(24)
            ],
        },
    ],
}
X3_DAY_SLOTS = {
    'daily_slots': [
        {
            'day': 3,
            'slots': [
                {'start': f'{x:02}:00', 'end': f'{(x+1)%24:02}:00'}
                for x in range(24)
            ],
        },
    ],
}
MIDNIGHT_SLOT = {
    'daily_slots': [
        {'day': 0, 'slots': [{'start': f'23:30', 'end': f'00:30'}]},
    ],
}

EMPTY_BRAND = 10
NEXT_DAY_BRAND = 11
MIDNIGHT_BRAND = 12
X3_DAY_BRAND = 13

BRAND_CONFIG = collections.defaultdict(
    lambda: DEFAULT_SLOTS,
    {
        EMPTY_BRAND: EMPTY_SLOTS,
        NEXT_DAY_BRAND: NEXT_DAY_SLOTS,
        MIDNIGHT_BRAND: MIDNIGHT_SLOT,
        X3_DAY_BRAND: X3_DAY_SLOTS,
    },
)

PARTNER_DELIVERY_SLOTS_REDIS_KEY_PREFIX = 'partner_delivery_slots'


def slots_enabled():
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_slots_enabled',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
            'eats-customer-slots/orders-per-slot-cache',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'enabled': True, 'is_asap_enabled': True},
    )


def slots_disabled():
    return pytest.mark.parametrize(
        '',
        [
            pytest.param(),
            pytest.param(
                marks=[
                    pytest.mark.experiments3(
                        is_config=True,
                        name='eats_customer_slots_slots_enabled',
                        consumers=[
                            'eats-customer-slots/calculate-slots',
                            'eats-customer-slots/calculate-delivery-time',
                            'eats-customer-slots/orders-per-slot-cache',
                        ],
                        match={'predicate': {'type': 'true'}, 'enabled': True},
                        clauses=[],
                        default_value={
                            'enabled': False,
                            'is_asap_enabled': True,
                        },
                    ),
                ],
            ),
        ],
    )


def daily_slots_config():
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_daily_slots',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
            'eats-customer-slots/orders-per-slot-cache',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'empty',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'string',
                        'value': str(EMPTY_BRAND),
                    },
                },
                'value': EMPTY_SLOTS,
            },
            {
                'title': 'next_day',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'string',
                        'value': str(NEXT_DAY_BRAND),
                    },
                },
                'value': NEXT_DAY_SLOTS,
            },
            {
                'title': 'midnight',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'string',
                        'value': str(MIDNIGHT_BRAND),
                    },
                },
                'value': MIDNIGHT_SLOT,
            },
            {
                'title': '3_day',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'string',
                        'value': str(X3_DAY_BRAND),
                    },
                },
                'value': X3_DAY_SLOTS,
            },
        ],
        default_value=DEFAULT_SLOTS,
    )


def settings_config(
        estimated_delivery_timepoint_shift=0,
        asap_disable_threshold=1,
        approximate_picking_time=0,
        asap_delivery_time_max_epsilon=300,
        finish_working_interval_offset=0,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_settings',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
            'eats-customer-slots/get-picking-slots',
            'eats-customer-slots/orders-per-slot-cache',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'estimated_delivery_timepoint_shift': (
                estimated_delivery_timepoint_shift
            ),
            'asap_disable_threshold': asap_disable_threshold,
            'approximate_picking_time': approximate_picking_time,
            'asap_delivery_time_max_epsilon': asap_delivery_time_max_epsilon,
            'finish_working_interval_offset': finish_working_interval_offset,
        },
    )


DEFAULT_TEXT_FORMATS = {
    'short_text_delivery_unavailable': 'доставка недоступна',
    'short_text_slots_unavailable': 'доставка ко времени недоступна',
    'short_text_today': 'Сегодня %H:%M',
    'short_text_tomorrow': 'Завтра %H:%M',
    'short_text_x_days': '%d %B, к %H:%M',
    'full_text_delivery_unavailable': 'доставка недоступна',
    'full_text_slots_unavailable': 'доставка ко времени недоступна',
    'full_text_today': 'Сегодня к %H:%M',
    'full_text_tomorrow': 'Завтра к %H:%M',
    'full_text_x_days': '%d %B, к %H:%M',
}


FULL_SLOT_TEXT_FORMATS = {
    'short_text_delivery_unavailable': 'доставка недоступна',
    'short_text_slots_unavailable': 'доставка ко времени недоступна',
    'short_text_today': 'Сегодня с %H:%M{delim}%H:%M',
    'short_text_tomorrow': 'Завтра с %H:%M{delim}%H:%M',
    'short_text_x_days': '%d %B, с %H:%M{delim}%H:%M',
    'full_text_delivery_unavailable': 'доставка недоступна',
    'full_text_slots_unavailable': 'доставка ко времени недоступна',
    'full_text_today': 'Сегодня с %H:%M{delim}%H:%M',
    'full_text_tomorrow': 'Завтра с %H:%M{delim}%H:%M',
    'full_text_x_days': '%d %B, с %H:%M{delim}%H:%M',
    'times_delimiter': {'delimiter_key': '{delim}', 'delimiter': ' до '},
}


def text_formats_config():
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_text_formats',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'no_asap',
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'app_version',
                                    'arg_type': 'string',
                                    'value': '1.2 (345)',
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'asap',
                                    'arg_type': 'bool',
                                    'value': False,
                                },
                            },
                        ],
                    },
                },
                'value': FULL_SLOT_TEXT_FORMATS,
            },
        ],
        default_value=DEFAULT_TEXT_FORMATS,
    )


def localize(timepoint, timezone):
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)
    if isinstance(timepoint, str):
        timepoint = datetime.datetime.fromisoformat(timepoint)
    if not timepoint.tzinfo:
        timepoint = timepoint.replace(tzinfo=pytz.UTC)
    return timepoint.astimezone(timezone)


def set_timezone(timepoint, timezone='Europe/Moscow') -> datetime.datetime:
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)
    if isinstance(timepoint, str):
        timepoint = datetime.datetime.fromisoformat(timepoint)
    if timepoint.tzinfo is not None:
        timepoint = timepoint.replace(tzinfo=None)
    return timezone.localize(timepoint)


def add_days(date, days):
    return date + datetime.timedelta(days=days)


def make_datetime(date, timestring, tzinfo):
    return datetime.datetime.combine(
        date, datetime.time.fromisoformat(timestring),
    ).replace(tzinfo=tzinfo)


def total_slots_count(config):
    return sum(len(item['slots']) for item in config['daily_slots'])


def make_working_intervals(now, working_intervals):
    return [
        {
            'start': make_datetime(
                add_days(now.date(), interval['day_from']),
                interval['time_from'],
                now.tzinfo,
            ).isoformat(),
            'end': make_datetime(
                add_days(now.date(), interval['day_to']),
                interval['time_to'],
                now.tzinfo,
            ).isoformat(),
        }
        for interval in working_intervals
    ]


def eta_fallback_config(eta_seconds=1200):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_eta_fallback',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'eta_seconds': eta_seconds},
    )


def make_order_item(i: int, **kwargs):
    return dict(
        {
            'category': {'id': 'category-id'},
            'public_id': f'public_id_{i}',
            'core_id': f'{i}',
            'quantity': 1,
            'is_catch_weight': False,
        },
        **kwargs,
    )


def make_order(**kwargs):
    return dict(
        {
            'place_id': 123456,
            'brand_id': '1',
            'flow_type': 'picking_only',
            'items': [make_order_item(0)],
            'time_to_customer': 600,
            'personal_phone_id': 'abc123edf567',
        },
        **kwargs,
    )


def make_picking_slot(date_from, date_to, duration, timezone='Europe/Moscow'):
    return {
        'slot_id': 'slot_id',
        'from': set_timezone(date_from, timezone).isoformat(),
        'to': set_timezone(date_to, timezone).isoformat(),
        'duration': duration,
    }


def make_delivery_slot(
        start,
        end,
        estimated_delivery_timepoint=None,
        timezone='Europe/Moscow',
        select_by_default=None,
):
    slot = {
        'start': set_timezone(start, timezone).isoformat(),
        'end': set_timezone(end, timezone).isoformat(),
        'estimated_delivery_timepoint': (
            None
            if estimated_delivery_timepoint is None
            else set_timezone(
                estimated_delivery_timepoint, timezone,
            ).isoformat()
        ),
    }
    if select_by_default:
        slot['select_by_default'] = select_by_default
    return slot


def make_place_load(now, place_id):
    return {
        'place_id': place_id,
        'brand_id': 1,
        'country_id': 1,
        'region_id': 1,
        'time_zone': 'Europe/Moscow',
        'city': 'Москва',
        'enabled': True,
        'working_intervals': make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '00:00',
                    'day_to': 1,
                    'time_to': '00:00',
                },
                {
                    'day_from': 1,
                    'time_from': '00:00',
                    'day_to': 2,
                    'time_to': '00:00',
                },
            ],
        ),
        'estimated_waiting_time': 0,
        'free_pickers_count': 2,
        'total_pickers_count': 2,
        'is_place_closed': False,
        'is_place_overloaded': False,
    }


def make_partner_delivery_slots():
    return [
        {
            'from': '2022-06-25T11:00:00+00:00',
            'to': '2022-06-25T12:00:00+00:00',
            'expires_at': '2022-06-25T11:05:00+00:00',
        },
        {
            'from': '2022-06-25T12:00:00+00:00',
            'to': '2022-06-25T13:00:00+00:00',
            'expires_at': '2022-06-25T12:05:00+00:00',
        },
    ]


# pylint: disable=invalid-name
def make_partner_place_delivery_slots(place_origin_id: str):
    return {
        'place_origin_id': place_origin_id,
        'slots': make_partner_delivery_slots(),
    }


def generate_place_origin_id(place_id: int):
    return f'place_origin_{place_id}'


def make_catalog_storage_cache(places_count: int):
    return pytest.mark.eats_catalog_storage_cache(
        [
            {
                'id': place_id,
                'categories': [
                    {'id': place_id, 'name': f'category_{place_id}'},
                ],
                'revision_id': 1,
                'slug': f'slug_{place_id}',
                'updated_at': '2022-06-25T10:59:00+00:00',
                'name': f'name_{place_id}',
                'origin_id': generate_place_origin_id(place_id),
            }
            for place_id in range(places_count)
        ],
    )


# pylint: disable=invalid-name
def make_partner_delivery_slots_redis_location_key(
        place_id: str, latitude: float, longitude: float,
):
    return (
        f'{PARTNER_DELIVERY_SLOTS_REDIS_KEY_PREFIX}:'
        f'{place_id}:{latitude}:{longitude}'
    )


# pylint: disable=invalid-name
def make_partner_delivery_slots_redis_place_key(place_id: str):
    return f'{PARTNER_DELIVERY_SLOTS_REDIS_KEY_PREFIX}:{place_id}'


def _compare_place_capacities(db_data, expected_data):
    for key, value in expected_data.items():
        if isinstance(value, datetime.datetime):
            db_capacity = localize(db_data[key], 'UTC')
            value = localize(value, 'UTC')
            assert (
                db_capacity.isoformat() == value.isoformat()
            ), f'Key: {key}, value: {db_capacity}, expected: {value}'
        else:
            assert (
                db_data[key] == value
            ), f'Key: {key}, value: {db_data[key]}, expected: {value}'


def compare_place_interval(db_data, expected_data):
    for key, value in expected_data.items():
        if key == 'capacities':
            assert len(value) == len(db_data[key])
            db_capacities = db_data[key]
            sorted(value, key=lambda interval: interval['interval_start'])
            sorted(
                db_capacities, key=lambda interval: interval['interval_start'],
            )
            for i, db_capacity in enumerate(db_capacities):
                _compare_place_capacities(db_capacity, value[i])
        else:
            assert (
                db_data[key] == value
            ), f'Key: {key}, value: {db_data[key]}, expected: {value}'


def to_string(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


def slots_loading_feature_enabled():
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_slots_loading_enabled',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
            'eats-customer-slots/orders-per-slot-cache',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'enabled': True},
    )


def slot_capacity_coefficients(add=0, multiply=1):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_capacity_coefficients',
        consumers=['eats-customer-slots/capacity-coefficients'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'add': add, 'multiply': multiply},
    )


def slot_load_threshold(value=1):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_load_threshold',
        consumers=['eats-customer-slots/load-threshold'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'threshold': value},
    )


def replace_place_id(substituted_place_id):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_replace_place_id',
        consumers=['eats-customer-slots/replace-place-id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'place_id': substituted_place_id},
    )


def places_load_batching(our_picking_batch, shop_picking_batch):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_place_load_settings',
        consumers=['eats-customer-slots/place-load-settings'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'our_picking_batch_size': our_picking_batch,
            'shop_picking_batch_size': shop_picking_batch,
        },
    )


def cart_partner_picking_slots(items_quantity_diff_threshold, ttl=None):
    value = {
        'enabled': True,
        'items_quantity_diff_threshold': items_quantity_diff_threshold,
    }
    if ttl:
        value['ttl'] = ttl
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_cart_partner_picking_slots',
        consumers=['eats-customer-slots/cart-partner-picking-slots'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value=value,
    )


def partner_picking_slots(
        partner_slots_max_filtering_threshold=None,
        picking_slots_validation_right_offset=None,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_partner_picking_slots',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/get-picking-slots',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'partner_slots_max_filtering_threshold': (
                partner_slots_max_filtering_threshold
            ),
            'picking_slots_validation_right_offset': (
                picking_slots_validation_right_offset
            ),
        },
    )


def fallback_overall_time(
        enabled_for_checkout=False, enabled_for_catalog=False,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_fallback_overall_time',
        consumers=[
            'eats-customer-slots/calculate-slots',
            'eats-customer-slots/calculate-delivery-time',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'enabled_for_checkout': enabled_for_checkout,
            'enabled_for_catalog': enabled_for_catalog,
        },
    )


def partner_delivery_slots_config3(
        are_slots_enabled=False,
        cache_enabled=False,
        cache_strategy=None,
        slots_ttl=None,
        validate_expiration=False,
        slot_max_end_threshold=None,
):
    return pytest.mark.experiments3(
        is_config=True,
        name='eats_customer_slots_partner_delivery_slots',
        consumers=[
            'eats-customer-slots/partner-delivery-slots-cache',
            'eats-customer-slots/calculate-delivery-time',
            'eats-customer-slots/calculate-slots',
        ],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'slots_enabled': are_slots_enabled,
            'cache_settings': {
                'enabled': cache_enabled,
                'strategy': cache_strategy,
                'slots_ttl': slots_ttl,
            },
            'filtration_settings': {
                'validate_expiration': validate_expiration,
                'slot_max_end_threshold': slot_max_end_threshold,
            },
        },
    )
