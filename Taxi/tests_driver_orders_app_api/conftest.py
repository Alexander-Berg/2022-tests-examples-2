# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

from driver_orders_app_api_plugins import *  # noqa: F403 F401
import pytest

from .plugins import taximeter_version_helpers as tvh


TEST_APIKEY = 'MyAwesomeAPIKEY'

BAD_REQUEST_RESPONSE = {'error': {'text': 'Bad Request'}}
FORBIDDEN_RESPONSE = {'error': {'text': 'Forbidden'}}
NOT_FOUND_RESPONSE = {'error': {'text': 'Not Found'}}
WRONGWAY_RESPONSE = {'error': {'text': 'wrongway'}}
BAD_POSITION_RESPONSE = {'error': {'text': 'bad_position'}}
GONE_RESPONSE = {'error': {'text': 'Gone'}}

RESPONSE500 = {'code': '500', 'message': 'InternalError'}
REQUESTCONFIRM_OK = {
    'phone_options': [
        {
            'call_dialog_message_prefix': 'Телефон пассажира',
            'label': 'Телефон пассажира.',
            'type': 'main',
        },
    ],
}

RESPONSES_SEEN = {
    'driver_not_found': {
        'status': 404,
        'response': json.dumps(NOT_FOUND_RESPONSE),
    },
    'driver_wrongway': {
        'status': 410,
        'response': json.dumps(WRONGWAY_RESPONSE),
    },
    'driver_bad_position': {
        'status': 410,
        'response': json.dumps(BAD_POSITION_RESPONSE),
    },
    'driver_gone': {'status': 410, 'response': json.dumps(GONE_RESPONSE)},
    'driver_int_error': {'status': 500, 'response': '{}'},
}

RESPONSES_REQUESTCONFIRM = {
    'MOCK_BAD_REQUEST': {
        'status': 400,
        'response': json.dumps(BAD_REQUEST_RESPONSE),
    },
    'MOCK_FORBIDDEN': {
        'status': 403,
        'response': json.dumps(FORBIDDEN_RESPONSE),
    },
    'MOCK_OK': {'status': 200, 'response': json.dumps(REQUESTCONFIRM_OK)},
}

RESPONSES_UPDATE_POINTS = {
    'MOCK_BAD_REQUEST': {
        'status': 400,
        'response': json.dumps(BAD_REQUEST_RESPONSE),
    },
    'MOCK_FORBIDDEN': {
        'status': 403,
        'response': json.dumps(FORBIDDEN_RESPONSE),
    },
    'order_internal_not_found': {
        'status': 404,
        'response': json.dumps(NOT_FOUND_RESPONSE),
    },
    'order_internal_gone': {
        'status': 410,
        'response': json.dumps(GONE_RESPONSE),
    },
    'order_internal_error': {'status': 500, 'response': '{}'},
}

PREFIX = 'http://'


class DUPContext:
    def __init__(self):
        self.response = {'display_mode': 'orders', 'display_profile': 'orders'}
        self.has_error = False

    def set_response(self, mode):
        self.response = {'display_mode': mode, 'display_profile': mode}

    def set_error(self):
        self.has_error = True


@pytest.fixture(name='driver_ui_profile', autouse=True)
def mock_dup(mockserver):
    context = DUPContext()

    @mockserver.json_handler('/driver-ui-profile/v1/mode')
    def _get(request):
        if context.has_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'lalala'},
            )
        return mockserver.make_response(status=200, json=context.response)

    return context


def make_dict_response(x, response_dict, content_type, default_response):
    resp = response_dict.get(x, default_response)
    resp['content_type'] = content_type
    return resp


def response_seen(x):
    return make_dict_response(
        x,
        RESPONSES_SEEN,
        'application/json',
        {'status': 200, 'response': '{}'},
    )


def response_requestconfirm(mock_type):
    return make_dict_response(
        mock_type,
        RESPONSES_REQUESTCONFIRM,
        'application/json',
        {'status': 200, 'response': '{}'},
    )


