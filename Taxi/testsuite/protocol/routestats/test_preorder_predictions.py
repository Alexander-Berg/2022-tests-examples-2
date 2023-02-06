import json

import pytest

from protocol.routestats import utils


pytestmark = [
    pytest.mark.experiments3(filename='preorder_experiments3.json'),
    pytest.mark.now('2017-05-25T11:30:00+0300'),
]


@pytest.fixture
def mock_preorder(mockserver):
    @mockserver.handler('/preorder/4.0/preorder/v1/availability')
    def return_500(response):
        return mockserver.make_response(status=500)


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('is_preorder', 'predict_surge', 'offer_surge_value'),
    (
        pytest.param(
            False, True, 2, id='current_surge_ordinary_order_with_prediction',
        ),
        pytest.param(True, True, 3, id='future_surge_with_prediction'),
        pytest.param(
            False,
            False,
            2,
            id='current_surge_ordinary_order_without_prediction',
        ),
        pytest.param(True, False, 1, id='disable_surge_without_prediction'),
    ),
)
def test_surge_prediction(
        local_services,
        taxi_protocol,
        load_json,
        db,
        mockserver,
        is_preorder,
        predict_surge,
        offer_surge_value,
        pricing_data_preparer,
):
    pricing_data_preparer.set_user_surge(offer_surge_value)

    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        if predict_surge:
            return load_json('predict_surge.json')
        else:
            return {'something': 'wrong'}

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def _mock_surge_get_surge(request):
        request_data = json.loads(request.get_data())
        value = 3 if 'due' in request_data else 2
        return utils.get_surge_calculator_response(request, value)

    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    offer_id = response.json()['offer']

    offer = utils.get_offer(offer_id, db)
    for price in offer['prices']:
        assert price['sp'] == offer_surge_value


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'],
    PREORDER_CLASSES=['econom'],
    ROUTER_ORDER_BY_ZONE={
        '__default__': ['yamaps'],
        'calculator::': ['yamaps-v2'],
    },
)
@pytest.mark.config(DEFAULT_URGENCY=600)
@pytest.mark.parametrize(
    ('is_preorder', 'predict_route', 'dtm_value'),
    (
        pytest.param(False, True, None, id='current_time_no_preorder'),
        pytest.param(True, False, None, id='current_time_no_predict'),
        pytest.param(True, True, '1495701600', id='predicted_time_predict'),
    ),
)
def test_route_prediction(
        local_services,
        taxi_protocol,
        load_json,
        mockserver,
        load_binary,
        is_preorder,
        predict_route,
        dtm_value,
        pricing_data_preparer,
):
    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        if predict_route:
            return load_json('predict_route.json')
        else:
            return {'something': 'wrong'}

    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200


@pytest.mark.config(
    PREORDER_PAYMENT_METHODS=['card'], PREORDER_CLASSES=['econom'],
)
@pytest.mark.parametrize(
    ('is_preorder', 'router_name', 'new_router_called'),
    (
        pytest.param(False, 'yamaps-v2', False, id='old_router_common_order'),
        pytest.param(True, None, False, id='old_router_by_default'),
        pytest.param(True, 'yamaps', False, id='old_router_by_config'),
        pytest.param(True, 'yamaps-v2', True, id='new_router_by_config'),
    ),
)
def test_router_selection(
        local_services,
        taxi_protocol,
        load_json,
        mockserver,
        load_binary,
        is_preorder,
        router_name,
        new_router_called,
        pricing_data_preparer,
):
    @mockserver.json_handler('/v1/configs/updates')
    def experiments3_proxy(*args, **kwargs):
        experiments = load_json('predict_route.json')
        if router_name:
            predict_route_clause = experiments['configs'][0]['clauses'][0]
            predict_route_clause['value']['router_name'] = router_name
        return experiments

    request = load_json('request.json')
    if not is_preorder:
        request.pop('preorder_request_id')

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200
