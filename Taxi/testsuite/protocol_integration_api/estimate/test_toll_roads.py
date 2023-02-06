import copy
import json

import pytest


USER = {
    'phone': '+79061112255',
    'personal_phone_id': 'p00000000000000000000005',
    'user_id': 'e4707fc6e79e4562b4f0af20a8e877a6',
}

BASE_REQUEST = {
    'user': USER,
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.565210, 55.734434]],
    'selected_class': 'econom',
    'sourceid': 'turboapp',
    'all_classes': False,
    'chainid': 'chainid_1',
    'agent': {'agent_user_type': 'individual', 'agent_id': 'gepard'},
}


@pytest.fixture
def mock_request():
    def _mock(use_toll_roads):
        request = copy.deepcopy(BASE_REQUEST)
        if use_toll_roads is not None:
            request['use_toll_roads'] = use_toll_roads
        return request

    return _mock


@pytest.fixture
def mock_external(mockserver, load_json):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        return {}

    @mockserver.json_handler('/driver-eta/eta')
    def mock_eta_drivers(request):
        return load_json('eta_response.json')

    @mockserver.json_handler('/toll_roads/toll-roads/v1/offer')
    def mock_offer_save(request):
        request_json = json.loads(request.get_data())
        assert 'offer_id' in request_json
        return mockserver.make_response('', status=200)


@pytest.mark.parametrize(
    'request_use_toll_roads',
    [
        pytest.param(None, id='use_tr_null'),
        pytest.param(False, id='use_tr_false'),
        pytest.param(True, id='use_tr_true'),
    ],
)
@pytest.mark.parametrize(
    'toll_roads_exp_on',
    [
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='experiments3_toll_roads_off.json',
            ),
            id='tr_exp_off',
        ),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='experiments3_toll_roads_on.json',
            ),
            id='tr_exp_on',
        ),
    ],
)
@pytest.mark.now('2020-01-21T11:30:00+0300')
class TestTollRoads:
    def test_use_toll_road_flag(
            self,
            taxi_integration,
            mock_request,
            mock_external,
            request_use_toll_roads,
            toll_roads_exp_on,
            pricing_data_preparer,
    ):
        pricing_data_preparer.set_fixed_price(enable=True)
        pricing_data_preparer.set_strikeout(100)
        pricing_data_preparer.set_meta('min_price', 99)

        request = mock_request(request_use_toll_roads)

        response = taxi_integration.post('v1/orders/estimate', json=request)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        'response_use_toll_roads',
        [
            pytest.param(False, id='route_wo_tolls'),
            pytest.param(True, id='route_with_tolls'),
        ],
    )
    def test_return_toll_road_flag(
            self,
            taxi_integration,
            mock_request,
            mock_external,
            mockserver,
            request_use_toll_roads,
            response_use_toll_roads,
            toll_roads_exp_on,
            pricing_data_preparer,
    ):
        pricing_data_preparer.set_fixed_price(enable=True)
        pricing_data_preparer.set_trip_information(
            100, 100, response_use_toll_roads,
        )
        pricing_data_preparer.set_strikeout(100)
        pricing_data_preparer.set_meta('min_price', 99)

        request = mock_request(request_use_toll_roads)
        response = taxi_integration.post('v1/orders/estimate', json=request)
        assert response.status_code == 200

        resp = response.json()
        if request_use_toll_roads is None or not toll_roads_exp_on:
            assert 'toll_roads' not in resp
            return

        toll_roads_resp = resp['toll_roads']
        assert toll_roads_resp['has_tolls'] == response_use_toll_roads
