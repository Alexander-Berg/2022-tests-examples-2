# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import functools
import random
import typing

from aiohttp import web
import pytest

import hiring_taxiparks_gambling.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_taxiparks_gambling.generated.cron import run_cron  # noqa: I100

pytest_plugins = ['hiring_taxiparks_gambling.generated.service.pytest_plugins']

DB = 'hiring_misc'
DEFAULT_PARK_FILE = 'new_parks.json'
EDA_HANDLER_HUBS = '/eda-education/infranaim_api/v1/exports/courier_hubs.json'
EDA_HANDLER_OAUTH = '/eda-education/oauth/token'
EDA_HANDLER_SERVICES = (
    '/eda-education/infranaim_api/v1/exports/courier_services.json'
)
EDA_OAUTH_FIELDS = ('grant_type', 'client_id', 'client_secret')
EDA_RESPONSE_OAUTH_FILE = 'anakin_response_oauth.json'
EDA_RESPONSE_HUBS_FILE = 'anakin_response_hubs.json'
EDA_RESPONSE_SERVICES_FILE = 'anakin_response_services.json'
FIELD_BILLING_TYPES = 'billing_types'
FIELD_COURIER_HUBS = 'courier_hubs'
FIELD_COURIER_SERVICES = 'courier_services'
FIELD_COURIER_SERVICE_IDS = 'courier_service_ids'
FIELD_SETTINGS = 'settings'
FIELD_PAGE = 'page'
HEADER_AUTH = 'Authorization'


def gen_phone():
    return '+79' + str(random.randint(10 ** 8, 10 ** 9 - 1))


@functools.lru_cache(None)
def personal_response(type_, id_):
    if type_ == 'phone':
        value = gen_phone()
    else:
        value = id_
    response = {'value': value, 'id': id_}
    return response


