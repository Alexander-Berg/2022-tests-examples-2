# pylint: disable=redefined-outer-name,duplicate-code,unused-variable
# pylint: disable=invalid-name
import concurrent.futures
import copy
import datetime
import os
import uuid

import bson
import pytest
import ticket_parser2

from taxi import discovery
from taxi.clients import archive_api
from taxi.clients import chatterbox
from taxi.clients import experiments3
from taxi.clients import tvm
from testsuite.utils import matching

from taxi_support_chat.components import logbroker_producer
import taxi_support_chat.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from taxi_support_chat.internal import csat


pytest_plugins = ['taxi_support_chat.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
async def vgw_api_tasks_mock_s3(mds_s3_client, patch):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _upload_content(key, body, *args, **kwargs):
        return await mds_s3_client.upload_content(key, body, *args, **kwargs)

    @patch('taxi.clients.mds_s3.MdsS3Client.get_object')
    async def _get_object(key, *args, **kwargs):
        return await mds_s3_client.get_object(key)

    @patch('taxi.clients.mds_s3.MdsS3Client.delete_object')
    async def _delete_object(key, *args, **kwargs):
        return await mds_s3_client.delete_object(key)

    @patch('taxi.clients.mds_s3.MdsS3Client.generate_download_url')
    async def _generate_download_url(key, *args, **kwargs):
        return await mds_s3_client.generate_download_url(key)

    @patch('taxi.clients.mds_s3.MdsS3Client.download_content')
    async def _download_content(key, *args, **kwargs):
        return await mds_s3_client.download_content(key)

    @patch('taxi.clients.mds_s3.MdsS3Client.head_object')
    async def _head_object(key, *args, **kwargs):
        return await mds_s3_client.head_object(key)


@pytest.fixture
def mock_uuid4(monkeypatch, mock):
    @mock
    def _dummy_uuid4():
        return uuid.UUID(int=0, version=4)

    monkeypatch.setattr(uuid, 'uuid4', _dummy_uuid4)


@pytest.fixture
def patch_resizer(patch_aiohttp_session, response_mock, mockserver):
    def wrapper(sender_id: str, attachment_id: str, file: bytes):
        resizer_gen_url = '/resizer/genurl'
        image_url = 'http://resize.yandex.net/{}_{}'.format(
            sender_id, attachment_id,
        )

        @mockserver.json_handler(resizer_gen_url)
        def gen_url(request):
            return mockserver.make_response(
                response=image_url.encode('utf-8'),
                content_type='text/plain',
                status=200,
            )

        @patch_aiohttp_session(image_url, 'GET')
        def get_file(method, url, **kwargs):
            assert method == 'get'
            assert url == image_url

            return response_mock(
                read=file,
                headers={'Content-Type': 'application/binary'},
                status=200,
            )

        return gen_url, get_file

    return wrapper


@pytest.fixture
def mock_chatterbox_tasks(monkeypatch, mock):
    @mock
    async def _dummy_tasks(**kwargs):
        assert 'external_id' in kwargs
        return {'id': 'some_task_id'}

    monkeypatch.setattr(chatterbox.ChatterboxApiClient, 'tasks', _dummy_tasks)
    return _dummy_tasks


@pytest.fixture
def mock_get_user_phone(mockserver, load_json):
    try:
        user_phones = load_json('user_api_user_phones.json')
    except FileNotFoundError:
        user_phones = []

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _get_user_phone(request):
        request_phone = request.json['phone']
        request_type = request.json['type']
        for user_phone in user_phones:
            if (
                    user_phone['phone'] == request_phone
                    and user_phone['type'] == request_type
            ):
                return user_phone
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': ''},
        )

    return _get_user_phone


@pytest.fixture(autouse=True)
def patch_random_choice(patch):
    @patch('random.choice')
    def patch_choice(items):
        return items[0]


@pytest.fixture(autouse=True)
def mock_shuffle(patch):
    @patch('random.shuffle')
    def shuffle(array):  # pylint: disable=unused-variable
        array.reverse()


@pytest.fixture(autouse=True)
def patch_current_date(patch_current_date):
    pass


@pytest.fixture(autouse=True)
def mock_stq_put(patch, mock):
    @mock
    @patch('taxi.stq.client.put')
    async def _dummy_put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    return _dummy_put


@pytest.fixture
def image_sampler_getter():
    def upload_content(filename: str) -> bytes:
        file_path = os.path.join(
            os.path.dirname(__file__),
            'web/static/samplers/{}'.format(filename),
        )
        with open(file_path, 'rb') as file:
            return file.read()

    return upload_content


