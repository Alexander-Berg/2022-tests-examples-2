import unittest.mock

import pytest

from taxi_selfreg import lead_validation
from taxi_selfreg.api import selfreg_v1_eats_lead_create
from taxi_selfreg.generated.service.cities_cache import plugin as cities_cache

VALIDATORS_FIELDS = (
    'first_name',
    'last_name',
    'middle_name',
    'date_of_birth',
    'email',
    'telegram',
)


@pytest.mark.config(
    HIRING_SELFREG_FORMS_CITIZENSHIP_MAPPERS=[
        {
            'salesforce': 'citizenship_ru',
            'selfreg_form': 'RU',
            'zendesk': 'Россия',
        },
    ],
)
@pytest.mark.client_experiments3(
    file_with_default_response='exp3_all_methods_enabled.json',
)
@pytest.mark.config(TVM_RULES=[{'src': 'selfreg', 'dst': 'stq-agent'}])
async def test_lead_create_profile_exist(
        taxi_selfreg,
        mock_hiring_api_v2_leads_create,
        mock_internal_v1_eda_data,
        mock_hsf_vacancy_choose,
        client_experiments3,
        mock_hiring_selfreg_forms,
        patch,
        load_json,
        mongo,
):
    response_body_hiring_api = load_json('response_body_hiring_api.json')
    mock_hiring_api_v2_leads_create(
        response_body_hiring_api['body'], response_body_hiring_api['status'],
    )

    @patch(
        'taxi_selfreg.generated.service.cities_cache.plugin.'
        'CitiesCache.get_city',
    )
    def _get_city(city_name: str):
        return cities_cache.City(
            name='Москва',
            lat=55.45,
            lon=37.37,
            country_id='rus',
            geoarea='moscow',
            region_id='213',
        )

    body = load_json('lead_body.json')
    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    profile = await mongo.selfreg_profiles.find_one({'token': 'token3'})
    for key, value in body.items():
        if key == 'vehicle_type':
            key = 'courier_' + key
        assert value == profile[key]

    exp_res = {'status': 'pending'}
    assert await response.json() == exp_res


@pytest.mark.parametrize(
    'response_name',
    [
        pytest.param('not valid citizenship'),
        pytest.param('not valid vehicle type'),
    ],
)
async def test_not_valid_citizenship_vehicle_type(
        taxi_selfreg,
        mock_hiring_api_v2_leads_create,
        mock_suggests_vehicle_citizen,
        client_experiments3,
        mock_hiring_selfreg_forms,
        mock_personal,
        patch,
        response_name,
        load_json,
):
    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(request):
        assert request.method == 'GET'
        assert request.query.get('region') == 'Москва'
        return load_json('suggested_citizenship_vehicle_type.json')[
            response_name
        ]

    body = load_json('lead_body.json')
    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert content['code'] == '400'
    assert suggests_handler.times_called == 1
    assert (
        content['message']
        == 'not valid citizenship or vehicle type: RU, pedestrian'
    )


@pytest.mark.config(
    HIRING_SELFREG_FORMS_CITIZENSHIP_MAPPERS=[
        {
            'salesforce': 'citizenship_ru',
            'selfreg_form': 'RU',
            'zendesk': 'Россия',
        },
    ],
)
@pytest.mark.client_experiments3(
    file_with_default_response='exp3_all_methods_enabled.json',
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'selfreg', 'dst': 'stq-agent'}],
    SELFREG_ENABLE_FAKE_COURIER_DATA=True,
)
async def test_lead_create_with_only_citizenship(
        taxi_selfreg,
        mock_hiring_api_v2_leads_create,
        mock_internal_v1_eda_data,
        mock_hsf_vacancy_choose,
        client_experiments3,
        mock_hiring_selfreg_forms,
        patch,
        load_json,
        mongo,
):
    response_body_hiring_api = load_json('response_body_hiring_api.json')
    mock_hiring_api_v2_leads_create(
        response_body_hiring_api['body'], response_body_hiring_api['status'],
    )

    body = {'citizenship': 'RU'}
    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    fake_data = load_json('lead_fake_data.json')
    profile = await mongo.selfreg_profiles.find_one({'token': 'token3'})
    for field, value in fake_data.items():
        assert profile[field] == value

    exp_res = {'status': 'pending'}

    assert await response.json() == exp_res


@pytest.mark.client_experiments3(
    file_with_default_response='exp3_all_methods_enabled.json',
)
async def test_lead_create_no_profile(
        taxi_selfreg,
        mock_hiring_api_v2_leads_create,
        client_experiments3,
        mock_hiring_selfreg_forms,
        load_json,
):
    response_body_hiring_api = load_json('response_body_hiring_api.json')
    mock_hiring_api_v2_leads_create(
        response_body_hiring_api['body'], response_body_hiring_api['status'],
    )

    body = load_json('lead_body.json')
    request = load_json('lead_create_request.json')
    request['params']['token'] = 'token7'
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    json_response = await response.json()

    assert json_response['code'] == '401'
    assert json_response['message'] == 'profile with token token7 not found'


