# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import re
import typing
import uuid

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http

import hiring_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_api.internal import constants

pytest_plugins = ['hiring_api.generated.service.pytest_plugins']


DATA_MARKUP_RESPONSE = 'response_data_markup.json'
EXP3_RESPONSES = 'exp3_responses.json'

PERSONAL_FIELDS = ['phone', 'driver_license', 'contact_email', 'Phone']
PERSONAL_ID_FIELDS = [
    'personal_phone_id',
    'personal_license_id',
    'personal_contact_email_id',
]

PROPER_MARKUP = {
    'new_field': 'new_value',
    'false_field': False,
    'false_field_again': False,
    'missing_field': 'missing_value',
    'missing_field_again': 'missing_value_again',
    'empty_string_field': 'empty_string_value',
    'empty_string_field_again': '',
}
QUEUE_CANDIDATES_CREATE = 'hiring_candidates_create_lead'
QUEUE_SALESFORCE_CREATE = 'hiring_send_to_salesforce'
QUEUE_SALESFORCE_UPDATE = 'hiring_send_update_to_salesforce'
QUEUE_INFRANAIM_UPDATE = 'hiring_infranaim_api_updates'
QUEUE_SALESFORCE_OBJECTS = 'hiring_create_salesforce_objects'
SALESFORCE_FIELDS = ['ExternalId__c', 'Phone', 'LastName', 'Status']
SERVICE_NAME = 'hiring-api'

TEST_UUID_REGEXP = re.compile(r'[\da-f]{16}')
X_DELIVERY_ID = 'das3tji43tjgj3j9u484tj3fiewo'


@pytest.fixture
def mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }


