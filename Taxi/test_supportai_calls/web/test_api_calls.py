import datetime

from aiohttp import web
import pytest

from supportai_calls import models as db_models

# Generated via `tvmknife unittest service -s 222 -d 111`
TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUI3gEQbw:Tc0fid-P9vc-dPS_UEQcQoDtM25vXU'
    '-seEZpTLaLla8WDsG5swfFS46FQilr41TH9XHBgIVoaNC-aNFuuLqdqGB8zifyjig'
    'XReodgtA-Qy5hkJ4qv6dCpmez6bmeMl_wQxVqds35ZxfT1EWyjfHHoalP2EzS-dAem'
    '3V5k_EwBsE'
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_calls', files=['outgoing_calls.sql']),
]


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-calls'}],
    TVM_SERVICES={'supportai-calls': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_api_tvm_auth(web_app_client, mock_tasks_handles):
    request = {'calls': [{'phone': '74957397000', 'features': []}]}

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json=request,
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test', json=request,
    )
    assert response.status == 403

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test1',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json=request,
    )
    assert response.status == 403


async def test_api_token_auth(web_app_client, mock_tasks_handles):
    request = {'calls': [{'phone': '74957397000', 'features': []}]}

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test1', json=request,
    )
    assert response.status == 403

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test1',
        headers={'X-YaTaxi-API-Key': 'test_token', 'X-Real-IP': '127.0.0.1'},
        json=request,
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test1',
        headers={
            'X-YaTaxi-API-Key': 'test_token_incorrect',
            'X-Real-IP': '127.0.0.1',
        },
        json=request,
    )
    assert response.status == 403

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test2',
        headers={'X-Real-IP': '127.0.0.1'},
        json=request,
    )
    assert response.status == 403

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch?project_slug=test3',
        headers={'X-Real-IP': '8.8.8.8'},
        json=request,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    ('callback_after', 'num_attempts'), [(None, None), (3, None), (3, 5)],
)
async def test_api_calls_batch_init(
        web_app_client, mock_tasks_handles, callback_after, num_attempts,
):
    request_body = {
        'calls': [
            {
                'phone': '74957397000',
                'features': [{'key': 'feature1', 'value': 'Feature 1'}],
            },
            {
                'personal_id': 'id',
                'features': [{'key': 'feature2', 'value': 'Feature 2'}],
            },
            {'external_phone_id': 'ext_1', 'features': []},
        ],
    }
    if callback_after is not None:
        request_body['callback_after'] = callback_after
        if num_attempts is not None:
            request_body['num_attempts'] = num_attempts

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch'
        '?project_slug=test_ignore_ivr_framework',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status == 200

    batch_id = (await response.json())['batch_id']

    status_response = await web_app_client.get(
        f'/supportai-calls/v1/calls/batch/'
        f'{batch_id}/status?project_slug=test_ignore_ivr_framework',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )
    assert status_response.status == 200
    assert (await status_response.json())['status'] == 'created'

    response = await web_app_client.get(
        f'v1/calls?project_slug=test_ignore_ivr_framework&user_id=34'
        f'&task_id={batch_id}&limit=10&offset=0',
    )
    assert response.status == 200
    response_json = await response.json()
    calls = response_json['calls']
    assert len(calls) == 3
    assert {call.get('phone') for call in calls} == {
        '',
        '+74957397000',
        '+79991234567',
    }


