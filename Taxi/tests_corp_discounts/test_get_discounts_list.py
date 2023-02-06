import pytest


@pytest.mark.parametrize(
    ['limit', 'offset', 'expected_discounts'],
    [
        pytest.param(1, 1, [2], id='1'),
        pytest.param(1, 3, [], id='2'),
        pytest.param(50, 0, [3, 2, 1], id='3'),
    ],
)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_get_discounts(
        taxi_corp_discounts, limit, offset, expected_discounts, load_json,
):
    expected_discounts_json = load_json('expected_discounts.json')

    expected_response = {
        'discounts': [
            expected_discounts_json[str(i)] for i in expected_discounts
        ],
    }

    response = await taxi_corp_discounts.get(
        f'/v1/admin/discounts/list?limit={limit}&offset={offset}',
    )
    assert response.status == 200
    res = response.json()
    for i in res['discounts']:
        i.pop('created_at')

    assert res == expected_response
