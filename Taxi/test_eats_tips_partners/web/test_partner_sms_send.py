import datetime
import http

from aiohttp import web
import pytest

from taxi.util import dates

from test_eats_tips_partners import conftest

NOW = datetime.datetime(2021, 6, 15, 14, 30, 15)
BAD_TIME = datetime.datetime(2021, 6, 15, 12, 00, 00)

PERSONAL_PHONE_MAP = {
    '+79000000000': 'ok_phone_id',
    '+1234567': 'bad_format_phone_id_',
}


def _format_eats_tips_partners_sms_response(
        *, timestamp, phone, message_type, signature=None, auth_code=None,
):
    timestamp = dates.timestamp(timestamp, timezone='UTC')
    if not signature:
        signature = conftest.create_hmac(
            str(timestamp) + phone + message_type, 'awesome-hmac-token',
        )
    if not auth_code:
        return {
            'timestamp': timestamp,
            'message_type': message_type,
            'phone': phone,
            'signature': signature,
        }
    return {
        'timestamp': int(timestamp),
        'message_type': message_type,
        'phone': phone,
        'signature': signature,
        'auth_code': auth_code,
    }


@pytest.mark.parametrize(
    ('params', 'expected_code'),
    (
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=NOW,
                phone='+79000000000',
                message_type='eats_tips_invite_partner',
            ),
            http.HTTPStatus.OK,
            id='ok-sms-send',
        ),
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=NOW,
                phone='aaaaaa',
                message_type='eats_tips_invite_partner',
            ),
            http.HTTPStatus.BAD_REQUEST,
            id='error-sms-send',
        ),
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=NOW,
                phone='+79000000000',
                message_type='eats_tips_auth_message',
                auth_code='000000',
            ),
            http.HTTPStatus.OK,
            id='ok-auth-sms-send',
        ),
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=NOW,
                phone='+79000000000',
                message_type='eats_tips_auth_message',
                auth_code='0000',
            ),
            http.HTTPStatus.BAD_REQUEST,
            id='error-auth-sms-send-1',
        ),
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=NOW,
                phone='+79000000000',
                message_type='eats_tips_auth_message',
                auth_code='aaaaaa',
            ),
            http.HTTPStatus.BAD_REQUEST,
            id='error-auth-sms-send-2',
        ),
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=BAD_TIME,
                phone='+79000000000',
                message_type='eats_tips_auth_message',
                auth_code='000000',
            ),
            http.HTTPStatus.FORBIDDEN,
            id='bad-time-sms-send',
        ),
        pytest.param(
            _format_eats_tips_partners_sms_response(
                timestamp=NOW,
                phone='+79000000000',
                message_type='eats_tips_auth_message',
                auth_code='000000',
                signature='0000000000000',
            ),
            http.HTTPStatus.CONFLICT,
            id='conflict-sms-send',
        ),
    ),
)
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'eats-tips-partners', 'dst': 'personal'},
        {'src': 'eats-tips-partners', 'dst': 'stq-agent'},
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_partner_sms_send(
        taxi_eats_tips_partners_web,
        web_context,
        mockserver,
        stq,
        params,
        expected_code,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    async def _mock_phones_retrieve(request):
        value = PERSONAL_PHONE_MAP.get(request.json['value'])
        print(value)
        if value:
            return {'value': request.json['value'], 'id': value}
        return web.json_response({}, status=http.HTTPStatus.NOT_FOUND)

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/sms/send',
        json=params,
        headers={'X-Tips-Api-Token': 'some-token'},
    )
    assert response.status == expected_code

    config = web_context.config.EATS_TIPS_PARTNERS_SMS_SEND_SETTINGS
    text = config[params['message_type']]['message_text']['default']
    if params['message_type'] == 'eats_tips_auth_message':
        text = text.format(auth_code=params['auth_code'])
    if response.status == http.HTTPStatus.OK:
        assert stq.eats_tips_partners_send_sms.times_called == 1
        conftest.check_task_queued(
            stq,
            stq.eats_tips_partners_send_sms,
            {
                'text': text,
                'phone_id': PERSONAL_PHONE_MAP.get(params['phone']),
                'intent': params['message_type'],
            },
        )