@pytest.fixture  # noqa: F405
def driver_profiles_mock(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def retrieve_by_license(request):
        return load_json('response_driver_profiles.json')


@pytest.fixture  # noqa: F405
def driver_profiles_fail_mock(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_license',
    )
    def retrieve_by_license(request):
        return web.Response(status=500)


@pytest.fixture  # noqa: F405
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def retrieve_phones_bulk(request):
        type_ = 'phone'
        items = []
        for item in request.json['items']:
            items.append(personal_response(type_, item['id']))
        return {'items': items}

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def retrieve_emails_bulk(request):
        type_ = 'email'
        items = []
        for item in request.json['items']:
            items.append(personal_response(type_, item['id']))
        return {'items': items}


@pytest.fixture(autouse=True)
def mock_personal_license_find(mockserver, license_pd_id='123'):
    """mock personal client"""

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def foo_handler(request):  # pylint: disable=unused-variable
        return {'id': license_pd_id, 'value': request.json['value']}


@pytest.fixture
def run_update_parks():
    async def _run_cron():
        argv = [
            'hiring_taxiparks_gambling.crontasks.update_parks',
            '-d',
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron


@pytest.fixture
def find_parks(web_app_client):
    async def _wrapper(
            query: dict, headers: typing.Optional[dict] = None,
    ) -> dict:
        return await web_app_client.post(
            '/taxiparks/choose', json=query, headers=headers,
        )

    return _wrapper


@pytest.fixture
def full_scan_parks(web_app_client):
    async def _wrapper() -> dict:
        response = await web_app_client.get('/taxiparks/full_scan')
        response_body = await response.json()
        return response_body

    return _wrapper


@pytest.fixture
async def upload_parks(
        load_json, hiring_oldparks_mockserver, run_update_parks,
):
    hiring_oldparks_mockserver(load_json('new_parks.json'))
    await run_update_parks()


def main_configuration(func):
    @pytest.mark.config(  # noqa: F405
        TVM_RULES=[{'dst': 'personal', 'src': 'hiring-taxiparks-gambling'}],
        HIRING_CITIES_MAPPER=[
            {
                'hiring': 'Набережные Челны',
                'taximeter': 'Набережные Челны (Республика Татарстан)',
            },
        ],
        HIRING_INTERNAL_SERVICES=['taximeter', 'salesforce'],
    )
    @pytest.mark.usefixtures('personal')  # noqa: F405
    @pytest.mark.usefixtures('upload_parks')
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture
def simple_secdist(simple_secdist):
    # в нужные секции дописываем свои значения
    simple_secdist['settings_override'].update(
        {
            'ANAKIN_EDA': {
                'grant_type': 'client_credentials',
                'client_id': 'ID',
                'client_secret': 'SECRET',
            },
        },
    )
    return simple_secdist


@pytest.fixture  # noqa: F405
def mock_anakin_oauth(mockserver, load_json):
    @mockserver.json_handler(EDA_HANDLER_OAUTH)
    async def handler(request):
        for field in EDA_OAUTH_FIELDS:
            assert request.json[field]
        return web.json_response(
            load_json(EDA_RESPONSE_OAUTH_FILE), status=200,
        )

    return handler


@pytest.fixture
def mock_anakin_get_services_200(mockserver, load_json):
    @mockserver.json_handler(EDA_HANDLER_SERVICES)
    async def handler(request):
        assert request.headers[HEADER_AUTH]
        page = str(request.query[FIELD_PAGE])
        return web.json_response(
            load_json(EDA_RESPONSE_SERVICES_FILE)[page], status=200,
        )

    return handler


@pytest.fixture
def mock_anakin_get_hubs_200(mockserver, load_json):
    @mockserver.json_handler(EDA_HANDLER_HUBS)
    async def handler(request):
        assert request.headers[HEADER_AUTH]
        page = str(request.query[FIELD_PAGE])
        return web.json_response(
            load_json(EDA_RESPONSE_HUBS_FILE)[page], status=200,
        )

    return handler


@pytest.fixture
def run_courier_cron():
    async def _wrapper(name):
        return await run_cron.main([name, '-t', '0'])

    return _wrapper


@pytest.fixture
def count_sum(load_json):
    def _wrapper(kind):
        _sum = 0
        if kind == 'HUB':
            template = load_json(EDA_RESPONSE_HUBS_FILE)
        else:
            template = load_json(EDA_RESPONSE_SERVICES_FILE)
        for item in template.values():
            if kind == 'HUB':
                for hub in item[FIELD_COURIER_HUBS]:
                    _sum += len(hub[FIELD_COURIER_SERVICE_IDS]) * len(
                        hub[FIELD_BILLING_TYPES],
                    )
            else:
                for service_ in item[FIELD_COURIER_SERVICES]:
                    _sum += len(service_[FIELD_SETTINGS])
        return _sum

    return _wrapper


@pytest.fixture
def run_sf_fetch_territories():
    async def _run_cron():
        argv = [
            'hiring_taxiparks_gambling.crontasks.sf_fetch_territories',
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron


@pytest.fixture
def run_sf_update_hiring_conditions():
    async def _run_cron():
        argv = [
            'hiring_taxiparks_gambling.crontasks.sf_update_hiring_conditions',
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron


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
def mock_salesforce_make_query(mock_salesforce, load_json):
    data = load_json('sf_query_mocks.json')

    @mock_salesforce('/services/data/v50.0/query/')
    async def _handler(request):
        assert request.query['q'] in data
        response = data[request.query['q']]
        return web.json_response(response)

    return _handler


@pytest.fixture
def mock_salesforce_query_next(mock_salesforce, load_json):
    data = load_json('sf_query_mocks.json')

    @mock_salesforce(
        r'/services/data/v50.0/query/(?P<cursor>\w+-\d+)', regex=True,
    )
    async def _handler(request, cursor):
        response = data[cursor]
        return web.json_response(response)

    return _handler


@pytest.fixture
def mock_salesforce_make_query_name(mock_salesforce, load_json):
    def _wrapper(territory_name):
        data = load_json('sf_query_mocks.json')[territory_name]

        @mock_salesforce('/services/data/v50.0/query/')
        async def _handler(request):
            response = data[request.query['q']]
            return web.json_response(response)

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_get_territory(mock_salesforce, load_json):
    responses = load_json('sf_territories.json')

    @mock_salesforce(
        r'/services/data/v50.0/sobjects/Territory2/(?P<sf_id>\w+)', regex=True,
    )
    async def _handler(request, sf_id):
        if sf_id in responses:
            return web.json_response(responses[sf_id])
        return web.HTTPNotFound()

    return _handler


@pytest.fixture
def mock_salesforce_updated(mock_salesforce):
    @mock_salesforce(
        '/services/data/v49.0/sobjects/ParkConditions__c/updated/',
    )
    async def _handler(request):
        assert request.query['start'] == '2018-12-31T23:50:00+03:00'
        assert request.query['end'] == '2019-01-01T15:00:00+03:00'
        return web.json_response(
            {
                'ids': ['must_update', 'must_add'],
                'latestDateCovered': '2020-01-01T00:00:00.000+0000',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_salesforce_deleted(mock_salesforce):
    @mock_salesforce(
        '/services/data/v49.0/sobjects/ParkConditions__c/deleted/',
    )
    async def _handler(request):
        assert request.query['start'] == '2018-12-31T23:50:00+03:00'
        assert request.query['end'] == '2019-01-01T15:00:00+03:00'
        return web.json_response(
            {
                'deletedRecords': [
                    {
                        'deletedDate': '2020-01-01T00:00:00.000+0000',
                        'id': 'must_delete',
                    },
                ],
                'latestDateCovered': '2020-01-02T00:00:00.000+0000',
                'earliestDateAvailable': '2020-01-01T00:00:00.000+0000',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_salesforce_get_hc(mock_salesforce, load_json):

    hiring_condition_types = load_json('hiring_condition_types.json')

    def wrapper(hiring_condition_type):
        hiring_condition = hiring_condition_types[hiring_condition_type]

        @mock_salesforce(
            '/services/data/v49.0/sobjects/ParkConditions__c/{}/'.format(
                hiring_condition_type,
            ),
        )
        async def _handler(request):
            return web.json_response(hiring_condition, status=200)

        return _handler

    return wrapper


@pytest.fixture
def mock_pd_personal(mockserver, response_mock, load_json):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _store_phone(request):
        assert request.json['value'] == '+79876543210'
        return {
            'id': 'eb79288c2399407c8f1319ed6ba5f873',
            'value': '+79876543210',
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def _store_email(request):
        return {
            'id': 'eb79288c2399407c8f1319ed6ba5f874',
            'value': 'jason@fthrtn.com',
        }


@pytest.fixture
def mock_pd_territories(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _get_countries_list(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
                {
                    '_id': 'blr',
                    'phone_code': '37',
                    'phone_max_length': 12,
                    'phone_min_length': 11,
                },
            ],
        }


@pytest.fixture
def choose_handler(web_app_client, load_json):
    request = load_json('requests.json')

    async def wrapper(name):
        response = await web_app_client.post(
            '/v2/hiring-conditions/choose',
            json=request[name],
            headers={'X-External-Service': 'mytest'},
        )
        assert response.status == 200
        return [record for record in await response.json()]

    return wrapper


@pytest.fixture
def mock_experiments3(mockserver, load_json):
    def wrapper(response):
        @mockserver.json_handler('/experiments3/v1/experiments')
        def _handler(request):
            return response

        return _handler

    return wrapper


@pytest.fixture
def filter_experiment(patch, load_json):
    experiment_results = load_json('experiment_results.json')

    def wrapper(name):
        @patch(
            (
                'hiring_taxiparks_gambling.internal.experiments'
                '.request_experiment'
            ),
        )
        async def handler(*args, **kwargs):  # noqa pylint: disable=W0612
            return experiment_results[name]

    return wrapper


@pytest.fixture
def group_experiment(patch, load_json):
    experiment_results = load_json('group_experiment_results.json')
    expected_requests = load_json('group_experiment_requests.json')

    @patch(
        (
            'hiring_taxiparks_gambling.internal.experiments'
            '.request_experiment'
        ),
    )
    async def handler(*args, **kwargs):  # noqa pylint: disable=W0612
        data = kwargs.get('data')
        sf_id = data['sf_id']
        assert data == expected_requests[sf_id]
        return experiment_results[sf_id]


@pytest.fixture
def mock_taximeter_parks(mockserver, load_json):
    responses = load_json('taximeter_responses.json')
    expected_requests = load_json('taximeter_expected_requests.json')

    @mockserver.json_handler(
        r'/taximeter-admin/api/support/park_hiring_options/(?P<park_id>\w+)',
        regex=True,
    )
    async def _handler(request, park_id):
        if request.method == 'GET':
            if park_id in responses:
                return web.json_response(responses[park_id])
            return web.HTTPConflict()
        if request.method == 'POST':
            assert park_id in expected_requests
            assert request.json == expected_requests[park_id]
            return web.HTTPOk()

    return _handler
