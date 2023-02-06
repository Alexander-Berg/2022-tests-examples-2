import json

import pytest

from protocol.ordercommit import order_commit_common


@pytest.fixture(autouse=True)
def _mock_special_zones(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return mockserver.make_response('', 501)


def full_auction_exp(
        enabled: bool, round_rule: float, start_fake_user_price=None,
):
    value = {
        'enabled': enabled,
        'percent_steps': {
            'min_ratio': 0.6,
            'max_ratio': 1.4,
            'step_percent': 0.1,
            'decrease_steps': 3,
            'increase_steps': 3,
        },
    }
    if start_fake_user_price is not None:
        value['start_fake_user_price'] = start_fake_user_price
    return [
        pytest.mark.experiments3(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='full_auction',
            consumers=['protocol/ordercommit'],
            clauses=[
                {'title': 'a', 'value': value, 'predicate': {'type': 'true'}},
            ],
        ),
        pytest.mark.experiments3(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='order_maker_plugin_full_auction',
            consumers=['client_protocol/commit_handling'],
            clauses=[
                {'title': 'a', 'value': {}, 'predicate': {'type': 'true'}},
            ],
        ),
        pytest.mark.config(
            CURRENCY_ROUNDING_RULES={
                '__default__': {'__default__': 1},
                'RUB': {'__default__': 1, 'full_auction': round_rule},
            },
        ),
    ]


def user_auction_exp(enabled):
    return [
        pytest.mark.experiments3(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='user_auction',
            consumers=['protocol/ordercommit'],
            clauses=[
                {
                    'title': 'Econom as auction',
                    'value': {'enabled': enabled},
                    'predicate': {
                        'init': {
                            'arg_name': 'tariff_classes',
                            'set_elem_type': 'string',
                            'value': 'econom',
                        },
                        'type': 'contains',
                    },
                },
            ],
        ),
    ]


@pytest.mark.parametrize(
    'enabled,etalon',
    [
        pytest.param(False, None, marks=full_auction_exp(False, 10)),
        pytest.param(
            True,
            {
                'min_price': 200.0,
                'max_price': 450.0,
                'price_options': [230.0, 260.0, 290.0, 360.0, 390.0, 420.0],
                'passenger_price': {'base': 322, 'current': 322},
            },
            marks=full_auction_exp(True, 10),
        ),
        pytest.param(
            True,
            {
                'min_price': 200.0,
                'max_price': 400.0,
                'passenger_price': {'base': 322, 'current': 322},
                'price_options': [300.0, 400.0],
            },
            marks=full_auction_exp(True, 100),
        ),
        pytest.param(
            True,
            {
                'min_price': 322.0,
                'max_price': 322.0,
                'price_options': [],
                'passenger_price': {'base': 322, 'current': 322},
            },
            marks=full_auction_exp(True, 1000),
        ),
    ],
)
@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
def test_passenger_price(
        taxi_protocol,
        load_json,
        mockserver,
        enabled,
        db,
        etalon,
        pricing_data_preparer,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        return load_json('pdp_v2_prepare_response.json')

    request = load_json('passenger_price_request.json')
    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    proc = db.order_proc.find_one(order_id)
    driver_bid_info = proc.get('driver_bid_info')
    if enabled:
        assert commit_resp.status_code == 200
        assert mock_new_pricing.has_calls
        assert driver_bid_info == etalon
    else:
        assert driver_bid_info is None
        assert commit_resp.status_code == 406


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='full_auction',
    consumers=['protocol/ordercommit'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_pdp_price_override(taxi_protocol, load_json, mockserver, db):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        request_data = json.loads(request.get_data())
        assert request_data['calc_additional_prices']['full_auction'] is True
        return load_json('pdp_v2_prepare_response.json')

    request = load_json('passenger_price_request.json')
    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == 200
    proc = db.order_proc.find_one(order_id)
    user_pricing_data = proc['order']['pricing_data']['user']
    assert 'full_auction' in user_pricing_data['additional_prices']
    auction_price = user_pricing_data['additional_prices']['full_auction']
    assert user_pricing_data['price'] == auction_price['price']


@pytest.mark.parametrize(
    'etalon',
    [
        pytest.param(None, marks=full_auction_exp(True, 10, None)),
        pytest.param(
            {
                'min_price': 300.0,
                'max_price': 700.0,
                'price_options': [350.0, 400.0, 450.0, 550.0, 600.0, 650.0],
                'passenger_price': {'base': 500, 'current': 500},
            },
            marks=full_auction_exp(True, 10, 500),
        ),
    ],
)
@pytest.mark.config(COMMIT_PLUGINS_ENABLED=True)
def test_without_passenger_price(
        taxi_protocol,
        load_json,
        mockserver,
        etalon,
        db,
        pricing_data_preparer,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        return load_json('pdp_v2_prepare_response.json')

    request = load_json('passenger_price_request.json')
    del request['passenger_price']
    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    proc = db.order_proc.find_one(order_id)
    driver_bid_info = proc.get('driver_bid_info')
    assert commit_resp.status_code == 200
    assert driver_bid_info == etalon


@pytest.mark.parametrize(
    'enabled',
    [
        pytest.param(False, marks=user_auction_exp(False)),
        pytest.param(True, marks=user_auction_exp(True)),
    ],
)
@pytest.mark.config(USER_AUCTION_ENABLED=True)
def test_user_auction(
        taxi_protocol,
        load_json,
        mockserver,
        enabled,
        db,
        pricing_data_preparer,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_new_pricing(request):
        return load_json('pdp_v2_prepare_response.json')

    request = load_json('passenger_price_request.json')
    order_id = order_commit_common.create_draft(taxi_protocol, request)
    commit_resp = order_commit_common.commit_order(
        taxi_protocol, order_id, request,
    )
    assert commit_resp.status_code == 200

    proc = db.order_proc.find_one(order_id)
    auction = proc.get('auction')
    if enabled:
        assert auction['iteration'] == 0
        assert auction['prepared'] is False
        assert 'change_ts' in auction
    else:
        assert auction is None
