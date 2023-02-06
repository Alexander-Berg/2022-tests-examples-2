# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

import pytest

from callcenter_qa_plugins import *  # noqa: F403 F401


CALLS = [
    {
        'queue': 'ru_taxi_test_on_99',
        'metaqueue': 'ru_taxi_test',
        'subcluster': '99',
        'queued_at': '2021-07-01T13:51:13+0000',
        'completed_at': '2021-07-01T13:51:18+0000',
        'waiting_duration': 5,
        'abonent_phone_number': '+79990000001',
        'endreason': 'abandoned',
        'call_id': 'taxi-sas-qproc5.yndx.net-111.222',
        'internal_id': 'internalid1',
        'called_number': '+79990010001',
        'call_guid': '0000000001-0000000001-1625233827-0000000001',
    },
    {
        'operator_login': 'operator1@drvrc.com',
        'operator_full_name': 'operator1 operator1 operator1',
        'queue': 'ru_taxi_test_on_99',
        'metaqueue': 'ru_taxi_test',
        'subcluster': '99',
        'queued_at': '2021-07-01T13:51:07+0000',
        'answered_at': '2021-07-01T13:51:09+0000',
        'completed_at': '2021-07-01T13:51:10+0000',
        'talking_duration': 1,
        'waiting_duration': 2,
        'abonent_phone_number': '+79990000002',
        'endreason': 'completed_by_caller',
        'call_id': 'taxi-sas-qproc20.yndx.net-333.444',
        'internal_id': 'internalid2',
        'called_number': '+79990010002',
        'call_guid': '0000000001-0000000001-1625233862-0000000002',
    },
    {
        'operator_login': 'operator2@drvrc.com',
        'operator_full_name': 'operator2 operator2 operator2',
        'queue': 'ru_davos_test_on_99',
        'metaqueue': 'ru_davos_test',
        'subcluster': '99',
        'queued_at': '2021-07-01T13:51:03+0000',
        'answered_at': '2021-07-01T13:51:04+0000',
        'completed_at': '2021-07-01T13:51:17+0000',
        'talking_duration': 13,
        'waiting_duration': 1,
        'abonent_phone_number': '+79990000003',
        'endreason': 'completed_by_agent',
        'call_id': 'taxi-sas-qproc18.yndx.net-555.666',
        'internal_id': 'internalid3',
        'called_number': '+79990010003',
        'call_guid': '0000000001-0000000001-1625233813-0000000003',
    },
    {
        'operator_login': 'operator3@drvrc.com',
        'operator_full_name': 'operator3 operator3 operator3',
        'queue': 'ru_davos_test_on_99',
        'metaqueue': 'ru_davos_test',
        'subcluster': '99',
        'queued_at': '2021-07-01T13:50:55+0000',
        'answered_at': '2021-07-01T13:50:57+0000',
        'completed_at': '2021-07-01T13:51:14+0000',
        'talking_duration': 17,
        'waiting_duration': 2,
        'abonent_phone_number': '+79990000004',
        'transfered_to_number': 'D79990000005',
        'endreason': 'transfered',
        'call_id': 'taxi-m9-qproc19.yndx.net-777.888',
        'internal_id': 'internalid4',
        'called_number': '+79990010004',
        'call_guid': '0000000001-0000000001-1625233812-0000000004',
    },
    {
        'operator_login': 'operator4@drvrc.com',
        'operator_full_name': 'operator4 operator4 operator4',
        'queue': 'ru_taxi_test_filtered_on_99',
        'metaqueue': 'ru_taxi_test_filtered',
        'subcluster': '99',
        'queued_at': '2021-07-01T14:50:55+0000',
        'answered_at': '2021-07-01T14:50:57+0000',
        'completed_at': '2021-07-01T14:51:14+0000',
        'talking_duration': 17,
        'waiting_duration': 2,
        'abonent_phone_number': '+79990000005',
        'transfered_to_number': 'D79990000006',
        'endreason': 'transfered',
        'call_id': 'taxi-m9-qproc19.yndx.net-999.000',
        'internal_id': 'internalid4',
        'called_number': '+79990010005',
        'call_guid': '0000000001-0000000001-1625233812-0000000005',
    },
]


_NOW_DATE = datetime.date(year=2022, month=1, day=1)


