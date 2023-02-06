import enum
from typing import Optional

import pytest


def insert_place_setting(
        eats_smart_prices_cursor,
        place_id: str,
        partner_id: Optional[str],
        max_modification_percent: str,
        start_time: str,
        end_time: Optional[str],
        deleted_at: Optional[str],
):
    eats_smart_prices_cursor.execute(
        'INSERT INTO eats_smart_prices.places_settings '
        '(place_id, partner_id, max_modification_percent, '
        'start_time, end_time, deleted_at) '
        'VALUES (%s, %s, %s, %s, %s, %s) '
        'RETURNING id',
        (
            place_id,
            partner_id,
            max_modification_percent,
            start_time,
            end_time,
            deleted_at,
        ),
    )
    return eats_smart_prices_cursor.fetchall()


class PlaceRecalcStatus(enum.Enum):
    success = 1
    error = 2
    need_recalculation = 3


def insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id: str,
        status: PlaceRecalcStatus,
        updated_at: str,
):
    eats_smart_prices_cursor.execute(
        'INSERT INTO eats_smart_prices.place_recalculation '
        '(place_id, update_status, status_time) '
        'VALUES (%s, %s, %s) '
        'RETURNING id',
        (place_id, status.name, updated_at),
    )
    return eats_smart_prices_cursor.fetchall()


def insert_item_setting(
        eats_smart_prices_cursor,
        item_id: str,
        place_id: str,
        dynamic_part: str,
        start_time: str,
        end_time: Optional[str],
        deleted_at: Optional[str],
        experiment_tag: Optional[str] = None,
):
    eats_smart_prices_cursor.execute(
        'INSERT INTO eats_smart_prices.items_settings '
        '(place_id, item_id, experiment_tag, dynamic_price_part, '
        'start_time, end_time, deleted_at) '
        'VALUES (%s, %s, %s, %s, %s, %s, %s) '
        'RETURNING id',
        (
            place_id,
            item_id,
            experiment_tag,
            dynamic_part,
            start_time,
            end_time,
            deleted_at,
        ),
    )
    return eats_smart_prices_cursor.fetchall()


EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT = [
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'Europe/Moscow',
        },
        'working_intervals': [],
        'business': 'restaurant',
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'Europe/Samara',
        },
        'working_intervals': [],
        'business': 'restaurant',
    },
    {
        'id': 3,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'Europe/Samara',
        },
        'working_intervals': [],
        'business': 'restaurant',
    },
    {
        'id': 4,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'Europe/Samara',
        },
        'working_intervals': [],
        'business': 'restaurant',
    },
]


def smart_prices_disabled_places(disabled):
    return pytest.mark.experiments3(
        name='eats_smart_prices_disabled_places',
        consumers=['eats_smart_prices_places_kwargs'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'disabled': disabled},
            },
        ],
    )
