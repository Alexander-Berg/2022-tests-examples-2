import datetime

import pytest

NOW = datetime.datetime(2021, 6, 15, 14, 30, 15, tzinfo=datetime.timezone.utc)


@pytest.mark.parametrize(
    ('box_id', 'expected_status'),
    (
        pytest.param('20000000-0000-0000-0000-000000000200', 404, id='normal'),
        pytest.param(
            '20000000-0000-0000-0000-000000000777', 404, id='not-exists',
        ),
        pytest.param(
            '20000000-0000-0000-0000-000000000202', 404, id='deleted',
        ),
        pytest.param('bad', 404, id='bad-id'),
    ),
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('eats_tips_partners', files=['pg_money_box.sql'])
async def test_money_box_delete(
        taxi_eats_tips_partners_web, web_context, box_id, expected_status,
):
    response = await taxi_eats_tips_partners_web.delete(
        '/v1/money-box', params={'id': box_id},
    )
    assert response.status == expected_status
    if expected_status == 204:
        async with web_context.pg.replica_pool.acquire() as conn:
            val = await conn.fetchval(
                f"""
                SELECT deleted_at
                FROM eats_tips_partners.money_box
                WHERE id = {box_id!r}
                """,
            )
        assert val == NOW
