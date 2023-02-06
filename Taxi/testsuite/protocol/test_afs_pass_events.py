import json
import shutil

import pytest

from order_core_exp_parametrize import CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
from protocol.order.order_draft_common import orderdraft
from protocol.routestats import utils
from protocol.test_order import make_order


@pytest.fixture
def local_services_base(request, load_binary, load_json, mockserver):
    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_pickup_altpoints(request):
        body = json.loads(request.get_data())
        assert body['eta_classes'] == ['econom']
        assert len(body['prices']) == 1
        assert len(body['svs']) == 1
        return load_json('altpoints.json')

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        # no 'fixed_price' experiment here, so by default - false
        assert not json.loads(request.get_data())['fixed_price_classes']
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        assert 'tariff_zone' in json.loads(request.get_data()).get('pin')


@pytest.fixture
def local_services(local_services_base, request, load_json, mockserver):
    @mockserver.json_handler('/driver-eta/eta')
    def mock(request):
        return utils.mock_driver_eta(load_json, 'driver_eta.json')(request)


@pytest.fixture(autouse=True)
def clear_exp3_cache(exp3_cache_path):
    shutil.rmtree(exp3_cache_path, True)


@pytest.fixture()
def mock_mqc_personal_phones(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_presonal(request):
        return {
            'items': [
                {
                    'id': 'c6a07d2420d9461eadc8cbe815c36c28',
                    'value': '+79023217910',
                },
            ],
        }


_NEARESTZONE_INPUT = {
    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
    'point': [37.588144, 55.733842],
}


_ZONEINFO_INPUT = {
    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
    'zone_name': 'moscow',
}


_GEOFENCES_INPUT = {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}


_ORDERDRAFT_INPUT = {
    'dont_call': False,
    'dont_sms': False,
    'id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
    'parks': [],
    'payment': {'type': 'cash'},
    'requirements': {'childchair_moscow': [3, 7]},
    'route': [
        {
            'country': 'Russian Federation',
            'description': 'Moscow, Russian Federation',
            'exact': False,
            'fullname': 'Russian Federation, Moscow, Okhotny Ryad Street',
            'geopoint': [37.61672446877377, 55.75774301935856],
            'locality': 'Moscow',
            'object_type': 'другое',
            'porchnumber': '4',
            'premisenumber': '',
            'short_text': 'Okhotny Ryad Street',
            'short_text_from': 'Okhotny Ryad Street',
            'short_text_to': 'Okhotny Ryad Street',
            'thoroughfare': 'Okhotny Ryad Street',
            'type': 'address',
            'use_geopoint': False,
        },
    ],
    'service_level': 50,
    'supported': ['code_dispatch'],
    'tips': {'type': 'flat', 'value': 15},
    'zone_name': 'moscow',
}


_ORDERCOMMIT_INPUT = {
    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
    'orderid': '8c83b49edb274ce0992f337061047399',
}


_ORDER_INPUT = {
    'dont_call': False,
    'dont_sms': False,
    'id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
    'parks': [],
    'payment': {'type': 'cash'},
    'requirements': {'childchair_moscow': [3, 7]},
    'route': [
        {
            'country': 'Russian Federation',
            'description': 'Moscow, Russian Federation',
            'exact': False,
            'fullname': 'Russian Federation, Moscow, Okhotny Ryad Street',
            'geopoint': [37.61672446877377, 55.75774301935856],
            'locality': 'Moscow',
            'object_type': 'другое',
            'porchnumber': '',
            'premisenumber': '',
            'short_text': 'Okhotny Ryad Street',
            'short_text_from': 'Okhotny Ryad Street',
            'short_text_to': 'Okhotny Ryad Street',
            'thoroughfare': 'Okhotny Ryad Street',
            'type': 'address',
            'use_geopoint': False,
        },
    ],
    'service_level': 50,
    'terminal': {
        'id': 'terminal_id',
        'key': 'ca5949f4b7d84a11984178657ed20443',
        'phone': '+79008007060',
    },
    'tips': {'type': 'percent', 'value': 5},
    'zone_name': 'moscow',
}


_ROUTESTATS_INPUT = {
    'id': 'b300bda7d41b4bae8d58dfa93221ef16',
    'city': 'Москва',
}


_LAUNCH_INPUT = {'id': 'b300bda7d41b4bae8d58dfa93221ef16'}


def _make_experiment(name, consumer, match=None, clauses=None):
    _DEFAULT_MATH = {'predicate': {'type': 'true'}, 'enabled': True}

    return {
        'name': name,
        'consumers': [consumer],
        'match': match if match is not None else _DEFAULT_MATH,
        'clauses': clauses if clauses is not None else [],
        'default_value': {},
    }


def _make_expected(handler):
    if handler == 'orderdraft':
        return {
            'device_id': 'c02c705e98588f724ca046ac59cafece65501e36',
            'phone_id': '59246c5b6195542e9b084206',
            'user_id': 'f4eb6aaa29ad4a6eb53f8a7620793561',
        }
    if handler in ['ordercommit', 'launch', 'zoneinfo', 'routestats']:
        return {
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'phone_id': '5714f45e98956f06baaae3d4',
            'device_id': 'E4249906-EA48-4269-A8D1-D230572845ED',
        }
    return {'user_id': 'b300bda7d41b4bae8d58dfa93221ef16'}


def _make_kwargs(handler, input):
    return {
        'url': '/3.0/{}'.format(handler),
        'mock_url': '/antifraud/v1/events/protocol/{}'.format(handler),
        'input': input,
        'mock_expected': _make_expected(handler),
    }


@pytest.mark.experiments3(
    **_make_experiment(
        'afs_notify_handler_call_nearest_zone', 'protocol/nearest_zone',
    ),
)
def test_afs_pass_events_nearestzone_on(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        **_make_kwargs('nearestzone', _NEARESTZONE_INPUT),
    )


def test_afs_pass_events_nearestzone_off(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        **_make_kwargs('nearestzone', _NEARESTZONE_INPUT),
    )


# @pytest.mark.filldb(
#     localization_client_messages='zoneinfo', localization_tariff='zoneinfo',
# )
# def test_afs_pass_events_zoneinfo_on(
#         taxi_protocol, mockserver, experiments3, pricing_data_preparer,
# ):
#     experiments3.add_experiment(
#         match={'predicate': {'type': 'true'}, 'enabled': True},
#         name='afs_notify_handler_call_zone_info',
#         consumers=['protocol/zoneinfo'],
#         clauses=[
#             {
#                 'predicate': {
#                     'type': 'eq',
#                     'init': {
#                         'arg_type': 'string',
#                         'arg_name': 'user_id',
#                         'value': 'b300bda7d41b4bae8d58dfa93221ef16',
#                     },
#                 },
#                 # TODO(d4rk): add `value` field
#             },
#         ],
#     )
#     _test_base(
#         taxi_protocol,
#         mockserver,
#         pricing_data_preparer,
#         True,
#         **_make_kwargs('zoneinfo', _ZONEINFO_INPUT),
#     )


@pytest.mark.filldb(
    localization_client_messages='zoneinfo', localization_tariff='zoneinfo',
)
def test_afs_pass_events_zoneinfo_off(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        **_make_kwargs('zoneinfo', _ZONEINFO_INPUT),
    )


@pytest.mark.experiments3(
    **_make_experiment(
        'afs_notify_handler_call_geofences', 'protocol/geofences',
    ),
)
def test_afs_pass_events_geofences_on(
        taxi_protocol, mockserver, testpoint, pricing_data_preparer,
):
    @testpoint('afs_geofence_most_recent_update')
    def afs_geofence_most_recent_update(_):
        return {'clear': True}

    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        **_make_kwargs('geofences', _GEOFENCES_INPUT),
    )


