import pytest


DEFAULT_VERSION = 'basic'


@pytest.fixture(name='get_version')
def get_version_(taxi_fleet_payouts):
    async def get_version(clid, at_time=None):
        return await taxi_fleet_payouts.get(
            'internal/payouts/v1/fleet-version',
            params={'clid': clid, **({'at': at_time} if at_time else {})},
        )

    return get_version


async def test_null(get_version):
    response = await get_version('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {'fleet_version': DEFAULT_VERSION}


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_default(get_version):
    response = await get_version('CLID00', '2020-01-01T23:59:59.999999+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {'fleet_version': DEFAULT_VERSION}


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_simple(get_version):
    response = await get_version('CLID00', '2020-01-02T00:00:00+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {'fleet_version': 'simple'}


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_basic(get_version):
    response = await get_version('CLID00', '2020-03-02T00:00:00+03:00')
    assert response.status_code == 200, response.text
    assert response.json() == {'fleet_version': 'basic'}


@pytest.mark.pgsql('fleet_payouts', files=['changes.sql'])
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_now(get_version):
    response = await get_version('CLID00')
    assert response.status_code == 200, response.text
    assert response.json() == {'fleet_version': 'basic'}
