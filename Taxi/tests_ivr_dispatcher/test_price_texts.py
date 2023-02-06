import pytest

from tests_ivr_dispatcher import utils


# Octonode action results
OCTONODE_INITIAL_RESULT_OK = {
    'caller_number': utils.DEFAULT_USER_PHONE,  # call_from
    'called_number': utils.DEFAULT_TAXI_PHONE,  # call_to
    'status': 'ok',
    'call_guid': 'some_guid',
    'origin_called_number': utils.DEFAULT_TAXI_PHONE,
    'type': 'initial',
}
OCTONODE_ANSWER_RESULT_OK = {'status': 'ok', 'type': 'answer'}

# Dispatcher possible answers
DISPATCHER_ANSWER_REPLY = {
    'type': 'answer',
    'params': {'start_recording': True},
}

DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY = {
    'params': {
        'engine': 'ya_speechkit',
        'language': 'ru-RU',
        'speed': 0.9,
        'text': (
            'Здравствуйте. В 22:40 приедет синий Audi A8. '
            'Номер A666MP77.Цена поездки 75 рублей.'
        ),  # be carefulr, real text is different from this in tests
        'voice': 'alena',
    },
    'type': 'speak',
}


# Scenarios
SIMPLE_CALL_SCENARIO: list = [
    (OCTONODE_INITIAL_RESULT_OK, DISPATCHER_ANSWER_REPLY, []),
    (OCTONODE_ANSWER_RESULT_OK, DISPATCHER_ON_ASSIGNED_EXACT_SPEAK_REPLY, []),
]


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_changed_dst(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # changed destination
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['changes'] = load_json('order_core_changes.json')
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'Цена поездки от ' in response_json['params']['text']
    assert '50' in response_json['params']['text']  # min price


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_fixed_price_simple(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # has fixed price simple
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'Цена поездки' in response_json['params']['text']
    assert 'Цена поездки от' not in response_json['params']['text']
    assert 'Цена поездки ориентировочно' not in response_json['params']['text']
    assert '75' in response_json['params']['text']  # current price


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
    IVR_DISPATCHER_PRICE_TEXT_ENABLER=False,
)
async def test_price_disabled(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # has fixed price simple
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'Цена поездки' not in response_json['params']['text']


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_not_fixed_predicted(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # not fixed by reason, Predicted Price
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order'].pop('fixed_price')
        response['fields']['order']['pricing_data'][
            'fixed_price_discard_reason'
        ] = 'LONG_TRIP'  # in config.json
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'Цена поездки ориентировочно' in response_json['params']['text']
    assert '75' in response_json['params']['text']  # current price


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_not_fixed_minimal(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # not fixed by reason, minimal Price
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order'].pop('fixed_price')
        response['fields']['order']['pricing_data'][
            'fixed_price_discard_reason'
        ] = 'SOME_UNNECESSARY_REASON'
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'Цена поездки от' in response_json['params']['text']
    assert '50' in response_json['params']['text']  # min price


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_no_frac_currency(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # russian without frac
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'рублей' in response_json['params']['text']
    assert 'копеек' not in response_json['params']['text']


@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        utils.DEFAULT_TAXI_PHONE: {
            'application': utils.DEFAULT_APPLICATION,
            'city_name': 'Неизвестен',
            'geo_zone_coords': {'lon': 0.0, 'lat': 0.0},
            'metaqueue': utils.DEFAULT_METAQUEUE,
        },
    },
    CALLCENTER_STATS_ROUTING_PHONE_MAP={
        '__default__': {'metaqueue': utils.DEFAULT_METAQUEUE},
        utils.DEFAULT_TAXI_PHONE: {'metaqueue': utils.DEFAULT_METAQUEUE},
    },
    IVR_DISPATCHER_INBOUND_NUMBERS_WORKER_MAP={
        'private_numbers': {},
        'public_numbers': {
            utils.DEFAULT_TAXI_PHONE: {
                'name': 'order_status_worker_2_0',
                'type': 'native_worker',
            },
        },
    },
)
async def test_with_frac_currency(
        taxi_ivr_dispatcher,
        mongodb,
        mock_user_api,
        mock_personal,
        mock_octonode,
        mock_driver_profiles,
        mock_fleet_vehicles,
        mock_cars_catalog,
        mock_fleet_parks,
        mock_tariffs,
        mock_parks,
        mockserver,
        load_json,
        mock_int_authproxy,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/search')
    def _mock_search(request, *args, **kwargs):
        assert request.json['user']['user_id'] == utils.DEFAULT_USER_ID
        assert 'User-Agent' in request.headers
        assert request.headers.get('User-Agent') == utils.DEFAULT_APPLICATION
        return {
            'orders': [
                {
                    'orderid': '9b0ef3c5398b3e07b59f03110563479d',
                    'status': 'driving',
                },
            ],
        }

    response_json = {}  # dict, where last answer will lay down
    # blr with frac
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core(request):
        response = load_json('order_core_default_response.json')
        response['fields']['order'].pop('fixed_price')
        response['fields']['order']['pricing_data']['currency'] = {
            'name': 'BYN',
            'symbol': ' Br',
        }
        return response

    for action, _, _ in SIMPLE_CALL_SCENARIO:
        request = {'session_id': utils.DEFAULT_SESSION_ID, 'action': action}
        response = await taxi_ivr_dispatcher.post('/action', json=request)
        assert response.status == 200, response.text
        response_json = response.json()
    assert 'рублей' in response_json['params']['text']
    assert '1 копейка' in response_json['params']['text']
