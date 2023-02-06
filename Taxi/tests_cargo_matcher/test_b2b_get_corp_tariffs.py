import copy
import datetime

import pytest

from . import conftest


NOW = datetime.datetime.utcnow().replace(microsecond=0)

CORP_CLIENT_ID = 'corp_client_id_12312312312312312'

TARIFF_DESCRIPTIONS = {
    'express': {
        'title_key': {'__default__': 'tariff.express.title'},
        'text_key': {'__default__': 'tariff.express.text'},
    },
    'cargo': {
        'title_key': {'__default__': 'tariff.cargo.title'},
        'text_key': {'__default__': 'tariff.cargo.text'},
    },
}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.translations(
        cargo={
            'tariff.express.title': {'ru': 'Экспресс'},
            'tariff.express.text': {'ru': 'Тариф экспресс'},
            'tariff.cargo.title': {'ru': 'Грузовой'},
            'tariff.cargo.text': {'ru': 'Тариф грузовой'},
        },
    ),
]

HEADERS = {
    'Accept-Language': 'ru',
    'X-B2B-Client-Id': CORP_CLIENT_ID,
    'X-Cargo-Api-Prefix': '/b2b/cargo/integration/',
}

_TARIFF_REQUIREMENTS_CARGO_TYPE_LCV_L = {
    'cargo_type': {
        'text_key': 'requirement.cargo_type.text',
        'title_key': 'requirement.cargo_type.title',
        'type': 'select',
        'variants': [
            {
                'name': 'cargo_type.lcv_l',
                'text_key': 'requirement.cargo_type.lcv_l.text',
                'title_key': 'requirement.cargo_type.lcv_l.title',
                'value': 'lcv_l',
            },
        ],
    },
}


def timedelta_dec(**kwargs):
    return (NOW - datetime.timedelta(**kwargs)).isoformat() + 'Z'


def timedelta_inc(**kwargs):
    return (NOW - datetime.timedelta(**kwargs)).isoformat() + 'Z'


@pytest.fixture(name='request_api_integration_v1_tariffs')
def _request_api_integration_v1_tariffs(taxi_cargo_matcher):
    async def wrapper(headers=None, request=None):
        headers = headers if headers else HEADERS
        request = request if request else {'start_point': [37.1, 55.1]}
        response = await taxi_cargo_matcher.post(
            '/api/integration/v1/tariffs', headers=headers, json=request,
        )
        return response

    return wrapper


@pytest.fixture(name='request_v1_admin_tariffs')
def _request_v1_admin_tariffs(taxi_cargo_matcher):
    async def wrapper(request=None):
        request = request if request else {'start_point': [37.1, 55.1]}
        response = await taxi_cargo_matcher.post(
            '/v1/admin/tariffs',
            headers={'Accept-Language': 'ru'},
            params={'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2'},
            json=request,
        )
        return response

    return wrapper


async def test_zone_not_found(taxi_cargo_matcher):
    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/tariffs',
        headers=HEADERS,
        json={'start_point': [100, 100]},
    )

    assert response.status_code == 200
    assert response.json() == {'available_tariffs': []}


async def test_current_tariff_not_found(
        request_api_integration_v1_tariffs, mocker_tariff_corp_current,
):
    mocker_tariff_corp_current(
        response={
            'code': 'current_tariff_not_found',
            'message': 'not_found',
            'details': {},
        },
        status=404,
    )

    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert response.json() == {'available_tariffs': []}


@pytest.mark.config(CARGO_MATCHER_TARIFF_CHECK_USER=True)
async def test_user_has_no_tariffs(request_api_integration_v1_tariffs):
    response = await request_api_integration_v1_tariffs(
        headers={
            'Accept-Language': 'ru',
            'X-B2B-Client-Id': '7ff7900803534212a3a66f4d0e114fc2',
            'X-Cargo-Api-Prefix': '/b2b/cargo/integration/',
        },
    )

    assert response.status_code == 200
    assert response.json() == {'available_tariffs': []}


