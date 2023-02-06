# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
import collections
import json
import tempfile
from typing import Dict

import pytest

from taxi import discovery
from taxi import memstorage
from taxi.clients import replication

from taxi_exp import settings
from taxi_exp import util
from taxi_exp import web_context
from taxi_exp.generated.web import run_web
from taxi_exp.util import pg_helpers


class FakeTVMClient:
    async def get_auth_headers(self, dst_service_name, log_extra=None):
        return {'X-Ya-Service-Ticket': '123'}


@pytest.fixture
async def _taxi_exp_app(
        loop, simple_secdist, pgsql, pgsql_local, mds_s3_client, patch,
):
    @patch('taxi_exp.web_context.TaxiExpApplication._get_connection_kwargs')
    def _get_connection_kwargs(is_read_only=False):
        result = {'min_size': 1, 'max_size': 1}
        if not is_read_only:
            result['init'] = web_context._init_postgres_connection
        return result

    exp_db_uri = pgsql_local['taxi_exp'].get_dsn()
    simple_secdist['postgresql_settings'] = {
        'databases': {'taxi_exp': [{'hosts': [exp_db_uri]}]},
    }
    simple_secdist['settings_override'] = {
        'TAXI_EXP_API_TOKEN': 'secret',
        'EXPERIMENTS3_MDS_S3': {
            'bucket': '',
            'url': '',
            'access_key_id': '',
            'secret_key': '',
        },
        'API_ADMIN_SERVICES_TOKENS': {'taxi_exp': 'admin_secret'},
        'STARTRACK_API_TOKEN': 'secret',
        'STARTRACK_API_PROFILES': {
            'taxi_exp': {
                'url': 'http://test-startrack-url/',
                'org_id': None,
                'oauth_token': 'secret',
            },
        },
    }
    application = run_web.create_app()
    application.s3_client = mds_s3_client
    application.tvm = FakeTVMClient()
    temp_dir = tempfile.TemporaryDirectory()
    application.files_snapshot_path = temp_dir.name
    application.replication_client = replication.ReplicationClient(
        service=discovery.find_service('replication'),
        session=application.session,
        tvm_client=application.tvm,
    )
    application.on_startup.append(fill_db_version)

    yield application

    temp_dir.cleanup()

    for sequence in (
            'clients_schema.experiments_history_rev_seq',
            'clients_schema.clients_rev',
            'clients_schema.revision_history_experiment_id_seq',
    ):
        await pg_helpers.execute_sql_function(
            application['pool'], f'ALTER SEQUENCE {sequence} RESTART WITH 1',
        )

    memstorage.invalidate()


async def fill_db_version(app):
    await pg_helpers.execute_sql_function(
        app['pool'],
        (
            'INSERT INTO clients_schema.exp_schema_version(fake_field) '
            'VALUES (1);'
        ),
    )


@pytest.fixture
def taxi_exp_client(aiohttp_client, _taxi_exp_app, loop):
    return loop.run_until_complete(aiohttp_client(_taxi_exp_app))


@pytest.fixture
def set_and_clean_cache_path(taxi_exp_client, monkeypatch, patch):
    old_snapshot_path = taxi_exp_client.app.files_snapshot_path

    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr('taxi_exp.settings.FILES_SNAPSHOT_PATH', temp_dir)
        taxi_exp_client.app.files_snapshot_path = temp_dir
        yield

    taxi_exp_client.app.files_snapshot_path = old_snapshot_path


@pytest.fixture
def patch_util_now(patch, mocked_time):
    @patch('taxi_exp.util.now')
    def _now():
        return mocked_time.now().astimezone(util.MOSCOW).replace(tzinfo=None)


@pytest.fixture
def relative_load_jsons_from_file(load):
    """Load file from `./static/filename`.

    Raises `ValueError` if file not found.
    """

    def _wrapper(filename):
        file = load(filename)
        return (json.loads(line) for line in file.splitlines())

    return _wrapper


@pytest.fixture
def relative_load_json_from_file(load):
    """Load file from `./static/filename`.

    Raises `ValueError` if file not found.
    """

    def _wrapper(filename):
        file = load(filename)
        return json.loads(file)

    return _wrapper


@pytest.fixture(autouse=True)
def _territories(mockserver, response_mock):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _countries_from_territories(*args, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'aaaaa',
                    'phone_code': '7',
                    'phone_min_length': 11,
                    'phone_max_length': 11,
                    'national_access_code': '7',
                },
            ],
        }


