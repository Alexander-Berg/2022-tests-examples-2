import uuid

import pytest


@pytest.mark.parametrize(
    ('request_body', 'expected_status', 'alias'),
    (
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'display_name': 'копилочка 1',
            },
            201,
            '3000000',
            id='minimal-create',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'fallback_partner_id': '00000000-0000-0000-0000-000000000004',
                'display_name': 'копилочка 1',
                'avatar': '42',
                'caption': 'какая-то подпись',
            },
            201,
            '3000010',
            id='full-create',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000777',
                'display_name': 'копилочка 1',
            },
            400,
            None,
            id='place-not-found',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'fallback_partner_id': '00000000-0000-0000-0000-000000000707',
                'display_name': 'копилочка 1',
            },
            400,
            None,
            id='partner-not-found',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'fallback_partner_id': '00000000-0000-0000-0000-000000000003',
                'display_name': 'копилочка 1',
            },
            400,
            None,
            id='partner-not-belong-place',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'fallback_partner_id': '00000000-0000-0000-0000-000000000003',
                'display_name': 'копилочка 1',
            },
            400,
            None,
            id='partner-not-confirmed',
        ),
        pytest.param(
            {'place_id': 'bad', 'display_name': 'копилочка 1'},
            400,
            None,
            id='bad-place',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'fallback_partner_id': 'bad',
                'display_name': 'копилочка 1',
            },
            400,
            None,
            id='bad-partner',
        ),
        pytest.param(
            {
                'place_id': '10000000-0000-0000-0000-000000000101',
                'fallback_partner_id': None,
                'display_name': 'копилочка 1',
            },
            201,
            '3000020',
            id='minimal-create-null',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg_money_box.sql'])
async def test_money_box_create(
        taxi_eats_tips_partners_web,
        web_context,
        request_body,
        expected_status,
        alias,
):
    response = await taxi_eats_tips_partners_web.post(
        '/v1/money-box', json=request_body,
    )
    assert response.status == expected_status
    content = await response.json()
    if expected_status == 201:
        async with web_context.pg.replica_pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT place_id, fallback_partner_id, display_name,
                       avatar, caption, alias
                FROM eats_tips_partners.money_box
                WHERE id = {content['box_id']!r}
                """,
            )
        assert dict(row) == {
            'place_id': uuid.UUID(request_body['place_id']),
            'fallback_partner_id': (
                uuid.UUID(request_body['fallback_partner_id'])
                if request_body.get('fallback_partner_id')
                else None
            ),
            'display_name': request_body['display_name'],
            'avatar': request_body.get('avatar'),
            'caption': request_body.get('caption'),
            'alias': alias,
        }
