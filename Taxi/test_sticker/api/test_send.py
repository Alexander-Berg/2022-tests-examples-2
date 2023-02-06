# type: ignore
import copy
import datetime
import itertools

import pytest

from sticker.mail import types
from test_sticker.mail import smailik as smailik_test


DEFAULT_PARAM_VALUES = {
    'body': smailik_test.VAILD_MAIL_REQUEST_BODY,
    'send_to': ['id02'],
    'idempotence_token': '10',
}
DEFAULT_PARAM_VALUES_INTERNAL = {
    'body': smailik_test.VAILD_MAIL_REQUEST_BODY,
    'send_to': 'someone@yandex-team.ru',
    'idempotence_token': '10',
}


@pytest.mark.pgsql(
    'sticker', files=['test_add_mail_to_queue_bad_requests.sql'],
)
@pytest.mark.parametrize(
    'params',
    [
        {},
        *(
            param_set
            for params_num in range(1, len(DEFAULT_PARAM_VALUES))
            for param_set in list(
                itertools.combinations(
                    DEFAULT_PARAM_VALUES.items(), params_num,
                ),
            )
        ),
    ],
)
async def test_missing_required_params(web_app_client, params):
    response = await web_app_client.post(path='/send/', json=dict(params))
    assert response.status == 400


@pytest.mark.pgsql(
    'sticker', files=['test_add_mail_to_queue_bad_requests.sql'],
)
@pytest.mark.parametrize(
    'override_params, expected_status',
    [
        # invalid mail bodies
        *(
            pytest.param({'body': xml_body}, 400, id='bad_xml_body')
            for xml_body in smailik_test.INVALID_MAIL_REQUEST_BODIES
        ),
        # letters already in queue with the same body;
        # different tokens correspond to different statuses
        *(
            pytest.param(
                {
                    'send_to': ['id01'],
                    'body': '<mails><mail><from>a@a.a</from></mail></mails>',
                    'idempotence_token': str(i),
                },
                200,
                id=f'letter_already_in_queue_{i}',
            )
            for i in range(1, 6)
        ),
        # letters already in queue with a different body;
        # different tokens correspond to different statuses
        *(
            ({'send_to': ['id01'], 'idempotence_token': str(i)}, 403)
            for i in range(1, 6)
        ),
        # no more than one recipient
        ({'send_to': ['id03', 'id04']}, 400),
        ({}, 200),
        ({'send_to': ['id01']}, 200),
        ({'idempotence_token': '12'}, 200),
    ],
)
async def test_add_mail_to_queue_bad_requests(
        web_app_client, override_params, expected_status,
):
    params = copy.copy(DEFAULT_PARAM_VALUES)
    params.update(override_params)

    response = await web_app_client.post(path='/send/', json=params)
    assert response.status == expected_status


@pytest.mark.config(
    STICKER_INTERNAL_EMAIL_SETTINGS={
        'allowed_domains': [],
        'allowed_emails': ['ya@ya.ru'],
    },
)
@pytest.mark.parametrize(
    'endpoint, recipient',
    [('/send/', ['id01']), ('/send-internal/', 'ya@ya.ru')],
)
@pytest.mark.usefixtures('mock_tvm')
@pytest.mark.config(
    TVM_ENABLED=True,
    STICKER_RAW_SEND_ALLOWED_SERVICES={'tvm_names': ['src_test_service']},
    STICKER_SEND_AFTER_SETTINGS={
        'delay': 90,
        'look_back_interval': 60,
        'max_count': 5,
        'set_send_after': True,
    },
)
@pytest.mark.config(TVM_RULES=[{'src': 'sticker', 'dst': 'personal'}])
async def test_add_with_attachment(
        web_context, web_app_client, endpoint, recipient,
):
    response = await web_app_client.post(
        endpoint,
        headers={'X-Ya-Service-Ticket': 'good'},
        json={
            'body': smailik_test.VAILD_MAIL_REQUEST_BODY,
            'send_to': recipient,
            'idempotence_token': '123',
            'attachments': [
                {
                    'filename': 'a.json',
                    'mime_type': 'application/json',
                    'data': smailik_test.VALID_B64_JSON_DATA,
                },
            ],
        },
    )
    assert response.status == 200
    async with web_context.pg.master.acquire() as connection:
        query = (
            'SELECT recipient, recipient_type, '
            'tvm_name FROM sticker.mail_queue;'
        )
        data = await connection.fetch(query)
    assert len(data) == 1
    assert data[0]['tvm_name'] == 'src_test_service'


@pytest.mark.config(
    STICKER_SEND_AFTER_SETTINGS={
        'set_send_after': True,
        'delay': 60,
        'look_back_interval': 60,
        'max_count': 3,
    },
)
@pytest.mark.parametrize(
    'send_to,token,expected_send_after',
    [
        ('test1', '0', datetime.datetime(2019, 11, 29, 10, 1, 2)),
        ('test2', '0', datetime.datetime(2019, 11, 29, 10, 0, 1)),
        ('test3', '0', datetime.datetime(2019, 11, 29, 10, 5, 0)),
        ('test4', '0', None),
    ],
)
@pytest.mark.usefixtures('mock_tvm')
@pytest.mark.pgsql('sticker', files=['test_set_send_after.sql'])
async def test_set_send_after(
        web_app_client, send_to, token, expected_send_after, web_context,
):
    response = await web_app_client.post(
        '/send/',
        json={
            'body': smailik_test.VAILD_MAIL_REQUEST_BODY,
            'send_to': [send_to],
            'idempotence_token': token,
        },
    )
    assert response.status == 200
    if not expected_send_after:
        return
    async with web_context.pg.master.acquire() as connection:
        query = (
            f'SELECT * FROM sticker.mail_queue '
            f'WHERE recipient = \'{send_to}\' '
            f'AND idempotence_token = \'{token}\''
        )
        row = await connection.fetchrow(query)
    assert row['send_after'] == expected_send_after