@pytest.fixture
def patch_user_api(mockserver):
    class _UserApiStorage:
        PHONES = collections.OrderedDict()
        PHONE_IDS = collections.OrderedDict()
        STATE_FAIL = False

        def add(self, phone_id, phone):
            self.PHONES.__setitem__(phone, phone_id)
            self.PHONES.move_to_end(phone)
            self.PHONE_IDS.__setitem__(phone_id, phone)
            self.PHONE_IDS.move_to_end(phone_id)

    created_user_api = _UserApiStorage()

    @mockserver.json_handler('/user-api/user_phones/bulk')
    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve_bulk')
    def _by_number_retrieve_bulk(request):
        if created_user_api.STATE_FAIL:
            return mockserver.make_response(status=500)
        phone_data = [item['phone'] for item in request.json['items']]
        result = []
        for phone in phone_data:
            if phone not in created_user_api.PHONES:
                return mockserver.make_response(status=400)
            result.append(
                {'id': created_user_api.PHONES[phone], 'phone': phone},
            )

        return {'items': result}

    @mockserver.json_handler('/user-api/user_phones/get_bulk')
    def _get_bulk(request):
        if created_user_api.STATE_FAIL:
            return mockserver.make_response(status=500)
        phone_ids = request.json['ids']

        result = []
        for phone_id in phone_ids:
            if phone_id not in created_user_api.PHONE_IDS:
                return mockserver.make_response(status=400)
            result.append(
                {
                    'id': phone_id,
                    'phone': created_user_api.PHONE_IDS[phone_id],
                },
            )

        return {'items': result}

    return created_user_api


@pytest.fixture
def patch_personal(mockserver):
    class _PersonalStorage:
        PHONES = collections.OrderedDict()
        PHONE_IDS = collections.OrderedDict()
        STATE_FAIL = False

        def add(self, phone_id, phone):
            self.PHONES.__setitem__(phone, phone_id)
            self.PHONES.move_to_end(phone)
            self.PHONE_IDS.__setitem__(phone_id, phone)
            self.PHONE_IDS.move_to_end(phone_id)

    created_personal = _PersonalStorage()

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    async def _phone_ids_from_personal(request):
        if created_personal.STATE_FAIL:
            return mockserver.make_response(status=500)
        request_json = request.json
        assert set(item['value'] for item in request_json['items']) == set(
            created_personal.PHONES,
        )

        return {
            'items': [
                {'id': phone_id, 'value': phone}
                for phone_id, phone in zip(
                    created_personal.PHONE_IDS, created_personal.PHONES,
                )
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _phones_from_personal(request):
        if created_personal.STATE_FAIL:
            return mockserver.make_response(status=500)
        request_json = request.json
        assert set(item['id'] for item in request_json['items']) == set(
            created_personal.PHONE_IDS,
        )

        return {
            'items': [
                {'id': phone_id, 'value': phone}
                for phone_id, phone in zip(
                    created_personal.PHONE_IDS, created_personal.PHONES,
                )
            ],
        }

    return created_personal


@pytest.fixture
def patch_staff(patch_aiohttp_session, response_mock):
    class _LoginByData:
        STAFF_DATA: Dict[str, Dict] = {}

        def fill(self, data):
            self.STAFF_DATA.update(data)

    login_by_data = _LoginByData()

    @patch_aiohttp_session(f'{settings.STAFF_API_URL}/v3/persons')
    def _data_from_staff(method, url, headers, **kwargs):
        assert 'params' in kwargs
        params = kwargs['params']
        assert 'login' in params

        if '_one' in params and params['_one'] == '1':
            login = params['login']
            one_result = '{}'
            if login in login_by_data.STAFF_DATA:
                one_result = json.dumps(login_by_data.STAFF_DATA[login])
            return response_mock(text=one_result)
        logins = params['login'].split(',')
        result = {
            'page': 1,
            'pages': 1,
            'result': [
                login_by_data.STAFF_DATA[login]
                for login in logins
                if login in login_by_data.STAFF_DATA
            ],
        }
        return response_mock(json=result)

    return login_by_data


@pytest.fixture
def patch_sticker(patch_aiohttp_session, response_mock):
    class _CollectData:
        data = []

    collect_data = _CollectData()

    @patch_aiohttp_session(f'{settings.STICKER_API_URL}/send-internal/')
    def _send_email(method, url, headers, **kwargs):
        collect_data.data.append(kwargs['json'])
        return response_mock(text='{}')

    return collect_data
