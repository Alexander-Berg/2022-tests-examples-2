# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
# ^^^ to use functions as fixtures in the same file
from typing import Optional

from cargo_matcher_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='exp3_offer_ttl_enabled')
async def _exp3_exp3_offer_ttl_enabled(
        taxi_cargo_matcher, experiments3, load_json,
):
    experiments3.add_experiments_json(load_json('exp3_offer_ttl_enabled.json'))
    await taxi_cargo_matcher.invalidate_caches()


@pytest.fixture(name='exp3_pricing_disabled')
async def _exp3_pricing_disabled(taxi_cargo_matcher, experiments3, load_json):
    experiments3.add_experiments_json(load_json('exp3_pricing_disabled.json'))
    await taxi_cargo_matcher.invalidate_caches()


@pytest.fixture(name='exp3_pricing_enabled')
async def _exp3_pricing_enabled(taxi_cargo_matcher, experiments3, load_json):
    async def _exp_setter(only_for_dragon_flow=False):
        exp_json = load_json('exp3_pricing_enabled.json')
        if only_for_dragon_flow:
            exp_json['configs'][0]['clauses'][0]['predicate'] = {
                'init': {
                    'arg_name': 'dispatch_flow',
                    'arg_type': 'string',
                    'value': 'newway',
                },
                'type': 'eq',
            }
        experiments3.add_experiments_json(exp_json)
        await taxi_cargo_matcher.invalidate_caches()

    await _exp_setter()
    return _exp_setter


@pytest.fixture(name='exp3_work_mode_new_way')
async def _exp3_work_mode_new_way(taxi_cargo_matcher, experiments3):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_type_requirement_work_mode',
        consumers=['cargo-matcher/estimate'],
        clauses=[],
        default_value={'work_mode': 'newway'},
    )
    await taxi_cargo_matcher.invalidate_caches()


@pytest.fixture(name='exp3_cargo_add_fake_middle_point')
async def _exp3_cargo_add_fake_middle_point(taxi_cargo_matcher, experiments3):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_add_fake_middle_point',
        consumers=['cargo-matcher/estimate'],
        clauses=[],
        default_value={'enabled': True},
    )
    await taxi_cargo_matcher.invalidate_caches()


@pytest.fixture(name='conf_exp3_requirements_from_options')
def _conf_exp3_requirements_from_options(experiments3, taxi_cargo_matcher):
    async def configurate(requirement=None):
        default_value = {}
        if requirement is not None:
            default_value = {'requirement': requirement}
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_matcher_options_to_requirements_map',
            consumers=['cargo-matcher/estimate-options-to-requirements'],
            clauses=[],
            default_value=default_value,
        )
        await taxi_cargo_matcher.invalidate_caches()

    return configurate


@pytest.fixture(name='conf_exp3_cargocorp_autoreplacement')
def _conf_exp3_cargocorp_autoreplacement(experiments3, taxi_cargo_matcher):
    async def configurate(is_enabled):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_matcher_enable_cargocorp_autoreplacement',
            consumers=['cargo-matcher/estimate'],
            clauses=[],
            default_value={'enabled': is_enabled},
        )
        await taxi_cargo_matcher.invalidate_caches()

    return configurate


@pytest.fixture(name='set_dynamic_requirements_config')
def _set_dynamic_requirements_config(taxi_config, taxi_cargo_matcher):
    async def setter(dynamic_requirements):
        taxi_config.set_values(
            {
                'CARGO_MATCHER_DYNAMIC_REQUIREMENTS': {
                    'requirements': dynamic_requirements,
                },
            },
        )
        await taxi_cargo_matcher.invalidate_caches()

    return setter


@pytest.fixture(name='config_dynamic_requirements')
async def _config_dynamic_requirements(set_dynamic_requirements_config):
    await set_dynamic_requirements_config(
        dynamic_requirements=['dynamic_requirement'],
    )


@pytest.fixture(name='config_switchable_requirement')
def _config_switchable_requirement(taxi_config, taxi_cargo_matcher):
    async def configurate(config):
        taxi_config.set_values(config)
        await taxi_cargo_matcher.invalidate_caches()

    return configurate


