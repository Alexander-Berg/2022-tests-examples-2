# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy
import json
from typing import Optional

import bson
import deprecated
from driver_orders_builder_plugins import *  # noqa: F403 F401
import pytest

from tests_plugins import json_util

from tests_driver_orders_builder import utils

PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}
REDIS_RULE_TYPE_BY_NAME = 'RuleType:ByName:Items'
REDIS_RULE_TYPE_ITEMS = 'RuleType:Items'


class LegalEntitiesContext:
    def __init__(self):
        self.requests = []
        self.has_error = False

    def set_error(self, value):
        self.has_error = value

    def get_requests(self):
        return self.requests


@pytest.fixture(name='legal_entities', autouse=True)
def _mock_legal_entities(mockserver):
    context = LegalEntitiesContext()

    @mockserver.json_handler('/parks/cars/legal-entities')
    def _legal_entities_empty(request):
        context.requests.append(request)

        if context.has_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'lalala'},
            )

        assert request.query['car_id']
        assert request.query['park_id']
        return mockserver.make_response(status=200, json={})

    return context


class TollRoadsContext:
    def __init__(self):
        self.has_toll_road = False
        self.can_switch_road = False
        self.auto_payment = False

    def set_response(self, can_switch_road, has_toll_road, auto_payment):
        self.has_toll_road = has_toll_road
        self.can_switch_road = can_switch_road
        self.auto_payment = auto_payment


@pytest.fixture(name='toll_roads', autouse=True)
def mock_toll_roads(mockserver):
    context = TollRoadsContext()

    @mockserver.json_handler('/tolls/tolls/v1/order/retrieve')
    def _order(request):
        response = {
            'has_toll_road': context.has_toll_road,
            'can_switch_road': context.can_switch_road,
            'visible': True,
            'auto_payment': context.auto_payment,
            'cost': {
                'limits': {
                    'min': '100',
                    'max': str(utils.MAX_COST_TOLL_ROADS),
                },
            },
        }
        return response

    return context


class ParksContext:
    def __init__(self):
        self.country_id = 'rus'
        self.requests = []
        self.aggregators_id = {}
        self.country_ids = {}
        self.has_error = False

    def set_response(self, country_id):
        self.country_id = country_id

    def set_countries(self, country_ids):
        self.country_ids = country_ids

    def set_error(self, value):
        self.has_error = value

    def set_aggregators_id(self, aggregators_id):
        self.aggregators_id = aggregators_id

    def get_requests(self):
        return self.requests


@pytest.fixture(name='parks', autouse=True)
def mock_parks(mockserver):
    context = ParksContext()

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _list(request):
        context.requests.append(request)

        if context.has_error:
            return mockserver.make_response(
                status=500, json={'code': '500', 'message': 'lalala'},
            )

        parks = []
        for x in request.json['query']['park']['ids']:
            country_id = context.country_ids.get(x, context.country_id)
            park = {
                'id': x,
                'login': f'{x}_login',
                'name': f'{x}_name',
                'is_active': True,
                'city_id': f'{x} town',
                'locale': 'ru',
                'is_billing_enabled': True,
                'is_franchising_enabled': True,
                'country_id': country_id,
                'demo_mode': False,
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            }

            aggregator_id = context.aggregators_id.get(x, None)
            if aggregator_id:
                park['provider_config'] = {
                    'clid': aggregator_id + '_clid',
                    'apikey': aggregator_id + '_apikey',
                    'aggregator_id': aggregator_id + '_guid',
                    'type': 'production',
                }

            parks.append(park)

        response = {'parks': parks}
        return mockserver.make_response(status=200, json=response)

    return context


class OrderProcContext:
    def __init__(self, load_json):
        self.order_proc = load_json('order_core_response.json')
        self.has_error = False
        self.drop_nones = True
        self.set_fields_request_assert = lambda x: True

    def set_file(self, load_json, file_name):
        self.order_proc = load_json(file_name)

    def set_response(self, fields, key=None):
        if key:
            self.order_proc['fields'][key].update(fields)
        else:
            self.order_proc['fields'].update(fields)

    def set_error(self):
        self.has_error = True


