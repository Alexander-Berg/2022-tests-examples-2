import json

import pytest

from tests_lookup import airport_config
from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DRIVER_CAR_NUMBER = 'test_car_X'
UNIQUE_DRIVER_ID = 'unique_driver_id_X'
DRIVER_LICENSE_ID = 'license-1234'
LICENSE_NUMBER_PREFIX = 'number-'


@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES=airport_config.make_airport_config(),
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_direct_request(acquire_candidate, mockserver, load_json):
    @mockserver.json_handler('/metadata-storage-json/v2/metadata/retrieve')
    def _metadata_for_order(request):
        return load_json('metadata_response.json')

    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        driver = json.loads(request.get_data())['driver_ids'][0]
        return {
            'drivers': [
                {
                    'uuid': driver['uuid'],
                    'dbid': driver['dbid'],
                    'position': [0, 0],
                    'classes': ['econom', 'business'],
                    'car_model': 'Audi A6',
                },
            ],
        }

    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        # some sample answer from testing
        result = mock_candidates.make_candidates()
        result_driver = result['candidates'][2]
        point = order['order']['request']['source']['geopoint']
        result_driver['position'] = [point[0] + 0.05, point[1] + 0.05]
        result_driver['unique_driver_id'] = UNIQUE_DRIVER_ID
        result_driver['car_number'] = DRIVER_CAR_NUMBER
        result_driver['license_id'] = DRIVER_LICENSE_ID
        return result

    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def ordering(request):
        # do minimal sort by time
        body = json.loads(request.get_data())['request']
        search_dict = body['search']
        assert (
            search_dict['order_id'],
            search_dict['order']['nearest_zone'],
        ) == (order['_id'], 'moscow')
        candidates = [
            {
                'id': candidate['id'],
                'score': float(candidate['route_info']['time']),
            }
            for candidate in body['candidates']
        ]
        ordered_candidates = {
            'candidates': sorted(
                candidates, key=lambda candidate: candidate['score'],
            ),
            'source': 'scoring',
        }
        return ordered_candidates

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        body = json.loads(request.get_data())
        if (body.get('unique_driver_id'), body.get('car_id')) == (
                UNIQUE_DRIVER_ID,
                DRIVER_CAR_NUMBER,
        ):
            return {'freezed': True}
        return {'freezed': False, 'reason': 'invalid udid'}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        assert False, 'should not be called'

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _personal_license_retrieve(request):
        body = json.loads(request.get_data())
        license_id = body['id']
        license_number = LICENSE_NUMBER_PREFIX + license_id
        return {'id': license_id, 'value': license_number}

    order = lookup_params.create_params()
    order['order']['request']['source']['geopoint'] = [5, 5]

    candidate = await acquire_candidate(order)
    assert candidate['car_number'] == DRIVER_CAR_NUMBER

    await order_search.wait_call(timeout=1)
    await ordering.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)
