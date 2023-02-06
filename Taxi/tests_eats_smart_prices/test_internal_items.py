import pytest

from tests_eats_smart_prices import utils


@pytest.mark.now('2022-03-31T19:00:00+00:00')
@pytest.mark.parametrize(
    'updated_from',
    [
        pytest.param(None, id='full_select'),
        pytest.param('2022-03-22T00:00:00Z', id='incremental_select'),
    ],
)
async def test_internal_items(
        taxi_eats_smart_prices, eats_smart_prices_cursor, updated_from,
):

    # add recalculating settings
    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='1',
        status=utils.PlaceRecalcStatus.success,
        updated_at='2022-03-25T19:00:00+00:00',
    )
    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='2',
        status=utils.PlaceRecalcStatus.success,
        updated_at='2022-03-20T19:00:00+00:00',
    )

    # error, but returns for fetch without updated_from
    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='3',
        status=utils.PlaceRecalcStatus.error,
        updated_at='2022-03-28T19:00:00+00:00',
    )

    utils.insert_place_recalc_setting(
        eats_smart_prices_cursor,
        place_id='4',
        status=utils.PlaceRecalcStatus.success,
        updated_at='2022-03-29T19:00:00+00:00',
    )

    # add items settings
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='12',
        dynamic_part='20',
        start_time='2022-04-01T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
        experiment_tag='some_tag2',
    )  # future
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='12',
        dynamic_part='20.1',
        start_time='2022-04-01T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # future
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='12',
        dynamic_part='20.2',
        start_time='2022-04-01T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
        experiment_tag='some_tag',
    )  # future
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='12',
        dynamic_part='40',
        start_time='2022-03-29T00:00:00+00:00',
        end_time='2022-03-30T00:00:00+00:00',
        deleted_at=None,
    )  # finished, must not return
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='12',
        dynamic_part='30.1',
        start_time='2022-03-30T00:00:00+00:00',
        end_time='2022-04-01T00:00:00+00:00',
        deleted_at=None,
    )  # active
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='12',
        dynamic_part='31.2',
        start_time='2022-04-01T00:00:00+00:00',
        end_time=None,
        deleted_at='2022-03-30T00:00:00+00:00',
    )  # deleted
    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='1',
        item_id='13',
        dynamic_part='50',
        start_time='2022-04-01T03:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # future

    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='2',
        item_id='22',
        dynamic_part='50.1',
        start_time='2022-04-01T03:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # future

    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='3',
        item_id='32',
        dynamic_part='23',
        start_time='2022-03-30T00:00:00+00:00',
        end_time=None,
        deleted_at=None,
    )  # active

    utils.insert_item_setting(
        eats_smart_prices_cursor,
        place_id='4',
        item_id='42',
        dynamic_part='23',
        start_time='2022-03-29T00:00:00+00:00',
        end_time='2022-03-30T00:00:00+00:00',
        deleted_at=None,
    )  # finished, will not return

    req_body = {}
    if updated_from:
        req_body['updated_from'] = updated_from
    resp = await taxi_eats_smart_prices.post(
        '/internal/eats-smart-prices/v1/get_items_settings', json=req_body,
    )

    assert resp.status_code == 200

    data = resp.json()
    assert len(data['places']) == 1 if req_body else 3
    assert data['places'][0] == {
        'place_id': '1',
        'updated_at': '2022-03-25T19:00:00+00:00',
        'items': [
            {
                'item_id': '12',
                'values_wiht_intervals': [
                    {
                        'starts': '2022-04-01T00:00:00+00:00',
                        'value': {
                            'some_tag2': '20',
                            'default_tag': '20.1',
                            'some_tag': '20.2',
                        },
                    },
                    {
                        'value': {'default_tag': '30.1'},
                        'starts': '2022-03-30T00:00:00+00:00',
                        'ends': '2022-04-01T00:00:00+00:00',
                    },
                ],
            },
            {
                'item_id': '13',
                'values_wiht_intervals': [
                    {
                        'starts': '2022-04-01T03:00:00+00:00',
                        'value': {'default_tag': '50'},
                    },
                ],
            },
        ],
    }
    if not updated_from:
        assert data['places'][1] == {
            'place_id': '2',
            'updated_at': '2022-03-20T19:00:00+00:00',
            'items': [
                {
                    'item_id': '22',
                    'values_wiht_intervals': [
                        {
                            'starts': '2022-04-01T03:00:00+00:00',
                            'value': {'default_tag': '50.1'},
                        },
                    ],
                },
            ],
        }

        assert data['places'][2] == {
            'place_id': '3',
            'updated_at': '2022-03-28T19:00:00+00:00',
            'items': [
                {
                    'item_id': '32',
                    'values_wiht_intervals': [
                        {
                            'starts': '2022-03-30T00:00:00+00:00',
                            'value': {'default_tag': '23'},
                        },
                    ],
                },
            ],
        }
