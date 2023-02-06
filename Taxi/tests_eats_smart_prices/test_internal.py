import pytest

from tests_eats_smart_prices import utils


@pytest.mark.now('2022-03-31T19:00:00+00:00')
async def test_internal_simple(
        taxi_eats_smart_prices, eats_smart_prices_cursor,
):
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='20',
        start_time='2022-04-01T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # future
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='40',
        start_time='2022-03-29T00:00:00+00:00',
        end_time='2022-03-30T00:00:00+00:00',
        deleted_at=None,
    )  # finished
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='40',
        start_time='2022-03-30T00:00:00+00:00',
        end_time='2022-04-01T00:00:00+00:00',
        deleted_at=None,
    )  # active
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='1',
        partner_id='12',
        max_modification_percent='30',
        start_time='2022-03-29T00:00:00+00:00',
        end_time=None,
        deleted_at='2022-03-28T00:00:00+00:00',
    )  # deleted

    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='2',
        partner_id='12',
        max_modification_percent='50',
        start_time='2022-04-01T03:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # future

    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='3',
        partner_id='12',
        max_modification_percent='23',
        start_time='2022-03-30T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # active
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id='4',
        partner_id='12',
        max_modification_percent='23',
        start_time='2022-03-29T00:00:00+00:00',
        end_time='2022-03-30T00:00:00+00:00',
        deleted_at=None,
    )  # finished

    resp = await taxi_eats_smart_prices.post(
        '/internal/eats-smart-prices/v1/get_places_settings',
    )

    assert resp.status_code == 200

    data = resp.json()
    assert len(data['places']) == 3
    assert data['places'][0] == {
        'place_id': '1',
        'values_wiht_intervals': [
            {'max_percent': '20', 'starts': '2022-04-01T00:00:00+00:00'},
            {
                'max_percent': '40',
                'starts': '2022-03-30T00:00:00+00:00',
                'ends': '2022-04-01T00:00:00+00:00',
            },
        ],
    }
    assert data['places'][1] == {
        'place_id': '2',
        'values_wiht_intervals': [
            {'max_percent': '50', 'starts': '2022-04-01T03:00:00+00:00'},
        ],
    }
    assert data['places'][2] == {
        'place_id': '3',
        'values_wiht_intervals': [
            {'max_percent': '23', 'starts': '2022-03-30T00:00:00+00:00'},
        ],
    }
