import pytest

ENDPOINT = '/reports-api/v1/parks-rating/status'

DISTANCE = 4


@pytest.mark.now('2021-07-10T13:04:49+03:00')
@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-05'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'park': {
            'tier': 'gold',
            'rank': 49,
            'rank_change': 0,
            'points': {
                'current': 0.0,
                'maximum': 1000.0,
                'next_tier_diff': 117.35,
            },
        },
        'is_valid': True,
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_park_not_found(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-04'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'is_valid': False}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_park_has_bad_tier(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'is_valid': False}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_period_validator(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-02'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'is_valid': False}
