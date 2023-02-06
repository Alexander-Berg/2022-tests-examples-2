import functools
import random

import freezegun
import pytest

from hiring_trigger_zend.internal import rate_accounting
from test_hiring_trigger_zend import conftest


def manage_supply_configuration(func):
    @freezegun.freeze_time('2019-10-10T12:00:00')
    @conftest.configuration
    @pytest.mark.client_experiments3(
        file_with_default_response='experiments3.json',
    )
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        await func(*args, **kwargs)

    return wrapped


@pytest.fixture(name='rate_accounting_calculate_default')
def fixture_rate_calculate(
        load_json, hiring_rate_accounting_calculate_mockserver,
):
    response = load_json('response_calculate.json')['default']
    return hiring_rate_accounting_calculate_mockserver(response)


@pytest.fixture(name='rate_accounting_update_default')
def fixture_rate_update(load_json, hiring_rate_accounting_update_mockserver):
    response = load_json('response_update.json')['default']
    return hiring_rate_accounting_update_mockserver(response)


@pytest.fixture(name='default_request')
def fixture_default_request(load_json):
    return load_json('request.json')['default']


@manage_supply_configuration
async def test_should_return_500_if_hiring_rate_accounting_calculate_fails(
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
):
    hiring_rate_accounting_calculate_mockserver(
        load_json('response_calculate.json')['error500'],
    )
    await request_manage_supply(default_request, status_code=500)


@manage_supply_configuration
async def test_should_return_500_if_hiring_rate_accounting_update_fails(
        load_json,
        hiring_rate_accounting_update_mockserver,
        rate_accounting_calculate_default,
        request_manage_supply,
        default_request,
):
    hiring_rate_accounting_update_mockserver(
        load_json('response_update.json')['error500'],
    )
    await request_manage_supply(default_request, status_code=500)


@manage_supply_configuration
async def test_should_return_500_if_hiring_rate_accounting_update_return_400(
        load_json,
        hiring_rate_accounting_update_mockserver,
        rate_accounting_calculate_default,
        request_manage_supply,
        default_request,
):
    hiring_rate_accounting_update_mockserver(
        load_json('response_update.json')['not_unique_request_id'],
    )
    await request_manage_supply(default_request, status_code=500)


@manage_supply_configuration
async def test_should_correct_has_calls_in_hiring_rate_accounting(
        rate_accounting_calculate_default,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
):
    await request_manage_supply(default_request)
    assert rate_accounting_calculate_default.has_calls
    assert rate_accounting_update_default.has_calls


@manage_supply_configuration
@pytest.mark.parametrize(
    'pause, is_last_candidate', [(1.0, True), (0.0, False)],
)
async def test_is_last_candidate(
        load_json,
        hiring_rate_accounting_update_mockserver,
        rate_accounting_calculate_default,
        request_manage_supply,
        default_request,
        pause,
        is_last_candidate,
):
    """
        Should setup is_last_candidate to True
        if hiring_rate_accounting_update return pause more than zero
        Else should setup is_last_candidate to False
    """
    update_response = load_json('response_update.json')['default']
    update_response['statistics']['pause'] = pause
    hiring_rate_accounting_update_mockserver(update_response)
    body = await request_manage_supply(default_request)
    assert body['is_last_candidate'] == is_last_candidate


@manage_supply_configuration
@pytest.mark.parametrize(
    'update_ticket, ticket_data_in_body', [(False, True), (True, False)],
)
async def test_ticket_data_existing(
        load_json,
        rate_accounting_calculate_default,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
        update_ticket,
        ticket_data_in_body,
):
    default_request['update_ticket'] = update_ticket
    body = await request_manage_supply(default_request)
    assert ('ticket_data' in body) == ticket_data_in_body


@manage_supply_configuration
async def test_should_return_empty_vacancy_if_limits_is_zero(
        rate_accounting_calculate_default,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
):
    default_request['city'] = 'ТЕСТ'
    body = await request_manage_supply(default_request)
    assert body['vacancy'] == ''
    assert rate_accounting_calculate_default.has_calls
    assert not rate_accounting_update_default.has_calls


@manage_supply_configuration
async def test_should_return_empty_vacancy_if_not_desired(
        rate_accounting_calculate_default,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
):
    default_request['desired_vacancies'] = ['doesnt_want_anything']
    body = await request_manage_supply(default_request)
    assert body['vacancy'] == ''
    assert rate_accounting_calculate_default.has_calls
    assert not rate_accounting_update_default.has_calls


@manage_supply_configuration
async def test_should_return_vacancy_with_highest_priority(
        rate_accounting_calculate_default,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
):
    default_request['city'] = 'ПРИОРИТЕТЫ'
    body = await request_manage_supply(default_request)
    assert body['vacancy'] == 'eda_bicycle'


@manage_supply_configuration
async def test_should_correct_return_vacancies_with_weights(
        rate_accounting_calculate_default,
        rate_accounting_update_default,
        request_manage_supply,
        default_request,
):
    default_request['city'] = 'ВЕСА'
    highest_weight = lowest_weight = 0
    for _ in range(100):
        body = await request_manage_supply(default_request)
        if body['vacancy'] == 'eda_bicycle':
            highest_weight += 1
        if body['vacancy'] == 'eda_car':
            lowest_weight += 1

    assert highest_weight > lowest_weight


def _generate_params(data, ticket_id):
    params = {item['ticket_param_name']: item['tag'] for item in data}
    return {'params': {**params, 'ticket_id': ticket_id}}


def _prepare_request(data: dict, case: str) -> dict:
    if case not in data:
        request = data['default']
    else:
        request = data[case]
    if not request.get('ticket_id'):
        request['ticket_id'] = str(random.randint(50000, 500500))
    return request


def _generate_settings_set(driver_weight, delivery_weight):
    return {
        'eda_bicycle': {
            'unit': 'days',
            'value': 1,
            'limit': 10,
            'priority': 0,
            'weight': driver_weight,
        },
        'eda_car': {
            'unit': 'days',
            'value': 1,
            'limit': 10,
            'priority': 0,
            'weight': delivery_weight,
        },
    }


@pytest.mark.parametrize(
    'city,citizenship,expected_weights',
    [
        ('Казань', 'UZ', [30, 70]),
        ('Казань', None, [40, 60]),
        ('Казань', 'KZ', [50, 50]),
        ('Москва', 'UZ', [20, 80]),
        ('Москва', 'RU', [10, 90]),
    ],
)
@pytest.mark.client_experiments3(
    file_with_default_response='experiments3.json',
)
async def test_get_settings_set(
        web_context, city, citizenship, expected_weights,
):
    config = {
        'namespace': 'hiring-supply',
        '__default__': _generate_settings_set(10, 90),
        'supply_settings': [
            {
                'cities': ['Москва'],
                'citizenships': ['UZ'],
                'vacancies_settings': _generate_settings_set(20, 80),
            },
            {
                'cities': ['Казань'],
                'citizenships': ['UZ'],
                'vacancies_settings': _generate_settings_set(30, 70),
            },
            {
                'cities': ['Казань'],
                'vacancies_settings': _generate_settings_set(40, 60),
            },
            {
                'cities': ['Казань'],
                'citizenships': ['KZ'],
                'vacancies_settings': _generate_settings_set(50, 50),
            },
        ],
    }
    # pylint: disable=protected-access
    result = rate_accounting.RequestsRateAccounting._get_settings_set(
        city, citizenship, config,
    )
    assert result
    weights = [result['eda_bicycle']['weight'], result['eda_car']['weight']]
    assert weights == expected_weights
