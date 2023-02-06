# pylint: disable=redefined-outer-name
import typing

import pytest

from test_hiring_candidates import conftest


ROUTE = '/v1/leads/list'

GAMBLING_RESPONSE_FILE = 'park_condition_bulk.json'
LIST_OF_VALUES_MAP = {
    'vacancies': 'vacancy',
    'personal_user_login_creator_id_in': 'user_login_creator',
}


def _check_list_of_values(leads: typing.List[dict], params: dict):
    query = {
        LIST_OF_VALUES_MAP[key]: value
        for key, value in params.items()
        if isinstance(value, list)
    }
    for lead in leads:
        for field in lead['fields']:
            name = field['name']
            if name in query:
                assert field['value'] in query[name]


async def _generate_leads_fetch_config(config_raw: dict):
    return {
        consumer: setting
        for setting in config_raw['settings']
        for consumer in setting['consumers']
    }


@pytest.mark.usefixtures('fill_initial_data')
@pytest.mark.parametrize(
    'request_name',
    [
        'default',
        'default_2',
        'by_status',
        'full',
        'by_customer',
        'date_lte_ok',
        'empty_date_lte_fail',
        'wrong_params',
        'wrong_params_bad_consumer',
        'fallback_default_settings',
        'list_of_values',
        'all_extra_fields',
        'one_extra_field',
    ],
)
@conftest.main_configuration
async def test_get_leads(
        taxi_hiring_candidates_web,
        load_json,
        request_name,
        taxi_config,
        mock_hiring_taxiparks_gambling,
):
    request = load_json('requests.json')[request_name]

    @mock_hiring_taxiparks_gambling('/v2/territories/bulk_post')
    def _mock(request_bulk):
        assert request_bulk.method == 'POST'
        assert set(request_bulk.json['region_ids']) == set(
            request['expected_region_ids'],
        )
        return request['territories_response']

    @mock_hiring_taxiparks_gambling('/v2/hiring-conditions/bulk_post')
    def _park_conditions(request_bulk):
        assert set(request_bulk.json['sf_ids']) == set(
            request['expected_park_condition_ids'],
        )
        return load_json(GAMBLING_RESPONSE_FILE)[request_name]

    async def make_request(params, consumer, code):
        _response = await taxi_hiring_candidates_web.post(
            ROUTE, json=params, headers={'X-Consumer-Id': consumer},
        )
        assert _response.status == code
        return _response

    response = await make_request(
        params=request['params'],
        code=request['code'],
        consumer=request['consumer'],
    )
    body = await response.json()

    if request['code'] != 200:
        return
    if request_name.startswith('empty'):
        assert not body['leads']
        return

    assert body['leads'] == request['expected_body']['leads']
    if request_name == 'fallback_default_settings':
        return
    config_all = await _generate_leads_fetch_config(
        taxi_config.get('HIRING_CANDIDATES_GET_LEADS_SETTINGS'),
    )
    config = config_all[request['consumer']]
    for lead in body['leads']:
        fields = {
            field_obj['name']: field_obj['value']
            for field_obj in lead['fields']
        }
        for search_field in config['required_search_fields']:
            if search_field == 'statuses':
                continue
            value = fields.get(search_field)
            assert value == request['params'][search_field]
    if request_name == 'list_of_values':
        _check_list_of_values(body['leads'], request['params'])


@pytest.mark.parametrize(
    'request_name',
    ['status', 'active', 'external_id', 'activator_check_filtered'],
)
@pytest.mark.usefixtures('fill_initial_data')
@conftest.main_configuration
async def test_active_status_external_id(
        taxi_hiring_candidates_web, load_json, request_name,
):
    request = load_json('requests.json')[request_name]

    response = await taxi_hiring_candidates_web.post(
        ROUTE,
        json=request['params'],
        headers={'X-Consumer-Id': request['consumer']},
    )

    assert response.status == request['code']

    body = await response.json()
    assert body == request['expected_body']


@pytest.mark.parametrize(
    'request_name', ['pagination_1', 'pagination_2', 'pagination_3'],
)
@pytest.mark.usefixtures('fill_initial_data')
async def test_pagination(taxi_hiring_candidates_web, load_json, request_name):
    request = load_json('requests.json')[request_name]

    response = await taxi_hiring_candidates_web.post(
        ROUTE,
        json=request['params'],
        headers={'X-Consumer-Id': request['consumer']},
    )
    body = await response.json()

    assert body == request['expected_body']


@pytest.mark.parametrize(
    'request_name',
    [
        'user_by_date_active',
        'user_by_employment_types',
        'user_by_cities_and_tariffs',
        'user_by_cities',
        'user_by_tariffs',
        'user_by_source_park_db_ids',
    ],
)
@pytest.mark.usefixtures('fill_initial_data')
@conftest.main_configuration
async def test_partners_app_filters(
        taxi_hiring_candidates_web, load_json, request_name,
):
    request = load_json('requests.json')[request_name]

    response = await taxi_hiring_candidates_web.post(
        ROUTE,
        json=request['params'],
        headers={'X-Consumer-Id': request['consumer']},
    )

    assert response.status == request['code']

    body = await response.json()
    assert body == request['expected_body']


@pytest.mark.translations(
    hiring_suggests={
        'employment_type.self_employed': {
            'ru': 'Тип занятости',
            'en': 'Employment Type',
        },
        'status.active_5': {'ru': 'Активен 5'},
        'tariff.comfort': {'ru': 'Комфорт', 'en': 'Comfort'},
        'car_colors.black': {'ru': 'Чёрный', 'en': 'Black'},
    },
)
@pytest.mark.parametrize(
    'request_name',
    [
        'translate_default_ru',
        'translate_empty_fields',
        'translate_not_full_en',
    ],
)
@pytest.mark.usefixtures('fill_initial_data')
async def test_translate(
        taxi_hiring_candidates_web,
        load_json,
        request_name,
        mock_hiring_taxiparks_gambling,
):
    request = load_json('requests.json')[request_name]

    @mock_hiring_taxiparks_gambling('/v2/territories/bulk_post')
    def _mock(request_bulk):
        assert request_bulk.method == 'POST'
        assert set(request_bulk.json['region_ids']) == set(
            request['expected_region_ids'],
        )
        return request['territories_response']

    response = await taxi_hiring_candidates_web.post(
        ROUTE,
        json=request['params'],
        headers={'X-Consumer-Id': request['consumer']},
    )
    body = await response.json()
    assert body == request['expected_body']
