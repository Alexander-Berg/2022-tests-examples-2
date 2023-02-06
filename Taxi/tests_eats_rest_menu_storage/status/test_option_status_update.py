import datetime as dt

import pytest
import pytz

HANDLER = '/internal/v1/stop/item/option'
MOCK_NOW = dt.datetime(2021, 8, 1, 0, 0, 0, tzinfo=pytz.UTC)
REACTIVATE_AT = dt.datetime(2021, 12, 1, 0, 0, 0, tzinfo=pytz.UTC)


@pytest.mark.now(MOCK_NOW.isoformat())
@pytest.mark.pgsql(
    'eats_rest_menu_storage', files=['fill_data.sql', 'fill_options_data.sql'],
)
async def test_option_status_update(
        taxi_eats_rest_menu_storage, load_json, sql_get_option_statuses,
):
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'updated': [
            {'origin_id': 'option_origin_id_1'},
            {'origin_id': 'option_origin_id_2'},
            {'origin_id': 'option_origin_id_3'},
            {'origin_id': 'option_origin_id_4'},
            {'origin_id': 'option_origin_id_5'},
            {'origin_id': 'option_origin_id_6'},
        ],
    }

    expected_option_statuses = {
        (1, 'option_origin_id_1', False, MOCK_NOW, REACTIVATE_AT, False),
        (2, 'option_origin_id_2', True, None, None, False),
        (3, 'option_origin_id_3', False, MOCK_NOW, REACTIVATE_AT, False),
        (4, 'option_origin_id_4', True, None, None, False),
        (5, 'option_origin_id_5', True, None, None, False),
        (6, 'option_origin_id_6', False, MOCK_NOW, REACTIVATE_AT, False),
    }
    assert (
        sql_get_option_statuses(with_updated_at=False)
        == expected_option_statuses
    )
