import datetime

import dateutil.parser
import pytest


def parse_datetime(date_string: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(
            date_string, '%Y-%m-%dT%H:%M:%S.%f%z',
        )
    except ValueError:
        return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')


def to_string(now):
    if isinstance(now, str):
        return now
    return now.strftime('%Y-%m-%dT%H:%M:%S.%f+0000')


def enum_status(status):
    statuses = [
        'new',
        'waiting_dispatch',
        'dispatching',
        'dispatch_failed',
        'assigned',
        'picking',
        'waiting_confirmation',
        'confirmed',
        'picked_up',
        'receipt_processing',
        'receipt_rejected',
        'paid',
        'packing',
        'handing',
        'cancelled',
        'complete',
    ]
    assert status in statuses
    return statuses.index(status)


def place_disable_exp3():
    return pytest.mark.experiments3(
        name='eats_picker_dispatch_place_disable',
        match={
            'consumers': [{'name': 'eats-picker-dispatch/place-info'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={'enabled': True},
    )


def periodic_dispatcher_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_picker_dispatch_periodic_dispatcher',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-picker-dispatch/place-info'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {
                'period_seconds': 5,
                'max_picking_duration_limit': 36000,
                'max_place_idle_duration': 3600,
                'place_disable_offset_time': 3600,
                'place_enable_delay': 1800,
            },
            **kwargs,
        ),
    )


def stq_place_toggle_config3(**kwargs):
    return pytest.mark.experiments3(
        name='eats_picker_dispatch_stq_place_toggle',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-picker-dispatch/place-info'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value=dict(
            {'polling_delay': 0, 'polling_timeout': 600}, **kwargs,
        ),
    )


def make_expected_data(places, delivery_zones, working_intervals_limit=7):
    expected_data = []
    for place in places:
        if place['business'] != 'shop':
            continue
        expected_place = {
            'id': place['id'],
            'revision_id': place['revision_id'],
            'slug': place['slug'],
            'brand_id': place['brand']['id'],
            'country_id': place['country']['id'],
            'region_id': place['region']['id'],
            'time_zone': place['region']['time_zone'],
            'city': place['address']['city'],
            'working_intervals': [],
            'enabled': place['enabled'],
            'updated_at': dateutil.parser.parse(place['updated_at']),
        }
        if expected_place['id'] in delivery_zones:
            delivery_zone = delivery_zones[expected_place['id']]
            for working_interval in sorted(
                    delivery_zone['working_intervals'],
                    key=lambda interval: interval['to'],
            )[:working_intervals_limit]:
                expected_place['working_intervals'].append(
                    [
                        dateutil.parser.parse(working_interval['from']),
                        dateutil.parser.parse(working_interval['to']),
                    ],
                )
        expected_data.append(expected_place)
    return expected_data


def compare_db_with_expected_data(db_data, expected_data):
    for i, expected_item in enumerate(expected_data):
        assert i < len(db_data)
        for key, value in expected_item.items():
            assert db_data[i][key] == value


def timeshift_exp3(timeshift):
    return {
        'name': 'eats_picker_dispatch_timeshift',
        'match': {
            'consumers': [{'name': 'eats-picker-dispatch/timeshift'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [],
        'default_value': {'timeshift': timeshift},
    }


def delivery_duration_fallback(fallback):
    return {
        'name': 'eats_picker_dispatch_delivery_duration_fallback',
        'match': {
            'consumers': [
                {'name': 'eats-picker-dispatch/delivery-duration-fallback'},
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [],
        'default_value': {'delivery_duration': fallback},
    }


def use_eta_config(
        use_for_picking, use_for_delivery, use_initial_picking_duration=False,
):
    return {
        'name': 'eats_picker_dispatch_use_eta',
        'match': {
            'consumers': [{'name': 'eats-picker-dispatch/use-eta'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [],
        'default_value': {
            'use_eta_for_picking_duration': use_for_picking,
            'use_eta_for_delivery_duration': use_for_delivery,
            'use_initial_picking_duration': use_initial_picking_duration,
            'initial_picking_duration_after_picked_up': 300,
        },
    }


def picking_in_advance_settings(
        is_enabled, free_pickers_threshold, ignore_racks,
):
    return {
        'name': 'eats_picker_dispatch_picking_in_advance',
        'match': {
            'consumers': [{'name': 'eats-picker-dispatch/picking-in-advance'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [],
        'default_value': {
            'is_picking_in_advance_enabled': is_enabled,
            'free_pickers_threshold': free_pickers_threshold,
            'ignore_racks': ignore_racks,
        },
    }


OFFSET_CONSUMER = 'eats-picker-dispatch/picking-in-advance-preorders-offset'


def picking_in_advance_offset(offset=86400):
    return {
        'name': 'eats_picker_dispatch_picking_in_advance_preorders_offset',
        'match': {
            'consumers': [{'name': OFFSET_CONSUMER}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [],
        'default_value': {'offset': offset},
    }


def queue_length_config3(offset):
    return pytest.mark.experiments3(
        name='eats_picker_dispatch_queue_length',
        is_config=True,
        match={
            'consumers': [{'name': 'eats-picker-dispatch/place-info'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={'offset': offset},
    )


# pylint: disable=invalid-name
def merge_working_intervals_exp3():
    return pytest.mark.experiments3(
        name='eats_picker_dispatch_merge_working_intervals',
        match={
            'consumers': [{'name': 'eats-picker-dispatch/place-info'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        clauses=[],
        default_value={'enabled': True},
    )