def get_bool_switchable_req_config(requirement):
    return {
        'CARGO_MATCHER_SWITCHABLE_REQUIREMENTS': {
            requirement: {
                'title_key': 'requirement.dynamic_requirement.title',
                'text_key': 'requirement.dynamic_requirement.text',
                'type': 'bool',
                'experiment': 'cargo_matcher_switchable_requirement_enabled',
                'default': False,
            },
        },
    }


@pytest.fixture(name='config_bool_switchable_requirement')
async def _config_bool_switchable_requirement(config_switchable_requirement):
    await config_switchable_requirement(
        config=get_bool_switchable_req_config(
            requirement='dynamic_requirement',
        ),
    )


def _get_select_switchable_requirement_config(select_type):
    return {
        'CARGO_MATCHER_SWITCHABLE_REQUIREMENTS': {
            'dynamic_requirement': {
                'title_key': 'requirement.dynamic_requirement.title',
                'text_key': 'requirement.dynamic_requirement.text',
                'type': select_type,
                'required': False,
                'experiment': 'cargo_matcher_switchable_requirement_enabled',
                'variants': [
                    {
                        'name': 'select_req_case1',
                        'title_key': 'requirement.select_req_case1.title',
                        'text_key': 'requirement.select_req_case1.text',
                        'value': 1,
                    },
                    {
                        'name': 'select_req_case2',
                        'title_key': 'requirement.select_req_case2.title',
                        'text_key': 'requirement.select_req_case2.text',
                        'value': 2,
                    },
                    {
                        'name': 'unavailable_select_req_case',
                        'title_key': (
                            'requirement.unavailable_select_req_case.title'
                        ),
                        'text_key': (
                            'requirement.unavailable_select_req_case.text'
                        ),
                        'value': 3,
                    },
                ],
            },
        },
    }


@pytest.fixture(name='config_select_switchable_requirement')
async def _config_select_switchable_requirement(config_switchable_requirement):
    await config_switchable_requirement(
        config=_get_select_switchable_requirement_config('select'),
    )


@pytest.fixture(name='config_multiselect_switchable_requirement')
async def _config_multiselect_switchable_requirement(
        config_switchable_requirement,
):
    await config_switchable_requirement(
        config=_get_select_switchable_requirement_config('multi_select'),
    )


@pytest.fixture(name='conf_exp3_switchable_requirement')
def _conf_exp3_switchable_requirement(experiments3, taxi_cargo_matcher):
    async def configurate(visible_in):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_matcher_switchable_requirement_enabled',
            consumers=['cargo-matcher/switchable_requirements'],
            clauses=[],
            default_value={'visible_in': visible_in},
        )
        await taxi_cargo_matcher.invalidate_caches()

    return configurate


@pytest.fixture(name='mock_corp_tariffs', autouse=True)
def _mock_corp_tariffs(mockserver, load_json):
    context = {
        'response': {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'activation_zone': 'moscow_activation',
                'categories': load_json('categories.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        },
    }

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _tariffs(request):
        return context['response']

    context['handler'] = _tariffs
    return context


@pytest.fixture(name='mock_user_api', autouse=True)
def _mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _user_api(request):
        return {
            'id': 'user_phone_id',
            'phone': '+70009999987',
            'type': 'yandex',
            'is_taxi_staff': False,
            'is_yandex_staff': False,
            'is_loyal': False,
            'stat': {
                'total': 0,
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
            },
        }


@pytest.fixture(name='mock_paymentmethods', autouse=True)
def _mock_paymentmethods(mockserver):
    context = {
        'response': {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id_12312312312312312',
                    'label': 'Yandex team',
                    'description': 'Осталось 4000 из 5000 руб.',
                    'cost_center': 'cost center',
                    'cost_centers': {
                        'required': False,
                        'format': 'mixed',
                        'values': [],
                    },
                    'can_order': True,
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'user_id_1',
                    'client_comment': 'comment',
                    'currency': 'RUB',
                    'classes_available': [
                        'express',
                        'cargo',
                        'cargocorp',
                        'night',
                    ],
                },
            ],
        },
    }

    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def _paymentmethods(request):
        return context['response']

    context['handler'] = _paymentmethods
    return context


