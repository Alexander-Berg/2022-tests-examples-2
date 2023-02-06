import typing

from aiohttp import web
import pytest

import hiring_telephony_oktell_callback.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'hiring_telephony_oktell_callback.generated.service.pytest_plugins',
]


CREATE = 'request_create_tasks.json'


@pytest.fixture
def mock_salesforce_auth(mock_salesforce):
    @mock_salesforce('/services/oauth2/token')
    async def _handler(request):
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': 'URL',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_salesforce_upload_data(mockserver):
    @mockserver.handler(
        r'/salesforce/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)/batches',
        regex=True,
    )
    async def _handler(request, job_id):
        return web.Response(status=201)

    return _handler


@pytest.fixture
def mock_salesforce_create_bulk_job(mock_salesforce):
    def _wrapper(response: dict):
        @mock_salesforce('/services/data/v52.0/jobs/ingest')
        async def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_close_bulk_job(mock_salesforce):
    @mock_salesforce(
        r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)', regex=True,
    )
    async def _handler(request, job_id):
        return {}

    return _handler


@pytest.fixture
def send_event(mockserver, mock_hiring_sf_events):
    def _wrapper(code, msg):
        @mock_hiring_sf_events('/v1/send-event')
        def _handler(request):
            return mockserver.make_response(
                status=code[request.json['task_id']],
                json=msg[request.json['task_id']],
            )

        return _handler

    return _wrapper


@pytest.fixture
def create_tasks(web_app_client):  # pylint: disable=W0621
    async def _do_it(request):
        assert request
        return await web_app_client.post(
            '/v1/tasks/create', json={'tasks': request['tasks']},
        )

    return _do_it


@pytest.fixture  # noqa: F405
def geobase(mockserver, load_json):
    def _wrapper():
        @mockserver.json_handler('/geobase/v1/region_by_id')
        async def region_by_id(request):  # pylint: disable=unused-variable
            data = load_json('geobase_response.json')
            return data

        return region_by_id

    return _wrapper


@pytest.fixture
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def phones_retrieve(request):
        return {
            'id': 'd0b8374506614a95a9b347b1cf747c0c',
            'value': '+79998887766',
        }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/store')
    def phones_store(request):
        return {
            'id': 'd0b8374506614a95a9b347b1cf747c0c',
            'value': '+79998887766',
        }


@pytest.fixture
def mock_solomon(mockserver):
    def _wrapper():
        @mockserver.json_handler('/solomon/')
        async def _handler(request):
            return {}

        return _handler

    return _wrapper


@pytest.fixture
def _check_dates():
    def _do_it(task: dict):
        for key in [
                'archived_at_dt',
                'created_at_dt',
                'deleted_at_dt',
                'expires_at_dt',
                'rots_at_dt',
                'task_state_dt',
                'updated_at_dt',
        ]:
            assert task[key]

    return _do_it


@pytest.fixture
def _check_call_intervals():
    def _do_it(call_intervals: typing.List[dict]):
        for interval in call_intervals:
            for subkey in ['from', 'to']:
                assert interval[subkey]

    return _do_it


@pytest.fixture
def ensure_results(_check_dates, _check_call_intervals):
    def _do_it(check, response):
        for task in check['results']:
            response_task = next(
                (
                    item
                    for item in response['results']
                    if item['task_id'] == task['task_id']
                ),
                None,
            )
            assert response_task
            _check_dates(response_task)
            call_intervals = response_task.pop('call_intervals', None)
            assert call_intervals
            _check_call_intervals(call_intervals)
            assert task.items() <= response_task.items()
        assert check['next_cursor'] == response['next_cursor']

    return _do_it


@pytest.fixture
def composite_lead_task(mockserver, load_json):
    def _wrapper(response):
        @mockserver.json_handler('/hiring-api/v2/composite/lead-task')
        async def handler(request):
            return response

        return handler

    return _wrapper
