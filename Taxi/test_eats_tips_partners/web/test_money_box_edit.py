import uuid

import pytest


@pytest.mark.parametrize(
    ('box_id', 'request_body', 'expected_status'),
    (
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            {
                'fallback_partner_id': '00000000-0000-0000-0000-000000000002',
                'display_name': 'копилочка 2',
                'avatar': '42',
                'caption': 'какая-то подпись',
            },
            200,
            id='normal',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            {
                'fallback_partner_id': '10000000-0000-0000-0000-000000000777',
                'display_name': 'копилочка 1',
            },
            400,
            id='partner-not-found',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            {
                'fallback_partner_id': '00000000-0000-0000-0000-000000000004',
                'display_name': 'копилочка 1',
            },
            400,
            id='partner-not-belong-place',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            {
                'fallback_partner_id': '00000000-0000-0000-0000-000000000003',
                'display_name': 'копилочка 1',
            },
            400,
            id='partner-not-confirmed',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000777',
            {'display_name': 'копилочка 1'},
            404,
            id='box-not-found',
        ),
        pytest.param(
            'bad', {'display_name': 'копилочка 1'}, 400, id='bad-box',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000200',
            {'fallback_partner_id': 'bad', 'display_name': 'копилочка 1'},
            400,
            id='bad-partner',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg_money_box.sql'])
async def test_money_box_edit(
        taxi_eats_tips_partners_web,
        web_context,
        box_id,
        request_body,
        expected_status,
):
    response = await taxi_eats_tips_partners_web.put(
        '/v1/money-box', params={'id': box_id}, json=request_body,
    )
    assert response.status == expected_status
    if expected_status == 200:
        async with web_context.pg.replica_pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT fallback_partner_id, display_name, avatar, caption
                FROM eats_tips_partners.money_box
                WHERE id = {box_id!r}
                """,
            )
        assert dict(row) == {
            'fallback_partner_id': (
                uuid.UUID(request_body['fallback_partner_id'])
                if request_body.get('fallback_partner_id')
                else None
            ),
            'display_name': request_body['display_name'],
            'avatar': request_body.get('avatar'),
            'caption': request_body.get('caption'),
        }
