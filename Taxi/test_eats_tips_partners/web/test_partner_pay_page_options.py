import http

import pytest


def _format_options(*, pay_page_name='Таката', pay_page_caption=None):
    request = {'pay_page_name': pay_page_name}
    if pay_page_caption:
        request['pay_page_caption'] = pay_page_caption
    return request


@pytest.mark.parametrize(
    ('params', 'partner_id', 'expected_code'),
    (
        pytest.param(
            _format_options(),
            '00000000-0000-0000-0000-000000000010',
            http.HTTPStatus.OK,
            id='ok',
        ),
        pytest.param(
            _format_options(),
            '00000000-0000-0000-1111-000000000000',
            http.HTTPStatus.NOT_FOUND,
            id='error',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_partner_set_displayed_params(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        web_context,
        mockserver,
        params,
        partner_id,
        expected_code,
):

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/pay-page-options',
        json=params,
        headers={'X-Tips-Partner-Id': partner_id},
    )
    assert response.status == expected_code
    if response.status == http.HTTPStatus.OK:
        await _check_pg(web_context, params, partner_id)


async def _check_pg(web_context, params, partner_id):
    async with web_context.pg.replica_pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            select pay_page_name, pay_page_caption
            from eats_tips_partners.partner
            where id = '{partner_id}';
            """,
        )
        assert dict(row) == {
            'pay_page_name': params.get('pay_page_name'),
            'pay_page_caption': params.get('pay_page_caption'),
        }
