import datetime as dt

import psycopg2.tz
import pytest

TZ = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)

HANDLER = '/internal/v1/stop/category'
MOCK_NOW = dt.datetime(2021, 8, 1, 0, 3, 0, tzinfo=TZ)
REACTIVATE_AT = dt.datetime(2021, 12, 1, 0, 0, 0, tzinfo=TZ)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_rest_menu_storage',
    files=['fill_data.sql', 'fill_categories_data.sql'],
)
async def test_category_status_update(
        taxi_eats_rest_menu_storage, load_json, sql_get_category_statuses,
):
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'updated': [
            {'origin_id': 'category_origin_id_1'},
            {'origin_id': 'category_origin_id_2'},
            {'origin_id': 'category_origin_id_3'},
            {'origin_id': 'category_origin_id_4'},
            {'origin_id': 'category_origin_id_5'},
            {'origin_id': 'category_origin_id_6'},
        ],
    }

    expected_category_statuses = {
        ('category_origin_id_1', False, MOCK_NOW, REACTIVATE_AT, False),
        ('category_origin_id_2', True, None, None, False),
        ('category_origin_id_3', False, MOCK_NOW, REACTIVATE_AT, False),
        ('category_origin_id_4', True, None, None, False),
        ('category_origin_id_5', True, None, None, False),
        ('category_origin_id_6', False, MOCK_NOW, REACTIVATE_AT, False),
    }
    assert (
        sql_get_category_statuses(with_updated_at=False)
        == expected_category_statuses
    )