@pytest.fixture
def get_default_full_claim_response():
    return {
        'id': 'claim_id_1',
        'corp_client_id': 'corp_client_id_12312312312312312',
        'initiator_yandex_uid': '123',
        'emergency_contact': {
            'name': 'name',
            'personal_phone_id': '+79998887777_id',
        },
        'items': [
            {
                'id': 123,
                'extra_id': '123',
                'pickup_point': 1,
                'droppof_point': 2,
                'title': 'Холодильник карманный',
                'size': {'length': 0.8, 'width': 0.4, 'height': 0.3},
                'weight': 5,
                'quantity': 1,
                'cost_value': '10.20',
                'cost_currency': 'RUR',
            },
        ],
        'route_points': [
            {
                'id': 1,
                'address': {'fullname': '', 'coordinates': [37.1, 55.1]},
                'contact': {
                    'personal_phone_id': 'personal_phone_id_123',
                    'personal_email_id': 'personal_email_id_123',
                    'name': 'Petya',
                },
                'type': 'source',
                'visit_order': 1,
                'visit_status': 'pending',
                'visited_at': {},
            },
            {
                'id': 2,
                'address': {'fullname': '', 'coordinates': [37.2, 55.3]},
                'contact': {
                    'personal_phone_id': 'personal_phone_id_456',
                    'personal_email_id': 'personal_email_id_123',
                    'name': 'Vasya',
                },
                'type': 'destination',
                'visit_order': 2,
                'visit_status': 'pending',
                'visited_at': {},
            },
        ],
        'status': 'new',
        'user_request_revision': '123',
        'version': 0,
        'pricing': {},
        'created_ts': '2020-03-31T18:35:00+00:00',
        'updated_ts': '2020-03-31T18:35:00+00:00',
    }


@pytest.fixture
def mock_claims_full(mockserver, get_default_full_claim_response):
    class Context:
        def __init__(self):
            self.response = get_default_full_claim_response
            self.mock = None

    ctx = Context()

    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _handler(request):
        return ctx.response

    ctx.mock = _handler
    return ctx


@pytest.fixture
def get_default_profile_response():
    return {
        'dont_ask_name': False,
        'experiments': [],
        'name': 'Petya',
        'personal_phone_id': 'personal_phone_id_123',
        'user_id': 'taxi_user_id_1',
    }


def get_currency_rules():
    return {
        'code': 'RUB',
        'sign': '₽',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'руб.',
    }


@pytest.fixture(name='get_currency_rules')
def currency_rules():
    return get_currency_rules()


@pytest.fixture
def mock_int_api_profile(mockserver, get_default_profile_response):
    class Context:
        def __init__(self):
            self.response = get_default_profile_response
            self.expected_request = {
                'user': {'personal_phone_id': 'personal_phone_id_123'},
                'name': 'Petya',
                'sourceid': 'cargo',
            }
            self.mock = None

    ctx = Context()

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _handler(request):
        assert request.json == ctx.expected_request
        return ctx.response

    ctx.mock = _handler
    return ctx


def get_default_estimate_response(taxi_class='cargo'):
    return {
        'offer': 'taxi_offer_id_1',
        'is_fixed_price': True,
        'currency_rules': get_currency_rules(),
        'service_levels': [{'class': taxi_class, 'price_raw': 999.001}],
        'is_delayed': False,
    }


def get_default_cargo_type_limits():
    return {
        'van': {
            'carrying_capacity_max_kg': 100,
            'carrying_capacity_min_kg': 0,
            'height_max_cm': 100,
            'height_min_cm': 0,
            'length_max_cm': 100,
            'length_min_cm': 0,
            'width_max_cm': 100,
            'width_min_cm': 0,
            'requirement_value': 1,
        },
        'lcv_m': {
            'carrying_capacity_max_kg': 1000,
            'carrying_capacity_min_kg': 100,
            'height_max_cm': 400,
            'height_min_cm': 200,
            'length_max_cm': 400,
            'length_min_cm': 200,
            'width_max_cm': 400,
            'width_min_cm': 200,
            'requirement_value': 2,
        },
        'lcv_l': {
            'carrying_capacity_max_kg': 10000,
            'carrying_capacity_min_kg': 1000,
            'height_max_cm': 400,
            'height_min_cm': 200,
            'length_max_cm': 400,
            'length_min_cm': 200,
            'width_max_cm': 400,
            'width_min_cm': 200,
            'requirement_value': 3,
        },
    }


