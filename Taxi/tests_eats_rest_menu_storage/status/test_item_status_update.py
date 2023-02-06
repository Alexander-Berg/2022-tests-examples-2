import datetime as dt

import psycopg2.tz
import pytest

TZ = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)

HANDLER = '/internal/v1/stop/item'
MOCK_NOW = dt.datetime(2021, 8, 1, 0, 0, 0, tzinfo=TZ)
REACTIVATE_AT = dt.datetime(2021, 12, 1, 3, 0, 0, tzinfo=TZ)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_rest_menu_storage', files=['fill_data.sql', 'fill_item_data.sql'],
)
async def test_item_status_update(
        taxi_eats_rest_menu_storage, load_json, sql_get_item_statuses,
):
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'updated': [
            {'origin_id': 'item_origin_id_1'},
            {'origin_id': 'item_origin_id_2'},
            {'origin_id': 'item_origin_id_3'},
            {'origin_id': 'item_origin_id_4'},
            {'origin_id': 'item_origin_id_5'},
            {'origin_id': 'item_origin_id_6'},
        ],
    }

    expected_item_statuses = {
        ('item_origin_id_1', False, MOCK_NOW, REACTIVATE_AT, False),
        ('item_origin_id_2', True, None, None, False),
        ('item_origin_id_3', False, MOCK_NOW, REACTIVATE_AT, False),
        ('item_origin_id_4', True, None, None, False),
        ('item_origin_id_5', True, None, None, False),
        ('item_origin_id_6', False, MOCK_NOW, REACTIVATE_AT, False),
    }
    assert (
        sql_get_item_statuses(with_updated_at=False) == expected_item_statuses
    )
