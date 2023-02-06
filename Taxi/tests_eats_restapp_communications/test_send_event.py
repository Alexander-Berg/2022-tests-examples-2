# pylint: disable=too-many-lines, import-only-modules

import json

from dateutil.parser import parse
import pytest

CONFIG_EMAIL_SETTINGS = {
    'email_events': [
        {
            'event_type': 'password-request-reset',
            'sender_slug': '8Y2IS654-4J2',
            'permissions': ['permission1', 'permission2'],
        },
    ],
    'sender_account': 'yandex.food',
}
RECIPIENTS = {
    'recipient_types': [
        {
            'recipient_type': 'special_recipient',
            'email': 'mail@mail.ru',
            'name': 'Recipient Name',
            'locale': 'ru',
        },
    ],
}
CFG_RETRY_SETTINGS = {'limit': 30, 'delay': 60000}


def get_restrict_send(enabled: bool):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_restapp_communications_restrict_send',
        consumers=['eats_restapp_communications/internal'],
        clauses=[],
        default_value={'enabled': enabled},
    )


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_event(taxi_eats_restapp_communications, stq, pgsql):
    event = 'password-request-reset'
    partner_ids = [1, 2, 3]
    partnerish_uuids = ['uuid1', 'uuid2']
    emails = ['e1@m.ru', 'e2@m.ru']
    json_data = {
        'some_data1': partner_ids,
        'some_data2': 'string',
        'some_data3': 123,
    }
    attachments_data = [
        {'filename': 'file1', 'mime_type': 'application/type', 'data': '1abc'},
        {'filename': 'file2', 'mime_type': 'application/type', 'data': '2abc'},
    ]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {
            'partner_ids': partner_ids,
            'partnerish_uuids': partnerish_uuids,
            'emails': emails,
        },
        'data': json_data,
        'attachments': attachments_data,
    }
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204

    assert stq.eats_restapp_communications_event_sender.times_called == 1
    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    assert arg['args'] == []
    assert arg['kwargs']['attachments'] == attachments_data

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'asap',
            {
                'emails_types': [],
                'recipients': {
                    'partnerish_uuids': partnerish_uuids,
                    'partner_ids': partner_ids,
                    'emails': emails,
                },
            },
            json_data,
            None,
            None,
        ),
    ]


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_not_contained_event_with_metrics(
        taxi_eats_restapp_communications,
        taxi_eats_restapp_communications_monitor,
        stq,
):
    metrics_name = 'global-statistics'
    metrics = (
        await taxi_eats_restapp_communications_monitor.get_metrics(
            metrics_name,
        )
    )[metrics_name]
    errors_on_start = metrics.get('slug_error', 0)

    event = 'event'
    partner_ids = [1, 2, 3]
    partnerish_uuids = ['uuid1', 'uuid2']
    emails = ['e1@m.ru', 'e2@m.ru']

    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {
            'partner_ids': partner_ids,
            'partnerish_uuids': partnerish_uuids,
            'emails': emails,
        },
        'data': {},
    }
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 400
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    metrics = (
        await taxi_eats_restapp_communications_monitor.get_metrics(
            metrics_name,
        )
    )[metrics_name]
    errors = metrics.get('slug_error', 0)
    assert errors == errors_on_start + 1


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_not_contained_event(taxi_eats_restapp_communications, stq):
    event = 'event'
    partner_ids = [1, 2, 3]
    partnerish_uuids = ['uuid1', 'uuid2']
    emails = ['e1@m.ru', 'e2@m.ru']
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {
            'partner_ids': partner_ids,
            'partnerish_uuids': partnerish_uuids,
            'emails': emails,
        },
    }
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 400
    assert stq.eats_restapp_communications_event_sender.times_called == 0


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
@pytest.mark.parametrize('expected_calls, enabled', [(0, False), (1, True)])
async def test_send_event_for_only_one_partner_with_disabled_config(
        taxi_eats_restapp_communications,
        mock_get_partnerish_200,
        mock_send_event_200,
        stq_runner,
        experiments3,
        expected_calls,
        enabled,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_restapp_communications_restrict_send',
        consumers=['eats_restapp_communications/internal'],
        clauses=[],
        default_value={'enabled': enabled},
    )
    event = 'password-request-reset'
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {'recipients': {'partnerish_uuids': ['1a']}, 'data': {}}
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='fake_task',
    )
    assert mock_get_partnerish_200.times_called == 1
    assert mock_send_event_200.times_called == expected_calls

    await taxi_eats_restapp_communications.invalidate_caches()


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_event_for_only_one_partner(
        taxi_eats_restapp_communications,
        mock_get_partnerish_200,
        mock_send_event_200,
        stq_runner,
):
    event = 'password-request-reset'
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {'recipients': {'partnerish_uuids': ['1a']}, 'data': {}}
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='fake_task',
    )
    assert mock_get_partnerish_200.times_called == 1
    assert mock_send_event_200.times_called == 1