def test_afs_pass_events_geofences_off(
        taxi_protocol, mockserver, testpoint, pricing_data_preparer,
):
    @testpoint('afs_geofence_most_recent_update')
    def afs_geofence_most_recent_update(_):
        return {'clear': True}

    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        **_make_kwargs('geofences', _GEOFENCES_INPUT),
    )


@pytest.mark.filldb(users='orderdraft', user_phones='orderdraft')
@pytest.mark.experiments3(
    **_make_experiment(
        'afs_notify_handler_call_order_draft', 'protocol/createdraft',
    ),
)
@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_afs_pass_events_orderdraft_on(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        pricing_data_preparer,
        mock_mqc_personal_phones,
        load_json,
):
    def exec_order_draft_request():
        return orderdraft(
            taxi_protocol,
            mockserver,
            load_json,
            _ORDERDRAFT_INPUT,
            'order1',
            bearer='test_token',
        )

    pricing_data_preparer.set_locale('ru')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        request_func=exec_order_draft_request,
        **_make_kwargs('orderdraft', _ORDERDRAFT_INPUT),
    )
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.config(
    ADMIN_MQC_USER_PHONES=['79034431132', '+79023217910', '79023217960'],
)
@pytest.mark.filldb(users='orderdraft', user_phones='orderdraft')
@CHECK_CREATE_DRAFT_IN_ORDER_CORE_EXP
def test_afs_pass_events_orderdraft_off(
        taxi_protocol,
        mockserver,
        mock_order_core,
        order_core_exp_enabled,
        pricing_data_preparer,
        mock_mqc_personal_phones,
        load_json,
):
    def exec_order_draft_request():
        return orderdraft(
            taxi_protocol,
            mockserver,
            load_json,
            _ORDERDRAFT_INPUT,
            'order1',
            bearer='test_token',
        )

    pricing_data_preparer.set_locale('ru')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        request_func=exec_order_draft_request,
        **_make_kwargs('orderdraft', _ORDERDRAFT_INPUT),
    )
    assert mock_order_core.create_draft_times_called == order_core_exp_enabled


