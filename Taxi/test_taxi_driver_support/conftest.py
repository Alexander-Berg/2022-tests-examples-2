# pylint: disable=redefined-outer-name,unused-variable
import copy

import pytest

from taxi import discovery
from taxi import secdist
from taxi.clients import driver_authorizer
from taxi.clients import experiments3
from taxi.clients import startrack
from taxi.pytest_plugins import fixtures_content as conftest
from taxi.pytest_plugins import service
from taxi.stq import client as stq_client

from taxi_driver_support import app
from taxi_driver_support import app_stq
from taxi_driver_support.api import support_chat

service.install_service_local_fixtures(__name__)

pytest_plugins = ['taxi.pytest_plugins.order_archive']


TRANSLATIONS = {
    'notify': {
        'user_chat.new_message': {
            'ru': 'Вам поступил ответ от службы поддержки',
            'en': 'Support response',
        },
        'user_chat.csat_request': {
            'ru': 'Оцените ответ',
            'en': 'Rate response',
        },
    },
    'taximeter_messages': {
        'notification_open_driver_messages': {
            'ru': 'Посмотреть',
            'en': 'Watch',
        },
    },
}


EXPERIMENT_CSAT_RESPONSE = {
    'csat_options': {
        'questions': [
            {
                'id': 'quality_score',
                'text': 'user_chat_csat.quality_score',
                'with_input': False,
                'values': [
                    {
                        'id': 'horrible',
                        'text': 'user_chat_csat.horrible',
                        'with_input': False,
                        'shuffle': True,
                        'reasons': [
                            {
                                'id': 'long_answer',
                                'text': 'user_chat_csat_reasons.long_answer',
                                'with_input': False,
                                'shuffle': True,
                                'reasons': [
                                    {
                                        'id': 'long_initial_answer',
                                        'text': (
                                            'user_chat_csat_reasons'
                                            '.long_initial_answer'
                                        ),
                                        'with_input': False,
                                    },
                                    {
                                        'id': 'long_interval_answer',
                                        'text': (
                                            'user_chat_csat_reasons'
                                            '.long_interval_answer'
                                        ),
                                        'with_input': False,
                                    },
                                ],
                            },
                            {
                                'id': 'template_answer',
                                'text': (
                                    'user_chat_csat_reasons.template_answer'
                                ),
                                'with_input': False,
                            },
                            {
                                'id': 'disagree_solution',
                                'text': (
                                    'user_chat_csat_reasons.disagree_solution'
                                ),
                                'with_input': False,
                            },
                            {
                                'id': 'problem_not_solved',
                                'text': (
                                    'user_chat_csat_reasons.problem_not_solved'
                                ),
                                'with_input': False,
                            },
                        ],
                    },
                    {
                        'id': 'good',
                        'text': 'user_chat_csat.good',
                        'with_input': False,
                    },
                    {
                        'id': 'amazing',
                        'text': 'user_chat_csat.amazing',
                        'with_input': False,
                    },
                ],
            },
            {
                'id': 'response_speed_score',
                'text': 'user_chat_csat.response_speed_score',
                'with_input': False,
                'values': [
                    {
                        'id': 'horrible',
                        'text': 'user_chat_csat.horrible',
                        'with_input': False,
                    },
                    {
                        'id': 'good',
                        'text': 'user_chat_csat.good',
                        'with_input': False,
                    },
                    {
                        'id': 'amazing',
                        'text': 'user_chat_csat.amazing',
                        'with_input': False,
                    },
                ],
            },
        ],
    },
}


@pytest.fixture
def driver_support_secdist(
        loop,
        monkeypatch,
        mongo_settings,
        redis_settings,
        postgresql_local_settings,
):
    settings_override = conftest.SETTINGS_OVERRIDE
    settings_override.update({'DRIVER_SUPPORT_COOKIES_SALT': 'test_salt'})
    settings_override['STARTRACK_API_PROFILES'].update(
        {
            'driver-support': {
                'url': 'http://st.test-startrack-url/',
                'org_id': 0,
                'oauth_token': 'some_startrack_token',
            },
        },
    )

    def load_secdist():
        return {
            'mongo_settings': mongo_settings,
            'postgresql_settings': postgresql_local_settings,
            'redis_settings': redis_settings,
            'settings_override': settings_override,
            'client_apikeys': conftest.CLIENT_APIKEYS,
        }

    monkeypatch.setattr(secdist, 'load_secdist', load_secdist)
    monkeypatch.setattr(secdist, 'load_secdist_ro', load_secdist)


@pytest.fixture
def taxi_driver_support_app(loop, db, driver_support_secdist):
    return app.create_app(loop=loop, db=db)


@pytest.fixture
def taxi_driver_support_client(aiohttp_client, taxi_driver_support_app, loop):
    return loop.run_until_complete(aiohttp_client(taxi_driver_support_app))


