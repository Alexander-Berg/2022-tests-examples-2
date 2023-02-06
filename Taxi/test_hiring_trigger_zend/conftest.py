# pylint: disable=wildcard-import, unused-wildcard-import
# pylint: disable=redefined-outer-name, invalid-name

import functools

from aiohttp import web
import pytest

from generated.models import hiring_st as model

import hiring_trigger_zend.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_trigger_zend.generated.service.pytest_plugins']

SERVICE_NAME = 'hiring-trigger-zend'
TVM_DESTINATIONS = [
    'personal',
    'experiments3',
    'hiring-rate-accounting',
    'stq-agent',
]

TEST_VACANCIES = {
    'taxi': {
        'default_supply_settings': {
            'namespace': 'hiring-supply',
            '__default__': {
                'driver': {
                    'unit': 'days',
                    'value': 1,
                    'limit': 0,
                    'priority': 0,
                    'weight': 50,
                },
                'delivery': {
                    'unit': 'days',
                    'value': 1,
                    'limit': 0,
                    'priority': 0,
                    'weight': 50,
                },
            },
            'supply_settings': [
                {
                    'cities': ['Казань'],
                    'vacancies_settings': {
                        'driver': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 0,
                            'weight': 50,
                        },
                        'delivery': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 1,
                            'weight': 50,
                        },
                    },
                },
            ],
        },
        'config_name': 'HIRING_SUPPLY_VACANCIES_LIMITS_BY_CITIES',
        'vacancies': ['driver', 'delivery'],
    },
    'eda': {
        'default_supply_settings': {
            'namespace': 'hiring-supply',
            '__default__': {
                'eda_car': {
                    'unit': 'days',
                    'value': 1,
                    'limit': 0,
                    'priority': 0,
                    'weight': 50,
                },
                'eda_bicycle': {
                    'unit': 'days',
                    'value': 1,
                    'limit': 0,
                    'priority': 0,
                    'weight': 50,
                },
            },
            'supply_settings': [
                {
                    'cities': ['Казань'],
                    'vacancies_settings': {
                        'eda_car': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 0,
                            'weight': 50,
                        },
                        'eda_bicycle': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 1,
                            'weight': 50,
                        },
                    },
                },
                {
                    'cities': ['ПРИОРИТЕТЫ'],
                    'vacancies_settings': {
                        'eda_car': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 0,
                            'weight': 1,
                        },
                        'eda_bicycle': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 1,
                            'weight': 2,
                        },
                    },
                },
                {
                    'cities': ['ВЕСА'],
                    'vacancies_settings': {
                        'eda_car': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 0,
                            'weight': 0,
                        },
                        'eda_bicycle': {
                            'unit': 'days',
                            'value': 1,
                            'limit': 10,
                            'priority': 1,
                            'weight': 100,
                        },
                    },
                },
            ],
        },
        'config_name': 'HIRING_SUPPLY_VACANCIES_LIMITS_BY_CITIES_EDA',
        'vacancies': ['eda_car', 'eda_bicycle'],
    },
}


@pytest.fixture
async def call_st_handler(web_context):
    """Запуск получения данных"""

    async def _wrapper():
        return await web_context.timer_interval.timers['st'].handler()

    return _wrapper


@pytest.fixture
async def build_update_ticket(load_json):
    """Принимает запрос и возвращает обновленный тикет"""

    async def _wrapper(request):
        tickets = load_json('tickets.json')

        ticket = tickets[request.json['ticket_id']]
        assert ticket, 'Тестовый тикет не найден'

        # Обновим поля из запроса
        for field_set in request.json['set']:
            if field_set.get('namespace') == 'ticket':
                ticket[field_set['field']] = field_set['value']
            else:
                for field in ticket['fields']:
                    if field['field'] == field_set['field']:
                        field['value'] = field_set['value']
                        break

        ticket.pop('resolution', None)

        return model.TicketResponse.deserialize(data=ticket)

    return _wrapper


@pytest.fixture
async def build_update_ticket_status_transition_error(load_json):
    """Принимает запрос и ошибку статуса тикета"""

    async def _wrapper(request):
        data = load_json('error_status_transition.json')
        return model.Error.deserialize(data=data), 400

    return _wrapper