@pytest.fixture
def mock_ticket_update(patch, mock):
    @mock
    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_update')
    async def update_ticket(ticket_id, data):
        if 'uploads' in data['ticket']['comment']:
            assert data['ticket']['comment']['body']

    return update_ticket


@pytest.fixture
def mock_attachment_upload(patch, mock):
    @mock
    @patch('taxi.clients.zendesk.ZendeskApiClient.attachment_upload')
    async def upload_attachment(name, binary_data, log_extra=None):
        return {'upload': {'token': '6bk_%s' % name}}

    return upload_attachment


@pytest.fixture(name='mock_tvm_keys')
def mock_tvm_keys_fixture(patch_aiohttp_session, response_mock, monkeypatch):
    tvm_keys_url = (
        f'https://tvm-api.yandex.net/2/keys?lib_version'
        f'={ticket_parser2.__version__.decode()}'
    )

    class DummyServiceContext:
        class DummyTicket:
            def __init__(self, src):
                self.src = src

            def debug_info(self):
                pass

        def __init__(self, *args, **kwargs):
            pass

        def check(self, ticket_body):
            if ticket_body == b'backend_service_ticket':
                return self.DummyTicket(1)
            if ticket_body == b'corp_service_ticket':
                return self.DummyTicket(2)
            if ticket_body == b'disp_service_ticket':
                return self.DummyTicket(3)
            raise RuntimeError

    @patch_aiohttp_session(tvm_keys_url, 'GET')
    def _patch_get_keys(method, url, **kwargs):
        return response_mock(text='keys')

    monkeypatch.setattr(
        'ticket_parser2.api.v1.ServiceContext', DummyServiceContext,
    )


@pytest.fixture
def mock_exp3_get_values(patch):
    def _wrap(response_by_name, next_response_by_name=None):
        state = {'already_called': False}

        @patch('taxi.clients.experiments3.Experiments3Client.get_values')
        async def _get_values(
                consumer,
                experiments_args,
                client_application=None,
                user_agent=None,
                log_extra=None,
        ):
            if next_response_by_name is not None and state['already_called']:
                response_map = next_response_by_name
            else:
                response_map = response_by_name
            state['already_called'] = True

            if consumer != csat.EXPERIMENT_CONSUMER:
                return []

            exp_args = {}
            for arg in experiments_args:
                exp_args[arg.name] = arg.value

            return [
                experiments3.ExperimentsValue(
                    name=name, value=copy.deepcopy(response),
                )
                for name, response in response_map.items()
            ]

        return _get_values

    return _wrap


@pytest.fixture
def dummy_tvm_check(monkeypatch):
    async def _check_tvm(*args, **kwargs):
        return tvm.CheckResult(src_service_name='backend')

    monkeypatch.setattr('taxi.clients.tvm.check_tvm', _check_tvm)


@pytest.fixture
def patch_support_scenarios_matcher(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200, expected_request=None):
        if response is None:
            response = {'actions': [], 'view': {'show_message_input': True}}
        route = '{}{}'.format(
            discovery.find_service('support-scenarios').url,
            '/v1/actions/match',
        )

        @patch_aiohttp_session(route, 'POST')
        def mock(method, url, **kwargs):
            # assert kwargs = {}
            result = dict(response)
            if expected_request is not None:
                assert expected_request == kwargs['json']
            return response_mock(json=result, status=status)

        return mock

    return wrapper


@pytest.fixture
def patch_support_scenarios_display(patch_aiohttp_session, response_mock):
    def wrapper(response=None, status=200):
        if response is None:
            response = {'id': 'action_1', 'text': 'anime'}
        route = '{}{}'.format(
            discovery.find_service('support-scenarios').url,
            '/v1/actions/display',
        )

        @patch_aiohttp_session(route, 'GET')
        def mock(method, url, **kwargs):
            return response_mock(json=response, status=status)

        return mock

    return wrapper


@pytest.fixture
def mock_ucommunications(mockserver, patch):
    @patch(
        'taxi.clients.ucommunications.UcommunicationsClient._get_auth_headers',
    )
    async def _get_auth_headers(*args, **kwargs):
        return {'X-Ya-Service-Ticket': 'ticket'}

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push_notification(request):
        return {}

    return _push_notification