def response_update_points(x):
    return make_dict_response(
        x,
        RESPONSES_UPDATE_POINTS,
        'application/xml',
        {'status': 200, 'response': '{}'},
    )


def remove_prefix(park_url):
    return park_url[park_url.startswith(PREFIX) and len(PREFIX) :]


def mock_integeration_url(host, port, park_url):
    park_url = remove_prefix(park_url)
    return PREFIX + host + ':' + str(port) + '/' + park_url


class YaTaxiClientContext:
    def __init__(self):
        self.comment_id = None
        self.receipt = None
        self.status_distance = None
        self.driver_calc_receipt_overrides = None
        self.taximeter_cost = None
        self.cargo_pricing_receipt = None
        self.current_cost = None
        self.current_cost_called = 0
        self.seen_called = 0
        self.requestconfirm_response = None
        self.final_cost = None
        self.final_cost_meta = None
        self.dispatch_selected_price = None
        self.need_manual_accept = None
        self.taximeter_version = 'Taximeter 9.7 (1234)'


@pytest.fixture(name='yataxi_client', autouse=True)
def mock_ya_taxi_client(mockserver):
    context = YaTaxiClientContext()

    @mockserver.json_handler('/taximeter-api/1.x/seen')
    def _mock_taxi_seen(request):
        assert request.method == 'POST'
        if 'YaTaxi-Api-Key' not in request.headers:
            return mockserver.make_response(
                status=400,
                response=json.dumps(BAD_REQUEST_RESPONSE),
                content_type='application/json',
            )
        if request.headers.get('YaTaxi-Api-Key') != TEST_APIKEY:
            return mockserver.make_response(
                status=403,
                response=json.dumps(FORBIDDEN_RESPONSE),
                content_type='application/json',
            )

        context.seen_called += 1
        return mockserver.make_response(
            **response_seen(request.args.get('uuid', '')),
        )

    @mockserver.json_handler('/taximeter-api/1.x/updatepoints')
    def _mock_taxi_update_points(request):
        assert request.method == 'POST'
        if 'YaTaxi-Api-Key' not in request.headers:
            return mockserver.make_response(
                **response_update_points('MOCK_BAD_REQUEST'),
            )
        if request.headers.get('YaTaxi-Api-Key') != TEST_APIKEY:
            return mockserver.make_response(
                **response_update_points('MOCK_FORBIDDEN'),
            )
        return mockserver.make_response(
            **response_update_points(request.json.get('order_id', '')),
        )

    @mockserver.json_handler('/taximeter-api/1.x/requestconfirm')
    def _mock_taxi_requestconfirm(request):
        assert request.method == 'POST'
        assert request.args['taximeter_app'] == context.taximeter_version
        if 'YaTaxi-Api-Key' not in request.headers:
            return mockserver.make_response(
                **response_requestconfirm('MOCK_BAD_REQUEST'),
            )
        if request.headers.get('YaTaxi-Api-Key') != TEST_APIKEY:
            return mockserver.make_response(
                **response_requestconfirm('MOCK_FORBIDDEN'),
            )
        req = request.json
        if req.get('status') == 'reject':
            comment_value = context.comment_id or 'UNDEFINED'
            assert req.get('comment_id') == comment_value
        if req.get('origin') == 'dispatch':
            assert req.get('user_login') is not None  # maybe empty
            if req.get('dispatch_selected_price'):
                assert 'use_recommended_cost' not in req
            else:
                assert req.get('use_recommended_cost') is True
            assert req.get('dispatch_selected_price') == (
                context.dispatch_selected_price
            )
            assert req.get('need_manual_accept') == (
                context.need_manual_accept
            )
            assert req.get('dispatch_api_version') == '1.0'
        else:
            assert 'dispatch_api_version' not in req
        assert (float(req.get('direction', 0.0))) >= 0.0
        assert req.get('receipt') == context.receipt
        assert req.get('distance') == context.status_distance
        assert req.get('final_cost_meta') == context.final_cost_meta
        assert (
            req.get('driver_calc_receipt_overrides')
            == context.driver_calc_receipt_overrides
        )
        response = response_requestconfirm('MOCK_OK')
        response_field = context.requestconfirm_response or json.loads(
            response['response'],
        )
        response_field.update(
            {
                'taximeter_cost': context.taximeter_cost,
                'cargo_pricing_receipt': context.cargo_pricing_receipt,
            },
        )
        if req.get('status') == 'complete':
            if context.final_cost:
                response_field.update(
                    {
                        'final_cost': {
                            'driver': context.final_cost.get('driver'),
                            'user': context.final_cost.get('user'),
                        },
                    },
                )
            elif req.get('sum') and req.get('total'):
                response_field.update(
                    {
                        'final_cost': {
                            'driver': req.get('total'),
                            'user': req.get('sum'),
                        },
                    },
                )
        elif response_field.get('final_cost'):
            response_field.pop('final_cost')
        response['response'] = json.dumps(response_field)
        return mockserver.make_response(**response)

    return context