def regular_operator(number):
    return {
        'id': 1000 + number,
        'login': f'operator_{number:03}',
        'agent_id': f'1000000{number:03}',
        'state': 'ready',
        'callcenter_id': ('volgograd_cc' if number % 2 else 'krasnodar_cc'),
        'full_name': 'some_full_name',
        'yandex_uid': f'461{number:03}',
        'queues': [],
        'role_in_telephony': (
            'ru_disp_operator' if number % 4 else 'ru_disp_team_leader'
        ),
        'supervisor_login': f'operator_{1 + number % 2}',
        'employment_date': _NOW_DATE.isoformat(),
    }


OPERATORS = [
    {
        'id': 1,
        'login': 'operator_1',
        'agent_id': '111',
        'state': 'ready',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': 'yandex_uid_test_1',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 2,
        'login': 'operator_2',
        'agent_id': '222',
        'state': 'ready',
        'callcenter_id': 'krasnodar_cc',
        'full_name': 'some_full_name',
        'yandex_uid': 'yandex_uid_test_2',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 3,
        'login': 'operator_no_calls',
        'agent_id': 'no_calls_id',
        'state': 'ready',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': 'yandex_uid_test_3',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 4,
        'login': 'operator_no_agent_id',
        'agent_id': None,
        'state': 'ready',
        'callcenter_id': 'krasnodar_cc',
        'full_name': 'some_full_name',
        'yandex_uid': 'yandex_uid_test_4',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 1111,
        'login': 'operator_111',
        'agent_id': '1000000111',
        'state': 'deleted',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '11111',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'employment_date': _NOW_DATE.isoformat(),
    },
] + [regular_operator(i) for i in range(1, 19)]


@pytest.fixture
def mock_tracker(mockserver):
    class MockTracker:
        @staticmethod
        @mockserver.json_handler('/startrek/v2/issues', prefix=True)
        async def create_issue(request):
            return mockserver.make_response(
                status=201,
                json={
                    'id': request.json['queue'],
                    'key': request.json['queue'],
                    'self': 'https://example.ru',
                },
            )

        @staticmethod
        @mockserver.json_handler('/startrek/v2/issues/', prefix=True)
        async def create_attachment(request):
            return mockserver.make_response(status=201, json={})

    return MockTracker()


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    class MockPersonal:
        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/store', prefix=True)
        async def store_phone(request):
            return mockserver.make_response(
                status=200,
                json={
                    'id': request.json['value'] + '_id',
                    'value': request.json['value'],
                },
            )

        @staticmethod
        @mockserver.json_handler(
            '/personal/v1/phones/bulk_retrieve', prefix=True,
        )
        async def create_attachment(request):
            return mockserver.make_response(
                status=200,
                json={
                    'items': [
                        {'id': phone_pd_id['id'], 'value': phone_pd_id['id']}
                        for phone_pd_id in request.json['items']
                    ],
                },
            )

        @staticmethod
        @mockserver.json_handler('/personal/v1/phones/retrieve', prefix=True)
        async def create_attachment(request):
            return mockserver.make_response(
                status=200,
                json={{'id': request.json['id'], 'value': request.json['id']}},
            )

    return MockPersonal()


@pytest.fixture(name='mock_callcenter_operators_list_full', autouse=False)
def _mock_callcenter_operators_list_full(mockserver):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(request):
        ops = [
            {
                'id': op['id'],
                'login': op['login'],
                'telegram_login': 'telegram_' + op['login'],
                'yandex_uid': op['yandex_uid'],
                'agent_id': op['agent_id'],
                'state': op['state'],
                'first_name': 'name',
                'last_name': 'surname',
                'callcenter_id': op['callcenter_id'],
                'roles': [op['role_in_telephony']],
                'name_in_telephony': op['login'],
                'created_at': '2016-06-01T22:05:25Z',
                'updated_at': '2016-06-22T22:05:25Z',
                'supervisor_login': op.get('supervisor_login'),
                'employment_date': op.get('employment_date'),
                'roles_info': [{'role': 'ru_disp_operator', 'source': 'idm'}],
            }
            for op in OPERATORS
        ]
        return mockserver.make_response(
            status=200, json={'next_cursor': len(OPERATORS), 'operators': ops},
        )


@pytest.fixture(name='mock_callcenter_operators_list_empty', autouse=True)
def _mock_callcenter_operators_list_empty(mockserver):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(request):
        return mockserver.make_response(
            status=200, json={'next_cursor': 0, 'operators': []},
        )