@pytest.fixture
def mock_infranaim_api_superjob(mock_infranaim_api):
    def _wrapper(response_code: int = 200):
        @mock_infranaim_api(f'/api/v1/submit/superjob')
        async def handler(request):
            if request.headers['token'] != 'TOKEN_SUPERJOB':
                raise ValueError(request.headers['token'])
            assert request.json.get('params', {}).get('comment')
            return web.json_response(
                {'code': response_code, 'message': '', 'details': ''},
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_infranaim_api_zarplataru(mock_infranaim_api):
    def _wrapper(response_code: int = 200):
        @mock_infranaim_api(f'/api/v1/submit/zarplataru')
        async def handler(request):
            if request.headers['token'] != 'TOKEN_ZARPLATARU':
                raise ValueError(request.headers['token'])
            assert request.json.get('params', {}).get('comment')
            return web.json_response(
                {'code': response_code, 'message': '', 'details': ''},
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_infranaim_api_rabotaru(mock_infranaim_api):
    def _wrapper(response_code: int = 200):
        @mock_infranaim_api(f'/api/v1/submit/rabotaru')
        async def handler(request):
            if request.headers['token'] != 'TOKEN_RABOTARU':
                raise ValueError(request.headers['token'])
            assert request.json.get('params', {}).get('comment')
            return web.json_response(
                {'code': response_code, 'message': '', 'details': ''},
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_infranaim_api_appdrivers(mock_infranaim_api):
    def _wrapper(response_code: int = 200):
        @mock_infranaim_api(f'/api/v1/submit/app_drivers')
        async def handler(request):
            if request.headers['token'] != 'TOKEN_APPDRIVERS':
                raise ValueError(request.headers['token'])
            return web.json_response(
                {'code': response_code, 'message': '', 'details': ''},
                status=response_code,
            )

        return handler

    return _wrapper


def tvm_rules():
    return [
        {'src': SERVICE_NAME, 'dst': _service} for _service in TVM_DESTINATIONS
    ]


def default_supply_settings(type_):
    return TEST_VACANCIES[type_]['default_supply_settings']


def configuration(func):
    @pytest.mark.config(
        TVM_RULES=tvm_rules(),
        INFRANAIM_API_UPDATE_TICKET_PATH='all_tickets',
        HIRING_SUPPLY_EXPERIMENTS_CONFIG={
            'experiments': [
                {
                    'name': 'hiring_supply_populate_fields',
                    'consumer': 'hiring_supply/populate_fields',
                },
            ],
        },
        HIRING_SUPPLY_VACANCIES_LIMITS_BY_CITIES=default_supply_settings(
            'taxi',
        ),
        HIRING_SUPPLY_VACANCIES_LIMITS_BY_CITIES_EDA=default_supply_settings(
            'eda',
        ),
    )
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        await func(*args, **kwargs)

    return wrapped


@pytest.fixture
def request_manage_supply(taxi_hiring_trigger_zend_web):
    async def _wrapper(request, status_code=200):
        response = await taxi_hiring_trigger_zend_web.post(
            '/v1/data/manage-supply', json=request,
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


def update_supply_config(type_, limits, priorities, weights):
    config = default_supply_settings(type_)
    vacancies = TEST_VACANCIES[type_]['vacancies']
    for limit, priority, weight, vacancy in zip(
            limits, priorities, weights, vacancies,
    ):
        config['supply_settings'][0]['vacancies_settings'][vacancy].update(
            {'limit': limit, 'priority': priority, 'weight': weight},
        )
    return config


@pytest.fixture
def update_config(taxi_config, taxi_hiring_trigger_zend_web):
    async def _wrapper(type_, limits, priorities, weights):
        name = TEST_VACANCIES[type_]['config_name']
        config = update_supply_config(type_, limits, priorities, weights)
        taxi_config.set_values({name: config})
        await taxi_hiring_trigger_zend_web.post(
            '/tests/control', json={'invalidate_caches': True},
        )

    return _wrapper


@pytest.fixture
def mock_hiring_api_bulk_create(mock_hiring_api, load_json):
    data = load_json('hiring_api_bulk_create_mock.json')
    for value in data.values():
        for t in value['request']['data']['tickets']:
            comment = t.pop('comment')
            t['comment'] = '\n'.join(comment)

    @mock_hiring_api('/v1/tickets/bulk/create')
    async def _handler(request):
        endpoint = request.query['endpoint']
        assert endpoint in data
        expected = data[endpoint]['request']
        assert request.query['consumer'] == expected['consumer']
        assert request.json == expected['data']
        return data[endpoint]['response']

    return _handler
