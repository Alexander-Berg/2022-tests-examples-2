import http

from aiohttp import web
import pytest

from test_eats_tips_partners import conftest


USER_INFO_ANSWER = """<b2p_user>
    <reg_date>2022.04.29 14:18:53</reg_date>
    <sector>3879</sector>
    <client_ref>43464</client_ref>
    <state>0</state>
    <auth_state>0</auth_state>
    <active>0</active>
    <card_usage>
        <allowed_params/>
        <restricted_params/>
    </card_usage>
    <pan>478390******4291</pan>
    <expdate>11/2026</expdate>
    <limit>0</limit>
    <available_balance>1000</available_balance>
    <currency>643</currency>
    <status>OPEN</status>
    <card_limits>
        <limit>
            <limit_id>1044</limit_id>
            <current>0</current>
            <max>40000</max>
        </limit>
    </card_limits>
    <signature>ZmRjNjYwNTkxYzc4MzkxN2ZmYjUxY2Y3MWY2NjIwNTU=</signature>
</b2p_user>"""


@pytest.mark.parametrize(
    ('alias', 'jwt', 'expected_code', 'expected_response', 'user_info_answer'),
    (
        pytest.param(
            '0000100',
            conftest.JWT_USER_11,
            http.HTTPStatus.FORBIDDEN,
            {
                'code': 'not_allowed',
                'message': 'Method not allowed for this user group',
            },
            USER_INFO_ANSWER,
            id='no_access',
        ),
        pytest.param(
            '0000990',
            conftest.JWT_USER_27,
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'Partner not found'},
            USER_INFO_ANSWER,
            id='no_partner',
        ),
        pytest.param(
            '0000100',
            conftest.JWT_USER_27,
            http.HTTPStatus.BAD_REQUEST,
            {'code': '109', 'message': 'Ошибка: неверная цифровая подпись.'},
            conftest.SOME_B2P_ERROR_RESPONSE,
            id='b2p_info_error',
        ),
        pytest.param(
            '0000100',
            conftest.JWT_USER_27,
            http.HTTPStatus.OK,
            {},
            USER_INFO_ANSWER,
            id='success',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
@pytest.mark.mysql('chaevieprosto', files=['chaevie.sql'])
async def test_support_recreate_card(
        taxi_eats_tips_partners_web,
        mockserver,
        web_context,
        mock_best2pay,
        mock_tvm_rules,
        alias,
        jwt,
        expected_code,
        expected_response,
        user_info_answer,
):
    @mock_best2pay('/webapi/b2puser/Info')
    async def _mock_user_info(request):
        return web.Response(
            body=user_info_answer,
            headers={'content-type': 'application/xml'},
            status=200,
        )

    response = await taxi_eats_tips_partners_web.get(
        '/v1/support/card/recreate',
        params={'alias': alias},
        headers={'X-Chaevie-Token': jwt},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if expected_code == 200:
        async with web_context.mysql.chaevieprosto.get_mysql_cursor() as conn:
            await conn.execute(
                'select best2pay, best2pay_phone, best2pay_card_token, '
                'best2pay_card_pan, best2pay_card_exp '
                'from modx_web_user_attributes'
                f' where internalKey="10";',
            )
            user_attributes = await conn.fetchone()
            assert user_attributes['best2pay'] == '478390******4291'
            assert user_attributes['best2pay_phone'] == 0
            assert user_attributes['best2pay_card_token'] == ''
            assert user_attributes['best2pay_card_pan'] == ''
            assert user_attributes['best2pay_card_exp'] == ''