@pytest.fixture(autouse=True)
def mock_cc_stats(mockserver):
    @mockserver.json_handler('/callcenter-stats/v1/calls/history')
    def _calls_bulk_retrieve(request):
        json_body = request.json
        last_cursor = 0
        if 'cursor' in json_body:
            last_cursor = json_body['cursor']
        calls = []
        cursor = 0
        for call in CALLS:
            cursor += 1
            if cursor > last_cursor:
                calls.append(call)
        return mockserver.make_response(
            status=200, json={'calls': calls, 'cursor': cursor},
        )


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):
    class MockDriverProfiles:
        @staticmethod
        @mockserver.json_handler(
            '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
            prefix=True,
        )
        def driver_profiles_retrieve(request):
            return mockserver.make_response(
                status=200,
                json={
                    'profiles_by_phone': [
                        {
                            'driver_phone': request.json[
                                'driver_phone_in_set'
                            ][0],
                            'profiles': [
                                {
                                    'data': {
                                        'park_id': 'test_park_id',
                                        'uuid': 'driver_uuid',
                                    },
                                    'park_driver_profile_id': 'test_profile',
                                },
                            ],
                        },
                    ],
                },
            )

    return MockDriverProfiles()


@pytest.fixture(name='mock_tags')
def _mock_tags(mockserver):
    class MockTags:
        @staticmethod
        @mockserver.json_handler('/tags/v2/upload')
        def tags_upload(request):
            return mockserver.make_response(status=200, json={})

    return MockTags()


@pytest.fixture(autouse=True)
def moc_transcribe_api_cloud(mockserver):
    @mockserver.json_handler(
        '/transcribe-api-cloud/speech/stt/v2/longRunningRecognize',
    )
    def _transcribe(request):
        json_body = request.json
        op_id = 'default_id'
        if (
                'https://'
                + mockserver.url(
                    'mds-s3-external/external-bucket/call-id-01-in.wav',
                )
                == json_body['audio']['uri']
        ):
            op_id = 'operation_1_in'
        elif (
            'https://'
            + mockserver.url(
                'mds-s3-external/external-bucket/call-id-01-out.wav',
            )
            == json_body['audio']['uri']
        ):
            op_id = 'operation_2_out'
        elif (
            'https://'
            + mockserver.url(
                'mds-s3-external/external-bucket/quota-limit-in.wav',
            )
            == json_body['audio']['uri']
            or 'https://'
            + mockserver.url(
                'mds-s3-external/external-bucket/quota-limit-out.wav',
            )
            == json_body['audio']['uri']
        ):
            return mockserver.make_response('Too many requests', 429)
        elif (
            'https://'
            + mockserver.url(
                'mds-s3-external/external-bucket/internal-error-in.wav',
            )
            == json_body['audio']['uri']
            or 'https://'
            + mockserver.url(
                'mds-s3-external/external-bucket/internal-error-out.wav',
            )
            == json_body['audio']['uri']
        ):
            return mockserver.make_response('Internal Server Error', 500)
        return mockserver.make_response(
            status=200,
            json={
                'done': False,
                'id': op_id,
                'createdAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
                'createdBy': 'ajes08feato88ehbbhqq',
                'modifiedAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
            },
        )