@pytest.mark.parametrize(
    ('with_begin_at', 'with_end_at'),
    [(True, True), (True, False), (False, True)],
)
@pytest.mark.parametrize('task_timezone_shift', [5.0, None])
async def test_batch_init_deferred_calls(
        web_app_client,
        mock_tasks_handles,
        get_task,
        stq3_context,
        with_begin_at,
        with_end_at,
        task_timezone_shift,
):
    phone_to_timezone_shift = {'+1': 1.0, '+2': None, '+3': -1.0}
    calls_data = []
    for phone, timezone_shift in phone_to_timezone_shift.items():
        call_data = {'phone': phone, 'features': []}
        if timezone_shift:
            call_data['timezone_shift'] = timezone_shift
        calls_data.append(call_data)
    request_body = {'calls': calls_data}

    local_now = (
        datetime.datetime.now().astimezone(
            datetime.timezone(
                offset=datetime.timedelta(hours=task_timezone_shift),
            ),
        )
        if task_timezone_shift is not None
        else datetime.datetime.now()
    )
    begin_calls_at = local_now + datetime.timedelta(hours=1)
    end_calls_at = local_now + datetime.timedelta(hours=1.5)

    if with_begin_at:
        request_body['begin_calls_at'] = str(begin_calls_at)
    if with_end_at:
        request_body['end_calls_at'] = str(end_calls_at)

    real_task_timezone_shift = task_timezone_shift or 3.0

    response = await web_app_client.post(
        '/supportai-calls/v1/calls/batch'
        '?project_slug=test_ignore_ivr_framework',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status == 200

    batch_id = (await response.json())['batch_id']
    task = get_task(batch_id)
    assert (
        task.params.extra.get('begin_calls_at') is not None
    ) is with_begin_at
    assert (task.params.extra.get('end_calls_at') is not None) is with_end_at

    async with stq3_context.pg.slave_pool.acquire() as conn:
        calls = await db_models.Call.select_by_task_id(
            stq3_context, conn, batch_id,
        )
    assert len(calls) == 3

    phone_to_expected_interval = {}
    for phone, call_timezone_shift in phone_to_timezone_shift.items():
        difference_hours = (
            0.0
            if call_timezone_shift is None
            else real_task_timezone_shift - call_timezone_shift
        )
        time_delta = datetime.timedelta(hours=difference_hours)
        phone_to_expected_interval[phone] = (
            begin_calls_at.astimezone() + time_delta
            if with_begin_at
            else None,
            end_calls_at.astimezone() + time_delta if with_end_at else None,
        )

    def _check_timestamp(timestamp, expected_timestamp):
        if expected_timestamp is None:
            assert timestamp is None
            return
        assert abs((timestamp - expected_timestamp).total_seconds()) < 5.0

    for call in calls:
        expected_begin_at, expected_end_at = phone_to_expected_interval[
            call.phone
        ]
        _check_timestamp(call.begin_at, expected_begin_at)
        _check_timestamp(call.end_at, expected_end_at)


@pytest.fixture(name='context_response')
def get_context_response():
    return {
        'contexts': [
            {
                'created_at': '2021-04-01 10:00:00+03',
                'chat_id': 'chat1',
                'records': [
                    {
                        'id': '1',
                        'created_at': '2021-04-01 10:00:00+03',
                        'request': {
                            'dialog': {
                                'messages': [{'text': '', 'author': 'ai'}],
                            },
                            'features': [
                                {'key': 'event_type', 'value': 'dial'},
                            ],
                        },
                        'response': {'reply': {'text': '1', 'texts': ['1']}},
                    },
                    {
                        'id': '2',
                        'created_at': '2021-04-01 10:02:00+03',
                        'request': {
                            'dialog': {
                                'messages': [
                                    {
                                        'text': 'help help help',
                                        'author': 'user',
                                    },
                                ],
                            },
                            'features': [],
                        },
                        'response': {
                            'reply': {'text': '300', 'texts': ['300']},
                            'features': {
                                'probabilities': [],
                                'features': [
                                    {'key': 'f_key', 'value': 'f_value'},
                                ],
                            },
                            'closed': {},
                        },
                    },
                ],
            },
        ],
        'total': 1,
    }


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'supportai-calls', 'dst': 'personal'},
        {'src': 'supportai-calls', 'dst': 'supportai-context'},
    ],
)
@pytest.mark.parametrize('used_entity', ['phone', 'external_phone_id'])
async def test_api_one_call(
        web_app_client,
        mockserver,
        mock_tasks_handles,
        context_response,
        used_entity,
):
    call_service = 'ivr_framework'
    project_slug = 'test_ignore_ivr_framework'
    personal_id = 'phone_id'
    external_phone_id = 'ext_1'
    phone = '79997654321' if used_entity == 'phone' else '79991234567'

    response = await web_app_client.put(
        f'v1/project_configs?project_slug={project_slug}&user_id=34',
        json={'dispatcher_params': {'call_service': call_service}},
    )
    assert response.status == 200

    @mockserver.json_handler('/personal/v1/phones/store')
    def _(_):
        return {'id': personal_id, 'value': phone}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _(_):
        return {'id': personal_id, 'value': phone}

    @mockserver.json_handler('/ivr-dispatcher/v1/ivr-framework/create-call')
    async def _(request):
        assert request.json['context'] == {
            'features': [{'key': 'feature1', 'value': 'Feature 1'}],
        }
        return web.json_response()

    request_json = {
        'features': [{'key': 'feature1', 'value': 'Feature 1'}],
        used_entity: phone if used_entity == 'phone' else external_phone_id,
    }

    post_call_url = f'/supportai-calls/v1/calls?project_slug={project_slug}'

    response = await web_app_client.post(
        post_call_url,
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json=request_json,
    )
    assert response.status == 200

    call = (await response.json())['call']
    assert call['phone'] == f'+{phone}'

    @mockserver.json_handler('/supportai-context/v1/contexts/multiple')
    async def _(_):
        context_response['contexts'][0]['chat_id'] = call['chat_id']
        context_response['total'] = 1
        return web.json_response(data=context_response)

    response = await web_app_client.post(
        f'/supportai-calls/v1/calls/results?project_slug={project_slug}',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        json={'call_ids': [call['id']]},
    )

    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['results']) == 1
    assert response_json['results'][0]['call_id'] == call['id']