def pytest_register_matching_hooks():
    def _custom_tuple_match(doc: dict):
        return tuple(doc['value'])

    def _custom_list_match(doc: dict):
        return list(doc['value'])

    class _ObjectId(matching.ObjectIdString):
        def __eq__(self, other):
            if isinstance(other, bson.ObjectId):
                return super().__eq__(str(other))
            return False

    class AnyDict:
        def __eq__(self, other):
            return isinstance(other, dict)

    class Datetime:
        def __eq__(self, other):
            return isinstance(other, datetime.datetime)

    return {
        'datetime': Datetime(),
        'list': _custom_list_match,
        'tuple': _custom_tuple_match,
        'objectid': _ObjectId(),
        'any-dict': AnyDict(),
    }


@pytest.fixture
def mock_get_users(mockserver, load_json):
    users = load_json('user_api_users.json')

    @mockserver.json_handler('/user-api/users/get')
    def _get_user(request):
        for user in users:
            if request.json['id'] == user['id']:
                return user
        return mockserver.make_response(status=404)


@pytest.fixture
def mock_personal_custom(mockserver, load_json, patch):

    pd_data = load_json('personal_data.json')

    default_response = {'id': 'test_pd_id', 'value': 'test_value'}

    @patch('taxi.clients.personal.PersonalApiClient._get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {'auth': 'ticket'}

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>\w+)/retrieve', regex=True,
    )
    def mock_retrieve_item(request, personal_type, *args, **kwargs):
        items = pd_data[personal_type]
        for item in items:
            if item['id'] == request.json['id']:
                return item
        return default_response

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>\w+)/find', regex=True,
    )
    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>\w+)/store', regex=True,
    )
    def mock_store_item(request, personal_type, *args, **kwargs):
        items = pd_data[personal_type]
        for item in items:
            if item['value'] == request.json['value']:
                return item
        return default_response


@pytest.fixture
def mock_additional_meta(patch_aiohttp_session, response_mock):
    support_info_url = discovery.find_service('support_info').url

    def wrapper(metadata=None, status='ok'):
        @patch_aiohttp_session(
            support_info_url + '/v1/get_additional_meta', 'POST',
        )
        def get_additional_meta(method, url, json, **kwargs):
            return response_mock(
                json={
                    'metadata': metadata if metadata is not None else {},
                    'status': status,
                },
            )

        return get_additional_meta

    return wrapper


@pytest.fixture(autouse=True)
def patch_lookup_rows(monkeypatch):
    async def lookup_rows(*args, **kwargs):
        if kwargs['query'] == [{'id': '5b436ca8779fb3302cc784b0'}]:
            return [
                {
                    'doc': {
                        '_id': bson.ObjectId('5b436ece779fb3302cc784b0'),
                        'incident_timestamp': datetime.datetime(
                            2018, 11, 30, 12, 34,
                        ),
                        'last_message_from_user': False,
                        'messages': [
                            {
                                'author': 'user',
                                'id': 'message_31',
                                'message': 'text_1',
                                'timestamp': datetime.datetime(
                                    2018, 11, 30, 12, 34,
                                ),
                            },
                            {
                                'author': 'support',
                                'id': 'message_32',
                                'message': 'text_2',
                                'timestamp': datetime.datetime(
                                    2018, 11, 30, 12, 34,
                                ),
                            },
                        ],
                        'open': True,
                        'owner_id': '5b4f5092779fb332fcc26154',
                        'support_avatar_url': 2,
                        'support_name': 'Петр',
                        'type': 'client_support',
                        'updated': datetime.datetime(2018, 11, 30, 12, 34),
                        'user_id': 'user_id3',
                        'user_phone_id': bson.ObjectId(
                            '5b4f5092779fb332fcc26154',
                        ),
                        'visible': False,
                    },
                },
            ]
        return []

    monkeypatch.setattr(
        archive_api.ArchiveApiClient, 'lookup_rows', lookup_rows,
    )


@pytest.fixture(autouse=True)
def patch_logbroker_producer(monkeypatch):
    sent = []

    class _DummyFutureResult:
        @staticmethod
        def HasField(field):
            return True

        class init:
            max_seq_no = 0

    class _DummyProducer:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            return future

        def __init__(self):
            self._to_send = []

        def stop(self):
            pass

        def write(self, seq_no, message):
            future = concurrent.futures.Future()
            future.set_result(_DummyFutureResult)
            sent.append(message)
            return future

    class _DummyApi:
        def start(self):
            future = concurrent.futures.Future()
            future.set_result('start result')
            return future

        @staticmethod
        def stop():
            future = concurrent.futures.Future()
            future.set_result('stop result')
            return future

        def create_retrying_producer(self, *args, **kwargs):
            return _DummyProducer()

    async def _create_api(*args, **kwargs):
        return _DummyApi

    monkeypatch.setattr(
        logbroker_producer.LogbrokerAsyncWrapper, '_create_api', _create_api,
    )