class DriverOrdersContext:
    def __init__(self):
        self.park_id = None
        self.order_id = None
        self.driver_id = None
        self.status = None
        self.provider = None
        self.category = None
        self.cost_pay = None
        self.cost_sub = None
        self.cost_total = None
        self.some_date = None


@pytest.fixture(name='driver_orders', autouse=True)
def mock_driver_orders(mockserver):
    context = DriverOrdersContext()

    @mockserver.json_handler(
        '/driver-orders/v1/parks/orders/bulk_retrieve/raw',
    )
    def _mock_return_v1_parks_list(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'orders': [
                        {
                            'id': context.order_id,
                            'order': {
                                'driver_id': context.driver_id,
                                'provider': context.provider,
                                'status': context.status,
                                'category': context.category,
                                'cost_pay': context.cost_pay,
                                'cost_sub': context.cost_sub,
                                'cost_total': context.cost_total,
                            },
                        },
                    ],
                },
            ),
            status=200,
        )

    return context


class FleetParksContext:
    def __init__(self):
        self.parks = {'parks': []}
        self.integration_called = 0
        self.communications = {
            'park_id': 'some_park_id',
            'sms': {
                'login': 'login',
                'password': 'password',
                'provider': 'provider',
            },
            'voip': {
                'ice_servers': 'ice_servers',
                'provider': 'provider',
                'show_number': False,
            },
        }


@pytest.fixture(name='fleet_parks', autouse=True)
def mock_fleet_parks(mockserver):
    context = FleetParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_return_v1_parks_list(request):
        if (
                context.parks['parks']
                and 'integration_events' in context.parks['parks'][0]
        ):
            context.parks['parks'][0]['integration_server_url'] = (
                mock_integeration_url(
                    mockserver.host,
                    mockserver.port,
                    context.parks['parks'][0]['integration_server_url'],
                )
            )
        return mockserver.make_response(json.dumps(context.parks), status=200)

    @mockserver.json_handler('/fleet-parks/v1/parks/communications/retrieve')
    def _mock_return_v1_parks_communications(request):
        return mockserver.make_response(
            json.dumps(context.communications), status=200,
        )

    @mockserver.json_handler('park_id_0.ru/sync/cancelrequest')
    def _cancelrequest(request):
        context.integration_called += 1
        assert request.get_data() == b'orderid=order_id_0&reason=shown'
        return mockserver.make_response('{}')

    @mockserver.json_handler('park_id_0.ru/sync/requestconfirm')
    def _requestconfirm(request):
        context.integration_called += 1
        return mockserver.make_response('{}')

    @mockserver.json_handler('park_id_0.ru/sync/setcar')
    def _setcar(request):
        context.integration_called += 1
        return mockserver.make_response('{}')

    return context