async def test_no_city_for_suggested_citizenship(
        taxi_selfreg,
        mock_hiring_api_v2_leads_create,
        client_experiments3,
        mock_hiring_selfreg_forms,
        mock_personal,
        patch,
        load_json,
):
    body = load_json('lead_body.json')
    request = load_json('lead_create_request.json')
    request['params']['token'] = 'token4'
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert content['code'] == '400'
    assert (
        content['message']
        == 'error with city info. There is no data for city Татуин'
    )


@pytest.mark.parametrize(
    'date_of_birth,citizenship,error_code,error_message',
    [
        pytest.param(
            '2010-01-01',
            'RU',
            'field_validation_courier_too_young',
            'Слишком молодой 16',
            id='too_young_16',
        ),
        pytest.param(
            '2010-01-01',
            'KZ',
            'field_validation_courier_too_young',
            'Слишком молодой 18',
            id='too_young_18',
        ),
        pytest.param(
            '1965-01-01',
            'RU',
            'field_validation_courier_too_experienced',
            'Слишком опытный',
            id='too_experienced',
        ),
        pytest.param(
            '123',
            'RU',
            'selfreg_eats.field_validation_wrong_date_of_birth',
            'Неправильная дата рождения',
            id='wrong_format',
        ),
    ],
)
async def test_not_valid_age(
        taxi_selfreg,
        client_experiments3,
        mock_hiring_selfreg_forms,
        date_of_birth,
        citizenship,
        error_code,
        error_message,
        load_json,
        localizations,
):
    body = load_json('lead_body.json')
    body['date_of_birth'] = date_of_birth
    body['citizenship'] = citizenship

    @mock_hiring_selfreg_forms(
        '/v1/eda/suggests/citizenships-and-vehicle-types',
    )
    def suggests_handler(request):
        assert request.method == 'GET'
        return {
            'citizenships': [
                {'id': 'RU', 'name': 'Российская Федерация'},
                {'id': 'KZ', 'name': 'Казахстан'},
            ],
            'vehicle_types': [{'id': 'pedestrian'}],
        }

    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert suggests_handler.times_called == 1

    assert content['status'] == 'error'
    assert content['violations'][0]['error_code'] == error_code
    assert content['violations'][0]['error_message'] == error_message


@pytest.mark.parametrize(
    'telegram,error_code,error_message',
    [
        pytest.param(
            'не_валидный_телеграм',
            'selfreg_eats.field_validation_wrong_telegram',
            'Неправильная телега',
            id='not_valid_telegram_1',
        ),
        pytest.param(
            'not_v@lid',
            'selfreg_eats.field_validation_wrong_telegram',
            'Неправильная телега',
            id='not_valid_telegram_2',
        ),
        pytest.param(
            'shor',
            'selfreg_eats.field_validation_wrong_telegram',
            'Неправильная телега',
            id='not_valid_telegram_3',
        ),
    ],
)
async def test_not_valid_telegram(
        taxi_selfreg,
        client_experiments3,
        mock_hiring_selfreg_forms,
        mock_suggests_vehicle_citizen,
        telegram,
        error_code,
        error_message,
        load_json,
        localizations,
):
    body = load_json('lead_body.json')
    body['telegram'] = telegram
    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert content['status'] == 'error'
    assert content['violations'][0]['error_code'] == error_code
    assert content['violations'][0]['error_message'] == error_message


@pytest.mark.parametrize(
    'telegram,valid',
    [
        pytest.param('не_валидный_телеграм', False, id='not_valid_telegram_1'),
        pytest.param('not_v@lid', False, id='not_valid_telegram_2'),
        pytest.param('shor', False, id='not_valid_telegram_3'),
        pytest.param('  valid_name   ', True, id='valid_telegram_4'),
        pytest.param('  @valid_name_t   ', True, id='valid_telegram_5'),
        pytest.param('@valid_name_5', True, id='valid_telegram_6'),
    ],
)
async def test_telegram_violation(telegram, valid, web_context):
    request = unittest.mock.Mock()
    profile = unittest.mock.Mock()
    request.body.telegram = telegram
    validator = lead_validation.TelegramValidator(
        web_context, request, profile,
    )
    validator.clean()
    assert validator.is_valid() == valid


