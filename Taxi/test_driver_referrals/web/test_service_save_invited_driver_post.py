import pytest

from test_driver_referrals import conftest

PARKS = {
    'p': {'id': 'p', 'locale': 'nor', 'country_id': 'nor'},
    'p1': {'id': 'p1', 'locale': 'nor', 'country_id': 'nor'},
    'np': {'id': 'np', 'locale': 'nor', 'country_id': 'rus'},
}

PROMOCODE = 'ПРОМОКОД1'
WRONG_PROMOCODE = 'НЕСУЩЕСТВУЮЩИЙ_ПРОМОКОД'
PARK_ID = 'p'
OTHER_COUNTRY_PARK_ID = 'np'
DRIVER_ID = 'd'


async def test_service_save_invited_driver_post(
        web_app_client,
        web_context,
        mock_fleet_parks_v1_parks_list,
        mock_driver_profiles_drivers_profiles,
):
    mock_fleet_parks_v1_parks_list(PARKS)
    mock_driver_profiles_drivers_profiles(eats_keys={})

    async with conftest.TablesDiffCounts(
            web_context, {'referral_profiles': 1, 'notifications': 1},
    ):
        response = await web_app_client.post(
            '/service/save-invited-driver',
            json={
                'park_id': PARK_ID,
                'driver_id': DRIVER_ID,
                'promocode': PROMOCODE,
            },
        )
        assert response.status == 200

    content = await response.json()
    assert content == {}

    async with web_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT * FROM referral_profiles
            WHERE park_id = $1 AND driver_id = $2""",
            PARK_ID,
            DRIVER_ID,
        )

    assert len(rows) == 1
    assert rows[0]['invite_promocode'] == PROMOCODE

    async with conftest.TablesDiffCounts(
            web_context, {'referral_profiles': 0, 'notifications': 0},
    ):
        retry_response = await web_app_client.post(
            '/service/save-invited-driver',
            json={
                'park_id': PARK_ID,
                'driver_id': DRIVER_ID,
                'promocode': PROMOCODE,
            },
        )
        assert retry_response.status == 200


@pytest.mark.parametrize(
    'park_id,driver_id,promocode',
    [
        (PARK_ID, DRIVER_ID, WRONG_PROMOCODE),
        (OTHER_COUNTRY_PARK_ID, DRIVER_ID, PROMOCODE),
    ],
)
async def test_service_save_invited_driver_post_invalid_request(
        web_app_client,
        web_context,
        mock_fleet_parks_v1_parks_list,
        mock_driver_profiles_drivers_profiles,
        park_id,
        driver_id,
        promocode,
):
    mock_fleet_parks_v1_parks_list(PARKS)
    mock_driver_profiles_drivers_profiles(eats_keys={})

    async with conftest.TablesDiffCounts(
            web_context, {'referral_profiles': 0, 'notifications': 0},
    ):
        response = await web_app_client.post(
            '/service/save-invited-driver',
            json={
                'park_id': PARK_ID,
                'driver_id': DRIVER_ID,
                'promocode': WRONG_PROMOCODE,
            },
        )
        assert response.status == 400