class FleetVehiclesContext:
    def __init__(self):
        pass


@pytest.fixture(name='fleet_vehicles', autouse=True)
def mock_vehicles_parks(mockserver):
    context = FleetVehiclesContext()

    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _mock_vehicle_cache_retrieve(request):
        data = json.loads(request.get_data())
        assert 'id_in_set' in data
        if not data['id_in_set']:
            return mockserver.make_response(json={}, status=400)

        vehicles = [
            {'park_id_car_id': x, 'data': {'callsign': 'birdperson'}}
            for x in data['id_in_set']
        ]
        return {'vehicles': vehicles}

    return context


@pytest.fixture(name='contractor_order_setcar', autouse=True)
def contractor_order_setcar_mock(mockserver, redis_store):
    class Context:
        def __init__(self):
            pass

        @mockserver.json_handler('/contractor-order-setcar/v1/order/cancel')
        @staticmethod
        def cancel_handler(request):
            # check json request body
            assert 'alias_id' in request.json
            assert 'park_id' in request.json
            assert 'profile_id' in request.json
            assert 'User-Agent' in request.headers
            park_id = request.json['park_id']
            profile_id = request.json['profile_id']
            alias_id = request.json['alias_id']
            redis_store.set(
                'Order:Driver:CancelRequest:MD5:' + park_id + ':' + profile_id,
                'asdaasdadasdadsd45834758943785',
            )
            redis_store.rpush(
                'Order:Driver:CancelRequest:Items:'
                + park_id
                + ':'
                + profile_id,
                alias_id,
            )
            return {}

        @mockserver.json_handler('/contractor-order-setcar/v1/order/complete')
        @staticmethod
        def complete_handler(request):
            # check json request body
            assert 'alias_id' in request.json
            assert 'park_id' in request.json
            assert 'profile_id' in request.json
            assert 'User-Agent' in request.headers
            park_id = request.json['park_id']
            profile_id = request.json['profile_id']
            alias_id = request.json['alias_id']
            redis_store.set(
                'Order:Driver:CompleteRequest:MD5:'
                + park_id
                + ':'
                + profile_id,
                'asdaasdadasdadsd45834758943785',
            )
            redis_store.rpush(
                'Order:Driver:CompleteRequest:Items:'
                + park_id
                + ':'
                + profile_id,
                alias_id,
            )
            return {}

        @mockserver.json_handler('/contractor-order-setcar/v1/order/delayed')
        @staticmethod
        def delayed_handler(request):
            assert 'alias_id' in request.json
            assert 'park_id' in request.json
            assert 'profile_id' in request.json
            assert 'User-Agent' in request.headers
            park_id = request.json['park_id']
            profile_id = request.json['profile_id']
            alias_id = request.json['alias_id']
            redis_store.set(
                'Order:Driver:CompleteRequest:MD5:'
                + park_id
                + ':'
                + profile_id,
                'asdaasdadasdadsd45834758943785',
            )
            redis_store.sadd(
                'Order:Driver:Delayed:Items:' + park_id + ':' + profile_id,
                alias_id,
            )
            return {}

        @mockserver.json_handler(
            '/contractor-order-setcar/v1/order/cancel-delayed',
        )
        @staticmethod
        def cancel_delayed_handler(request):
            assert 'park_id' in request.json
            assert 'profile_id' in request.json
            park_id = request.json['park_id']
            profile_id = request.json['profile_id']
            redis_store.set(
                'Order:Driver:CompleteRequest:MD5:'
                + park_id
                + ':'
                + profile_id,
                'asdaasdadasdadsd45834758943785',
            )
            res = redis_store.delete(
                'Order:Driver:Delayed:Items:' + park_id + ':' + profile_id,
            )
            return {'succeeded': res != 0}

    ctx = Context()
    return ctx


