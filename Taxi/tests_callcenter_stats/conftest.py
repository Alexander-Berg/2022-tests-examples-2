# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime
import json
import typing

from aiohttp import web
from callcenter_stats_plugins import *  # noqa: F403 F401
import pytest


_NOW_DATE = datetime.date(year=2007, month=1, day=1)


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
        'roles_info': [
            {
                'role': (
                    'ru_disp_operator' if number % 4 else 'ru_disp_team_leader'
                ),
                'source': 'admin',
            },
        ],
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
        'yandex_uid': '1001',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 2,
        'login': 'operator_2',
        'agent_id': '222',
        'state': 'ready',
        'callcenter_id': 'krasnodar_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1002',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'idm'}],
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 3,
        'login': 'operator_no_calls',
        'agent_id': 'no_calls_id',
        'state': 'ready',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1003',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 4,
        'login': 'operator_no_agent_id',
        'agent_id': None,
        'state': 'ready',
        'callcenter_id': 'krasnodar_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1004',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'idm'}],
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 1111,
        'login': 'operator_111',
        'agent_id': '1000000111',
        'state': 'deleted',
        'callcenter_id': 'volgograd_cc',
        'full_name': 'some_full_name',
        'yandex_uid': '1111111',
        'queues': [],
        'role_in_telephony': 'ru_disp_operator',
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'employment_date': _NOW_DATE.isoformat(),
    },
] + [regular_operator(i) for i in range(1, 19)]

PHONE_TO_PHONE_ID_MAPPING = {
    '79872676410': 'abonent_phone_id',
    '79999999999': 'phone_id_1_extra',
    '79991111111': 'phone_id_1',
    '79992222222': 'phone_id_2',
    '79993333333': 'phone_id_3',
    '+79872676410': 'abonent_phone_id',
    '+79999999999': 'phone_id_1_extra',
    '+79991111111': 'phone_id_1',
    '+79992222222': 'phone_id_2',
    '+79993333333': 'phone_id_3',
}


@pytest.fixture(name='mock_personal')
def _mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve', prefix=True)
    def _phones_bulk_retrieve(request):
        return web.Response(
            body='{"items":[{"id": "phone_id_1", "value": "+79991111111"}, '
            '{"id": "phone_id_1_extra", "value": "+79999999999"}, '
            '{"id": "phone_id_2", "value": "+79992222222"}, '
            '{"id": "phone_id_3", "value": "+79993333333"}, '
            '{"id": "phone_id_4", "value": "+79994444444"}]}',
        )

    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_find(request):
        json_body = request.json
        phone = json_body['value']
        phone_id = (
            PHONE_TO_PHONE_ID_MAPPING[phone]
            if phone in PHONE_TO_PHONE_ID_MAPPING
            else phone + '_id'
        )
        body = '{"id": "%s", "value": "%s"}' % (phone_id, phone)
        return web.Response(body=body)

    @mockserver.json_handler('/personal/v1/phones/store')
    def _phones_store(request):
        json_body = request.json
        phone = json_body['value']
        phone_id = PHONE_TO_PHONE_ID_MAPPING[phone]
        body = '{"id": "%s", "value": "%s"}' % (phone_id, phone)
        return web.Response(body=body)

    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    def _phones_bulk_store(request):
        return {
            'items': [
                {'id': x['value'] + '_id', 'value': x['value']}
                for x in request.json['items']
            ],
        }


@pytest.fixture(name='mock_callcenter_operators_list', autouse=True)
def _mock_callcenter_operators_list(mockserver):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(request):
        ops = [
            {
                'id': op['id'],
                'login': op['login'],
                'yandex_uid': op['yandex_uid'],
                'agent_id': op['agent_id'],
                'state': op['state'],
                'first_name': 'name',
                'last_name': 'surname',
                'callcenter_id': op['callcenter_id'],
                'roles': [op['role_in_telephony']],
                'roles_info': op['roles_info'],
                'name_in_telephony': op['login'],
                'created_at': '2016-06-01T22:05:25Z',
                'updated_at': '2016-06-22T22:05:25Z',
                'supervisor_login': op.get('supervisor_login'),
                'employment_date': op.get('employment_date'),
            }
            for op in OPERATORS
        ]
        return mockserver.make_response(
            status=200, json={'next_cursor': len(OPERATORS), 'operators': ops},
        )


