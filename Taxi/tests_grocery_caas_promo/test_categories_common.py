import pytest

from tests_grocery_caas_promo import common


HANDLERS = pytest.mark.parametrize(
    'handler',
    [
        '/internal/v1/caas-promo/v1/category/cashback',
        '/internal/v1/caas-promo/v1/category/discounts',
    ],
)


@HANDLERS
async def test_ya_plus_flag(
        taxi_grocery_caas_promo,
        overlord_catalog,
        grocery_products,
        mockserver,
        handler,
):
    @mockserver.json_handler('/grocery-discounts/v4/fetch-discounted-products')
    def _mock_grocery_discounts(request):
        assert request.json['has_yaplus']
        return mockserver.make_response(json={'items': []}, status=200)

    overlord_catalog.add_category_tree(
        depot_id=common.DEPOT['depot_id'], category_tree=common.build_tree([]),
    )
    grocery_products.add_layout(test_id='1')
    response = await taxi_grocery_caas_promo.post(
        handler,
        json=common.DISCOUNT_REQUEST,
        headers={'X-YaTaxi-Pass-Flags': 'ya-plus'},
    )

    assert response.status == 200
    assert _mock_grocery_discounts.times_called == 1
