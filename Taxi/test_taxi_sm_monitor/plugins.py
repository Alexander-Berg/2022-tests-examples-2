# pylint: disable=redefined-outer-name
import datetime

from aiohttp import web
import pytest

from taxi import discovery
from taxi.maintenance import run

from taxi_sm_monitor import app_stq
from taxi_sm_monitor import cron_run


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'FACEBOOK_CSRF_TOKEN': 'fb_csrf_token',
            'FACEBOOK_PAGE_TOKENS': {
                '1960892827353514': 'test_token',
                '563720454066049': 'acc_token',
                '563720454066048': 'acc_token',
            },
            'FACEBOOK_APP_SECRET': '714a4a3d7ebbdf573700763346fda495',
            'GOOGLE_PLAY_SERVICE_SECRETS': {
                'ru.yandex.uber': {
                    'type': 'service_account',
                    'project_id': 'app-4441',
                    'private_key_id': (
                        'd82555c1e1b4956a6b56f1111c865684ef3331af'
                    ),
                    'private_key': (
                        '-----BEGIN PRIVATE KEY-----\n\n+34megNGa2'
                        'zXwMrJajQ==\n-----END PRIVATE KEY-----\n'
                    ),
                    'client_email': 'as3@case-736.iam.gserviceaccount.com',
                    'client_id': '514213521220433372233',
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                },
            },
            'STARTRACK_API_PROFILES': {
                'support-taxi': {
                    'url': 'http://test-startrack-url/',
                    'org_id': 0,
                    'oauth_token': 'some_startrack_token',
                },
                'support-zen': {
                    'url': 'http://zen.test-startrack-url/',
                    'org_id': 1,
                    'oauth_token': 'some_startrack_token_zen',
                },
            },
            'YOUSCAN_TOPIC_GROUP_SWITCH_TO_SUPPORTAI': {
                'taxi': True,
                'zen': True,
            },
        },
    )
    return simple_secdist


@pytest.fixture
def taxi_sm_monitor_app(web_app):
    return web_app


@pytest.fixture
def taxi_sm_monitor_client(aiohttp_client, taxi_sm_monitor_app, loop):
    return loop.run_until_complete(aiohttp_client(taxi_sm_monitor_app))


@pytest.fixture
async def taxi_sm_monitor_app_stq(simple_secdist):
    stq_app = app_stq.TaxiSmMonitorSTQApplication()
    await stq_app.startup()
    yield stq_app
    await stq_app.shutdown()


@pytest.fixture
def mock_territories_all_countries(
        territories_response, territories_status, mockserver,
):
    class MockTerritories:
        @staticmethod
        @mockserver.json_handler('territories/v1/countries/list', prefix=True)
        def get_all_countries(request):
            return web.json_response(
                data=territories_response, status=territories_status,
            )

    return MockTerritories()


@pytest.fixture
def patch_created_startrack_ticket(patch_aiohttp_session, response_mock):
    def wrapper(
            response, status=200, startrack_url='http://test-startrack-url/',
    ):
        request_url = startrack_url + 'issues'

        @patch_aiohttp_session(request_url, 'POST')
        def created_ticket(method, url, **kwargs):
            assert url == request_url
            return response_mock(json=response, status=status)

        return created_ticket

    return wrapper


@pytest.fixture
def patch_support_ai(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200):
        method_url = (
            discovery.find_service('supportai-api').url
            + '/supportai-api/v1/support_internal'
        )

        @patch_aiohttp_session(method_url, 'POST')
        def support_internal(method, url, **kwargs):
            assert url == method_url
            assert kwargs['json']['chat_id']
            result = (
                {'close': {}, 'tag': {'add': ['1', '2']}}
                if response is None
                else response
            )
            return response_mock(json=result, status=status)

        return support_internal

    return wrapper


@pytest.fixture
async def sm_monitor_context(loop, db, simple_secdist):
    async for app in cron_run.create_app():
        yield run.StuffContext(
            None, 'test_task_id', datetime.datetime.utcnow(), app,
        )


@pytest.fixture()
def patch_stq_put(patch):
    @patch('taxi.stq.client.put')
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    return put
