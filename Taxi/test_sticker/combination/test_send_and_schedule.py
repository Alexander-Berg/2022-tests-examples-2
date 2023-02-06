import base64

import pytest

from sticker.generated.cron import run_cron
from sticker.mail import types
from test_sticker.mail import smailik as smailik_test

PERSONAL_MAP = {'id02': 'some@yandex.ru', 'id04': 'other-some@yandex.ru'}


@pytest.mark.usefixtures('mock_tvm')
@pytest.mark.parametrize(
    'endpoint, send_to, cc_send_to',
    [
        ('/send/', ['id02'], None),
        ('/send/', ['id02'], ['id04']),
        ('/send-internal/', 'ya@ya.ru', None),
        ('/send-raw/', 'ya@ya.ru', None),
        ('/send-internal/', 'ya@ya.ru', ['other@ya.ru']),
        ('/send-raw/', 'ya@ya.ru', ['other@ya.ru']),
    ],
)
@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
    STICKER_INTERNAL_EMAIL_SETTINGS={
        'allowed_domains': ['ya.ru'],
        'allowed_mails': [],
    },
    STICKER_RAW_SEND_ALLOWED_SERVICES={'tvm_names': ['src_test_service']},
    STICKER_MAX_ALLOWED_RECIPIENTS={
        'enabled': True,
        'services': {
            recipient_type.value.lower(): 2
            for recipient_type in types.RecipientType
        },
    },
    TVM_ENABLED=True,
)
async def test_send_and_schedule(
        patch, web_app_client, cron_context, endpoint, send_to, cc_send_to,
):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': PERSONAL_MAP[kwargs['request_id']]}

    @patch('sticker.mail.smailik.send_email')
    def _send_email(*args, **kwargs):
        pass

    json_body = {
        'body': smailik_test.VAILD_MAIL_REQUEST_BODY,
        'send_to': send_to,
        'idempotence_token': '10',
    }
    if cc_send_to is not None:
        json_body['copy_send_to'] = cc_send_to
    response = await web_app_client.post(
        endpoint, json=json_body, headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 200

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])

    async with cron_context.pg.master.acquire() as connection:
        row = await connection.fetchrow(
            'SELECT id, status FROM sticker.mail_queue',
        )

    assert row['id'] == 1
    assert row['status'] == 'SCHEDULED'


@pytest.mark.usefixtures('mock_tvm')
@pytest.mark.parametrize(
    'endpoint, send_to',
    [
        ('/send/', ['id02']),
        ('/send-internal/', 'ya@ya.ru'),
        ('/send-raw/', 'ya@ya.ru'),
    ],
)
@pytest.mark.config(
    STICKER_SCHEDULER_CHUNK_DELAY=0.0,
    STICKER_SCHEDULER_CHUNK_SETTINGS={'chunks_per_run': 1, 'chunk_size': 10},
    STICKER_INTERNAL_EMAIL_SETTINGS={
        'allowed_domains': ['ya.ru'],
        'allowed_mails': [],
    },
    STICKER_RAW_SEND_ALLOWED_SERVICES={'tvm_names': ['src_test_service']},
    TVM_ENABLED=True,
)
async def test_send_and_schedule_with_attach(
        patch, web_app_client, cron_context, endpoint, send_to,
):
    @patch('sticker.stuff.scheduler._personals_tvm_auth_cache_refresh')
    async def _personals_tvm_auth_cache_refresh(*args, **kwargs):
        return

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'email': 'some@yandex.ru'}

    @patch('sticker.mail.smailik.send_email')
    def _send_email(*args, **kwargs):
        pass

    @patch('sticker.mail.smailik.path.write_attachment')
    def _write_attachment(attach):
        assert attach.id == 1
        assert attach.file_name == 'filename.jpeg'
        assert attach.body == base64.b64decode(
            smailik_test.VALID_B64_JSON_DATA,
        )

    response = await web_app_client.post(
        endpoint,
        json={
            'body': smailik_test.VAILD_MAIL_REQUEST_BODY,
            'send_to': send_to,
            'idempotence_token': '10',
            'attachments': [
                {
                    'mime_type': 'image/jpeg',
                    'filename': 'filename.jpeg',
                    'data': smailik_test.VALID_B64_JSON_DATA,
                },
            ],
        },
        headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 200

    await run_cron.main(['sticker.stuff.scheduler', '-t', '0', '-d'])
    async with cron_context.pg.master.acquire() as connection:
        row = await connection.fetchrow(
            'SELECT id, status FROM sticker.mail_queue',
        )

    assert row['id'] == 1
    assert row['status'] == 'SCHEDULED'

    async with cron_context.pg.master.acquire() as connection:
        row = await connection.fetchrow(
            'SELECT id, file_name FROM sticker.attachment;',
        )

    assert row['id'] == 1
    assert row['file_name'] == 'filename.jpeg'

    assert len(_write_attachment.calls) == 1
