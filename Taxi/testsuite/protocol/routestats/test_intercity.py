import json

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils


def _make_intercity_plugin_exp():
    return {
        'name': 'plugin_intercity',
        'consumers': [
            'routestats',
            'protocol/routestats',
            'client_protocol/routestats',
        ],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [],
        'default_value': {},
    }


def _make_intercity_exp(enabled=True, min_distance=3000, allowed_zones=None):
    if allowed_zones is None:
        allowed_zones = ['moscow']

    return {
        'name': 'intercity',
        'consumers': ['protocol/routestats'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [],
        'default_value': {
            'enabled': enabled,
            'min_ride_m_distance': min_distance,
            'allowed_zones_for_point_b': allowed_zones,
        },
    }


def mock_driver_eta_v2_eta(mockserver, load_json, is_intercity=True):
    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def _handle(request):
        data = json.loads(request.get_data())

        if is_intercity:
            assert data['is_intercity'] is True
        else:
            assert 'is_intercity' not in data
        response = load_json('driver_eta_v2.json')
        return response

    return _handle


@pytest.mark.now('2020-04-28T15:36:09+0300')
@pytest.mark.experiments3(filename='show_eta_v2_on_ui.json')
@ORDER_OFFERS_SAVE_SWITCH
@pytest.mark.experiments3(**_make_intercity_plugin_exp())
@pytest.mark.experiments3(**_make_intercity_exp())
def test_ok(
        local_services,
        taxi_protocol,
        db,
        mockserver,
        load_json,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    utils.set_default_tariff_info_and_prices(pricing_data_preparer)
    eta_v2_mock = mock_driver_eta_v2_eta(mockserver, load_json)

    pricing_data_preparer.set_fixed_price(category='econom', enable=False)
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    offer = utils.get_saved_offer(
        db, mock_order_offers, order_offers_save_enabled,
    )

    extra_data = offer['extra_data']
    assert extra_data == {'intercity': {'enabled': True}}
    assert eta_v2_mock.times_called == 1


@pytest.mark.now('2020-04-28T15:36:09+0300')
@pytest.mark.experiments3(filename='show_eta_v2_on_ui.json')
@pytest.mark.parametrize(
    'is_plugin_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(**_make_intercity_plugin_exp()),
            id='Plugin enabled',
        ),
        pytest.param(False, id='Plugin disabled'),
    ],
)
@pytest.mark.parametrize(
    'is_exp_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                **_make_intercity_exp(enabled=True),
            ),
            id='Exp enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                **_make_intercity_exp(enabled=False),
            ),
            id='Exp disabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                **_make_intercity_exp(allowed_zones=['vladivostok']),
            ),
            id='Exp wrong point b',
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                **_make_intercity_exp(min_distance=9001),
            ),
            id='Exp wrong distance',
        ),
    ],
)
@ORDER_OFFERS_SAVE_SWITCH
def test_disabled(
        local_services,
        taxi_protocol,
        db,
        mockserver,
        load_json,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
        is_plugin_enabled,
        is_exp_enabled,
):
    is_intercity = is_plugin_enabled and is_exp_enabled

    utils.set_default_tariff_info_and_prices(pricing_data_preparer)
    eta_v2_mock = mock_driver_eta_v2_eta(
        mockserver, load_json, is_intercity=is_intercity,
    )

    pricing_data_preparer.set_fixed_price(category='econom', enable=False)
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200

    offer = utils.get_saved_offer(
        db, mock_order_offers, order_offers_save_enabled,
    )

    if is_intercity:
        extra_data = offer['extra_data']
        assert extra_data == {'intercity': {'enabled': True}}
    else:
        assert 'intercity' not in offer.get('extra_data', {})
    assert eta_v2_mock.times_called == 1