# convert from /order-core/v1/tc/order-fields respons notation
@pytest.fixture(name='order_proc', autouse=True)
def mock_order_proc(mockserver, load_json):
    context = OrderProcContext(load_json)

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _order_fields(request):
        if context.has_error:
            return mockserver.make_response(
                status=500,
                content_type='application/json',
                json={'code': '500', 'message': 'lalala'},
            )

        body = bson.BSON.decode(request.get_data())
        context.set_fields_request_assert(body['fields'])

        # result = copy.copy(context.order_proc)

        response = {'revision': {'order.version': 8, 'processing.version': 10}}
        response['document'] = utils.fields_filter(
            context.order_proc['fields'], body['fields'], context.drop_nones,
        )
        response['document']['_id'] = context.order_proc['order_id']
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response),
        )

    return context


@pytest.fixture(name='billing_subventions', autouse=True)
def mock_billing_subventions(mockserver, load_json):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        zone = request.json.pop('tariff_zone')
        all_subventions = load_json('subvention_rules.json')['subventions']
        response_subventions = []
        for subvention in all_subventions:
            if zone in subvention['tariff_zones']:
                response_subventions.append(dict(subvention))
        return {'subventions': response_subventions}


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


@pytest.fixture(name='mock_cargo_setcar_data')
def _mock_cargo_setcar_data(mockserver):
    def _wrapper(
            comment: Optional[str] = None,
            skip_eta: bool = False,
            points_count: int = 1,
            is_batch_order: bool = False,
            is_picker_order: bool = False,
            surge_offer=None,
            custom_context=None,
            comment_overwrites: list = None,
            do_fail: bool = False,
            claim_ids=None,
            expected_request_cargo_ref_id=None,
            expected_request_tariff_class=None,
            expected_request_performer_info: dict = None,
            expected_request_order_id=None,
            deeplink: str = None,
            pricing: dict = None,
            tariff_class: str = None,
            corp_client_ids: list = None,
            taximeter_tylers: list = None,
            truncated_current_route: list = None,
    ):
        comment = comment
        eta = 123 if not skip_eta else None

        @mockserver.json_handler('/cargo-orders/v1/setcar-data')
        def _mock(request):
            if expected_request_cargo_ref_id is not None:
                assert (
                    request.json['cargo_ref_id']
                    == expected_request_cargo_ref_id
                )
            if expected_request_tariff_class is not None:
                assert (
                    request.json['tariff_class']
                    == expected_request_tariff_class
                )
            if expected_request_order_id is not None:
                assert request.json['order_id'] == expected_request_order_id
            if expected_request_performer_info:
                assert (
                    request.json['performer_info']
                    == expected_request_performer_info
                )
            if do_fail:
                return mockserver.make_response('', status=500)
            response = {
                'claim_id': 'claim_id_1',
                'claim_ids': ['claim_id_1'],
                'points_count': points_count,
                'is_batch_order': is_batch_order,
                'is_picker_order': is_picker_order,
                'comment_overwrites': comment_overwrites or [],
            }
            if claim_ids:
                response['claim_ids'] = claim_ids
            if eta:
                response['eta'] = eta
            if comment:
                response['comment'] = comment
            if surge_offer:
                response['surge_offer'] = surge_offer
            if custom_context:
                response['custom_context'] = custom_context
            if deeplink:
                response['instructions_deeplink'] = deeplink
            if pricing:
                response['pricing'] = pricing
            if tariff_class:
                response['tariff_class'] = tariff_class
            if corp_client_ids:
                response['corp_client_ids'] = corp_client_ids
            if taximeter_tylers:
                response['taximeter_tylers'] = taximeter_tylers
            if truncated_current_route:
                response['truncated_current_route'] = truncated_current_route
            return response

        return _mock

    return _wrapper


@pytest.fixture(autouse=True, name='driver_app_profiles')
def _driver_app_profile(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': request.json['id_in_set'][0],
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': 'android',
                        'fleet_type': 'taximeter',
                    },
                },
            ],
        }

    return _mock_get_driver_app


