import pytest

from driver_referrals.common import fleet_parks

PARKS = {
    'p': {'id': 'p', 'locale': 'ru', 'country_id': 'rus'},
    'ppp': {'id': 'ppp', 'locale': 'ru', 'country_id': 'rus'},
    'np': {'id': 'np', 'locale': 'nor', 'country_id': 'nor'},
}


@pytest.mark.now('2019-04-25 15:00:00')
@pytest.mark.config(
    DRIVER_REFERRAL_WORDS_FOR_CODES_BY_COUNTRY={'__default__': ['ПРОМОКОД']},
)
async def test_service_save_invited_driver_with_new_code_post(
        web_app_client,
        web_context,
        mock_get_query_positions_default,
        mock_fail_to_get_nearest_zone,
        mock_fleet_parks_v1_parks_list,
):
    mock_fleet_parks_v1_parks_list(PARKS)

    child_park_id = 'p'
    child_driver_id = 'd'
    parent_park_id = 'ppp'
    parent_driver_id = 'ddd'

    response = await web_app_client.post(
        '/service/save-invited-driver-with-new-code',
        json={
            'child': {'park_id': child_park_id, 'driver_id': child_driver_id},
            'parent': {
                'park_id': parent_park_id,
                'driver_id': parent_driver_id,
            },
        },
    )
    assert response.status == 200

    content = await response.json()
    assert content == {}

    async with web_context.pg.master_pool.acquire() as conn:
        parent_data = await conn.fetch(
            """SELECT * FROM referral_profiles
            WHERE park_id = $1 AND driver_id = $2""",
            parent_park_id,
            parent_driver_id,
        )

        child_data = await conn.fetch(
            """SELECT * FROM referral_profiles
            WHERE park_id = $1 AND driver_id = $2""",
            child_park_id,
            child_driver_id,
        )

    assert len(parent_data) == 1
    assert len(child_data) == 1
    assert parent_data[0]['promocode'] == child_data[0]['invite_promocode']


@pytest.mark.parametrize(
    ('result', 'park_ids'), [[True, ['p', 'ppp']], [False, ['p', 'np']]],
)
async def test_check_parks_from_same_country(
        web_context, mock_fleet_parks_v1_parks_list, result, park_ids,
):
    mock_fleet_parks_v1_parks_list(PARKS)
    assert result == await fleet_parks.check_parks_from_same_country(
        web_context, *park_ids,
    )