@pytest.mark.parametrize(
    'telegram,date_of_birth,number_of_violations',
    [
        pytest.param('не_валидный_телеграм', '2010-01-01', 2),
        pytest.param('valid_telegram', '1947-01-01', 1),
    ],
)
async def test_not_valid_a_few_fields(
        taxi_selfreg,
        client_experiments3,
        mock_hiring_selfreg_forms,
        telegram,
        date_of_birth,
        number_of_violations,
        mock_suggests_vehicle_citizen,
        load_json,
        localizations,
):
    body = load_json('lead_body.json')
    body['date_of_birth'] = date_of_birth
    body['telegram'] = telegram

    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert len(content['violations']) == number_of_violations


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfreg_eats_status_error': '9.60'},
        },
    },
)
@pytest.mark.parametrize(
    'email,error_code,error_message',
    [
        pytest.param(
            'неправильная@почта.рф',
            'selfreg_eats.field_validation_wrong_email',
            'Неправильная почта',
            id='not_valid_email_1',
        ),
        pytest.param(
            'not_valid.@ya.ru',
            'selfreg_eats.field_validation_wrong_email',
            'Неправильная почта',
            id='not_valid_email_2',
        ),
        pytest.param(
            'not_valid@@gmail.com',
            'selfreg_eats.field_validation_wrong_email',
            'Неправильная почта',
            id='not_valid_email_3',
        ),
    ],
)
async def test_not_valid_email(
        taxi_selfreg,
        client_experiments3,
        mock_hiring_selfreg_forms,
        mock_suggests_vehicle_citizen,
        email,
        error_code,
        error_message,
        load_json,
        localizations,
):
    body = load_json('lead_body.json')
    body['email'] = email

    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert content['status'] == 'error'
    assert content['violations'][0]['error_code'] == error_code
    assert content['violations'][0]['error_message'] == error_message


@pytest.mark.parametrize(
    'field_name,error_code,error_message',
    [
        pytest.param(
            'first_name',
            'selfreg_eats.field_validation_empty_first_name',
            'Пустое имя',
            id='empty_first_name',
        ),
        pytest.param(
            'last_name',
            'selfreg_eats.field_validation_empty_last_name',
            'Пустая фамилия',
            id='empty_last_name',
        ),
    ],
)
@pytest.mark.parametrize('field_value', ['', '\n \t'])
async def test_empty_fields(
        taxi_selfreg,
        client_experiments3,
        mock_hiring_selfreg_forms,
        mock_suggests_vehicle_citizen,
        field_name,
        error_code,
        error_message,
        load_json,
        localizations,
        field_value,
):
    body = load_json('lead_body.json')
    body[field_name] = field_value

    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert content['status'] == 'error'
    assert content['violations'][0]['error_code'] == error_code
    assert content['violations'][0]['error_message'] == error_message


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'selfreg_eats_status_error': '9.61'},
        },
    },
)
async def test_old_app_version(
        taxi_selfreg,
        client_experiments3,
        mock_hiring_selfreg_forms,
        mock_suggests_vehicle_citizen,
        load_json,
        localizations,
):
    body = load_json('lead_body.json')
    body['email'] = 'неправильная@почта.рф'
    request = load_json('lead_create_request.json')
    response = await taxi_selfreg.post(
        request['path'],
        params=request['params'],
        headers=request['headers'],
        json=body,
    )

    content = await response.json()

    assert content['status'] == 'pending'


def test_validators_clean(web_context, load_json, localizations):
    body = load_json('lead_body_validation.json')
    body_with_whitespaces = load_json('lead_body_with_whitespaces.json')
    request = unittest.mock.Mock()
    profile = unittest.mock.Mock()
    request.middlewares.language_middleware.language = 'ru'
    for field, value in body_with_whitespaces.items():
        setattr(request.body, field, value)
    violations = selfreg_v1_eats_lead_create.update_profile_from_request(
        web_context, request, profile,
    )
    assert violations == []
    for field in VALIDATORS_FIELDS:
        assert getattr(profile, field) == body[field]
    assert profile.courier_fake_data is not True


@pytest.mark.config(SELFREG_ENABLE_FAKE_COURIER_DATA=True)
def test_validators_fake_data(web_context, load_json, localizations):
    request = unittest.mock.Mock()
    profile = unittest.mock.Mock()
    for field in VALIDATORS_FIELDS:
        setattr(request.body, field, None)
    request.middlewares.language_middleware.language = 'ru'
    request.token = 'token'

    violations = selfreg_v1_eats_lead_create.update_profile_from_request(
        web_context, request, profile,
    )

    assert violations == []
    assert profile.date_of_birth == '2000-01-01'
    assert profile.email == 'token@fake.email'
    assert profile.first_name == 'token'
    assert profile.last_name == 'token'
    assert profile.middle_name == ''
    assert profile.telegram == ''
    assert profile.courier_fake_data is True
