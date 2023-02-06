import http

import pytest


def _format_partner_register_request(
        *, first_name='Абоба', last_name='Бабобус', patronymic=None,
):
    request = {'first_name': first_name, 'last_name': last_name}
    if patronymic:
        request['patronymic'] = patronymic
    return request


@pytest.mark.parametrize(
    ('params', 'partner_id', 'expected_code', 'expected_response'),
    (
        pytest.param(
            _format_partner_register_request(),
            '00000000-0000-0000-0000-000003000020',
            http.HTTPStatus.OK,
            {},
            id='ok',
        ),
        pytest.param(
            _format_partner_register_request(patronymic='Дудусович'),
            '00000000-0000-0000-0000-000003000020',
            http.HTTPStatus.OK,
            {},
            id='ok_last_name',
        ),
        pytest.param(
            _format_partner_register_request(),
            '00000000-0000-0000-0000-000003000010',
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'partner already registered'},
            id='already-registered-partner',
        ),
        pytest.param(
            _format_partner_register_request(),
            '00000000-0000-0000-0000-000003000000',
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': 'partner already registered'},
            id='partner-with-null-status',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_partner_register(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        web_context,
        mockserver,
        params,
        partner_id,
        expected_code,
        expected_response,
):

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/register',
        json=params,
        headers={'X-Tips-Partner-Id': partner_id},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if response.status == http.HTTPStatus.OK:
        await _check_pg(web_context, params, partner_id)


async def _check_pg(web_context, params, partner_id):
    async with web_context.pg.replica_pool.acquire() as conn:
        row = await conn.fetchrow(
            f"""
            select first_name, last_name
            from eats_tips_partners.partner
            where alias = '{partner_id[-7:]}';
            """,
        )
        assert dict(row) == {
            'first_name': params['first_name'],
            'last_name': params['last_name'],
        }

        row = await conn.fetchrow(
            f"""
                    select migrated, type
                    from eats_tips_partners.alias
                    where alias = '{partner_id[-7:]}';""",
        )
        assert dict(row) == {'migrated': True, 'type': 'partner'}