@pytest.mark.experiments3(
    **_make_experiment(
        'afs_notify_handler_call_order_commit', 'protocol/ordercommit',
    ),
)
@pytest.mark.filldb(order_proc='ordercommit')
def test_afs_pass_events_ordercommit_on(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        **_make_kwargs('ordercommit', _ORDERCOMMIT_INPUT),
    )


@pytest.mark.filldb(order_proc='ordercommit')
def test_afs_pass_events_ordercommit_off(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        **_make_kwargs('ordercommit', _ORDERCOMMIT_INPUT),
    )


@pytest.mark.experiments3(
    **_make_experiment('afs_notify_handler_call_order', 'protocol/order'),
)
@pytest.mark.filldb(users='order', user_phones='order')
def test_afs_pass_events_order_on(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return mockserver.make_response('', 501)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    def make_request():
        return make_order(
            taxi_protocol, _ORDER_INPUT, x_real_ip='my-ip-address',
        )

    def check_expected(data):
        assert data['device_id'] == 'c02c705e98588f724ca046ac59cafece65501e36'
        assert data['user_id'] == 'f4eb6aaa29ad4a6eb53f8a7620793561'

    pricing_data_preparer.set_locale('en')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        request_func=make_request,
        check_expected_func=check_expected,
        **_make_kwargs('order', _ORDER_INPUT),
    )


@pytest.mark.filldb(users='order', user_phones='order')
def test_afs_pass_events_order_off(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        return mockserver.make_response('', 501)

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def mock_communications_sendsms(request):
        return mockserver.make_response('', 200)

    def make_request():
        return make_order(
            taxi_protocol, _ORDER_INPUT, x_real_ip='my-ip-address',
        )

    pricing_data_preparer.set_locale('en')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        request_func=make_request,
        **_make_kwargs('order', _ORDER_INPUT),
    )


@pytest.mark.experiments3(
    **_make_experiment(
        'afs_notify_handler_call_launch', 'client_protocol/launch',
    ),
)
def test_afs_pass_events_launch_on(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        **_make_kwargs('launch', _LAUNCH_INPUT),
    )


def test_afs_pass_events_launch_off(
        taxi_protocol, mockserver, pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        **_make_kwargs('launch', _LAUNCH_INPUT),
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(
    **_make_experiment(
        'afs_notify_handler_call_routestats', 'protocol/routestats',
    ),
)
def test_afs_pass_events_routestats_on(
        taxi_protocol, mockserver, local_services, pricing_data_preparer,
):
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        True,
        **_make_kwargs('routestats', _ROUTESTATS_INPUT),
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_afs_pass_events_routestats_off(
        taxi_protocol, mockserver, local_services, pricing_data_preparer,
):
    _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        False,
        **_make_kwargs('routestats', _ROUTESTATS_INPUT),
    )


def _test_base(
        taxi_protocol,
        mockserver,
        pricing_data_preparer,
        expected,
        url,
        mock_url,
        input,
        mock_expected,
        request_func=None,
        check_expected_func=None,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return utils.get_surge_calculator_response(request, 2)

    @mockserver.json_handler(mock_url)
    def mock_afs(mock_request):
        if check_expected_func is None:
            if expected:
                assert json.loads(mock_request.get_data()) == mock_expected
            else:
                assert False
        else:
            check_expected_func(json.loads(mock_request.get_data()))
        return {}

    if request_func is None:
        response = taxi_protocol.post(url, input)
        assert response.status_code == 200
    else:
        request_func()

    if expected:
        assert mock_afs.wait_call()
    else:
        assert not mock_afs.has_calls
