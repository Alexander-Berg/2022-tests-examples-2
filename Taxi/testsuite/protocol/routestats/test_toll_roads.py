import pytest


def try_convert_to_bool(source):
    values_map = {'true': True, 'false': False}
    return values_map.get(source.lower(), source)


def dict_contains_dict(bigger, smaller):
    return smaller.items() <= bigger.items()


@pytest.fixture
def mock_request(load_json):
    def _mock(use_toll_roads):
        request = load_json('simple_request.json')

        if use_toll_roads is not None:
            request['use_toll_roads'] = use_toll_roads

        return request

    return _mock


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
                filename='toll_roads_exp3_off.json',
            ),
            id='tr_exp_off',
        ),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(filename='toll_roads_exp3_on.json'),
            id='tr_exp_on',
        ),
    ],
)
@pytest.mark.now('2020-01-21T11:30:00+0300')
class TestTollRoads:
    @pytest.mark.parametrize(
        'default_toll_roads_exp_on',
        [
            pytest.param(
                False,
                marks=pytest.mark.experiments3(
                    filename='default_toll_roads_exp3_off.json',
                ),
                id='def_tr_exp_off',
            ),
            pytest.param(
                True,
                marks=pytest.mark.experiments3(
                    filename='default_toll_roads_exp3_on.json',
                ),
                id='def_tr_exp_on',
            ),
        ],
    )
    def test_use_toll_road_flag(
            self,
            local_services,
            taxi_protocol,
            mock_request,
            request_use_toll_roads,
            toll_roads_exp_on,
            default_toll_roads_exp_on,
            pricing_data_preparer,
    ):
        pricing_data_preparer.set_fixed_price(enable=True)

        request = mock_request(request_use_toll_roads)

        response = taxi_protocol.post('3.0/routestats', request)
        assert response.status_code == 200

    @pytest.mark.experiments3(filename='default_toll_roads_exp3_on.json')
    @pytest.mark.parametrize(
        'response_use_toll_roads',
        [
            pytest.param(False, id='route_wo_tolls'),
            pytest.param(True, id='route_with_tolls'),
        ],
    )
    def test_offer_saved_to_toll_roads_service(
            self,
            local_services,
            taxi_protocol,
            mockserver,
            mock_request,
            request_use_toll_roads,
            response_use_toll_roads,
            toll_roads_exp_on,
            pricing_data_preparer,
    ):
        request = mock_request(request_use_toll_roads)
        response = taxi_protocol.post('3.0/routestats', request)
        assert response.status_code == 200

    @pytest.mark.experiments3(filename='default_toll_roads_exp3_on.json')
    @pytest.mark.parametrize(
        'response_use_toll_roads',
        [
            pytest.param(False, id='route_wo_tolls'),
            pytest.param(True, id='route_with_tolls'),
        ],
    )
    def test_return_toll_road_flag(
            self,
            local_services,
            taxi_protocol,
            mock_request,
            request_use_toll_roads,
            response_use_toll_roads,
            toll_roads_exp_on,
            pricing_data_preparer,
    ):
        pricing_data_preparer.set_fixed_price(enable=True)
        pricing_data_preparer.set_trip_information(
            100, 100, response_use_toll_roads,
        )
        request = mock_request(request_use_toll_roads)
        response = taxi_protocol.post('3.0/routestats', request)
        assert response.status_code == 200

        resp = response.json()
        if request_use_toll_roads is None or not toll_roads_exp_on:
            assert 'toll_roads' not in resp
            return

        toll_roads_resp = resp['toll_roads']
        assert toll_roads_resp['has_tolls'] == response_use_toll_roads
