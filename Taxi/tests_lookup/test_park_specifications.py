import pytest

from tests_lookup import lookup_params


@pytest.mark.parametrize(
    'fleet_parks_error,park_found,park_specs',
    [
        pytest.param(True, False, None, id='fleet-parks 500'),
        pytest.param(False, False, None, id='park not found'),
        pytest.param(False, True, None, id='park specs are missing'),
        pytest.param(False, True, [], id='park specs are empty'),
        pytest.param(
            False, True, ['signalq', 'taxi'], id='park specs are present',
        ),
    ],
)
async def test_park_specifications(
        acquire_candidate,
        mockserver,
        fleet_parks_error,
        park_found,
        park_specs,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        if fleet_parks_error:
            return mockserver.make_response('', 500)
        if not park_found:
            return {'parks': []}
        park = {
            'id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'login': 'park_login',
            'name': 'park_name',
            'is_active': True,
            'city_id': 'city_id',
            'locale': 'locale',
            'is_billing_enabled': True,
            'is_franchising_enabled': True,
            'country_id': 'country_id',
            'demo_mode': False,
            'geodata': {'lat': 40, 'lon': 13, 'zoom': 9},
        }
        if park_specs is not None:
            park['specifications'] = park_specs
        return {'parks': [park]}

    request = lookup_params.create_params(generation=1, version=1, wave=1)
    candidate = await acquire_candidate(request)
    if fleet_parks_error:
        assert candidate.get('park') is None
    else:
        assert candidate['park']['specifications'] == (park_specs or [])