def _get_expected_express_and_cargo_tariffs(
        express_requirements, cargo_requirements,
):
    return {
        'available_tariffs': [
            {
                'minimal_price': 20.0,
                'name': 'express',
                'supported_requirements': express_requirements,
                'text': 'Тариф экспресс',
                'title': 'Экспресс',
            },
            {
                'minimal_price': 20.0,
                'name': 'cargo',
                'supported_requirements': cargo_requirements,
                'text': 'Тариф грузовой',
                'title': 'Грузовой',
            },
        ],
    }


def _get_frontend_headers():
    return {**HEADERS, 'X-Cargo-Api-Prefix': '/api/b2b/cargo-matcher/'}


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
)
async def test_b2b_get_tariffs_success(request_api_integration_v1_tariffs):
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=[],
    )


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
)
async def test_b2b_admin_get_tariffs_success(request_v1_admin_tariffs):
    response = await request_v1_admin_tariffs()

    assert response.status_code == 200, response.json()
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=[],
    )


@pytest.fixture(name='mock_corp_tariffs_with_cargocorp')
def _mock_corp_tariffs_with_cargocorp(mockserver, load_json):
    def wrapper(category_name):
        response = {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('categories_corpcargo.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_series_id_2',
                'date_from': timedelta_dec(hours=12),
                'date_to': timedelta_inc(hours=12),
            },
        }
        response['tariff']['categories'][0]['category_name'] = category_name

        @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
        def _tariffs(request):
            return response

        return _tariffs

    return wrapper


CARGO_REPLACED_BY_CARGOCORP_EXPECTED_TARIFF = {
    'available_tariffs': [
        {
            'name': 'cargo',
            'supported_requirements': [
                {
                    'name': 'cargo_type',
                    'text': 'Требование габаритов транспортного средства',
                    'title': 'Тип кузова',
                    'type': 'select',
                    'required': True,
                    'options': [
                        {
                            'text': (
                                '260 см в длину, 160 в ширину, ' '150 в высоту'
                            ),
                            'title': 'Большой кузов',
                            'value': 'lcv_l',
                        },
                    ],
                },
            ],
            'text': 'Тариф грузовой',
            'title': 'Грузовой',
            'minimal_price': 30,
        },
    ],
}


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_MATCHER_TARIFF_REQUIREMENTS=_TARIFF_REQUIREMENTS_CARGO_TYPE_LCV_L,
)
async def test_b2b_get_tariffs_corpcargo(
        request_api_integration_v1_tariffs,
        mock_corp_tariffs_with_cargocorp,
        conf_exp3_cargocorp_autoreplacement,
):
    await conf_exp3_cargocorp_autoreplacement(is_enabled=True)
    mock_corp_tariffs_with_cargocorp('cargocorp')
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert response.json() == CARGO_REPLACED_BY_CARGOCORP_EXPECTED_TARIFF


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_MATCHER_TARIFF_REQUIREMENTS=_TARIFF_REQUIREMENTS_CARGO_TYPE_LCV_L,
)
async def test_b2b_get_tariffs_corpcargo_disabled(
        request_api_integration_v1_tariffs,
        mock_corp_tariffs_with_cargocorp,
        conf_exp3_cargocorp_autoreplacement,
):
    await conf_exp3_cargocorp_autoreplacement(is_enabled=False)
    mock_corp_tariffs_with_cargocorp('cargo')
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert response.json() == CARGO_REPLACED_BY_CARGOCORP_EXPECTED_TARIFF


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_MATCHER_TARIFF_REQUIREMENTS=_TARIFF_REQUIREMENTS_CARGO_TYPE_LCV_L,
)
async def test_b2b_get_tariffs_corpcargo_wrong_json_exp(
        request_api_integration_v1_tariffs,
        mock_corp_tariffs_with_cargocorp,
        experiments3,
        taxi_cargo_matcher,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_matcher_enable_cargocorp_autoreplacement',
        consumers=['cargo-matcher/estimate'],
        clauses=[],
        default_value={},
    )
    await taxi_cargo_matcher.invalidate_caches()
    mock_corp_tariffs_with_cargocorp('cargo')
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert response.json() == CARGO_REPLACED_BY_CARGOCORP_EXPECTED_TARIFF


