import pytest


@pytest.mark.config(AFS_IS_ORDER_BLOCKED_BY_ANTIFAKE_ENABLED=True)
@pytest.mark.parametrize(
    'order_id,expected', [('not_existing_value', False), ('some_order', True)],
)
async def test_is_order_blocked_by_antifake_base(
        web_app_client, order_id, expected,
):
    response = await web_app_client.get(
        '/v1/is_order_blocked_by_antifake', params={'order_id': order_id},
    )
    assert response.status == 200

    assert await response.json() == expected
