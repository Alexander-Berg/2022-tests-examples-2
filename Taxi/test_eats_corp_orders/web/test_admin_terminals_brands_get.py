import pytest


@pytest.mark.pgsql('eats_corp_orders', files=['pg_eats_corp_orders.sql'])
@pytest.mark.parametrize(
    ('params', 'expected_status', 'expected_json'),
    [
        (
            {'limit': 10, 'offset': 0},
            200,
            {
                'brands': [{'brand_id': '777', 'brand_name': 'brand 777'}],
                'has_more': False,
            },
        ),
        ({'limit': 10, 'offset': 10}, 200, {'brands': [], 'has_more': False}),
    ],
)
async def test_admin_terminals_brands_get(
        taxi_eats_corp_orders_web, params, expected_status, expected_json,
):
    response = await taxi_eats_corp_orders_web.get(
        '/v1/admin/terminals/brands', params=params,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_json