@pytest.mark.translations(
    cargo={
        'requirement.cargo_options.title': {'ru': 'Дополнительные опции'},
        'requirement.cargo_options.text': {
            'ru': 'Дополнительные опции доставки',
        },
        'requirement.cargo_options.thermal_pack.title': {'ru': 'Термосумка'},
        'requirement.cargo_options.thermal_pack.text': {
            'ru': 'Сумка для доставки горячих блюд',
        },
    },
)
@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_MATCHER_TARIFF_OPTIONS={
        'thermal_pack': {
            'title_key': 'requirement.cargo_options.thermal_pack.title',
            'text_key': 'requirement.cargo_options.thermal_pack.text',
        },
    },
    CARGO_TARIFF_OPTIONS_EXPERIMENTS={'cargo': 'cargo_tariff_cargo_options'},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_tariff_cargo_options',
    consumers=['cargo-matcher/tariff-options'],
    clauses=[],
    is_config=True,
    default_value={'options': ['thermal_pack']},
)
async def test_b2b_get_tariffs_cargo_options(
        request_api_integration_v1_tariffs,
):
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    cargo_requirements = [
        {
            'name': 'cargo_options',
            'title': 'Дополнительные опции',
            'text': 'Дополнительные опции доставки',
            'type': 'multi_select',
            'required': False,
            'options': [
                {
                    'text': 'Сумка для доставки горячих блюд',
                    'title': 'Термосумка',
                    'value': 'thermal_pack',
                },
            ],
        },
    ]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=cargo_requirements,
    )


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_MATCHER_TARIFF_REQUIREMENTS={
        'cargo_type': {
            'title_key': 'requirement.cargo_type.title',
            'text_key': 'requirement.cargo_type.text',
            'type': 'select',
            'variants': [
                {
                    'name': 'cargo_type.lcv_m',
                    'title_key': 'cargo_type.lcv_m.title',
                    'text_key': 'cargo_type.lcv_m.text',
                    'value': 'lcv_m',
                },
            ],
        },
        'cargo_loaders': {
            'title_key': 'requirement.cargo_loaders.title',
            'text_key': 'requirement.cargo_loaders.text',
            'type': 'select',
            'variants': [
                {
                    'name': 'cargo_loaders',
                    'title_key': 'cargo_loaders.two_loaders.title',
                    'text_key': 'cargo_type.two_loaders.text',
                    'value': 2,
                },
            ],
        },
    },
)
async def test_b2b_get_tariffs_requirements(
        request_api_integration_v1_tariffs,
):
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    cargo_requirements = [
        {
            'name': 'cargo_loaders',
            'text': 'Требование количества грузчиков',
            'title': 'Количество грузчиков',
            'type': 'select',
            'required': False,
            'options': [
                {
                    'text': 'cargo_type.two_loaders.text',
                    'title': 'Два грузчика',
                    'value': 2,
                },
            ],
        },
        {
            'name': 'cargo_type',
            'text': 'Требование габаритов транспортного средства',
            'title': 'Тип кузова',
            'type': 'select',
            'required': True,
            'options': [
                {
                    'text': ('260 см в длину, 160 в ширину, ' '150 в высоту'),
                    'title': 'Средний кузов',
                    'value': 'lcv_m',
                },
            ],
        },
    ]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=cargo_requirements,
    )


def _get_door_to_door_requirement():
    return {
        'default': True,
        'name': 'door_to_door',
        'required': False,
        'text': 'От двери до двери',
        'title': 'От двери до двери',
        'type': 'bool',
    }


def _get_bool_switchable_requirement():
    return {
        'name': 'dynamic_requirement',
        'text': 'Текст требования',
        'title': 'Заголовок требования',
        'type': 'bool',
        'default': False,
        'required': False,
    }