@pytest.fixture
def mock_driver_session(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_driver_session(token, client_id, park_id, log_extra=None):
        if token.find('session') != -1:
            return {'uuid': token.replace('session', 'uuid'), 'ttl': 42}
        raise driver_authorizer.AuthError

    monkeypatch.setattr(
        taxi_driver_support_app.driver_authorizer_client,
        'check_driver_sessions',
        _dummy_driver_session,
    )

    return _dummy_driver_session


@pytest.fixture
async def taxi_driver_support_app_stq(loop, db, simple_secdist):
    app = app_stq.TaxiDriverSupportSTQApplication(loop=loop, db=db)
    yield app
    for func in app.on_shutdown:
        await func(app)


@pytest.fixture(autouse=True)
def mock_stq_put(monkeypatch, mock):
    @mock
    async def _dummy_put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    monkeypatch.setattr(stq_client, 'put', _dummy_put)
    return _dummy_put


@pytest.fixture
def mock_get_tags(mockserver):
    def _wrap(tags, tags_service='tags'):
        tags_v1_match_profile = f'/{tags_service}/v1/drivers/match/profile'
        tags_v2_match_single = f'/{tags_service}/v2/match_single'

        @mockserver.json_handler(tags_v1_match_profile)
        @mockserver.json_handler(tags_v2_match_single)
        def dummy_match(*args, **kwargs):
            return {'tags': tags or []}

        return dummy_match

    return _wrap


@pytest.fixture
def patch_additional_meta(patch_aiohttp_session, response_mock):
    def wrapper(metadata=None, status='ok'):
        additional_meta_url = (
            discovery.find_service('support_info').url
            + '/v1/get_additional_meta'
        )

        @patch_aiohttp_session(additional_meta_url, 'POST')
        def get_additional_meta(*args, **kwargs):
            return response_mock(
                json={
                    'metadata': metadata if metadata is not None else {},
                    'status': status,
                },
            )

        return get_additional_meta

    return wrapper


@pytest.fixture
def mock_st_create_ticket(monkeypatch, mock):
    @mock
    async def _dummy_create_ticket(**kwargs):
        if 'unique' in kwargs and 'duplicate' in kwargs['unique']:
            raise startrack.ConflictError
        return {'key': kwargs['queue'] + '-1'}

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'create_ticket', _dummy_create_ticket,
    )
    return _dummy_create_ticket


@pytest.fixture
def mock_st_attach_file(monkeypatch, mock):
    @mock
    async def _dummy_attach_file(**kwargs):
        return {'id': 'attachment_id'}

    monkeypatch.setattr(
        startrack.StartrackAPIClient,
        'attach_file_to_ticket',
        _dummy_attach_file,
    )
    return _dummy_attach_file


@pytest.fixture
def mock_driver_profiles(mockserver, load_json):
    def _get_profile(driver_uuid, profiles):
        for profile in profiles:
            if profile['data']['park_driver_profile_id'] == driver_uuid:
                return profile
        return {}

    driver_profiles = load_json('driver_profile_retrieve.json')

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_retrieve(request, *args, **kwargs):
        uuids = request.json['id_in_set']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': driver_uuid,
                    **_get_profile(driver_uuid, driver_profiles),
                }
                for driver_uuid in uuids
            ],
        }

    driver_apps = load_json('driver_profile_retrieve_app.json')

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def mock_retrieve_app(request, *args, **kwargs):
        uuids = request.json['id_in_set']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': driver_uuid,
                    **_get_profile(driver_uuid, driver_apps),
                }
                for driver_uuid in uuids
            ],
        }


@pytest.fixture(autouse=True)
def mock_qc_xservice(mockserver, load_json):
    @mockserver.json_handler('/qc_xservice/utils/qc/driver/exams/retrieve')
    def mock_qc_exams(request, *args, **kwargs):
        return {'dkvu_exam': {'summary': {'is_blocked': False}}}


@pytest.fixture(autouse=True)
def mock_fleet_parks(mockserver, load_json):
    @mockserver.json_handler('/fleet-parks/v1/parks')
    def _dummy_profiles_url(request):
        return {
            'driver_partner_source': 'self_assign',
            'provider_config': {'clid': 'some_clid100500'},
            'name': 'ЯЕстьПарк',
            'country_id': 'rus',
        }


@pytest.fixture
def mock_personal(mockserver, load_json, patch):

    pd_data = load_json('personal_data.json')

    @patch('taxi.clients.personal.PersonalApiClient._get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {'auth': 'ticket'}

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def mock_retrieve_license(request, *args, **kwargs):
        licenses = pd_data['driver_licenses']
        for driver_license in licenses:
            if driver_license['id'] == request.json['id']:
                return driver_license
        return None

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_retrieve_phone(request, *args, **kwargs):
        phones = pd_data['phones']
        for phone in phones:
            if phone['id'] == request.json['id']:
                return phone
        return None


@pytest.fixture
def mock_exp3_get_values(patch):
    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _get_values(
            consumer,
            experiments_args,
            client_application=None,
            user_agent=None,
            log_extra=None,
    ):
        if consumer != support_chat.EXPERIMENT_CONSUMER:
            return []

        exp_args = {}
        for arg in experiments_args:
            exp_args[arg.name] = arg.value

        if exp_args.get('platform') == 'dummy-platform':
            return [
                experiments3.ExperimentsValue(
                    name=support_chat.EXPERIMENT_NAME,
                    value=copy.deepcopy(EXPERIMENT_CSAT_RESPONSE),
                ),
            ]
        return []

    return _get_values


@pytest.fixture(autouse=True)
def mock_driver_diagnostics(mockserver):
    @mockserver.json_handler(
        '/driver-diagnostics'
        '/internal/driver-diagnostics/v1/common/restrictions',
    )
    def get_common_restrictions(request, *args, **kwargs):
        assert request.method == 'POST'
        assert len(request.query) == 2
        assert 'park_id' in request.query
        assert 'contractor_profile_id' in request.query

        return {
            'checks': [
                {
                    'id': 'temp',
                    'type': 'block',
                    'title': 'Доступ ограничен',
                    'items': [{'id': 'dkk', 'title': 'Пройдите dkk'}],
                },
            ],
            'tariffs': [
                {
                    'id': 'maybach',
                    'reasons': [
                        {
                            'id': 'disabled_in_zone_category',
                            'title': 'Отключено парком',
                        },
                    ],
                },
                {'id': 'econom', 'reasons': []},
            ],
        }
