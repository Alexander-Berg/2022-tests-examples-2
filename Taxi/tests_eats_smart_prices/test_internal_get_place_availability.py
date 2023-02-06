import pytest


from tests_eats_smart_prices import utils


@pytest.mark.now('2022-03-31T19:00:00+00:00')
@pytest.mark.parametrize(
    'db_place_id,place_id,start_time,end_time,deleted_at,expected',
    [
        ('1', '2', '2022-03-30T19:00:00+00:00', None, None, False),
        ('2', '2', '2022-03-30T19:00:00+00:00', None, None, True),
        (
            '1',
            '2',
            '2022-03-30T19:00:00+00:00',
            '2022-01-01T00:00:00+00:00',
            None,
            False,
        ),
        (
            '1',
            '2',
            '2022-03-30T19:00:00+00:00',
            None,
            '2022-01-01T00:00:00+00:00',
            False,
        ),
        (
            '2',
            '2',
            '2022-03-30T19:00:00+00:00',
            '2022-01-01T00:00:00+00:00',
            None,
            False,
        ),
        (
            '2',
            '2',
            '2022-03-30T19:00:00+00:00',
            '2022-04-01T00:00:00+00:00',
            '2022-04-01T00:00:00+00:00',
            False,
        ),
        (
            '2',
            '2',
            '2022-03-30T19:00:00+00:00',
            '2022-03-31T15:00:00+00:00',
            None,
            False,
        ),
        (
            '2',
            '2',
            '2022-03-30T19:00:00+00:00',
            '2022-03-31T20:00:00+00:00',
            None,
            True,
        ),
    ],
)
async def test_get_place_settings(
        taxi_eats_smart_prices,
        eats_smart_prices_cursor,
        db_place_id,
        place_id,
        start_time,
        end_time,
        deleted_at,
        expected,
):
    utils.insert_place_setting(
        eats_smart_prices_cursor,
        place_id=db_place_id,
        partner_id='12',
        max_modification_percent='20',
        start_time=start_time,
        end_time=end_time,
        deleted_at=deleted_at,
    )

    response = await taxi_eats_smart_prices.get(
        '/internal/eats-smart-prices/v1/get_place_availability',
        params={'place_id': place_id},
    )
    assert response.status_code == 200
    assert response.json()['enabled'] == expected
