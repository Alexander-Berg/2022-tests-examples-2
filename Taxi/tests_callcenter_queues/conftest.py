# pylint: disable=wrong-import-order
import datetime
import json
import typing

from aiohttp import web
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from callcenter_queues_plugins import *  # noqa: F403 F401

_NOW_DATE = datetime.date(year=2007, month=1, day=1)


@pytest.fixture(name='lb_message_sender')
async def _lb_message_sender(taxi_callcenter_queues, load, testpoint):
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
                response = await taxi_callcenter_queues.post(
                    'tests/logbroker/messages',
                    data=json.dumps(
                        {
                            'consumer': 'qproc_event_consumer',
                            'data': msg if raw else load(msg),
                            'topic': '/taxi/callcenter/testing/qapp-events',
                            'cookie': 'cookie1',
                            **kwargs,
                        },
                    ),
                )
                assert response.status_code == 200

            # flush all other messages from queue
            async with taxi_callcenter_queues.spawn_task(
                    'qproc-event-processor',
            ):
                for _ in messages:
                    await commit.wait_call()

    return SendMessageFixture()


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


@pytest.fixture
def set_now(mocked_time, taxi_callcenter_queues):
    async def do_set_now(now: typing.Union[str, datetime.datetime]):
        if isinstance(now, str):
            now = datetime.datetime.fromisoformat(now)
        mocked_time.set(now)
        await taxi_callcenter_queues.update_server_state()

    return do_set_now


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
]


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