async def test_send_event_empty_partners(
        taxi_eats_restapp_communications, stq,
):
    url = '/internal/communications/v1/send-event?event_type={}'.format(
        'password-request-reset',
    )
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {'recipients': {}, 'data': {}}
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 400
    assert stq.eats_restapp_communications_event_sender.times_called == 0


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_SPECIFIC_RECIPIENTS_SETTINGS=RECIPIENTS,
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_specific_recipient(mock_send_event_200, stq_runner):
    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='specific_task',
    )
    assert mock_send_event_200.times_called == 1


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_stq_send_by_place_ids(mockserver, mock_core_places, stq_runner):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        if request.json['to'][0]['email'] == 'common_email':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1, 3],
                'places': ['place1 (address1)', 'place3 (address3)'],
            }
        if request.json['to'][0]['email'] == 'email2':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [2],
                'places': ['place2 (address2)'],
            }
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='place_ids_task',
    )
    assert mock_core_places.times_called == 1
    assert _mock_send_event.times_called == 2


@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_by_place_ids(taxi_eats_restapp_communications, stq):
    url = '/internal/communications/v1/send-event?event_type={}'.format(
        'password-request-reset',
    )
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'place_ids': [1, 2]},
        'data': {},
        'email_type': 'my_email_type',
    }
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 1


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={'partner_search_limit': 1},
)
async def test_stq_send_by_place_ids_for_all_partners(
        mockserver, mock_core_places, mock_search_all_partners, stq_runner,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        if request.json['to'][0]['email'] == 'user1@mail.ru':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1, 2, 3],
                'places': [
                    'place1 (address1)',
                    'place2 (address2)',
                    'place3 (address3)',
                ],
            }
        if request.json['to'][0]['email'] == 'user2@mail.ru':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1],
                'places': ['place1 (address1)'],
            }
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    @mockserver.json_handler(
        '/eats-restapp-authorizer/v1/user-access/check-bulk',
    )
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'partners': [
                    {
                        'partner_id': 2,
                        'details': {'permissions': [], 'place_ids': [2, 3]},
                    },
                    {
                        'partner_id': 3,
                        'details': {
                            'permissions': ['permission2'],
                            'place_ids': [3],
                        },
                    },
                ],
            },
        )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='all_partnerts_task',
    )
    assert mock_core_places.times_called == 1
    assert mock_search_all_partners.times_called == 3
    assert _mock_send_event.times_called == 2


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS={
        'email_events': [
            {
                'event_type': 'password-request-reset',
                'sender_slug': '8Y2IS654-4J2',
                'permissions': ['password_reset_permission'],
            },
        ],
        'sender_account': 'yandex.food',
        'test_email': 'restapp-testing@yandex-team.ru',
    },
)
async def test_stq_send_by_place_ids_with_test_mail(
        mockserver, mock_core_places, stq_runner,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        if request.json['to'][0]['email'] == 'common_email':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1, 3],
                'places': ['place1 (address1)', 'place3 (address3)'],
            }
        if request.json['to'][0]['email'] == 'email2':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [2],
                'places': ['place2 (address2)'],
            }
        assert (
            request.json['to'][1]['email'] == 'restapp-testing@yandex-team.ru'
        )
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='place_ids_task',
        kwargs={
            'event_type': 'password-request-reset',
            'recipients': {'place_ids': [1, 2, 3]},
            'data': {},
            'email_type': 'my_email_type',
        },
    )
    assert mock_core_places.times_called == 1
    assert _mock_send_event.times_called == 2


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
@pytest.mark.parametrize(
    'communication_types',
    [
        pytest.param(
            ['email'],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                },
            ),
            id='without types in config',
        ),
        pytest.param(
            ['email'],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                    'event_communication_types': [
                        {
                            'event_type': 'other-type',
                            'communication_types': ['telegram'],
                        },
                    ],
                },
            ),
            id='with type not in list',
        ),
        pytest.param(
            [],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                    'event_communication_types': [
                        {
                            'event_type': 'password-request-reset',
                            'communication_types': [],
                        },
                    ],
                },
            ),
            id='with empty types in config',
        ),
        pytest.param(
            [],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                    'event_communication_types': [
                        {
                            'event_type': 'password-request-reset',
                            'communication_types': ['abacaba'],
                        },
                    ],
                },
            ),
            id='with unknown type in config',
        ),
        pytest.param(
            ['email'],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                    'event_communication_types': [
                        {
                            'event_type': 'password-request-reset',
                            'communication_types': ['email'],
                        },
                    ],
                },
            ),
            id='with email type in config',
        ),
        pytest.param(
            ['telegram'],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                    'event_communication_types': [
                        {
                            'event_type': 'password-request-reset',
                            'communication_types': ['telegram'],
                        },
                    ],
                },
            ),
            id='with telegram type in config',
        ),
        pytest.param(
            ['email', 'telegram'],
            marks=pytest.mark.config(
                EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={
                    'partner_search_limit': 1,
                    'event_communication_types': [
                        {
                            'event_type': 'password-request-reset',
                            'communication_types': ['email', 'telegram'],
                        },
                    ],
                },
            ),
            id='with email and telegram types in config',
        ),
    ],
)
async def test_send_event_for_different_types(
        mockserver,
        mock_send_event_200,
        mock_core_places,
        testpoint,
        stq_runner,
        communication_types,
):
    @testpoint('email_call')
    def _email_call(data):
        return data

    @testpoint('telegram_call')
    def _telegram_call(data):
        return data

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='all_types_fake_task',
    )

    send_email = 'email' in communication_types
    send_telegram = 'telegram' in communication_types
    assert _email_call.times_called == int(send_email)
    assert _telegram_call.times_called == int(send_telegram)


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
    EATS_RESTAPP_COMMUNICATIONS_EVENT_SENDER_RETRY_SETTINGS=CFG_RETRY_SETTINGS,
)
@pytest.mark.parametrize('reschedule_counter', [28, 29, 30])
async def test_stq_restart_if_bad_request(
        mockserver,
        mock_search_all_partners,
        testpoint,
        stq_runner,
        reschedule_counter,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_response400(request):
        return mockserver.make_response(
            status=400,
            json={
                'error': {'to': [{'name': ['Need value']}]},
                'status': 'ERROR',
            },
        )

    @testpoint('email_stq_restart')
    def _email_stq_event_sender_restart(data):
        return data

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='restart_task', reschedule_counter=reschedule_counter,
    )

    assert not _email_stq_event_sender_restart.has_calls


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
    EATS_RESTAPP_COMMUNICATIONS_EVENT_SENDER_RETRY_SETTINGS=CFG_RETRY_SETTINGS,
)
@pytest.mark.parametrize('reschedule_counter', [28, 29, 30])
async def test_stq_restart_if_received_4xx_status_from_sender_but_not_400(
        mockserver,
        mock_search_all_partners,
        testpoint,
        stq_runner,
        reschedule_counter,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_response403(request):
        return mockserver.make_response(status=403, json={})

    @testpoint('email_stq_restart')
    def _email_stq_event_sender_restart(data):
        return data

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='restart_task', reschedule_counter=reschedule_counter,
    )

    assert not _email_stq_event_sender_restart.has_calls


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
    EATS_RESTAPP_COMMUNICATIONS_EVENT_SENDER_RETRY_SETTINGS=CFG_RETRY_SETTINGS,
)
@pytest.mark.parametrize(
    'reschedule_counter, has_stq_restarted',
    [(28, True), (29, True), (30, False)],
)
async def test_stq_restart_w_different_reschedule_counter(
        mockserver,
        mock_search_all_partners,
        testpoint,
        stq_runner,
        reschedule_counter,
        has_stq_restarted,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_response500(request):
        return mockserver.make_response(
            status=500, json={'error': 'Internal Server Error'},
        )

    @testpoint('email_stq_restart')
    def _email_stq_event_sender_restart(data):
        return data

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='restart_task', reschedule_counter=reschedule_counter,
    )

    assert _email_stq_event_sender_restart.has_calls == has_stq_restarted


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_stq_send_with_differents_emails_types(
        mockserver, mock_core_places, stq_runner,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        if request.json['to'][0]['email'] == 'email2':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [2],
                'places': ['place2 (address2)'],
            }
        elif request.json['to'][0]['email'] == 'common_email':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1],
                'places': ['place1 (address1)'],
            }
        elif request.json['to'][0]['email'] == 'other_email':
            assert request.json['args'] == {
                'locale': 'ru',
                'place_ids': [1, 4],
                'places': ['place1 (address1)', 'place4 (address4)'],
            }
        else:
            assert request.json == ''
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='emails_types_task',
    )
    assert mock_core_places.times_called == 1
    assert _mock_send_event.times_called == 3


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_event_with_token(
        taxi_eats_restapp_communications, stq, pgsql,
):
    event = 'password-request-reset'
    task_id = 'custom_task_id'
    partner_ids = [1]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'partner_ids': partner_ids},
        'data': {},
        'idempotency_token': task_id,
    }
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 1
    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'
    assert arg['id'] == 'custom_task_id'

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'asap',
            {'emails_types': [], 'recipients': {'partner_ids': partner_ids}},
            {},
            None,
            None,
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_event_with_existing_token(
        taxi_eats_restapp_communications, stq, pgsql,
):
    event = 'password-request-reset'
    task_id = 'finished_task'
    partner_ids = [1]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'partner_ids': partner_ids},
        'data': {},
        'idempotency_token': task_id,
    }
    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 0
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        ('finished_task',),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'asap',
            {'emails_types': [], 'recipients': {'place_ids': [1, 2]}},
            {},
            None,
            parse('2022-07-13T00:00:00+03'),
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_event_with_secret_data(
        taxi_eats_restapp_communications, stq, pgsql, mockserver,
):
    event = 'password-request-reset'
    partner_ids = [1]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'partner_ids': partner_ids},
        'data': {'password': 'asdf'},
    }

    @mockserver.json_handler(
        '/personal/v1/personal_doc/identification_docs/store',
    )
    def _mock_personal(request):
        assert request.json['fields'] == [
            {'key': 'masked', 'value': '{"password":"asdf"}'},
        ]
        return mockserver.make_response(status=200, json={'id': 'stored_id'})

    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 1
    arg = stq.eats_restapp_communications_event_sender.next_call()
    assert arg['queue'] == 'eats_restapp_communications_event_sender'

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (arg['id'],),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'asap',
            {'emails_types': [], 'recipients': {'partner_ids': partner_ids}},
            None,
            'stored_id',
            None,
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
    EATS_RESTAPP_COMMUNICATION_SEND_EVENT_SETTINGS={'partner_search_limit': 1},
)
@pytest.mark.parametrize(
    'task_id',
    [
        pytest.param('unknown_task', id='unknown task'),
        pytest.param('finished_task', id='finished task'),
        pytest.param('delayed_task', id='delayed task'),
    ],
)
async def test_stq_send_skip_tasks(stq_runner, testpoint, task_id):
    @testpoint('email_call')
    def _email_call(data):
        return data

    @testpoint('telegram_call')
    def _telegram_call(data):
        return data

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id=task_id,
    )

    assert _email_call.times_called == 0
    assert _telegram_call.times_called == 0


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_stq_send_task_with_data(
        mockserver, mock_get_partners_200, stq_runner, pgsql,
):
    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        assert request.json['args'] == {'locale': 'ru', 'some': 'value'}
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='task_with_data',
    )
    assert mock_get_partners_200.times_called == 2
    assert _mock_send_event.times_called == 2
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        ('task_with_data',),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] is not None


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_stq_send_task_with_masked_data(
        mockserver, mock_get_partners_200, stq_runner, pgsql,
):
    @mockserver.json_handler(
        '/personal/v1/personal_doc/identification_docs/retrieve',
    )
    def _mock_personal(request):
        assert request.json['id'] == 'personal_doc_id'
        return mockserver.make_response(
            status=200,
            json={
                'id': 'personal_doc_id',
                'fields': [
                    {'key': 'masked', 'value': '{"password":"asdf"}'},
                    {'key': 'other', 'value': '{"password":"qwerty"}'},
                ],
            },
        )

    @mockserver.json_handler(
        '/sender/api/0/yandex.food/transactional/8Y2IS654-4J2/send',
    )
    def _mock_send_event(request):
        assert request.json['args'] == {'locale': 'ru', 'password': 'asdf'}
        return mockserver.make_response(
            status=200,
            json={
                'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'},
            },
        )

    await stq_runner.eats_restapp_communications_event_sender.call(
        task_id='task_with_masked_data',
    )
    assert _mock_personal.times_called == 1
    assert mock_get_partners_200.times_called == 2
    assert _mock_send_event.times_called == 2
    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        ('task_with_masked_data',),
    )
    res = cursor.fetchall()
    assert len(res) == 1
    assert res[0][0] is not None


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_new_delayed_event(
        taxi_eats_restapp_communications, stq, pgsql, mockserver,
):
    task_id = 'custom_task_id'
    event = 'password-request-reset'
    place_ids = [3]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'place_ids': place_ids},
        'data': {'key': 'new_value', 'some': ['c'], 'param': 'asdf'},
        'idempotency_token': task_id,
        'event_mode': 'delayed',
    }

    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (task_id,),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'delayed',
            {'emails_types': [], 'recipients': {'place_ids': place_ids}},
            {'key': 'new_value', 'some': ['c'], 'param': 'asdf'},
            None,
            None,
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_delayed_event_with_existing_unmasked(
        taxi_eats_restapp_communications, stq, pgsql, mockserver,
):
    task_id = 'delayed_task_with_data'
    event = 'password-request-reset'
    place_ids = [3]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'place_ids': place_ids},
        'data': {'key': 'new_value', 'some': ['c'], 'param': 'asdf'},
        'idempotency_token': task_id,
        'event_mode': 'delayed',
    }

    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (task_id,),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'delayed',
            {'emails_types': [], 'recipients': {'place_ids': place_ids}},
            {
                'key': 'new_value',
                'some': ['a', 'b', 'c'],
                'param': 'asdf',
                'keep': 'this',
            },
            None,
            None,
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_masked_delayed_event_with_existing(
        taxi_eats_restapp_communications, stq, pgsql, mockserver,
):
    task_id = 'delayed_task_with_data'
    event = 'password-request-reset'
    place_ids = [3]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'place_ids': place_ids},
        'data': {'key': 'new_value', 'some': ['c'], 'password': 'asdf'},
        'idempotency_token': task_id,
        'event_mode': 'delayed',
    }

    @mockserver.json_handler(
        '/personal/v1/personal_doc/identification_docs/store',
    )
    def _mock_personal(request):
        fields = request.json['fields'][0]
        assert fields['key'] == 'masked'
        assert json.loads(fields['value']) == {
            'key': 'new_value',
            'some': ['a', 'b', 'c'],
            'password': 'asdf',
            'keep': 'this',
        }
        return mockserver.make_response(status=200, json={'id': 'stored_id'})

    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (task_id,),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'delayed',
            {'emails_types': [], 'recipients': {'place_ids': place_ids}},
            None,
            'stored_id',
            None,
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_delayed_event_with_masked_existing(
        taxi_eats_restapp_communications, stq, pgsql, mockserver,
):
    task_id = 'delayed_task_with_masked_data'
    event = 'password-request-reset'
    place_ids = [3]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'place_ids': place_ids},
        'data': {'key': 'new_value', 'some': ['c'], 'keep': 'this'},
        'idempotency_token': task_id,
        'event_mode': 'delayed',
    }

    @mockserver.json_handler(
        '/personal/v1/personal_doc/identification_docs/retrieve',
    )
    def _mock_personal_retrieve(request):
        assert request.json['id'] == 'personal_doc_id'
        return mockserver.make_response(
            status=200,
            json={
                'id': 'personal_doc_id',
                'fields': [
                    {
                        'key': 'masked',
                        'value': json.dumps(
                            {
                                'key': 'value',
                                'some': ['a', 'b'],
                                'password': 'asdf',
                            },
                        ),
                    },
                    {'key': 'other', 'value': '{"password":"qwerty"}'},
                ],
            },
        )

    @mockserver.json_handler(
        '/personal/v1/personal_doc/identification_docs/store',
    )
    def _mock_personal_store(request):
        fields = request.json['fields'][0]
        assert fields['key'] == 'masked'
        assert json.loads(fields['value']) == {
            'key': 'new_value',
            'some': ['a', 'b', 'c'],
            'password': 'asdf',
            'keep': 'this',
        }
        return mockserver.make_response(status=200, json={'id': 'stored_id'})

    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (task_id,),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'delayed',
            {'emails_types': [], 'recipients': {'place_ids': place_ids}},
            None,
            'stored_id',
            None,
        ),
    ]


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_send_event_data.sql',),
)
@pytest.mark.config(
    EATS_RESTAPP_COMMUNICATIONS_EMAIL_SETTINGS=CONFIG_EMAIL_SETTINGS,
)
async def test_send_delayed_event_with_existing_finished(
        taxi_eats_restapp_communications, stq, pgsql, mockserver,
):
    task_id = 'delayed_task_finished'
    event = 'password-request-reset'
    place_ids = [3]
    url = '/internal/communications/v1/send-event?event_type={}'.format(event)
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    data = {
        'recipients': {'place_ids': place_ids},
        'data': {'key': 'new_value', 'some': ['c'], 'param': 'asdf'},
        'idempotency_token': task_id,
        'event_mode': 'delayed',
    }

    response = await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )
    assert response.status_code == 204
    assert stq.eats_restapp_communications_event_sender.times_called == 0

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        """
        SELECT event_type, event_mode, recipients,
               data, masked_data, deleted_at
        FROM eats_restapp_communications.send_event_data
        WHERE event_id = %s
        """,
        (task_id,),
    )
    res = cursor.fetchall()
    assert res == [
        (
            event,
            'delayed',
            {'emails_types': [], 'recipients': {'place_ids': place_ids}},
            {'key': 'new_value', 'param': 'asdf', 'some': ['c']},
            None,
            None,
        ),
    ]