@pytest.fixture
def mock_infranaim_api_create(mock_infranaim_api):
    def _wrapper(response_code: int = 200):
        @mock_infranaim_api('/api/v1/submit/to_infranaim_api')
        async def handler(request):
            if request.headers['token'] != 'TOKEN':
                raise ValueError(request.headers['token'])
            return web.json_response(
                {'code': response_code, 'message': '', 'details': ''},
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_salesforce_create(mock_salesforce):
    def _wrapper(
            response_code: int = 201,
            success: bool = True,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce('/services/data/v46.0/sobjects/Lead')
        async def handler(request):
            data = request.json
            for field in SALESFORCE_FIELDS:

                assert data.pop(field)
            assert not data
            return web.json_response(
                {
                    'id': uuid.uuid4().hex,
                    'success': success,
                    'errors': errors or [],
                },
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_salesforce_error(mock_salesforce):
    def _wrapper(
            response_code: int = 400,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce('/services/data/v46.0/sobjects/Lead')
        async def handler(request):
            return web.json_response(
                {'code': 'BAD_REQUEST', 'message': ', '.join(errors)},
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_salesforce_update(mockserver, mock_salesforce):
    def _wrapper(
            lead_id: str,
            response_code: int = 204,
            success: bool = True,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce(
            '/services/data/v46.0/sobjects/Lead/{}'.format(lead_id),
        )
        async def handler(request):
            return mockserver.make_response(
                status=response_code,
                json=[
                    {'message': ', '.join(errors or []), 'errorCode': 'some'},
                ],
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_salesforce_find_lead(mock_salesforce, load_json):
    def _wrapper(lead_id: str = None, response_code: int = 204):
        @mock_salesforce(
            r'/services/data/v46.0/sobjects/Lead/ExternalId__c/(?P<ext_id>\w+)'
            r'',
            regex=True,
        )
        async def handler(request, ext_id):
            assert ext_id
            assert request.query == {'fields': 'Id'}
            if not lead_id:
                return web.json_response(
                    {
                        'errorCode': 'NOT_FOUND',
                        'message': 'The requested resource does not exist',
                    },
                )
            return web.json_response({'Id': lead_id})

        return handler

    return _wrapper


@pytest.fixture
def mock_salesforce_make_query(mock_salesforce):
    def _wrapper(response):
        @mock_salesforce('/services/data/v50.0/query/')
        async def _handler(request):
            return response

        return _handler

    return _wrapper


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
def mock_sf_objects_lead(mock_salesforce):
    def _wrapper(
            expected_objects: dict,
            response_code: int = 201,
            success: bool = True,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce('/services/data/v46.0/sobjects/Lead/')
        async def handler(request):
            if response_code > 201:
                return web.json_response(
                    {'id': '', 'success': False, 'errors': []},
                    status=response_code,
                )
            data = request.json
            assert data
            assert expected_objects['Lead'].items() == data.items()
            return web.json_response(
                {'id': 'ID', 'success': success, 'errors': errors or []},
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_sf_objects_lead_update(mock_salesforce):
    def _wrapper(expected_objects: dict, response_code: int = 204):
        @mock_salesforce('/services/data/v50.0/sobjects/Lead/ID')
        async def handler(request):
            if response_code > 204:
                return {'id': '', 'success': False, 'errors': []}
            data = request.json
            assert data
            assert expected_objects['LeadUpdate'].items() == data.items()
            return web.json_response({}, status=response_code)

        return handler

    return _wrapper


@pytest.fixture
def mock_sf_objects_account_update(mock_salesforce):
    def _wrapper(expected_objects: dict, response_code: int = 204):
        @mock_salesforce('/services/data/v50.0/sobjects/Account/ID')
        async def handler(request):
            if response_code > 204:
                return {'id': '', 'success': False, 'errors': []}
            data = request.json
            assert data
            assert expected_objects['AccountUpdate'].items() == data.items()
            return web.json_response({}, status=response_code)

        return handler

    return _wrapper


@pytest.fixture
def mock_sf_objects_asset(mock_salesforce):
    def _wrapper(
            expected_objects: dict,
            response_code: int = 201,
            success: bool = True,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce('/services/data/v46.0/sobjects/Asset/')
        async def handler(request):
            if response_code > 201:
                return {'id': '', 'success': False, 'errors': []}
            data = request.json
            assert data
            assert expected_objects['Asset'].items() == data.items()
            return web.json_response(
                {
                    'id': uuid.uuid4().hex,
                    'success': success,
                    'errors': errors or [],
                },
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_personal_api(mockserver, response_mock, load_json):
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def _retrieve_license(request):
        assert request.json == {'id': 'bc8f4061436b47be8291cf1a753a7fc6'}
        return {
            'id': 'bc8f4061436b47be8291cf1a753a7fc6',
            'value': '12TK123456',
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def _store_license(request):
        assert request.json == {'value': '12TK123456', 'validate': True}
        return {
            'id': 'bc8f4061436b47be8291cf1a753a7fc6',
            'value': '12TK123456',
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _retrieve_phone(request):
        assert 'id' in request.json
        id_ = request.json['id']
        if id_ == '3c88e61e9c6c44a29f2a04294b337fb0':
            value = '+79998'
        elif id_ == 'fd835ed6a95f44b598cfca688c710c84':
            value = '+79998887766'
        else:
            raise ValueError(id_)
        return {'id': id_, 'value': value}

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _retrieve_email(request):
        assert request.json == {'id': 'eb79288c2399407c8f1319ed6ba5f873'}
        return {
            'id': 'eb79288c2399407c8f1319ed6ba5f873',
            'value': 'email@email.com',
        }

    @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
    def _retrieve_yandex_login(request):
        assert request.json == {'id': 'test_personal_yandex_login_id'}
        return {
            'id': 'test_personal_yandex_login_id',
            'value': 'test_personal_yandex_login',
        }

    @mockserver.json_handler('/personal/v1/phones/store')
    def _store_phone(request):
        assert request.json == {'value': '+79998887766', 'validate': True}
        return {
            'id': 'fd835ed6a95f44b598cfca688c710c84',
            'value': '+79998887766',
        }

    @mockserver.json_handler('/personal/v1/emails/store')
    def _store_email(request):
        assert request.json == {'value': 'email@email.com', 'validate': True}
        return {
            'id': 'eb79288c2399407c8f1319ed6ba5f873',
            'value': 'email@email.com',
        }


@pytest.fixture
def mock_hiring_data_markup(mockserver, load_json):
    @mockserver.json_handler('/hiring-data-markup/v1/experiments/perform')
    async def _handler(request):
        fields = {
            field['name']: field['value'] for field in request.json['fields']
        }
        if 'object' in fields:
            _object = fields['object']
            case = 'valid'
            if fields['markup'] == 'No markup':
                case = 'invalid'
            response_body = load_json(DATA_MARKUP_RESPONSE)[case][_object]
            return web.json_response(response_body, status=200)
        if fields.get(constants.FIELD_NAME) == 'No markup':
            response_body = load_json('response_data_markup.json')['invalid']
        else:
            response_body = load_json('response_data_markup.json')['valid']
        return web.json_response(response_body, status=200)

    return _handler


@pytest.fixture
def mock_hiring_data_markup_by_flow(mockserver):
    def _wrapper(responses_by_flows: typing.Dict[str, dict], status=200):
        @mockserver.json_handler('/hiring-data-markup/v1/experiments/perform')
        async def _handler(request: http.Request):
            assert request
            return mockserver.make_response(
                json=responses_by_flows[request.json.get('flow')],
                status=status,
            )

        return _handler

    return _wrapper


@pytest.fixture
def request_tickets_create(taxi_hiring_api_web):
    async def _wrapper(request, endpoint, status_code=200):
        response = await taxi_hiring_api_web.post(
            '/v1/tickets/create',
            json=request,
            params={'endpoint': endpoint},
            headers={'X-Delivery-Id': X_DELIVERY_ID},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def request_tickets_upsert(taxi_hiring_api_web):
    async def _wrapper(request, endpoint, status_code=200):
        response = await taxi_hiring_api_web.post(
            '/v1/tickets/upsert',
            json=request,
            params={'endpoint': endpoint},
            headers={'X-Delivery-Id': X_DELIVERY_ID},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def request_leads_create_sync(taxi_hiring_api_web):
    async def _wrapper(request, endpoint, status_code=200):
        response = await taxi_hiring_api_web.post(
            '/v1/leads/create-sync',
            json=request,
            params={'endpoint': endpoint},
            headers={'X-Delivery-Id': X_DELIVERY_ID},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def request_tickets_bulk_create(taxi_hiring_api_web):
    async def _wrapper(request, endpoint, consumer, status_code=200):
        response = await taxi_hiring_api_web.post(
            '/v1/tickets/bulk/create',
            json=request,
            params={'endpoint': endpoint, 'consumer': consumer},
            headers={'X-Delivery-Id': X_DELIVERY_ID},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def request_tickets_update(taxi_hiring_api_web):
    async def _wrapper(request, endpoint, status_code=200):
        params = {'endpoint': endpoint}
        response = await taxi_hiring_api_web.post(
            '/v1/tickets/update',
            json=request,
            params=params,
            headers={'X-Delivery-Id': X_DELIVERY_ID},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def request_objects_create(taxi_hiring_api_web):
    async def _wrapper(request, endpoint, status_code=201):
        response = await taxi_hiring_api_web.post(
            '/v1/objects/create',
            json=request,
            params={'endpoint': endpoint},
            headers={'X-Delivery-Id': X_DELIVERY_ID},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


def is_uuid_string(string):
    return bool(re.match(TEST_UUID_REGEXP, string))


def check_personal_fields(fields):
    for field in PERSONAL_FIELDS:
        assert field not in fields
    for field in PERSONAL_ID_FIELDS:
        if field in fields:
            assert is_uuid_string(fields[field])


@pytest.fixture
def stq_mock(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _wrapper(*args, queue_name, **kwargs):
        request = args[0].json
        if queue_name in [QUEUE_SALESFORCE_CREATE, QUEUE_SALESFORCE_UPDATE]:
            fields: dict = request['kwargs']['body']
            if queue_name == QUEUE_SALESFORCE_UPDATE:
                assert request['kwargs']['lead_id']
        elif queue_name == QUEUE_SALESFORCE_OBJECTS:
            for kwarg in ('objects', 'dynamic_flow', 'external_id'):
                assert request['kwargs'][kwarg]
            for sf_object in request['kwargs']['objects']:
                fields = sf_object['fields']
                assert fields
                assert isinstance(fields, list)
                for field in fields:
                    assert isinstance(field, dict)
                    for key in ('name', 'value'):
                        assert key in field
            return {}
        elif queue_name == QUEUE_CANDIDATES_CREATE:
            for kwarg in ('external_id', 'personal_phone_id'):
                assert request['kwargs'][kwarg]
            return {}
        else:
            fields: dict = request['kwargs']['ticket_data']['params']
            external_id = fields.get('external_id')
            assert external_id
        assert PROPER_MARKUP.items() <= fields.items()
        check_personal_fields(fields)
        assert '' not in fields
        return {}

    return _wrapper


@pytest.fixture
def mock_stq_queue(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _wrapper(request, queue_name):
        return {}

    return _wrapper


@pytest.fixture
def timeout_hiring_rate_calculate(mockserver):
    @mockserver.handler('/hiring-rate-accounting/v1/statistics/calculate')
    def handle(request):
        raise mockserver.TimeoutError()

    return handle


@pytest.fixture
def hiring_rate_calculate(mockserver):
    @mockserver.handler('/hiring-rate-accounting/v1/statistics/calculate')
    def handle(request):
        return web.json_response(
            {
                'statistics': {
                    'namespace': 'eats-taxi-selfreg',
                    'metric': '1',
                    'counters': [],
                },
            },
            status=200,
        )

    return handle


@pytest.fixture
def timeout_hiring_rate_update(mockserver):
    @mockserver.handler('/hiring-rate-accounting/v1/statistics/update')
    def handle(request):
        raise mockserver.TimeoutError()

    return handle


@pytest.fixture
def mock_hiring_partners_app(mockserver):
    @mockserver.handler('/hiring-partners-app/v1/users/user-by-invite-code')
    def handle(request):
        return web.json_response(
            {'personal_yandex_login_id': 'test_personal_yandex_login_id'},
            status=200,
        )

    return handle


@pytest.fixture
def hiring_rate_update(mockserver):
    @mockserver.handler('/hiring-rate-accounting/v1/statistics/update')
    def handle(request):
        return web.json_response(
            {
                'statistics': {
                    'namespace': 'eats-taxi-selfreg',
                    'metric': '1',
                    'counters': [],
                    'pause': 0.0,
                },
            },
            status=200,
        )

    return handle


@pytest.fixture
def mock_data_markup_experiments3(mockserver, load_json):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        objects_flow = next(
            (
                item['value']
                for item in request.json['args']
                if item['name'] == 'objects_flow'
            ),
            None,
        )
        if not objects_flow:
            raise BaseException
        return load_json(EXP3_RESPONSES)[objects_flow]

    return _handler


@pytest.fixture
def mock_gambling_territories(mock_hiring_taxiparks_gambling, mockserver):
    def _wrapper(response, status):
        @mock_hiring_taxiparks_gambling('/v2/territories/')
        def _handler(request):
            return mockserver.make_response(status=status, json=response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_gambling_get_territory(
        mock_hiring_taxiparks_gambling, load_json, mockserver,
):
    response = load_json('gambling_get_territory_response.json')

    @mock_hiring_taxiparks_gambling(
        r'/v2/territories/(?P<sf_id>\w+)', regex=True,
    )
    def _handler(request, sf_id):
        if sf_id not in response:
            return web.json_response(
                {'code': 'NOT_FOUND', 'message': 'Territory Not Found'},
                status=404,
            )
        return response[sf_id]

    return _handler


@pytest.fixture
def timeout_gambling_territories(mock_hiring_taxiparks_gambling, mockserver):
    @mock_hiring_taxiparks_gambling('/v2/territories/', prefix=True)
    def _handler(request):
        raise mockserver.TimeoutError()

    return _handler


@pytest.fixture
async def salesforce(mockserver):
    @mockserver.json_handler('/salesforce/services/oauth2/token')
    def auth(_):  # pylint: disable=W0612
        data = {
            'access_token': 'test_access_token',
            'instance_url': 'test_instance_url',
            'id': 'test_id',
            'token_type': 'test_token_type',
            'issued_at': 'test_issued_at',
            'signature': 'test_signature',
        }
        return data

    @mockserver.json_handler('/salesforce/services/data/v46.0/sobjects/Lead')
    def create(_):  # pylint: disable=W0612
        data = {'id': '00T0E00000FYSG4UAP', 'success': True, 'errors': []}
        return mockserver.make_response(json=data, status=201)


@pytest.fixture
def mock_salesforce_composite(mock_salesforce, load_json):
    sf_composite_response = load_json('sf_composite_response.json')

    def _wrapper(response_code: int = 200):
        @mock_salesforce('/services/data/v52.0/composite')
        def _handle(request):
            if response_code == 200:
                return sf_composite_response['200']
            if response_code == 403:
                return sf_composite_response['403']
            return sf_composite_response['4xx']

        return _handle

    return _wrapper


@pytest.fixture
def mock_salesforce_composite_error(mock_salesforce):
    def _wrapper(
            response_code: int = 400,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce('/services/data/v52.0/composite')
        async def handler(request):
            return web.json_response(
                [{'code': 'BAD_REQUEST', 'message': ', '.join(errors)}],
                status=response_code,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_salesforce_jobs_error(mock_salesforce):
    def _wrapper(
            response_code: int = 400,
            errors: typing.Optional[typing.List[str]] = None,
    ):
        @mock_salesforce(
            r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)', regex=True,
        )
        async def handler(request, job_id):
            return web.json_response(
                [{'code': 'BAD_REQUEST', 'message': ', '.join(errors)}],
                status=response_code,
            )

        return handler

    return _wrapper


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
def mock_salesforce_job_info(mock_salesforce):
    def _wrapper(response):
        @mock_salesforce(
            r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)', regex=True,
        )
        async def _handler(request, job_id):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_successful(mockserver, mock_salesforce):
    def _wrapper(response):
        @mock_salesforce(
            (
                r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)/'
                'successfulResults/'
            ),
            regex=True,
        )
        async def _handler(request, job_id):
            return mockserver.make_response(
                response=response, status=200, content_type='text/csv',
            )

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_failed(mockserver, mock_salesforce):
    def _wrapper(response):
        @mock_salesforce(
            r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)/failedResults/',
            regex=True,
        )
        async def _handler(request, job_id):
            return mockserver.make_response(
                response=response, status=200, content_type='text/csv',
            )

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_unprocessed(mockserver, mock_salesforce):
    def _wrapper(response):
        @mock_salesforce(
            (
                r'/services/data/v52.0/jobs/ingest/(?P<job_id>\w+)/'
                'unprocessedrecords/'
            ),
            regex=True,
        )
        async def _handler(request, job_id):
            return mockserver.make_response(
                response=response, status=200, content_type='text/csv',
            )

        return _handler

    return _wrapper


@pytest.fixture
def mock_hiring_candidates_eda_channel(  # pylint: disable=invalid-name
        mockserver, mock_hiring_candidates_py3,
):
    def _wrapper(response, status=200):
        @mock_hiring_candidates_py3('/v1/eda/channel')
        def _handler(request):
            return mockserver.make_response(json=response, status=status)

        return _handler

    return _wrapper


@pytest.fixture
def mock_hiring_candidates_region(mockserver, mock_hiring_candidates_py3):
    def _wrapper(response, status=200):
        @mock_hiring_candidates_py3('/v1/region-by-phone')
        def _handler(request):
            assert request
            return mockserver.make_response(json=response, status=status)

        return _handler

    return _wrapper