@pytest.fixture(autouse=True, name='driver_profiles')
def _driver_profile(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_get_driver(request):
        if 'id_in_set' not in request.json:
            return mockserver.make_response(status=400, json={})

        park_driver_ids = request.json['id_in_set']
        data = {}
        if 'projection' in request.json:
            if 'data.full_name' in request.json['projection']:
                data['full_name'] = {
                    'first_name': 'иван',
                    'last_name': 'иванов',
                    'middle_name': 'иванович',
                }
            if 'data.orders_provider' in request.json['projection']:
                data['orders_provider'] = {
                    'eda': True,
                    'lavka': False,
                    'taxi': False,
                    'taxi_walking_courier': False,
                }

        profiles = []
        for park_driver_id in park_driver_ids:
            profile = {'park_driver_profile_id': park_driver_id, 'data': data}
            profiles.append(profile)

        return mockserver.make_response(
            status=200, json={'profiles': profiles},
        )

    return _mock_get_driver


@pytest.fixture(name='contractor_orders_multioffer', autouse=True)
def contractor_orders_multioffer(mockserver):
    class Context:
        @mockserver.json_handler(
            '/contractor-orders-multioffer/internal/v1/'
            'multioffer/state_by_order',
        )
        def state_by_order(self):
            return mockserver.make_response(
                json={
                    'multioffer_id': '01234567-89ab-cdef-0123-456789abcdef',
                    'alias_id': 'alias_id',
                    'state': 'win',
                    'updated_at': '9999-12-31T23:59:59+00:00',
                    'seen_data': {
                        'reason': 'received',
                        'timestamp': 1234567890,
                    },
                },
                status=200,
            )

        @mockserver.json_handler(
            '/contractor-orders-multioffer/internal/v1/multioffer/state',
        )
        def state(self):
            return {
                'multioffer_id': '01234567-89ab-cdef-0123-456789abcdef',
                'state': 'chosen_candidate',
                'updated_at': '2020-02-07T19:45:00.922+00:00',
                'paid_supply': False,
                'timeout': 15,
                'play_timeout': 20,
                'route_info': {
                    'approximate': False,
                    'distance': 2523,
                    'time': 300,
                },
                'position': [37.5653059, 55.745537],
                'classes': ['econom'],
            }

    return Context()


@pytest.fixture(name='driver_orders_app_api', autouse=True)
def driver_orders_app_api(mockserver):
    class Context:
        @mockserver.json_handler(
            '/driver-orders-app-api/internal/v2/order/cancel/multioffer',
        )
        def cancel_v2(self):
            return mockserver.make_response(
                json={
                    'driver_cancel_statuses': [
                        {
                            'driver': {
                                'park_id': 'park_id',
                                'driver_profile_id': 'driver_profile_id',
                                'alias_id': 'alias_id',
                            },
                            'success': True,
                        },
                    ],
                },
                status=200,
            )

    return Context()


@pytest.fixture(name='zones', autouse=True)
def mock_zones_v2_empty(mockserver):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones_v2(request):
        return {'zones': [], 'notification_params': {}}


@pytest.fixture(name='yamaps', autouse=True)
def mock_yamaps_default(mockserver, load_json, yamaps):
    translations = load_json('localizeaddress_config.json')

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        yamaps_vars = None
        locale_translations = translations[request.args['lang']]
        if 'uri' in request.args:
            yamaps_vars = locale_translations[request.args['uri']]
        elif 'll' in request.args:
            yamaps_vars = locale_translations[request.args['ll']]
            yamaps_vars['point'] = request.args['ll']
        return [
            load_json(
                'yamaps_response_default.json',
                object_hook=json_util.VarHook(yamaps_vars),
            ),
        ]


@pytest.fixture(name='exp_cargo_setcar_requirements')
async def _exp_cargo_setcar_requirements(
        taxi_driver_orders_builder, experiments3,
):
    async def wrapper(*, tariff: str, hidden_requirements: list):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_setcar_requirements_settings',
            consumers=['driver-orders-builder/setcar'],
            clauses=[
                {
                    'title': 'clause_0',
                    'predicate': {
                        'init': {
                            'value': tariff,
                            'arg_name': 'tariff',
                            'arg_type': 'string',
                        },
                        'type': 'eq',
                    },
                    'value': {'hidden_requirements': hidden_requirements},
                },
            ],
            default_value={'hidden_requirements': []},
        )
        await taxi_driver_orders_builder.invalidate_caches()

    await wrapper(tariff='lavka', hidden_requirements=[])
    return wrapper


