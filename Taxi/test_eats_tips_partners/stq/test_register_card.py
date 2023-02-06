import http

from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http as testsuite_http

from taxi.stq import async_worker_ng

from eats_tips_partners.stq import register_card
from test_eats_tips_partners import conftest

PERSONAL_PHONE_MAP = {
    'ok_phone_id_1': '+79000000001',
    'ok_phone_id_2': '+79000000002',
}


def _format_b2p_response(
        b2p_id,
        first_name='Абоба',
        second_name='Бабобус',
        active=0,
        last_name=None,
        pan=None,
        phone=None,
):
    return conftest.b2p_user_answer(
        client_ref=b2p_id,
        first_name=first_name,
        second_name=second_name,
        last_name=last_name,
        active=active,
        pan=pan,
        phone=phone,
    )


def _format_database_response(
        virtual_card_pan='12345', virtual_card_status='success',
):
    best2pay = virtual_card_pan or ''
    pay_method = 'best2pay' if virtual_card_pan else ''
    return {
        'virtual_card_pan': virtual_card_pan,
        'virtual_card_status': virtual_card_status,
        'best2pay': best2pay,
        'pay_method': pay_method,
    }


def _format_b2_times_called(register=1, set_phone=1, info=1):
    return {'register': register, 'set_phone': set_phone, 'info': info}


@pytest.mark.parametrize(
    'b2p_id, b2p_register_response,'
    'b2p_set_phone_response, b2p_info_response,'
    'expected_database_info, b2_times_called, stq_id,',
    (
        pytest.param(
            '1',
            _format_b2p_response(b2p_id='1'),
            _format_b2p_response(b2p_id='1', phone='79000000001'),
            _format_b2p_response(b2p_id='1', active=1, pan='12345'),
            _format_database_response(),
            _format_b2_times_called(),
            1,
            id='ok',
        ),
        pytest.param(
            '1',
            conftest.SOME_B2P_ERROR_RESPONSE,
            _format_b2p_response(b2p_id='1'),
            _format_b2p_response(b2p_id='1', active=1, pan='12345'),
            _format_database_response(
                virtual_card_pan=None, virtual_card_status='error',
            ),
            _format_b2_times_called(1, 0, 0),
            1,
            id='error',
        ),
        pytest.param(
            '2',
            conftest.B2P_ALREADY_REGISTERED_RESPONSE,
            _format_b2p_response(b2p_id='2'),
            _format_b2p_response(b2p_id='2', active=1, pan='12345'),
            _format_database_response(),
            _format_b2_times_called(1, 1, 1),
            1,
            id='some-request-already-completed',
        ),
    ),
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-tips-partners', 'dst': 'personal'}],
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_register_card(
        stq3_context,
        stq,
        b2p_id,
        mockserver,
        mock_best2pay,
        b2p_register_response,
        b2p_set_phone_response,
        b2p_info_response,
        b2_times_called,
        expected_database_info,
        stq_id,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _mock_phones_retrieve(request: testsuite_http.Request):
        value = PERSONAL_PHONE_MAP.get(request.json['id'])
        if value:
            return {'value': value, 'id': request.json['id']}
        return web.json_response({}, status=http.HTTPStatus.NOT_FOUND)

    @mock_best2pay('/webapi/b2puser/Register')
    async def _mock_user_register(request):
        return web.Response(
            body=b2p_register_response,
            headers={'Content-Type': 'application/xml'},
            status=200,
        )

    @mock_best2pay('/gateweb/b2puser/SetPhone')
    async def _mock_user_set_phone(request):
        return web.json_response(
            {'success': True, 'client-ref': b2p_id}, status=200,
        )

    @mock_best2pay('/webapi/b2puser/Info')
    async def _mock_user_info(request):
        return web.Response(
            body=b2p_info_response,
            headers={'Content-Type': 'application/xml'},
            status=200,
        )

    partner_id = f'00000000-0000-0000-0000-{b2p_id.zfill(12)}'
    await register_card.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1,
            exec_tries=1,
            reschedule_counter=1,
            queue='eats_tips_partners_register_card',
        ),
        partner_id=partner_id,
    )
    assert b2_times_called == {
        'register': _mock_user_register.times_called,
        'set_phone': _mock_user_set_phone.times_called,
        'info': _mock_user_info.times_called,
    }

    async with stq3_context.pg.replica_pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            SELECT virtual_card_pan, virtual_card_status
            FROM eats_tips_partners.card_info
            WHERE partner_id = '{partner_id}'
            """,
        )
        assert (
            row.get('virtual_card_pan')
            == expected_database_info['virtual_card_pan']
        )
        assert (
            row.get('virtual_card_status')
            == expected_database_info['virtual_card_status']
        )