@pytest.mark.parametrize('has_record', [True, False])
async def test_api_call_record_ivr_framework(
        web_app_client, mockserver, has_record,
):
    file_data = b'file_data_ivr_framework'

    @mockserver.json_handler(
        '/ivr-dispatcher/v1/ivr-framework/get-call-record',
    )
    async def _(request):
        assert request.query['ivr_flow_id'] == 'test_ignore_ivr_framework'
        assert (
            request.query['call_record_id'] == 'call_record_id_ivr_framework'
        )
        return (
            web.Response(body=file_data, content_type='audio/wav')
            if has_record
            else web.Response(status=404)
        )

    response = await web_app_client.get(
        '/supportai-calls/v1/calls/2/record'
        '?project_slug=test_ignore_ivr_framework',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )

    assert response.status == 200 if has_record else 404

    if has_record:
        assert (await response.content.read()) == file_data
        assert '1.wav' in response.headers['Content-Disposition']
        assert response.headers['X-File-Name'] == 'chat1.wav'


@pytest.mark.parametrize('has_record', [True, False])
async def test_get_api_calls_call_record_voximplant(
        web_app_client, patch, has_record,
):
    call_record_content = b'voximplant call record content'

    @patch('aiohttp.request')
    def _(**kwargs):
        url = kwargs.get('url')
        assert url == 'https://records_for_vox_project/5.mp3'

        class RequestContextManager:
            class MockResponse:
                def __init__(self, body):
                    self.status = 200 if has_record else 404
                    self.body = body

                async def read(self):
                    return self.body

            async def __aenter__(self):
                return self.MockResponse(call_record_content)

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        return RequestContextManager()

    response_voximplant = await web_app_client.get(
        '/supportai-calls/v1/calls/3/record'
        '?project_slug=test_ignore_voximplant',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )
    assert response_voximplant.status == 200 if has_record else 204

    if has_record:
        assert (
            await response_voximplant.content.read()
        ) == call_record_content
        assert '1.mp3' in response_voximplant.headers['Content-disposition']
        assert response_voximplant.headers['X-File-Name'] == 'chat1.mp3'