@pytest.fixture()
@deprecated.deprecated(
    reason='This fixture is deprecated, use "params_wo_original_setcar"',
)
def setcar_create_params(load_json):
    def wrapper():
        setcar_json = load_json('setcar.json')
        request = copy.deepcopy(PARAMS)
        request['original_setcar'] = setcar_json
        return {'path': '/v2/setcar', 'json': request}

    return wrapper()


# later it will be renamed to setcar_create_params
@pytest.fixture()
def params_wo_original_setcar():
    def wrapper():
        request = copy.deepcopy(PARAMS)
        return {'path': '/v2/setcar', 'json': request}

    return wrapper()


@pytest.fixture(autouse=True, name='fleet_vehicles')
def _fleet_vehicles(mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def _mock_vehicles_retrieve(request):
        if 'id_in_set' not in request.json:
            return mockserver.make_response(status=400, json={})

        park_id_car_ids = request.json['id_in_set']

        data = {
            'amenities': ['franchise'],
            'brand': 'Pagani',
            'callsign': 'rogue_one',
            'model': 'Zonda R',
            'number': 'X666XXX666',
        }

        vehicles = []
        for park_id_car_id in park_id_car_ids:
            vehicle = {'park_id_car_id': park_id_car_id, 'data': data}
            vehicles.append(vehicle)

        return mockserver.make_response(
            status=200, json={'vehicles': vehicles},
        )


class OrderSoundsContext:
    def __init__(self):
        self.request = {}

    def set_sound(self, sound_id):
        self.request['sound_id'] = sound_id

    def get_request(self):
        return self.request


@pytest.fixture(autouse=True, name='driver_profile_view')
def _driver_profile_view(mockserver):
    context = OrderSoundsContext()

    @mockserver.json_handler(
        '/driver-profile-view/internal/v1/income-order-sounds',
    )
    def _mock_income_order_sounds(request):
        return mockserver.make_response(status=200, json=context.request)

    return context


class EulasContext:
    def __init__(self):
        self.response = {'required': False}

    def set_required(self, is_required):
        self.response['required'] = is_required

    def get_request(self):
        return self.response


@pytest.fixture(autouse=True, name='eulas')
def _eulas(mockserver):
    context = EulasContext()

    @mockserver.json_handler('/eulas/internal/eulas/v1/is-freightage-required')
    def _mock_income_order_sounds(request):
        assert 'nearest_zone' in request.json
        assert 'tariff_class' in request.json
        return mockserver.make_response(status=200, json=context.response)

    return context


@pytest.fixture(name='redis_base_work_rules', autouse=True)
def mock_redis_work_rules(mockserver, load_json, redis_store):
    park_work_rules = load_json('redis_work_rules.json')
    for [park_id, items] in park_work_rules.items():
        for [rule_name, rule_id] in items['rules'].items():
            redis_store.hset(
                f'{REDIS_RULE_TYPE_BY_NAME}:{park_id}', rule_name, rule_id,
            )
        for [rule_id, color] in items['colors'].items():
            redis_store.hset(
                f'{REDIS_RULE_TYPE_ITEMS}:{park_id}',
                rule_id,
                json.dumps(color),
            )


def get_parks_activation(has_corp_without_vat_contract):
    return [
        {
            'revision': 1,
            'last_modified': '1970-01-15T03:56:07.000',
            'park_id': 'park1',
            'city_id': 'park1 town',
            'data': {
                'deactivated': False,
                'can_cash': False,
                'can_card': False,
                'can_coupon': False,
                'can_corp': True,
                'has_corp_without_vat_contract': has_corp_without_vat_contract,
            },
        },
    ]


class ParksActivationContext:
    def __init__(self):
        self.has_corp_without_vat_contract = False

    def has_corp_without_vat_contract_(self, value):
        self.has_corp_without_vat_contract = value


@pytest.fixture(autouse=True, name='parks_activation')
def mock_parks_activation(mockserver):
    context = ParksActivationContext()

    @mockserver.json_handler('/parks-activation/v1/parks/activation/updates')
    def _mock_updates(request):
        revision = request.json['last_known_revision']
        parks_activation = get_parks_activation(
            context.has_corp_without_vat_contract,
        )
        response = {
            'last_revision': parks_activation[-1]['revision'],
            'parks_activation': [
                park
                for park in parks_activation
                if park['revision'] > revision
            ],
        }
        return response

    return context
