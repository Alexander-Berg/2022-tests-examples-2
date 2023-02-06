import pytest


DEFAULT_LEVEL = ''
DEFAULT_PARK_RATING = 'gold'
UNKNOWN_PARK_RATING = 'unknown'


@pytest.fixture(name='get_level')
def get_level_(taxi_fleet_payouts, mockserver):
    async def get_level(clid, at_time=None):
        @mockserver.json_handler('/fleet-reports/v1/parks-rating/tier-by-clid')
        async def _mock_parks_rating(request):
            return mockserver.make_response(
                json={'tier': DEFAULT_PARK_RATING}, status=200,
            )

        return await taxi_fleet_payouts.get(
            'internal/payouts/v1/fleet-subscription-level',
            params={'clid': clid, **({'at': at_time} if at_time else {})},
        )

    return get_level


async def test_null(get_level):
    response = await get_level('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': DEFAULT_LEVEL,
        'park_rating': UNKNOWN_PARK_RATING,
    }


@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_default(get_level):
    response = await get_level('CLID00', '2020-01-01T23:59:59.999999+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': DEFAULT_LEVEL,
        'park_rating': UNKNOWN_PARK_RATING,
    }


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_level1(get_level):
    response = await get_level('CLID00', '2020-01-02T00:00:00+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': 'LEVEL1',
        'park_rating': UNKNOWN_PARK_RATING,
    }


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_level2(get_level):
    response = await get_level('CLID00', '2020-02-02T00:00:00+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': 'LEVEL2',
        'park_rating': UNKNOWN_PARK_RATING,
    }


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_level3(get_level):
    response = await get_level('CLID00', '2020-03-02T00:00:00+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': 'LEVEL3',
        'park_rating': UNKNOWN_PARK_RATING,
    }


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_now(get_level):
    response = await get_level('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': 'LEVEL3',
        'park_rating': UNKNOWN_PARK_RATING,
    }


@pytest.mark.config(FLEET_PAYOUTS_SUBSCRIPTION_PARK_RATING_LOAD=True)
async def test_park_rating_config_enabled(get_level):
    response = await get_level('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fleet_subscription_level': DEFAULT_LEVEL,
        'park_rating': DEFAULT_PARK_RATING,
    }