@pytest.fixture(autouse=True)
def moc_operation_api_cloud(mockserver):
    @mockserver.handler(
        '/operation-api-cloud/operations/operation_1_in_not_found',
    )
    def _operation_1_in_not_found(request):
        return mockserver.make_response(status=404)

    @mockserver.handler(
        '/operation-api-cloud/operations/operation_2_out_not_found',
    )
    def _operation_2_in_not_found(request):
        return mockserver.make_response(status=404)

    @mockserver.json_handler(
        '/operation-api-cloud/operations/operation_1_in_not_ready',
    )
    def _operation_1_in_not_ready(request):
        return mockserver.make_response(
            status=200,
            json={
                'done': False,
                'id': 'operation_1_in_not_ready',
                'createdAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
                'createdBy': 'ajes08feato88ehbbhqq',
                'modifiedAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
            },
        )

    @mockserver.json_handler(
        '/operation-api-cloud/operations/operation_2_out_not_ready',
    )
    def _operation_2_out_not_ready(request):
        return mockserver.make_response(
            status=200,
            json={
                'done': False,
                'id': 'operation_2_out_not_ready',
                'createdAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
                'createdBy': 'ajes08feato88ehbbhqq',
                'modifiedAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
            },
        )

    @mockserver.json_handler('/operation-api-cloud/operations/operation_1_in')
    def _operation_1_in(request):
        return mockserver.make_response(
            status=200,
            json={
                'done': True,
                'response': {
                    '@type': (
                        'type.googleapis.com/'
                        'yandex.cloud.ai.stt.v2.'
                        'LongRunningRecognitionResponse'
                    ),
                    'chunks': [
                        {
                            'alternatives': [
                                {
                                    'words': [
                                        {
                                            'startTime': '0.879999999s',
                                            'endTime': '1.159999992s',
                                            'word': 'при',
                                            'confidence': 1,
                                        },
                                        {
                                            'startTime': '1.219999995s',
                                            'endTime': '1.539999988s',
                                            'word': 'написании',
                                            'confidence': 1,
                                        },
                                    ],
                                    'text': 'при написании',
                                    'confidence': 1,
                                },
                            ],
                            'channelTag': '1',
                        },
                    ],
                },
                'id': 'operation_1_in',
                'createdAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
                'createdBy': 'ajes08feato88ehbbhqq',
                'modifiedAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
            },
        )

    @mockserver.json_handler('/operation-api-cloud/operations/operation_2_out')
    def _operation_2_out(request):
        return mockserver.make_response(
            status=200,
            json={
                'done': True,
                'response': {
                    '@type': (
                        'type.googleapis.com/'
                        'yandex.cloud.ai.stt.v2.'
                        'LongRunningRecognitionResponse'
                    ),
                    'chunks': [
                        {
                            'alternatives': [
                                {
                                    'words': [
                                        {
                                            'startTime': '0.879999999s',
                                            'endTime': '1.159999992s',
                                            'word': 'за',
                                            'confidence': 1,
                                        },
                                        {
                                            'startTime': '1.219999995s',
                                            'endTime': '1.539999988s',
                                            'word': 'Родину',
                                            'confidence': 1,
                                        },
                                    ],
                                    'text': 'за Родину',
                                    'confidence': 1,
                                },
                            ],
                            'channelTag': '1',
                        },
                    ],
                },
                'id': 'operation_2_out',
                'createdAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
                'createdBy': 'ajes08feato88ehbbhqq',
                'modifiedAt': datetime.datetime.now(
                    datetime.timezone.utc,
                ).isoformat(timespec='seconds'),
            },
        )

    @mockserver.json_handler('/operation-api-cloud/operations/quota-limit')
    def _operation_quota_limit(request):
        return mockserver.make_response('Too many requests', 429)

    @mockserver.json_handler('/operation-api-cloud/operations/internal-error')
    def _operation_internal_error(request):
        return mockserver.make_response('Internal Server Error', 500)


@pytest.fixture(name='s3_storage', autouse=True)
def _s3_storage():
    class FakeMdsClient:
        def put_object(self, key, body):
            assert key.startswith('/mds-s3-external'), key
            assert body == b'WAV FILE MOCK'

        def get_object(self, key) -> bytearray:
            assert key.startswith('/mds-s3-internal'), key
            return bytearray(b'WAV FILE MOCK')

        def delete_object(self, key) -> bool:
            assert key.startswith('/mds-s3-external'), key
            return True

    client = FakeMdsClient()
    return client


@pytest.fixture(name='s3_internal', autouse=True)
def _mds_s3_internal(mockserver, s3_storage):
    @mockserver.handler('/mds-s3-internal', prefix=True)
    def _mock_all(request):
        if request.method == 'GET':
            if (
                    'not_found-in.wav' in request.path
                    or 'not_found-out.wav' in request.path
            ):
                return mockserver.make_response('not found', 404)
            data = s3_storage.get_object(request.path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('Not found or invalid method', 404)


@pytest.fixture(name='s3_external', autouse=True)
def _mds_s3_external(mockserver, s3_storage):
    @mockserver.handler('/mds-s3-external', prefix=True)
    def _mock_all(request):
        if request.method == 'PUT':
            s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'DELETE':
            data = s3_storage.delete_object(request.path)
            if data:
                return mockserver.make_response('OK', 200)
        return mockserver.make_response('Not found or invalid method', 404)
