import http

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as testsuite_http

PERSONAL_PHONE_MAP = {
    '+79000000000': 'ok_phone_id',
    '+79000000010': 'phone_id_10',
    '+79000000013': 'phone_id_13',
    '+79999999999': 'sms_limit',
}
TRACK_TO_PHONE = {
    '111111': '+79000000000',
    'limit': '+79999999999',
    'have_partner': '+79000000013',
    'deleted_partner': '+79000000010',
}
TRACK_TO_CODE = {
    '111111': 'ok_code',
    'limit': 'limit',
    'have_partner': 'partner',
    'deleted_partner': 'partner',
    'bad_request': 'bad_request',
}


def _format_check_verification_request(
        *, track_id='111111', confirmation_code='ok_code',
):
    return {'track_id': track_id, 'confirmation_code': confirmation_code}


def _format_check_verification_response(*, status='new'):
    return {'status': status}


def _format_partner_params(*, alias='3000000', b2p_id='3000000'):
    return {'alias': alias, 'b2p_id': b2p_id}


@pytest.mark.parametrize(
    ('params', 'partner_params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            _format_check_verification_request(),
            _format_partner_params(),
            http.HTTPStatus.OK,
            _format_check_verification_response(),
            id='ok',
        ),
        pytest.param(
            _format_check_verification_request(confirmation_code='bad_code'),
            _format_partner_params(),
            http.HTTPStatus.FORBIDDEN,
            {'code': 'forbidden', 'message': 'empty or invalid code'},
            id='invalid-code',
        ),
        pytest.param(
            _format_check_verification_request(
                track_id='have_partner', confirmation_code='partner',
            ),
            _format_partner_params(),
            http.HTTPStatus.OK,
            _format_check_verification_response(status='registered'),
            id='already-have-partner',
        ),
        pytest.param(
            _format_check_verification_request(
                track_id='deleted_partner', confirmation_code='partner',
            ),
            _format_partner_params(alias='0000100', b2p_id='10'),
            http.HTTPStatus.OK,
            _format_check_verification_response(),
            id='new-deleted-partner',
        ),
        pytest.param(
            _format_check_verification_request(
                track_id='limit', confirmation_code='limit',
            ),
            _format_partner_params(),
            http.HTTPStatus.TOO_MANY_REQUESTS,
            {
                'code': 'too_many_tries',
                'message': 'confirmation limits exceeded',
            },
            id='confirmation-limit-exceeded',
        ),
        pytest.param(
            _format_check_verification_request(
                track_id='bad_request', confirmation_code='bad_request',
            ),
            _format_partner_params(alias='0000100', b2p_id='10'),
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'passport error'},
            id='bad_request',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_partner_check_verification_code(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        web_context,
        mockserver,
        params,
        partner_params,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    async def _mock_phones_retrieve(request):
        value = PERSONAL_PHONE_MAP.get(request.json['value'])
        if value:
            return {'value': request.json['value'], 'id': value}
        return web.json_response({}, status=http.HTTPStatus.NOT_FOUND)

    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/commit/',
    )
    async def _commit(request: testsuite_http.Request):
        body = request.form
        track_id = body.get('track_id')
        code = TRACK_TO_CODE.get(track_id)
        if track_id == 'bad_request':
            return {'status': 'error'}
        if code != body.get('code'):
            return {'status': 'error', 'errors': ['code.invalid']}
        if code == 'limit':
            return {
                'status': 'error',
                'errors': ['confirmations_limit.exceeded'],
            }
        return {
            'status': 'ok',
            'number': {'original': TRACK_TO_PHONE[track_id][1:]},
        }

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/check-verification-code',
        json=params,
        headers={'X-Remote-IP': '1.2.3.4'},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if (
            expected_code == http.HTTPStatus.OK
            and expected_response['status'] == 'new'
    ):
        await _check_pg(
            web_context, expected_response['status'], partner_params,
        )


async def _check_pg(web_context, status, partner_params):
    alias = partner_params['alias']
    async with web_context.pg.replica_pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            select b2p_id, status
            from eats_tips_partners.partner
            where alias = '{alias}';
            """,
        )
        assert dict(row) == {
            'b2p_id': partner_params['b2p_id'],
            'status': status,
        }

        row = await conn.fetchrow(
            f"""
                    select migrated, type
                    from eats_tips_partners.alias
                    where alias = '{alias}';""",
        )
        assert dict(row) == {'migrated': True, 'type': 'partner'}
