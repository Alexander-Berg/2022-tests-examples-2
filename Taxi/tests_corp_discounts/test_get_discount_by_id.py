import pytest


@pytest.mark.parametrize(
    ['discount_id', 'expected_status'],
    [pytest.param(1, 200), pytest.param(777, 404)],
)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_get_discounts(
        taxi_corp_discounts, discount_id, expected_status, load_json,
):
    expected_discounts = load_json('expected_discounts.json')
    response = await taxi_corp_discounts.get(
        f'/v1/admin/discounts/get?discount_id={discount_id}',
    )
    assert response.status == expected_status

    if expected_status == 200:
        expected_response = expected_discounts[str(discount_id)]
        res = response.json()
        res.pop('created_at')
        assert expected_response == res