def _get_select_switchable_requirement(select_type):
    return {
        'name': 'dynamic_requirement',
        'options': [
            {'text': 'Текст1', 'title': 'Заголовок1', 'value': 1},
            {'text': 'Текст2', 'title': 'Заголовок2', 'value': 2},
        ],
        'required': False,
        'text': 'Текст требования',
        'title': 'Заголовок требования',
        'type': select_type,
    }


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
)
async def test_b2b_get_tariffs_fronted_check(
        request_api_integration_v1_tariffs,
):
    response = await request_api_integration_v1_tariffs(
        headers=_get_frontend_headers(),
    )

    assert response.status_code == 200
    express_requirements = [_get_door_to_door_requirement()]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
)
@pytest.mark.translations(
    cargo={
        'requirement.add_req1.title': {'ru': 'Заголовок1'},
        'requirement.add_req1.text': {'ru': 'Текст1'},
        'requirement.add_req2.title': {'ru': 'Заголовок2'},
        'requirement.add_req2.text': {'ru': 'Текст2'},
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_matcher_additional_tariff_requirements',
    consumers=['cargo-matcher/additional_tariff_requirements'],
    clauses=[],
    is_config=True,
    default_value={
        'requirements': [
            {
                'type': 'bool',
                'name': 'add_req1',
                'title_tanker_key': 'requirement.add_req1.title',
                'text_tanker_key': 'requirement.add_req1.text',
                'default': False,
                'required': True,
            },
            {
                'type': 'bool',
                'name': 'add_req2',
                'title_tanker_key': 'requirement.add_req2.title',
                'text_tanker_key': 'requirement.add_req2.text',
                'default': True,
                'required': False,
            },
        ],
    },
)
async def test_b2b_get_tariffs_with_additional_requirements(
        request_api_integration_v1_tariffs, experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_matcher_additional_tariff_requirements',
    )

    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200

    expected_requirements = [
        {
            'name': 'add_req1',
            'text': 'Текст1',
            'title': 'Заголовок1',
            'type': 'bool',
            'default': False,
            'required': True,
        },
        {
            'name': 'add_req2',
            'text': 'Текст2',
            'title': 'Заголовок2',
            'type': 'bool',
            'default': True,
            'required': False,
        },
    ]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=expected_requirements,
        cargo_requirements=expected_requirements,
    )

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    assert match_tries[0].kwargs['tariff_class'] == 'cargo'
    assert match_tries[1].kwargs['tariff_class'] == 'express'
    for match_trie in match_tries:
        kw = match_trie.kwargs
        assert kw['corp_client_id'] == CORP_CLIENT_ID
        assert not kw['is_corp_cabinet_request']
        assert kw['nearest_zone'] == 'moscow'