async def test_call_record_does_not_depend_on_project_call_service(
        web_app_client, mockserver,
):
    project_slug = 'various_call_service'
    call_services = ['ivr_framework', 'voximplant']

    call_record_ivr_framework = b'ivr_framework content'

    @mockserver.json_handler(
        '/ivr-dispatcher/v1/ivr-framework/get-call-record',
    )
    async def _(_):
        return web.Response(
            body=call_record_ivr_framework, content_type='audio/wav',
        )

    for project_call_service in call_services:
        dispatcher_params = {'call_service': project_call_service}
        if project_call_service == 'voximplant':
            dispatcher_params['account_id'] = 1
            dispatcher_params['rule_id'] = 1
            dispatcher_params['api_key'] = '1'
        response = await web_app_client.put(
            f'v1/project_configs?project_slug={project_slug}&user_id=34',
            json={'dispatcher_params': dispatcher_params},
        )
        assert response.status == 200

        response = await web_app_client.get(
            f'/supportai-calls/v1/calls/1/record'
            f'?project_slug={project_slug}',
            headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        )
        assert response.status == 200
        assert (await response.content.read()) == call_record_ivr_framework


@pytest.mark.config(TVM_RULES=[{'src': 'supportai-calls', 'dst': 'personal'}])
@pytest.mark.parametrize('used_entity', ['phone', 'personal_phone_id'])
async def test_register_incoming_call(web_app_client, mockserver, used_entity):
    phone = '79991234567'
    personal_phone_id = 'personal_phone_id'
    entity_value = phone if used_entity == 'phone' else personal_phone_id
    new_phone = '444444444444'
    new_personal_phone_id = 's(he) be(lie)ve(d)'
    new_entity_value = (
        new_phone if used_entity == 'phone' else new_personal_phone_id
    )
    chat_id = 'chat_id'

    @mockserver.json_handler('/personal/v1/phones/store')
    def _(_):
        return {'id': personal_phone_id, 'value': phone}

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _(_):
        return {'id': personal_phone_id, 'value': phone}

    request_json = {
        'call_service': 'ivr_framework',
        'chat_id': chat_id,
        'initiated': '2020.01.01 00:00:00',
        'features': [{'key': 'key', 'value': 'value'}],
        used_entity: entity_value,
    }

    async def make_request_and_check_result(first_attempt=True):
        response = await web_app_client.post(
            '/supportai-calls/v1/calls/incoming/register'
            '?project_slug=test_register_incoming_call&user_id=34',
            json=request_json,
            headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
        )
        if not first_attempt:
            assert response.status == 400
            response_json = await response.json()
            assert response_json['message'] == (
                f'The call with chat id {chat_id} '
                f'has been already registered'
            )
        else:
            assert response.status == 200

        response = await web_app_client.get(
            'v1/calls',
            params={
                'project_slug': 'test_register_incoming_call',
                'user_id': '34',
                'limit': 10,
                'offset': 0,
            },
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json['total_calls_count'] == 1
        assert len(response_json['calls']) == 1

        incoming_call = response_json['calls'][0]
        assert incoming_call['phone'] == f'+{phone}'
        assert incoming_call['direction'] == 'incoming'
        assert incoming_call['chat_id'] == 'chat_id'
        assert incoming_call['status'] == 'initiated'

    await make_request_and_check_result()
    request_json[used_entity] = new_entity_value
    await make_request_and_check_result(first_attempt=False)


async def test_cancel_batch(
        stq3_context, web_app_client, mock_tasks_handles, create_task,
):

    task = create_task(id_='2', type_='outgoing_calls_init')

    response_cancel = await web_app_client.post(
        '/supportai-calls/v1/calls/batch/2/cancel'
        '?project_slug=test_ignore_ivr_framework',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )
    assert response_cancel.status == 200
    assert (await response_cancel.json()) == {}

    status_to_expected_count = {
        db_models.CallStatus.QUEUED: 0,
        db_models.CallStatus.INITIATED: 1,
        db_models.CallStatus.ERROR: 1,
        db_models.CallStatus.CANCELLED: 2,
    }

    async with stq3_context.pg.slave_pool.acquire() as conn:
        for status, expected_count in status_to_expected_count.items():
            calls_count = await db_models.Call.count_by_filters(
                stq3_context,
                conn,
                project_slug='test_ignore_ivr_framework',
                task_id=task.id,
                statuses=[status],
            )
            assert calls_count == expected_count, status