@pytest.fixture(name='parks', autouse=True)
def mock_parks_client(mockserver):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_return_needed_fields(request):
        response = {
            'offset': 0,
            'total': 1,
            'limit': 1,
            'driver_profiles': [
                {
                    'driver_profile': {
                        'first_name': 'Alex',
                        'middle_name': 'Sergeevich',
                        'last_name': 'Pushkin',
                    },
                    'car': {
                        'id': 'car_id_0',
                        'normalized_number': 'V292IK929',
                        'callsign': 'birdperson',
                        'brand': 'blabla',
                        'model': 'blablabla',
                        'color': 'blue',
                        'year': 1994,
                        'number': 'V292IK929',
                    },
                },
            ],
            'parks': [{}],
        }
        return response


class DriverOrderMessagesContext:
    def __init__(self):
        self.last_request = None
        self.code = 200

    def set_code(self, code):
        self.code = code


@pytest.fixture(name='driver_order_messages', autouse=True)
def mock_driver_order_messages(mockserver):
    context = DriverOrderMessagesContext()

    @mockserver.json_handler('/driver-order-messages/v1/messages/add')
    def _mock_add(request):
        context.last_request = json.loads(request.get_data())
        return mockserver.make_response(json.dumps({}), status=context.code)

    return context


class TaximeterXserviceContext:
    def __init__(self):
        self.response = {}
        self.return_error = False
        self.called_start = 0
        self.called_remove = 0
        self.expected_request = None

    def set_response(self, response):
        self.response = response

    def set_return_error(self):
        self.return_error = True


@pytest.fixture(name='taximeter_xservice', autouse=True)
def taximeter_xservice_request(mockserver):
    context = TaximeterXserviceContext()

    @mockserver.json_handler(
        '/taximeter-xservice/xservice/yandex/1.x/calcservice/remove',
    )
    def _calcservice_remove(request):
        context.called_remove += 1
        if context.return_error:
            return mockserver.make_response(json=RESPONSE500, status=500)
        return context.response

    @mockserver.json_handler(
        '/taximeter-xservice/xservice/yandex/1.x/calcservice/start',
    )
    def _calcservice_start(request):
        context.called_start += 1
        if context.return_error:
            return mockserver.make_response(json=RESPONSE500, status=500)
        return context.response

    return context


@pytest.fixture(name='driver_trackstory', autouse=True)
def driver_trackstory_request(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _position(request):
        return mockserver.make_response(
            json={
                'position': {
                    'lat': 55.4183979995,
                    'lon': 37.8954151234,
                    'timestamp': 1533817820,
                },
                'type': 'adjusted',
            },
            status=200,
        )


@pytest.fixture(name='driver_work_rules', autouse=True)
def driver_work_rules_request(mockserver):
    @mockserver.json_handler('/driver-work-rules/v1/order-types')
    def _order_types(request):
        return mockserver.make_response(
            json={
                'id': 'random_other_order_type',
                'autocancel_time_in_seconds': 10,
                'driver_cancel_cost': '50.0000',
                'color': 'White',
                'morning_visibility': {'period': 'м', 'value': 3},
                'name': 'Random',
                'night_visibility': {'period': 'скрыть', 'value': -1},
                'is_client_address_shown': True,
                'is_client_phone_shown': True,
                'driver_waiting_cost': '50.0000',
                'weekend_visibility': {'period': '', 'value': 0},
            },
            status=200,
        )


@pytest.fixture(name='selfemployed', autouse=True)
def selfemployed_request(mockserver):
    @mockserver.json_handler('/selfemployed/add-order/v2')
    def _mock_add_order(request):
        return mockserver.make_response(status=200)


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'park_order: Tests related to park orders',
    )