@pytest.mark.config(
    CARGO_MATCHER_CARS=[
        {
            'carrying_capacity_kg': 10,
            'enabled': True,
            'height_cm': 50,
            'length_cm': 80,
            'max_loaders': 0,
            'taxi_class': 'courier',
            'width_cm': 50,
        },
    ],
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY={
        'courier': {
            'title_key': {
                '__default__': 'tariff.courier.title',
                'rus': 'tariff.courier.title.rus',
            },
            'text_key': {'__default__': 'tariff.courier.text'},
        },
    },
)
@pytest.mark.translations(
    cargo={
        'tariff.courier.title': {'ru': 'Курьер'},
        'tariff.courier.text': {'ru': 'Для небольших вещей и документов'},
        'tariff.courier.title.rus': {'ru': 'Стандарт'},
    },
)
async def test_b2b_rename_tariff(
        request_api_integration_v1_tariffs, mockserver, load_json,
):
    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _tariffs(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('categories_with_courier.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert len(response.json()['available_tariffs']) == 1

    available_tariff = response.json()['available_tariffs'][0]
    assert available_tariff['name'] == 'courier'
    assert available_tariff['title'] == 'Стандарт'
    assert available_tariff['text'] == 'Для небольших вещей и документов'


class TestPhoenixGetTariffs:
    @pytest.fixture(autouse=True)
    def init(self, mocker_tariff_current):
        mocker_tariff_current()

    @staticmethod
    def expected_phoenix_tariffs():
        express_requirements = [_get_door_to_door_requirement()]
        return _get_expected_express_and_cargo_tariffs(
            express_requirements=express_requirements, cargo_requirements=[],
        )

    @pytest.fixture
    def mock_cargo_corp(self, mockserver):
        @mockserver.json_handler(
            '/cargo-corp/internal/cargo-corp/v1/client/traits',
        )
        def _mock_cargo_corp(request):
            assert request.headers['X-B2B-Client-Id'] == CORP_CLIENT_ID
            return {'is_small_business': True}

        return _mock_cargo_corp

    async def test_success_phoenix_default_by_storage(
            self, request_api_integration_v1_tariffs, mock_cargo_corp,
    ):
        headers = copy.deepcopy(HEADERS)
        headers['X-B2B-Client-Storage'] = 'cargo'

        response = await request_api_integration_v1_tariffs(headers=headers)

        assert response.status_code == 200
        assert response.json() == self.expected_phoenix_tariffs()

        assert mock_cargo_corp.times_called == 1

    @pytest.mark.experiments3(
        filename='config_force_check_small_business_trait.json',
    )
    @pytest.mark.parametrize('storage', ('taxi', 'cargo'))
    async def test_success_phoenix_force_check(
            self, request_api_integration_v1_tariffs, mock_cargo_corp, storage,
    ):
        headers = copy.deepcopy(HEADERS)
        headers['X-B2B-Client-Storage'] = storage

        response = await request_api_integration_v1_tariffs(headers=headers)

        assert response.status_code == 200
        assert response.json() == self.expected_phoenix_tariffs()

        assert mock_cargo_corp.times_called == 1

    @pytest.mark.config(
        CARGO_SDD_TAXI_TARIFF_SETTINGS={
            'remove_in_tariffs': True,
            'remove_in_admin_tariffs': True,
            'name': 'express',
        },
    )
    async def test_phoenix_same_day_tariff(
            self, request_api_integration_v1_tariffs, mock_cargo_corp,
    ):
        headers = copy.deepcopy(HEADERS)
        headers['X-B2B-Client-Storage'] = 'cargo'

        response = await request_api_integration_v1_tariffs(headers=headers)

        assert response.status_code == 200
        assert len(response.json()['available_tariffs']) == 1

        available_tariff = response.json()['available_tariffs'][0]
        assert available_tariff['name'] == 'cargo'
        assert available_tariff['title'] == 'Грузовой'
        assert available_tariff['text'] == 'Тариф грузовой'


async def test_b2b_get_tariffs_with_bool_switchable_requirements(
        request_api_integration_v1_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api'])

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    express_requirements = [_get_bool_switchable_requirement()]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


async def test_b2b_get_tariffs_with_bool_switchable_requirements_disabled(
        request_api_integration_v1_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['corp_cabinet'])

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=[],
    )


async def test_b2b_get_tariffs_with_bool_switchable_requirements_no_in_tariff(
        request_api_integration_v1_tariffs,
        config_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api', 'corp_cabinet'])
    await config_switchable_requirement(
        config=conftest.get_bool_switchable_req_config(
            requirement='no_in_tariff',
        ),
    )

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=[],
    )


async def test_b2b_get_tariffs_with_switchable_requirements_wrong_exp(
        request_api_integration_v1_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['wrong_value'])

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=[], cargo_requirements=[],
    )


async def test_b2b_get_tariffs_with_bool_switchable_requirements_kwargs(
        request_api_integration_v1_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
        experiments3,
):
    await conf_exp3_switchable_requirement(visible_in=['corp_cabinet', 'api'])
    exp3_recorder = experiments3.record_match_tries(
        'cargo_matcher_switchable_requirement_enabled',
    )

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    assert match_tries[0].kwargs['tariff'] == 'cargo'
    assert match_tries[1].kwargs['tariff'] == 'express'
    for match_trie in match_tries:
        kw = match_trie.kwargs
        assert kw['corp_client_id'] == CORP_CLIENT_ID
        assert not kw['is_c2c']
        assert kw['zone'] == 'moscow'


async def test_b2b_frontend_tariffs_with_bool_switchable_requirements(
        request_api_integration_v1_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['corp_cabinet'])

    response = await request_api_integration_v1_tariffs(
        headers=_get_frontend_headers(),
    )
    assert response.status_code == 200

    express_requirements = [
        _get_door_to_door_requirement(),
        _get_bool_switchable_requirement(),
    ]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


async def test_b2b_frontend_tariffs_with_bool_switchable_requirements_disabled(
        request_api_integration_v1_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=[])

    response = await request_api_integration_v1_tariffs(
        headers=_get_frontend_headers(),
    )
    assert response.status_code == 200

    express_requirements = [_get_door_to_door_requirement()]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


async def test_b2b_get_tariffs_with_select_switchable_requirements(
        request_api_integration_v1_tariffs,
        config_select_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api', 'corp_cabinet'])

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    express_requirements = [_get_select_switchable_requirement('select')]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


async def test_b2b_get_tariffs_with_multiselect_switchable_requirements(
        request_api_integration_v1_tariffs,
        config_multiselect_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api', 'corp_cabinet'])

    response = await request_api_integration_v1_tariffs()
    assert response.status_code == 200

    express_requirements = [_get_select_switchable_requirement('multi_select')]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


async def test_b2b_get_admin_tariffs_with_bool_switchable_requirements(
        request_v1_admin_tariffs,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api'])

    response = await request_v1_admin_tariffs()
    assert response.status_code == 200

    express_requirements = [_get_bool_switchable_requirement()]
    assert response.json() == _get_expected_express_and_cargo_tariffs(
        express_requirements=express_requirements, cargo_requirements=[],
    )


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': False,
        'name': 'cargo',
    },
)
async def test_b2b_remove_sdd_internal_tariffs(
        request_api_integration_v1_tariffs,
):
    response = await request_api_integration_v1_tariffs()

    assert response.status_code == 200
    assert len(response.json()['available_tariffs']) == 1

    available_tariff = response.json()['available_tariffs'][0]
    assert available_tariff['name'] == 'express'
    assert available_tariff['title'] == 'Экспресс'
    assert available_tariff['text'] == 'Тариф экспресс'


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': False,
        'remove_in_admin_tariffs': True,
        'name': 'express',
    },
)
async def test_b2b_remove_sdd_admin_tariffs(request_v1_admin_tariffs):
    response = await request_v1_admin_tariffs()

    assert response.status_code == 200
    assert len(response.json()['available_tariffs']) == 1

    available_tariff = response.json()['available_tariffs'][0]
    assert available_tariff['name'] == 'cargo'
    assert available_tariff['title'] == 'Грузовой'
    assert available_tariff['text'] == 'Тариф грузовой'


async def test_b2b_empty_coordinates_and_address(taxi_cargo_matcher):
    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/tariffs', headers=HEADERS, json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Необходимо передать координаты или топоним точки',
    }


async def test_admin_b2b_empty_coordinates_and_address(taxi_cargo_matcher):
    response = await taxi_cargo_matcher.post(
        '/v1/admin/tariffs',
        headers=HEADERS,
        params={'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2'},
        json={},
    )
    assert response.status_code == 200
    assert response.json()['available_tariffs'] == []


async def test_b2b_undefined_address(
        request_api_integration_v1_tariffs, yamaps,
):
    response = await request_api_integration_v1_tariffs(
        request={'fullname': 'abracadabra'},
    )
    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )


async def test_b2b_admin_undefined_address(request_v1_admin_tariffs, yamaps):
    response = await request_v1_admin_tariffs(
        request={'fullname': 'abracadabra'},
    )
    assert response.status_code == 200
    assert response.json()['available_tariffs'] == []
