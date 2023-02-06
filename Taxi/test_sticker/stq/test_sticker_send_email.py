import json

from aiohttp import web
import pytest

from sticker.stq import sticker_send_email


@pytest.mark.now('2020-12-03T17:00:00Z')
@pytest.mark.parametrize(
    (
        'message_id,'
        'personal_error,'
        'expected_sender_times_called,'
        'sender_error,'
        'reschedule_times_called,'
        'expected_status,'
        'expected_fail_count,'
    ),
    [
        (1, False, 0, False, 0, 'SCHEDULED', 0),
        (2, False, 0, False, 0, 'PROCESSING', 0),
        (3, False, 1, False, 0, 'SCHEDULED', 1),
        (3, False, 1, True, 1, 'TO_RETRY', 2),
        (4, False, 1, False, 0, 'SCHEDULED', 9),
        (4, False, 1, True, 0, 'FAILED', 10),
        (5, False, 1, False, 0, 'SCHEDULED', 0),
        (5, False, 1, True, 1, 'TO_RETRY', 1),
        (5, True, 0, False, 0, 'FAILED', 1),
    ],
)
@pytest.mark.config(TVM_RULES=[{'src': 'sticker', 'dst': 'personal'}])
async def test_sticker_send_email(
        stq3_context,
        mockserver,
        message_id,
        personal_error,
        expected_sender_times_called,
        sender_error,
        reschedule_times_called,
        expected_status,
        expected_fail_count,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _stq_reschedule(request):
        data = request.json
        assert data['queue_name'] == 'sticker_send_email'
        assert data['task_id'] == str(message_id)
        return {}

    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def _personal_retrieve_email(request):
        if personal_error:
            return {'items': []}
        return {
            'items': [
                {'id': value['id'], 'value': f'test_{value["id"]}@yandex.ru'}
                for value in request.json['items']
            ],
        }

    @mockserver.json_handler('/sender', prefix=True)
    def _sender(request):
        if sender_error:
            return web.Response(status=400)
        expected_data = {
            'async': True,
            'args': json.dumps({'html_body': ''}),
            'headers': {'X-Yandex-Hint': 'label=SystMetkaSO:taxi'},
        }
        to_email = request.query['to_email']
        if to_email == 'test_2_with_attachment@yandex.ru':
            expected_data['attachments'] = [
                {
                    'data': 'test',
                    'filename': 'some.pdf',
                    'mime_type': 'application/pdf',
                },
            ]
        assert request.json == expected_data
        assert 'test_' in to_email
        assert request.query['from_email'] == 'no-reply@taxi.yandex.ru'
        assert request.query['from_name'] == 'Яндекс Go'
        return {}

    await sticker_send_email.task(stq3_context, message_id)
    assert _sender.times_called == expected_sender_times_called
    assert _stq_reschedule.times_called == reschedule_times_called
    async with stq3_context.pg.master.acquire() as connection:
        record = await connection.fetchrow(
            'SELECT * FROM sticker.mail_queue WHERE id = $1', message_id,
        )
    assert record['status'] == expected_status
    assert record['fail_count'] == expected_fail_count