@pytest.fixture(name='driver_orders_builder', autouse=True)
def driver_orders_builder(mockserver):
    class Context:
        def __init__(self):
            self.v2_setcar = None
            self.v2_setcar_bulk = None

            self.v2_setcar_req = None
            self.v2_setcar_resp = None
            self.v2_setcar_bulk_resp = None

        def set_v2_setcar_req(self, setcar_req):
            self.v2_setcar_req = setcar_req

        def set_v2_setcar_resp(self, setcar_resp):
            self.v2_setcar_resp = setcar_resp

        def set_v2_setcar_bulk_resp(self, setcar_bulk_resp):
            self.v2_setcar_bulk_resp = setcar_bulk_resp

    ctx = Context()

    @mockserver.json_handler('/driver-orders-builder/v2/setcar/bulk')
    def _v2_setcar_bulk(request):
        return mockserver.make_response(
            json=ctx.v2_setcar_bulk_resp
            or {
                'setcars': [
                    {
                        'driver': {
                            'park_id': 'park_id',
                            'driver_profile_id': 'driver_profile_id',
                            'alias_id': 'alias_id',
                        },
                        'setcar': {'setcar_key': 'setcar_data'},
                        'setcar_push': {'setcar_push_key': 'setcar_push_data'},
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler('/driver-orders-builder/v2/setcar')
    def _v2_setcar(request):
        if ctx.v2_setcar_req is not None:
            assert request.json['original_setcar'] == ctx.v2_setcar_req
        return mockserver.make_response(
            json=ctx.v2_setcar_resp or {'setcar': {}, 'setcar_push': {}},
            status=200,
        )

    ctx.v2_setcar = _v2_setcar
    ctx.v2_setcar_bulk = _v2_setcar_bulk
    return ctx


@pytest.fixture(name='contractor_orders_multioffer', autouse=True)
def contractor_orders_multioffer(mockserver):
    class Context:
        def __init__(self):
            self.offer_decline = None
            self.seen = None
            self.state = None
            self.state_resp = 'win'

        def set_state_resp(self, is_multioffer):
            if is_multioffer:
                self.state_resp = 'win'
            else:
                self.state_resp = 'sent'

    ctx = Context()

    @mockserver.json_handler(
        '/contractor-orders-multioffer/internal/v1/'
        'orders-offer/offer/decline',
    )
    def _offer_decline(self):
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler(
        '/contractor-orders-multioffer/internal/v1/multioffer/seen',
    )
    def _seen(self):
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler(
        '/contractor-orders-multioffer/internal/v1/multioffer/state',
    )
    def _state(self):
        return mockserver.make_response(
            json={
                'multioffer_id': '01234567-89ab-cdef-0123-456789abcdef',
                'state': ctx.state_resp,
                'updated_at': '2020-02-07T19:45:00.922+00:00',
                'timeout': 15,
                'play_timeout': 20,
                'paid_supply': False,
                'route_info': {
                    'approximate': False,
                    'distance': 2523,
                    'time': 300,
                },
                'position': [37.5653059, 55.745537],
                'classes': ['econom'],
            },
            status=200,
        )

    ctx.offer_decline = _offer_decline
    ctx.seen = _seen
    ctx.state = _state

    return ctx


@pytest.fixture(name='candidate_meta', autouse=True)
def candidate_meta(mockserver):
    class Context:
        def __init__(self):
            self.metadata = None
            self.active = False

        def set_active(self, active):
            self.active = active

    ctx = Context()

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/get')
    def _metadata(request):
        return mockserver.make_response(
            json={
                'metadata': {
                    'verybusy_order': False,
                    'combo': {'active': ctx.active},
                },
            },
            status=200,
        )

    ctx.metadata = _metadata

    return ctx


@pytest.fixture(name='communications', autouse=True)
def communications_mock(mockserver):
    class Context:
        @mockserver.json_handler('/communications/driver/notification/push')
        def driver_notification_push(self):
            return mockserver.make_response(json={}, status=200)

    return Context()


@pytest.fixture(name='client_notify', autouse=True)
def client_notify_mock(mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def v2_push(request):
        assert 'service' in request.json
        assert 'intent' in request.json
        assert 'client_id' in request.json
        return mockserver.make_response(
            json.dumps({'notification_id': '1488'}), status=200,
        )

    return v2_push


@pytest.fixture(name='driver_profiles', autouse=True)
def driver_profiles_mock(mockserver):
    class Context:
        def __init__(self):
            self.platform = 'android'
            self.taximeter_version = '9.7 (1234)'

        def set_platform(self, platform):
            self.platform = platform

        def set_taximeter_version(self, user_agent):
            self.taximeter_version = tvh.match_taximeter_version(user_agent)

    ctx = Context()

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_app_profile_retrieve(request):
        data = json.loads(request.get_data())
        assert 'id_in_set' in data
        if not data['id_in_set']:
            return mockserver.make_response(json={}, status=400)

        profiles = [
            {
                'park_driver_profile_id': x,
                'data': {
                    'taximeter_platform': ctx.platform,
                    'taximeter_version': ctx.taximeter_version,
                    'taximeter_version_type': '',
                },
            }
            for x in data['id_in_set']
        ]
        return {'profiles': profiles}

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles_retrieve(request):
        data = json.loads(request.get_data())
        assert 'id_in_set' in data
        if not data['id_in_set']:
            return mockserver.make_response(json={}, status=400)

        profiles = [
            {
                'park_driver_profile_id': x,
                'data': {
                    'full_name': {
                        'first_name': 'Alex',
                        'middle_name': 'Sergeevich',
                        'last_name': 'Pushkin',
                    },
                    'car_id': 'car_id_0',
                },
            }
            for x in data['id_in_set']
        ]
        return {'profiles': profiles}

    return ctx


@pytest.fixture(name='driver_status', autouse=True)
def driver_status_mock(mockserver):
    class Context:
        def __init__(self):
            self.order_store = None
            self.driver_statuses = None
            self.status = 'online'
            self.orders = None

        def set_status(self, status):
            self.status = status

        def set_orders(self, orders):
            self.orders = orders

    ctx = Context()

    @mockserver.json_handler('/driver-status/v2/order/store')
    def _mock_order_store(request):
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler('/driver-status/v2/statuses')
    def _mock_driver_statuses(request):
        data = json.loads(request.get_data())
        assert 'driver_ids' in data
        if not data['driver_ids']:
            return mockserver.make_response(json={}, status=400)
        statuses = [
            {
                'driver_id': x['driver_id'],
                'park_id': x['park_id'],
                'status': ctx.status,
                'orders': ctx.orders,
            }
            for x in data['driver_ids']
        ]
        return mockserver.make_response(
            json={'statuses': statuses}, status=200,
        )

    ctx.order_store = _mock_order_store
    ctx.driver_statuses = _mock_driver_statuses

    return ctx


@pytest.fixture(name='contractor_order_history', autouse=True)
def contractor_order_history_mock(mockserver):
    class Context:
        @mockserver.json_handler('/contractor-order-history/insert')
        def insert(self):
            return mockserver.make_response(json={}, status=200)

        @mockserver.json_handler('/contractor-order-history/update')
        def update(self):
            return mockserver.make_response(json={}, status=200)

    return Context()


@pytest.fixture(name='partner_api_proxy', autouse=True)
def partner_api_proxy_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {'isActive': True}

        def set_response(self, response):
            self.response = response

    ctx = Context()

    @mockserver.json_handler('/partner-api-proxy/performer-shift-state/')
    def _mock_performer_shift_state(request):
        return mockserver.make_response(json=ctx.response, status=200)

    return ctx


class EulasContext:
    def __init__(self):
        self.response = {'items': []}

    def set_response(self, response):
        self.response = response

    def get_response(self):
        return self.response


@pytest.fixture(autouse=True, name='eulas')
def _eulas(mockserver):
    context = EulasContext()

    @mockserver.json_handler('/eulas/internal/driver/v1/eulas/v1/freightage')
    def _mock_income_order_sounds(request):
        return mockserver.make_response(status=200, json=context.response)

    return context