@pytest.fixture(name='mock_api_tracker')
def _mock_api_tracker(mockserver):
    class Context:
        @staticmethod
        @mockserver.json_handler('/api-tracker/v2/issues')
        def external_issues(request):
            if request.headers['OrgId'] == '12345':
                assert request.headers['Authorization'] == 'OAuth 123'
            elif request.headers['OrgId'] == '54321':
                assert request.headers['Authorization'] == 'OAuth 321'
            else:
                return web.Response(status=401)
            return web.Response(
                status=201, body='{"id": "task_1", "key": "TASK-1"}',
            )

        @staticmethod
        @mockserver.json_handler('/startrek/v2/issues')
        def internal_issues(request):
            assert request.headers['Authorization'] == 'OAuth 111'
            return web.Response(
                status=201,
                body='{"id": "task_1", "key": "TASK-1", '
                '"self": "http://tracker/TASK-1"}',
            )

        @property
        def times_called(self):
            return (
                self.internal_issues.times_called
                + self.external_issues.times_called
            )

    return Context()


@pytest.fixture(autouse=True)
def _mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _user_phones_by_number(request):
        assert request.json['type'] == 'yandex'
        assert 'phone' in request.json
        phone = request.json['phone']
        response = load_json('user_api_user_phones_response.json')
        response['id'] = '{}_up_id'.format(phone)
        response['personal_phone_id'] = '{}_id'.format(phone)
        response['phone'] = phone
        return response

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    def _user_phones_by_personal(request):
        # Special for test_zero_suggest
        return {
            'items': [
                {
                    'id': '1234_up_id',
                    'phone': '+74999999999',
                    'type': 'yandex',
                },
            ],
        }

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        return {
            'items': [
                {
                    'phone_id': '+1234_up_id',
                    'yandex_uid': '+1234_uid',
                    'id': '+1234_user_id',
                },
            ],
        }


@pytest.fixture
def set_now(mocked_time, taxi_callcenter_stats):
    async def do_set_now(now: typing.Union[str, datetime.datetime]):
        if isinstance(now, str):
            now = datetime.datetime.fromisoformat(now)
        mocked_time.set(now)
        await taxi_callcenter_stats.update_server_state()

    return do_set_now


@pytest.fixture(name='lb_message_sender')
async def _lb_message_sender(taxi_callcenter_stats, load, testpoint):
    class SendMessageFixture:
        @staticmethod
        async def send(message, raw=False, **kwargs):
            @testpoint('logbroker_commit')
            def commit(cookie):
                assert cookie == 'cookie1'

            if not isinstance(message, list):
                messages = [message]
            else:
                messages = message
            for msg in messages:
                response = await taxi_callcenter_stats.post(
                    'tests/logbroker/messages',
                    data=json.dumps(
                        {
                            'consumer': 'tel_qapp_messages_cc_consumer',
                            'data': msg if raw else load(msg),
                            'topic': '/taxi/callcenter/production/qapp-events',
                            'cookie': 'cookie1',
                            **kwargs,
                        },
                    ),
                )
                assert response.status_code == 200

            # flush all other messages from queue
            async with taxi_callcenter_stats.spawn_task('qapp-event-consumer'):
                for _ in messages:
                    await commit.wait_call()

    return SendMessageFixture()


@pytest.fixture(name='mock_callcenter_queues', autouse=True)
def _mock_callcenter_queues(mockserver):
    @mockserver.json_handler('/callcenter-queues/v1/calls/balance')
    def _balance_handle(request):
        return mockserver.make_response(
            status=200,
            json={'subcluster': 's1', 'commutation_id': 'commutation_id'},
        )

    @mockserver.json_handler('/callcenter-queues/v1/queues/list')
    def _queues_list(request):
        return {'queues': [], 'subclusters': [], 'metaqueues': []}

    @mockserver.json_handler(
        '/callcenter-queues/cc/v1/callcenter-queues/v1/queues/statistics',
    )
    def _queues_statistics(request):
        return {
            'subclusters_statistics': [],
            'metaqueues_statistics': [],
            'queues_statistics': [
                {
                    'metaqueue': 'ru_taxi_test',
                    'subclusters': [
                        {
                            'subcluster': '1',
                            'operators_stats': {
                                'total': 10,
                                'connected': 10,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': '2020-07-07T16:30:00.00Z',
                                'calls_now_in_queue_count': 100,
                                'calls_now_in_queue_max_wait_time_sec': 5.5,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
            ],
        }
