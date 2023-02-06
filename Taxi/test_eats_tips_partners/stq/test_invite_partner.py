import datetime
import http

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as testsuite_http

from taxi.stq import async_worker_ng
from taxi.util import dates

from eats_tips_partners.stq import invite_partner


NOW = datetime.datetime(2022, 1, 1, 12, 0)

PERSONAL_PHONE_MAP = {
    'ok_phone_id': '+79000000000',
    'no_invites_phone_id': '+79000000001',
    'existing_phone_id': '+79000000002',
    'already_sent_sms_phone_id': '+79000000003',
    'bad_format_phone_id': '+7123456',
    'bad_format_phone_id_2': '+1234567',
}


@pytest.mark.parametrize(
    ('phone_id', 'is_sms_logged', 'sms_status', 'sms_ru_response'),
    (
        pytest.param(
            'ok_phone_id',
            True,
            'OK',
            {
                'status': 'OK',
                'status_code': 100,
                'sms': {'79000000000': {'status': 'OK', 'status_code': 100}},
            },
            id='ok',
        ),
        pytest.param(
            'ok_phone_id',
            True,
            'OK',
            {
                'status': 'OK',
                'status_code': 100,
                'sms': {'+79000000000': {'status': 'OK', 'status_code': 100}},
            },
            id='ok-with-plus',
        ),
        pytest.param(
            'no_invites_phone_id', False, None, None, id='no-invites',
        ),
        pytest.param(
            'existing_phone_id', False, None, None, id='existing-partner',
        ),
        pytest.param(
            'already_sent_sms_phone_id',
            False,
            None,
            None,
            id='already-sent-sms',
        ),
        pytest.param(
            'unexpected_phone_id',
            False,
            None,
            None,
            id='not-exists-in-personal',
        ),
        pytest.param(
            'bad_format_phone_id', False, None, None, id='bad-phone-format',
        ),
        pytest.param(
            'bad_format_phone_id_2',
            False,
            None,
            None,
            id='bad-phone-format-2',
        ),
        pytest.param(
            'ok_phone_id',
            True,
            'ERROR',
            {'status': 'ERROR', 'status_code': 200},
            id='sms-ru-error',
        ),
        pytest.param(
            'ok_phone_id',
            True,
            'ERROR',
            {
                'status': 'OK',
                'status_code': 100,
                'sms': {
                    '79000000000': {'status': 'ERROR', 'status_code': 200},
                },
            },
            id='sms-ru-error-2',
        ),
        pytest.param(
            'ok_phone_id',
            True,
            'ERROR',
            {'status': 'OK', 'status_code': 100},
            id='sms-ru-error-3',
        ),
    ),
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-partners', 'dst': 'personal'}],
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
@pytest.mark.now(NOW.isoformat())
async def test_invite_partner(
        stq3_context,
        mock_sms_ru,
        mockserver,
        pgsql,
        phone_id,
        is_sms_logged,
        sms_status,
        sms_ru_response,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _mock_phones_retrieve(request):
        value = PERSONAL_PHONE_MAP.get(request.json['id'])
        if value:
            return {'value': value, 'id': request.json['id']}
        return web.json_response({}, status=http.HTTPStatus.NOT_FOUND)

    @mock_sms_ru('/sms/send')
    async def _mock_send(request: testsuite_http.Request):
        return web.json_response(
            sms_ru_response, content_type='application/json',
        )

    await invite_partner.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1,
            exec_tries=1,
            reschedule_counter=1,
            queue='eats_tips_payments_invite_partner',
        ),
        phone_id=phone_id,
    )

    cursor = pgsql['eats_tips_partners'].cursor()
    cursor.execute(
        f"""
        SELECT phone_id, created_at, status
        FROM eats_tips_partners.sms_history
        """,
    )
    rows = cursor.fetchall()
    new_sms = [
        row[0] for row in rows if dates.localize(row[1]) >= dates.localize(NOW)
    ]
    if is_sms_logged:
        assert phone_id in new_sms
        assert sms_status == rows[-1][2]
    else:
        assert phone_id not in new_sms
