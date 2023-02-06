import pytest

from tests_fleet_synchronizer import common

OK_RESPONSE = {
    'mapping': [
        {'app_family': 'taximeter', 'park_id': 'p1'},
        {'app_family': 'uberdriver', 'park_id': 'uber_p1'},
        {'app_family': 'vezet', 'park_id': 'vezet_p1'},
    ],
}
EMPTY_RESPONSE: dict = {'mapping': []}
TAXIMETER_ONLY_RESPONSE = {
    'mapping': [{'app_family': 'taximeter', 'park_id': 'p1'}],
}


async def test_no_park(taxi_fleet_synchronizer):
    response = await taxi_fleet_synchronizer.get(
        'v1/mapping/park', params={'park_id': 'bad_park'},
    )
    assert response.status_code == 200
    assert response.json() == EMPTY_RESPONSE


@pytest.mark.parametrize(
    'park_id,load_cache,expected',
    [
        pytest.param('p1', True, OK_RESPONSE, id='from original'),
        pytest.param('uber_p1', True, OK_RESPONSE, id='from mapped'),
        pytest.param(
            'p1', False, TAXIMETER_ONLY_RESPONSE, id='from original nocache',
        ),
        pytest.param(
            'uber_p1',
            False,
            TAXIMETER_ONLY_RESPONSE,
            id='from mapped nocache',
        ),
    ],
)
@pytest.mark.pgsql('fleet-synchronizer-db', files=['mapping_test.sql'])
async def test_mapping_park(
        taxi_fleet_synchronizer, mongodb, park_id, load_cache, expected,
):
    if load_cache:
        common.clear_parks_mongo(mongodb)
        common.add_parks_mongo(mongodb)
        await taxi_fleet_synchronizer.invalidate_caches()

    response = await taxi_fleet_synchronizer.get(
        'v1/mapping/park', params={'park_id': park_id},
    )
    assert response.status_code == 200

    content = response.json()
    assert content == expected