@pytest.mark.config(
    STICKER_INTERNAL_EMAIL_SETTINGS={
        'allowed_domains': ['yandex-team.ru'],
        'allowed_emails': [],
    },
)
@pytest.mark.pgsql('sticker', files=['test_add_mail_to_queue_internal.sql'])
@pytest.mark.parametrize(
    'override_params, expected_status',
    [
        # invalid mail bodies
        *(
            pytest.param({'body': xml_body}, 400, id=f'invalid-body-{i}')
            for i, xml_body in enumerate(
                smailik_test.INVALID_MAIL_REQUEST_BODIES,
            )
        ),
        # letters already in queue with the same body;
        # different tokens correspond to different statuses
        *(
            pytest.param(
                {
                    'body': '<mails><mail><from>a@a.a</from></mail></mails>',
                    'idempotence_token': str(i),
                },
                200,
                id=f'already-in-queue-{i}',
            )
            for i in range(1, 6)
        ),
        # letters already in queue with a different body;
        # different tokens correspond to different statuses
        *(
            pytest.param(
                {'idempotence_token': str(i)},
                403,
                id=f'letter-in-queue_token-exists',
            )
            for i in range(1, 6)
        ),
        pytest.param({'send_to': 'someone@ya.ru'}, 400, id='invalid-email'),
        pytest.param({'send_to': 'someone'}, 400, id='malformed-email'),
        pytest.param(
            {'send_to': 'someone@yandex.net'},
            200,
            marks=pytest.mark.config(
                STICKER_INTERNAL_EMAIL_SETTINGS={
                    'allowed_domains': ['yandex-team.ru'],
                    'allowed_emails': ['someone@yandex.net'],
                },
            ),
            id='allowed_extra_email',
        ),
        pytest.param(
            {
                'send_to': 'someone@yandex-team.ru',
                'copy_send_to': ['other-someone@yandex-team.ru'],
            },
            400,
            marks=pytest.mark.config(
                STICKER_INTERNAL_EMAIL_SETTINGS={
                    'allowed_domains': ['yandex-team.ru'],
                    'allowed_emails': [],
                },
                STICKER_MAX_ALLOWED_RECIPIENTS={
                    'enabled': True,
                    'services': {
                        types.RecipientType.INTERNAL.value.lower(): 1,
                    },
                },
            ),
            id='bad recipients count',
        ),
    ],
)
async def test_add_mail_to_queue_internal(
        web_app_client, override_params, expected_status,
):
    params = copy.copy(DEFAULT_PARAM_VALUES_INTERNAL)
    params.update(override_params)

    response = await web_app_client.post(path='/send-internal/', json=params)
    assert response.status == expected_status


@pytest.mark.config(
    STICKER_INTERNAL_EMAIL_SETTINGS={
        'allowed_domains': ['yandex-team.ru'],
        'allowed_emails': [],
    },
)
async def test_send_external_and_internal_with_same_idemp_token(
        web_app_client, web_context,
):
    response = await web_app_client.post(
        path='/send-internal/', json=DEFAULT_PARAM_VALUES_INTERNAL,
    )
    assert response.status == 200

    response = await web_app_client.post(
        path='/send/', json=DEFAULT_PARAM_VALUES,
    )
    assert response.status == 403

    async with web_context.pg.master.acquire() as connection:
        query = 'SELECT count(*) FROM sticker.mail_queue;'
        val = await connection.fetchval(query)
    assert val == 1


@pytest.mark.usefixtures('mock_tvm')
@pytest.mark.config(
    TVM_ENABLED=True,
    STICKER_RAW_SEND_ALLOWED_SERVICES={'tvm_names': ['src_test_service']},
)
@pytest.mark.parametrize(
    'headers, status, is_error',
    [
        ({'X-Ya-Service-Ticket': 'good'}, 200, False),
        ({'X-Ya-Service-Ticket': 'some_service'}, 400, True),
        ({'X-Ya-Service-Ticket': 'auth_fail'}, 401, True),
        (None, 401, True),
    ],
)
async def test_send_raw(
        web_app_client, web_context, headers, status, is_error,
):
    response = await web_app_client.post(
        path='/send-raw/', json=DEFAULT_PARAM_VALUES_INTERNAL, headers=headers,
    )
    assert response.status == status
    if is_error:
        return
    async with web_context.pg.master.acquire() as connection:
        query = (
            'SELECT recipient, recipient_type, '
            'tvm_name FROM sticker.mail_queue;'
        )
        data = await connection.fetch(query)
    assert len(data) == 1
    assert dict(data[0]) == {
        'recipient': 'someone@yandex-team.ru',
        'recipient_type': 'RAW',
        'tvm_name': 'src_test_service',
    }
