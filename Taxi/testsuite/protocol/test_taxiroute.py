from datetime import datetime
import json

import pytest
import pytz

from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE


@pytest.mark.translations(
    client_messages={
        'taxiroute.shade_car_tooltip_title': {'ru': 'Положение неточное'},
        'taxiroute.shade_car_tooltip_text_driving': {
            'ru': (
                'Машина уже в пути — её положение на карте '
                'может быть неточным из-за плохого GPS-сигнала в районе.'
            ),
        },
        'taxiroute.shade_car_tooltip_text_waiting': {
            'ru': (
                'Машина рядом с вами, но её положение на карте неточное:'
                ' в районе плохой GPS-сигнал. Уточнить место встречи '
                'с водителем можно по телефону или в чате.'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'handler,req_extra,expected_code',
    [
        ('internal/taxiroute', None, 200),
        ('internal/taxiroute', {'authkey': 'ilyasov_v2'}, 200),
        ('internal/taxiroute', {'authkey': 'whatever'}, 200),
        ('3.0/taxiroutetest', {'authkey': 'ilyasov_v2'}, 200),
        ('3.0/taxiroutetest', None, 400),
        ('3.0/taxiroutetest', {'authkey': ''}, 401),
        ('3.0/taxiroutetest', {'authkey': 'whatever'}, 401),
        ('3.0/taxiroute', None, 400),
        # no such user
        ('3.0/taxiroute', {'id': '82f2709b33ceea13cac308f644de0fc2'}, 401),
        # different phone_id
        ('3.0/taxiroute', {'id': 'a300bda7d41b4bae8d58dfa93221ef16'}, 401),
        # crossdevice
        ('3.0/taxiroute', {'id': 'deadbeefdeadbeefdeadbeef00000075'}, 200),
        # order owner
        ('3.0/taxiroute', {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}, 200),
        # disable requests to /internal/taxiroute and /3.0/taxiroutetest
        # enable request to /3.0/taxiroute
        pytest.param(
            '3.0/taxiroute',
            {'id': 'deadbeefdeadbeefdeadbeef00000075'},
            200,
            marks=pytest.mark.config(
                TAXIROUTE_INTERNAL_REQUEST_ENABLED=False,
                TAXIROUTE_TEST_REQUEST_ENABLED=False,
            ),
        ),
        # disable requests to /internal/taxiroute
        pytest.param(
            'internal/taxiroute',
            None,
            400,
            marks=pytest.mark.config(TAXIROUTE_INTERNAL_REQUEST_ENABLED=False),
        ),
        # disable requests to /3.0/taxiroutetest
        pytest.param(
            '3.0/taxiroutetest',
            {'authkey': 'ilyasov_v2'},
            400,
            marks=pytest.mark.config(TAXIROUTE_TEST_REQUEST_ENABLED=False),
        ),
        # order not found
        pytest.param(
            '3.0/taxiroute',
            {
                'id': 'deadbeefdeadbeefdeadbeef00000075',
                'orderid': 'aaaabeefdeadbeefdeadbeef00000075',
            },
            404,
            marks=pytest.mark.config(
                TAXIROUTE_INTERNAL_REQUEST_ENABLED=False,
                TAXIROUTE_TEST_REQUEST_ENABLED=False,
            ),
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@pytest.mark.config(
    USE_DRIVER_TRACKSTORY_PERCENT=100, TAXIROUTE_FALLBACK_TO_RAW_TRACK=False,
)
@pytest.mark.now('2017-01-01T12:00:00+0000')
def test_general(
        taxi_protocol,
        mockserver,
        load_json,
        mock_order_core,
        handler,
        req_extra,
        expected_code,
        order_core_switch_on,
):
    shorttrack = load_json('shorttrack.json')

    @mockserver.json_handler('/driver_trackstory/shorttrack')
    def mock_shorttrack(request):
        data = json.loads(request.get_data())
        assert data['types'] == ['full-geometry', 'adjusted']
        return {'adjusted': shorttrack['positions'][::-1]}

    request = {
        'build_route': False,
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'orderid': '8c83b49edb274ce0992f337061047375',
        'timestamp': '2017-01-01T00:00:00.000Z',
        'use_history': True,
    }
    if req_extra is not None:
        request.update(req_extra)

    response = taxi_protocol.post(handler, request)

    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        assert resp['order_id'] == '8c83b49edb274ce0992f337061047375'
        assert resp['track'] == [_convert(i) for i in shorttrack['positions']]
        assert resp['driver'] == _convert(shorttrack['positions'][0])
        assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.translations(
    client_messages={
        'taxiroute.shade_car_tooltip_title': {'ru': 'Положение неточное'},
        'taxiroute.shade_car_tooltip_text_driving': {
            'ru': (
                'Машина уже в пути — её положение на карте '
                'может быть неточным из-за плохого GPS-сигнала в районе.'
            ),
        },
        'taxiroute.shade_car_tooltip_text_waiting': {
            'ru': (
                'Машина рядом с вами, но её положение на карте неточное:'
                ' в районе плохой GPS-сигнал. Уточнить место встречи '
                'с водителем можно по телефону или в чате.'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'handler,req_extra,expected_code',
    [
        ('internal/taxiroute', None, 200),
        ('internal/taxiroute', {'authkey': 'ilyasov_v2'}, 200),
        ('internal/taxiroute', {'authkey': 'whatever'}, 200),
        ('3.0/taxiroutetest', {'authkey': 'ilyasov_v2'}, 200),
        ('3.0/taxiroutetest', None, 400),
        ('3.0/taxiroutetest', {'authkey': ''}, 401),
        ('3.0/taxiroutetest', {'authkey': 'whatever'}, 401),
        ('3.0/taxiroute', None, 400),
        # no such user
        ('3.0/taxiroute', {'id': '82f2709b33ceea13cac308f644de0fc2'}, 401),
        # different phone_id
        ('3.0/taxiroute', {'id': 'a300bda7d41b4bae8d58dfa93221ef16'}, 401),
        # crossdevice
        ('3.0/taxiroute', {'id': 'deadbeefdeadbeefdeadbeef00000075'}, 200),
        # order owner
        ('3.0/taxiroute', {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}, 200),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@pytest.mark.config(
    USE_DRIVER_TRACKSTORY_PERCENT=100, TAXIROUTE_FALLBACK_TO_RAW_TRACK=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_taxiroute_use_full_geometry_positions',
    consumers=['protocol/taxiroute'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'title': 'Условие segmentation',
            'value': {'enabled': True, 'max_count': 15, 'max_age': 60},
        },
    ],
)
@pytest.mark.now('2017-01-01T12:00:00+0000')
def test_full_geometry_general(
        taxi_protocol,
        mockserver,
        load_json,
        mock_order_core,
        handler,
        req_extra,
        expected_code,
        order_core_switch_on,
):
    shorttrack = load_json('shorttrack.json')

    @mockserver.json_handler('/driver_trackstory/shorttrack')
    def mock_shorttrack(request):
        data = json.loads(request.get_data())
        assert data['types'] == ['raw', 'adjusted', 'full-geometry']
        return {
            'full_geometry': shorttrack['positions'][::-1],
            'adjusted': [shorttrack['positions'][-1]],
            'raw': [shorttrack['positions'][-1]],
        }

    request = {
        'build_route': False,
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'orderid': '8c83b49edb274ce0992f337061047375',
        'timestamp': '2017-01-01T00:00:00.000Z',
        'use_history': True,
    }
    if req_extra is not None:
        request.update(req_extra)

    response = taxi_protocol.post(handler, request)

    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        assert resp['order_id'] == '8c83b49edb274ce0992f337061047375'
        assert resp['track'] == [_convert(i) for i in shorttrack['positions']]
        assert resp['driver'] == _convert(shorttrack['positions'][0])
        assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.translations(
    client_messages={
        'taxiroute.shade_car_tooltip_title': {'ru': 'Положение неточное'},
        'taxiroute.shade_car_tooltip_text_driving': {
            'ru': (
                'Машина уже в пути — её положение на карте '
                'может быть неточным из-за плохого GPS-сигнала в районе.'
            ),
        },
        'taxiroute.shade_car_tooltip_text_waiting': {
            'ru': (
                'Машина рядом с вами, но её положение на карте неточное:'
                ' в районе плохой GPS-сигнал. Уточнить место встречи '
                'с водителем можно по телефону или в чате.'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'handler,req_extra,expected_code',
    [
        ('internal/taxiroute', None, 200),
        ('internal/taxiroute', {'authkey': 'ilyasov_v2'}, 200),
        ('internal/taxiroute', {'authkey': 'whatever'}, 200),
        ('3.0/taxiroutetest', {'authkey': 'ilyasov_v2'}, 200),
        ('3.0/taxiroutetest', None, 400),
        ('3.0/taxiroutetest', {'authkey': ''}, 401),
        ('3.0/taxiroutetest', {'authkey': 'whatever'}, 401),
        ('3.0/taxiroute', None, 400),
        # no such user
        ('3.0/taxiroute', {'id': '82f2709b33ceea13cac308f644de0fc2'}, 401),
        # different phone_id
        ('3.0/taxiroute', {'id': 'a300bda7d41b4bae8d58dfa93221ef16'}, 401),
        # crossdevice
        ('3.0/taxiroute', {'id': 'deadbeefdeadbeefdeadbeef00000075'}, 200),
        # order owner
        ('3.0/taxiroute', {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}, 200),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@pytest.mark.config(
    USE_DRIVER_TRACKSTORY_PERCENT=100, TAXIROUTE_FALLBACK_TO_RAW_TRACK=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_taxiroute_use_full_geometry_positions',
    consumers=['protocol/taxiroute'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'title': 'Условие segmentation',
            'value': {'enabled': True, 'max_count': 15, 'max_age': 60},
        },
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='protocol_taxiroute_use_fallback_in_full_geometry',
    consumers=['protocol/taxiroute'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'title': 'Условие segmentation',
            'value': {'fallback_threshold': 5},
        },
    ],
)
@pytest.mark.now('2017-01-01T12:00:00+0000')
def test_full_geometry_fallback_on_adjusted(
        taxi_protocol,
        mockserver,
        load_json,
        mock_order_core,
        handler,
        req_extra,
        expected_code,
        order_core_switch_on,
):
    shorttrack = load_json('shorttrack.json')

    @mockserver.json_handler('/driver_trackstory/shorttrack')
    def mock_shorttrack(request):
        data = json.loads(request.get_data())
        assert data['types'] == ['raw', 'adjusted', 'full-geometry']
        return {
            'full_geometry': shorttrack['positions'][:-1][::-1],
            'adjusted': shorttrack['positions'][::-1],
            'raw': [shorttrack['positions'][-1]],
        }

    request = {
        'build_route': False,
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'orderid': '8c83b49edb274ce0992f337061047375',
        'timestamp': '2017-01-01T00:00:00.000Z',
        'use_history': True,
    }
    if req_extra is not None:
        request.update(req_extra)

    response = taxi_protocol.post(handler, request)

    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        assert resp['order_id'] == '8c83b49edb274ce0992f337061047375'
        assert resp['track'] == [_convert(i) for i in shorttrack['positions']]
        assert resp['driver'] == _convert(shorttrack['positions'][0])
        assert mock_order_core.get_fields_times_called == order_core_switch_on


def _convert(p):
    tz = pytz.timezone('UTC')
    isoformat = '%Y-%m-%dT%H:%M:%S.%f%z'
    timestamp = datetime.fromtimestamp(p['timestamp'], tz).strftime(isoformat)
    return {
        'timestamp': timestamp,
        'direction': p['direction'],
        'speed': p['speed'],
        'coordinates': [p['lon'], p['lat']],
    }


@pytest.mark.config(SHADE_CAR_ON=True)
@pytest.mark.translations(
    client_messages={
        'taxiroute.shade_car_tooltip_title': {'ru': 'Положение неточное'},
        'taxiroute.shade_car_tooltip_text_driving': {
            'ru': (
                'Машина уже в пути — её положение на карте '
                'может быть неточным из-за плохого GPS-сигнала в районе.'
            ),
        },
        'taxiroute.shade_car_tooltip_text_waiting': {
            'ru': (
                'Машина рядом с вами, но её положение на карте неточное:'
                ' в районе плохой GPS-сигнал. Уточнить место встречи '
                'с водителем можно по телефону или в чате.'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'handler,req_extra,expected_code',
    [
        ('internal/taxiroute', None, 200),
        ('internal/taxiroute', {'authkey': 'ilyasov_v2'}, 200),
        ('internal/taxiroute', {'authkey': 'whatever'}, 200),
        ('3.0/taxiroutetest', {'authkey': 'ilyasov_v2'}, 200),
        ('3.0/taxiroutetest', None, 400),
        ('3.0/taxiroutetest', {'authkey': ''}, 401),
        ('3.0/taxiroutetest', {'authkey': 'whatever'}, 401),
        ('3.0/taxiroute', None, 400),
        ('3.0/taxiroute', {'id': '82f2709b33ceea13cac308f644de0fc2'}, 401),
        ('3.0/taxiroute', {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}, 200),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
@pytest.mark.now('2017-01-01T12:00:00+0000')
def test_bad_gps(
        taxi_protocol,
        mockserver,
        load_json,
        mock_order_core,
        handler,
        req_extra,
        expected_code,
        order_core_switch_on,
):
    shorttrack = load_json('shorttrack_bad_gps.json')

    @mockserver.json_handler('/tracker/shorttrack')
    def mock_shorttrack(request):
        return shorttrack

    request = {
        'build_route': False,
        'coordinates': [39.83839685690159, 57.63110673158881],
        'float_timestamp': True,
        'orderid': '8c83b49edb274ce0992f337061047375',
        'timestamp': '2017-01-01T00:00:00.000Z',
        'use_history': True,
    }
    if req_extra is not None:
        request.update(req_extra)

    response = taxi_protocol.post(handler, request)

    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        assert resp['order_id'] == '8c83b49edb274ce0992f337061047375'
        assert resp['track'] == [_convert(i) for i in shorttrack['positions']]
        assert resp['driver']['shade_car']
        assert resp['driver']['accuracy_radius'] == 500
        assert mock_order_core.get_fields_times_called == order_core_switch_on
