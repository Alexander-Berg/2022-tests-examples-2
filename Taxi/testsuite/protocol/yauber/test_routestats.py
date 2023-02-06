import collections
import json

import pytest

from protocol.yauber import yauber


SurchargeParams = collections.namedtuple(
    'SurchargeParams', ['alpha', 'beta', 'surcharge'],
)


def get_surge_calculator_response(request, surge_value, surcharge=None):
    data = json.loads(request.get_data())
    tariffs = data['tariffs']
    classes = []
    for t in tariffs:
        surge_doc = {
            'antisurge': False,
            'br': [37.85917661422693, 55.723102845215166],
            'free': 6,
            'free_chain': 0,
            'name': t,
            'pins': 0,
            'radius': 3000,
            'reason': 'pins_free',
            'tl': [37.76362738577307, 55.77699315478483],
            'total': 6,
            'value': surge_value,
            'value_raw': surge_value,
            'value_smooth': surge_value,
        }
        if surcharge is not None:
            surge_doc['surcharge_alpha'] = surcharge.alpha
            surge_doc['surcharge_beta'] = surcharge.beta
            surge_doc['surcharge'] = surcharge.surcharge
        classes.append(surge_doc)

    return {
        'zone_id': 'MSK-Entusiast Ryazan',
        'classes': classes,
        'br': [37.85917661422693, 55.723102845215166],
        'tl': [37.76362738577307, 55.77699315478483],
        'total': 6,
        'free': 6,
        'free_chain': 0,
        'method': 0,
        'pins': 0,
        'radius': 3000,
    }


@pytest.fixture
def local_services(request, load_binary, load_json, mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def mock_pickup_zones(request):
        try:
            return load_json('zones.json')
        except Exception:
            return {}

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        retval_json = load_json('driver_eta.json')
        data = json.loads(request.get_data())
        to_remove = set()
        for c in retval_json['classes']:
            if c not in data['classes']:
                to_remove.add(c)
        for c in to_remove:
            retval_json['classes'].pop(c)
        assert len(retval_json['classes']) == len(data['classes'])
        return retval_json

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        assert 'tariff_zone' in json.loads(request.get_data()).get('pin')


@pytest.mark.parametrize(
    'sorted_categories,expected_categories',
    [
        (['uberblack', 'uberx'], ['uberblack', 'uberx']),
        (['uberx', 'uberblack'], ['uberx', 'uberblack']),
        (['uberblack'], ['uberblack', 'uberx']),
        ([], ['uberx', 'uberblack']),
    ],
)
def test_basic(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        config,
        sorted_categories,
        expected_categories,
):
    request = {
        'id': 'test-user',
        'extended_description': True,
        'format_currency': True,
        'payment': {'type': 'cash'},
        'position_accuracy': 0,
        'route': [[37.64, 55.73]],
        'selected_class_only': False,
        'size_hint': 240,
        'skip_estimated_waiting': False,
        'summary_version': 2,
        'supported_markup': 'tml-0.1',
        'supports_forced_surge': True,
        'supports_hideable_tariffs': True,
        'supports_no_cars_available': True,
        'surge_fake_pin': False,
        'with_title': True,
        'zone_name': 'moscow',
    }

    config.set_values(dict(UBER_PREFERRED_CATEGORIES_ORDER=sorted_categories))
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '/3.0/routestats', json=request, headers=yauber.headers,
    )
    assert response.status_code == 200
    response = response.json()
    tariffs = response['service_levels']
    tariff_names = [tariff['class'] for tariff in tariffs]
    assert tariff_names == expected_categories


@pytest.mark.parametrize(
    'coupon_code, should_apply, size_hint, bad_request',
    [
        ('couponyandex', False, 240, False),
        ('couponuber', True, 240, False),
        ('couponyandex', False, -100, True),
        ('couponyandex', False, 999999999999999999999999999999999999, True),
    ],
)
def test_coupon(
        local_services,
        taxi_protocol,
        pricing_data_preparer,
        coupon_code,
        should_apply,
        size_hint,
        bad_request,
        blackbox_service,
):
    pricing_data_preparer.set_cost(900, 1000)
    pricing_data_preparer.set_strikeout(1000)
    pricing_data_preparer.set_coupon(
        value=100,
        percent=10,
        limit=50,
        price_before_coupon=1000,
        valid=should_apply,
    )

    blackbox_service.set_token_info(
        'test_token', '123', scope='yataxi:yauber_request',
    )

    request = {
        'id': 'test-user',
        'payment': {'type': 'cash'},
        'requirements': {'coupon': coupon_code},
        'route': [[37.64, 55.73]],
        'size_hint': size_hint,
        'supports_forced_surge': True,
        'zone_name': 'moscow',
    }

    response = taxi_protocol.post(
        '/3.0/routestats',
        json=request,
        headers={
            'Authorization': 'Bearer test_token',
            'User-Agent': yauber.user_agent,
        },
    )
    if not bad_request:
        assert response.status_code == 200
        response = response.json()
        tariffs = response['service_levels']
        tariff_names = {tariff['name'] for tariff in tariffs}
        assert tariff_names == {'UberX', 'UberBlack'}
        assert 'coupon' in response
        assert response['coupon']['valid'] is should_apply
    else:
        assert response.status_code == 400
