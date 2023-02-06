# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import hiring_data_markup.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_data_markup.generated.service.pytest_plugins']

CONSUMER_EXPERIMENTS = 'hiring_data_markup/flow_experiments'
CONSUMER_FLOW_NAME = 'hiring_data_markup/flow_name'
CONSUMER_MEDIUM = 'hiring_data_markup/add_medium'
CONSUMER_SOURCE = 'hiring_data_markup/add_source'
CONSUMER_STOPPER = 'hiring_data_markup/stopper'
DB = 'hiring_data_markup'
EXP3_RESPONSES = 'exp3_responses.json'
FIELD_ARGS = 'args'
FIELD_CONSUMER = 'consumer'
FIELD_ID = 'id'
FIELD_NAME = 'name'
FIELD_PHONE = 'value'
FIELD_VALUE = 'value'
NAME_RIDES = 'rides_count'
REQUEST_NO_FLOW = 'NO_FLOW'
REQUEST_NO_EXPERIMENTS = 'NO_EXPERIMENTS'
REQUEST_SOURCE_AND_MEDIUM = 'SOURCE_AND_MEDIUM'
REQUEST_SOURCE_AND_STOP = 'SOURCE_AND_STOP'
REQUEST_WITH_LOOPS = 'REQUEST_WITH_LOOPS'
REQUEST_WITH_LOOPS_AND_SKIP_ALL = 'REQUEST_WITH_LOOPS_AND_SKIP_ALL'
ROUTE_PERFORM = '/v1/experiments/perform'
ROUTE_CALCULATE = '/v1/experiments/calculate'
ROUTE_HISTORY_BY_PHONE = '/v1/experiments/history/by-phone'
ROUTE_HISTORY_BY_TICKET_ID = '/v1/experiments/history/by-ticket-id'
SERVICE_NAME = 'hiring-data-markup'
TVM_DESTINATIONS = ['personal', 'experiments3']

MAP_RIDES_ON_REQUEST = {
    1: REQUEST_NO_FLOW,
    2: REQUEST_NO_EXPERIMENTS,
    3: REQUEST_SOURCE_AND_MEDIUM,
    4: REQUEST_SOURCE_AND_STOP,
    5: REQUEST_WITH_LOOPS,
    6: REQUEST_WITH_LOOPS_AND_SKIP_ALL,
}


@pytest.fixture
def mock_request_perform(taxi_hiring_data_markup_web):
    async def _wrapper(request, status_code, params=None):
        response = await taxi_hiring_data_markup_web.post(
            ROUTE_PERFORM, json=request, params=params,
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def mock_request_calculate(taxi_hiring_data_markup_web):
    async def _wrapper(request, status_code):
        response = await taxi_hiring_data_markup_web.post(
            ROUTE_CALCULATE, json=request,
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def mock_request_history_phone(taxi_hiring_data_markup_web):
    async def _wrapper(request, status_code):
        response = await taxi_hiring_data_markup_web.post(
            ROUTE_HISTORY_BY_PHONE, json=request,
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def mock_request_history_ticket_id(taxi_hiring_data_markup_web):
    async def _wrapper(request, status_code):
        response = await taxi_hiring_data_markup_web.post(
            ROUTE_HISTORY_BY_TICKET_ID, json=request,
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def mock_personal_api(mockserver, response_mock, load_json):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _store_phone(request):
        if request.json[FIELD_PHONE] == '+79998887766':
            phone_id = 'fd835ed6a95f44b598cfca688c710c84'
        else:
            phone_id = 'b897ef6c827244b4b4880426eed33162'
        return {FIELD_ID: phone_id, FIELD_PHONE: request.json[FIELD_PHONE]}


@pytest.fixture
def mock_data_markup_experiments3(mockserver, load_json):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        consumer = request.json[FIELD_CONSUMER]
        rides = next(
            (
                item[FIELD_VALUE]
                for item in request.json[FIELD_ARGS]
                if item[FIELD_NAME] == NAME_RIDES
            ),
            None,
        )
        if not rides:
            raise BaseException
        request_name = MAP_RIDES_ON_REQUEST[rides]
        return load_json(EXP3_RESPONSES)[request_name][consumer]

    return _handler


@pytest.fixture
def insert_data_markup_history(pgsql):
    async def _wrapper(date: str):
        with pgsql[DB].cursor() as cursor:
            cursor.execute(
                'INSERT INTO '
                '"hiring_data_markup"."history"('
                '"ticket_id",'
                '"personal_phone_id",'
                '"flow",'
                '"name",'
                '"markup",'
                '"requested_at",'
                '"expires_at",'
                '"created_at"'
                ')'
                'VALUES('
                '\'31337\','
                '\'fd835ed6a95f44b598cfca688c710c84\','
                '\'some_flow\','
                '\'hiring_data_markup_experiment\','
                '\'{"fields": [{"name": "status", "value": "NEWSTATUS"}], '
                '"tags_add": [], "tags_remove": []}\'::JSONB,'
                '\'2020-01-01 12:00:00\','
                '\'2020-01-01 12:00:00\','
                f'\'{date}\''
                ')',
            )
            assert cursor.rowcount

    return _wrapper