def get_cargo_item(
        item_id=123,
        length=0.5,
        width=0.5,
        height=0.5,
        weight=50,
        quantity=1,
        has_params=True,
):
    item = {
        'id': item_id,
        'pickup_point': 1,
        'droppof_point': 2,
        'title': 'Холодильник',
        'quantity': quantity,
        'cost_value': '10.20',
        'cost_currency': 'RUR',
    }
    if has_params:
        item['size'] = {'length': length, 'width': width, 'height': height}
        item['weight'] = weight
    return item


def get_finish_estimate_request(cargo_type='lcv_m', quantity=1):
    return {
        'cars': [
            {
                'taxi_class': 'cargo',
                'taxi_requirements': {'cargo_type': cargo_type},
                'items': [{'id': 123, 'quantity': quantity}],
            },
        ],
        'offer': {
            'offer_id': 'taxi_offer_id_1',
            'price': '999.001',
            'price_raw': 999,
        },
        'zone_id': 'moscow',
        'is_delayed': False,
        'currency': 'RUB',
        'currency_rules': get_currency_rules(),
    }


@pytest.fixture
def mock_int_api_estimate(mockserver):
    context = {'response': get_default_estimate_response()}

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _handler(request):
        return context['response']

    return context


@pytest.fixture
def mock_finish_estimate(mockserver):
    context = {
        'expected-request': None,
        'response': {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        },
    }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _handler(request):
        if context['expected-request'] is not None:
            assert request.json == context['expected-request']
        return context['response']

    context['handler'] = _handler
    return context


@pytest.fixture
def mocker_client_tariff_plan(mockserver):
    def wrapper(response: Optional[dict] = None, status: int = 200):
        @mockserver.json_handler(
            '/taxi-corp-integration/v1/client_tariff_plan/current',
        )
        def client_tariff_plan(request):
            result = (
                {
                    'tariff_plan_series_id': 'tariff_plan_id_123',
                    'client_id': 'client_id_123',
                    'date_from': '2020-01-22T15:30:00+00:00',
                    'date_to': '2021-01-22T15:30:00+00:00',
                    'disable_tariff_fallback': False,
                }
                if response is None
                else response
            )
            return mockserver.make_response(json=result, status=status)

        return client_tariff_plan

    return wrapper


@pytest.fixture
def mocker_tariff_corp_current(mockserver, load_json):
    def wrapper(response: Optional[dict] = None, status: int = 200):
        @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
        def corp_current(request):
            result = (
                {
                    'tariff': {
                        'id': (
                            '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1'
                        ),
                        'home_zone': 'moscow',
                        'categories': load_json('categories.json'),
                    },
                    'disable_paid_supply_price': False,
                    'disable_fixed_price': True,
                    'client_tariff_plan': {
                        'tariff_plan_series_id': 'tariff_plan_id_123',
                        'date_from': '2020-01-22T15:30:00+00:00',
                        'date_to': '2021-01-22T15:30:00+00:00',
                    },
                }
                if response is None
                else response
            )
            return mockserver.make_response(json=result, status=status)

        return corp_current

    return wrapper


@pytest.fixture
def mocker_tariff_current(mockserver, load_json):
    def wrapper(response: Optional[dict] = None, status: int = 200):
        @mockserver.json_handler('/taxi-tariffs/v1/tariff/current')
        def tariff_current(request):
            result = (
                {
                    'home_zone': 'moscow_home_zone',
                    'activation_zone': 'moscow_activation_zone',
                    'date_from': '2020-01-22T15:30:00+00:00',
                    'categories': load_json('categories.json'),
                }
                if response is None
                else response
            )
            return mockserver.make_response(json=result, status=status)

        return tariff_current

    return wrapper


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


@pytest.fixture(name='default_pricing_response')
def _default_pricing_response():
    return {
        'calc_id': 'cargo-pricing/v1/123456',
        'is_fixed_price': True,
        'currency_rules': get_currency_rules(),
        'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        'price': '123.45',
        'units': {
            'currency': 'RUB',
            'distance': 'kilometer',
            'time': 'minute',
        },
        'services': [],
        'details': {
            'pricing_case': 'default',
            'paid_waiting_in_destination_price': '25.0000',
            'paid_waiting_in_destination_time': '30.0000',
            'total_time': '12',
            'total_distance': '1000',
            'paid_waiting_time': '5',
            'paid_waiting_price': '50',
            'paid_waiting_in_transit_time': '5',
            'paid_waiting_in_transit_price': '50',
        },
    }


