import uuid

from aiohttp import web
import pytest

from eats_tips import components as tips_common


SUCCESS_RESTRICT_OPERATION = """<?xml version="1.0" encoding="UTF-8"?><response>
    <code>1</code>
    <description>Successful financial transaction</description>
</response>"""
FAILED_RESTRICT_OPERATION = """<?xml version="1.0" encoding="UTF-8"?><error>
    <description>Ошибка: неверная цифровая подпись.</description>
    <code>109</code>
</error>"""


@pytest.mark.parametrize(
    'partner_id_to_block, mysql_user_id, set_restricted_response, who_blocked,'
    'reason_to_block, block_state, order_id, expected_history, '
    'expected_status,expected_output_block_state, expected_full_block_state,'
    'expected_response',
    [
        pytest.param(
            '00000000-0000-0000-0000-000000000010',
            10,
            SUCCESS_RESTRICT_OPERATION,
            '-1',
            'some reason',
            'output',
            '1',
            True,
            200,
            1,
            0,
            None,
            id='output_block',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000010',
            10,
            SUCCESS_RESTRICT_OPERATION,
            '-1',
            'some reason',
            'total',
            '2',
            True,
            200,
            0,
            1,
            None,
            id='total_block',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000011',
            11,
            SUCCESS_RESTRICT_OPERATION,
            '-1',
            'some reason',
            'total',
            '1',
            True,
            200,
            0,
            1,
            None,
            id='total_block_upon_output',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000011',
            11,
            '',
            '-1',
            'some reason',
            'output',
            '1',
            False,
            200,
            1,
            0,
            None,
            id='same_type_block',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000012',
            12,
            '',
            '-1',
            'some reason',
            'output',
            '1',
            False,
            400,
            0,
            1,
            {
                'code': 'block_conflict',
                'message': 'user already totally blocked',
            },
            id='failed_output_block_upon_total',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000012',
            12,
            SUCCESS_RESTRICT_OPERATION,
            '-1',
            'some reason',
            'none',
            '1',
            False,
            200,
            0,
            0,
            None,
            id='unblock',
        ),
    ],
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_partner_block(
        taxi_eats_tips_partners_web,
        mockserver,
        web_context,
        mock_tvm_rules,
        mock_best2pay,
        partner_id_to_block,
        mysql_user_id,
        set_restricted_response,
        who_blocked,
        reason_to_block,
        block_state,
        order_id,
        expected_history,
        expected_status,
        expected_output_block_state,
        expected_full_block_state,
        expected_response,
):
    @mock_best2pay('/webapi/b2puser/SetAllowedParams')
    async def _mock_set_restricted_params(request):
        return web.Response(
            body=set_restricted_response,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    user_attributes = await get_user_attributes(mysql_user_id, web_context)
    user_block_enum = tips_common.TrancodeUserBlock
    last_state = user_block_enum.NONE
    if user_attributes['b2p_block_mcc']:
        last_state = user_block_enum.OUTPUT
    elif user_attributes['b2p_block_full']:
        last_state = user_block_enum.TOTAL

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/block',
        json={
            'partner_id': partner_id_to_block,
            'reason': reason_to_block,
            'who': who_blocked,
            'block_state': block_state,
            'order_id': order_id,
        },
    )
    if expected_response:
        body = await response.json()
        assert body == expected_response
    assert response.status == expected_status

    user_attributes = await get_user_attributes(mysql_user_id, web_context)
    assert int(user_attributes['b2p_block_mcc']) == expected_output_block_state
    assert int(user_attributes['b2p_block_full']) == expected_full_block_state

    if not expected_history:
        return

    async with web_context.pg.master_pool.acquire() as conn:
        withdrawal_row = await conn.fetchrow(
            'select partner_id, block_state, reason, who, last_block_state, '
            'link_order_id from eats_tips_partners.users_block_history',
        )
        assert withdrawal_row['partner_id'] == uuid.UUID(partner_id_to_block)
        assert withdrawal_row['link_order_id'] == order_id
        assert withdrawal_row['reason'] == reason_to_block
        assert withdrawal_row['who'] == who_blocked
        assert withdrawal_row['block_state'] == block_state
        assert withdrawal_row['last_block_state'] == last_state.value


async def get_user_attributes(mysql_user_id: str, web_context):
    async with web_context.mysql.chaevieprosto.get_mysql_cursor() as cursor:
        await cursor.execute(
            'select b2p_block_mcc, b2p_block_full '
            'from modx_web_user_attributes'
            f' where internalKey="{mysql_user_id}";',
        )
        user_attributes = await cursor.fetchone()
    return user_attributes