@pytest.fixture(name='mock_cargo_pricing')
def _mock_cargo_pricing(mockserver, default_pricing_response):
    class Context:
        request = None
        mock = None
        response = default_pricing_response

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        return ctx.response

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='exp3_enabled')
def _exp3_enabled(exp3_pricing_enabled, exp3_offer_ttl_enabled):
    pass


@pytest.fixture(name='mock_v1_profile')
def _mock_v1_profile(mockserver):
    class Context:
        request = None
        mock = None

    ctx = Context()

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _mock(request, *args, **kwargs):
        ctx.request = request.json
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Petya',
            'personal_phone_id': 'personal_phone_id_123',
            'user_id': 'taxi_user_id_1',
        }

    ctx.mock = _mock

    return ctx


@pytest.fixture(name='personal_client', autouse=True)
def _personal_client(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones(_):
        return {
            'items': [
                {
                    'id': '1ebc244580cd48759e5d1764b759f9d1',
                    'value': '+70009999991',
                },
                {
                    'id': '2ebc244580cd48759e5d1764b759f9d2',
                    'value': '+70009999992',
                },
                {
                    'id': '3e243e5adea44cedacb69ef833315b23',
                    'value': '+70009999993',
                },
            ],
        }


@pytest.fixture(name='mock_pricing_processing', autouse=True)
def _mock_pricing_processing(mockserver):
    class Context:
        def __init__(self):
            self.is_c2c_claim = False
            self.request = None

    ctx = Context()

    @mockserver.json_handler('/cargo-pricing/v1/taxi/add-processing-event')
    def _mock(request):
        ctx.request = request
        return mockserver.make_response(status=200, json={})

    return ctx


@pytest.fixture(name='lazy_config_estimate_result_validation')
def _lazy_config_estimate_result_validation(taxi_config, taxi_cargo_matcher):
    async def configurate(config):
        taxi_config.set_values(config)
        await taxi_cargo_matcher.invalidate_caches()

    return configurate


@pytest.fixture(name='config_estimate_result_validation')
async def _config_estimate_result_validation(
        lazy_config_estimate_result_validation,
):
    await lazy_config_estimate_result_validation(
        config={
            'CARGO_MATCHER_ESTIMATE_RESULT_VALIDATION_PARAMS': {
                'max_route_distance_meter': 1500,
                'max_route_time_minutes': 15,
            },
        },
    )


@pytest.fixture(name='exp3_same_day')
def exp3_same_day(experiments3, taxi_cargo_matcher):
    async def configurate(corp_id):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='cargo_sdd_delivery_intervals_options',
            consumers=['cargo-matcher/delivery-intervals'],
            clauses=[
                {
                    'title': 'clause',
                    'predicate': {
                        'init': {
                            'predicates': [
                                {
                                    'init': {
                                        'arg_name': 'corp_client_id',
                                        'arg_type': 'string',
                                        'value': corp_id,
                                    },
                                    'type': 'eq',
                                },
                            ],
                        },
                        'type': 'all_of',
                    },
                    'value': {'allow_intervals': True},
                },
            ],
            default_value={'allow_intervals': False},
        )
        await taxi_cargo_matcher.invalidate_caches()

    return configurate


@pytest.fixture(name='cargo_corp_client_info')
def _cargo_corp_client_info(mockserver):
    context = {
        'response': {
            'company': {
                'city': 'Москва',
                'country': 'Россия',
                'name': 'Vice.Delivery',
                'segment': 'other',
            },
            'corp_client_id': '9f7c5bf0c4f14a52a0ee02715a1766f4',
            'created_ts': '2022-05-25T11:37:32.03759+00:00',
            'payment': {'schema': {'id': 'corp', 'localized_id': 'Агентская'}},
            'registered_ts': '2022-05-25T11:38:25.374281+00:00',
            'revision': 3,
            'updated_ts': '2022-05-25T11:38:25.376564+00:00',
            'web_ui_languages': ['ru', 'en'],
        },
    }

    @mockserver.json_handler('/cargo-corp/internal/cargo-corp/v1/client/info')
    def _client_info_get(request):
        return context['response']

    return context
