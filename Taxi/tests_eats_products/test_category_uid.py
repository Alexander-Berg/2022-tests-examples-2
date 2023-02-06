import pytest

from tests_eats_products import utils


NOMENCLATURE_RESPONSE = {
    'categories': [
        {
            'available': True,
            'id': 'category_id_2',
            'images': [],
            'items': [],
            'name': 'Молочные продукты',
            'public_id': 102,
            'sort_order': 4,
        },
    ],
}

FILTERED_RESPONSE = {
    'categories': [
        {
            'id': '1',
            'child_ids': [],
            'name': 'Молочные продукты',
            'sort_order': 4,
            'type': 'partner',
            'images': [],
            'filters': [],
            'products': [],
        },
    ],
}


@pytest.mark.parametrize(
    ('input_id', 'input_uid', 'output_category'),
    [
        pytest.param(None, None, None),
        pytest.param(1, '1', '1'),
        pytest.param(1, None, '1'),
        pytest.param(None, '1', '1'),
        pytest.param(2, '1', '1'),
    ],
)
async def test_menu_goods_category_id(
        taxi_eats_products, mockserver, input_id, input_uid, output_category,
):
    """
    Проверяем, что правильный id категории прокидывается в номенклатуру.
    Если заданы оба category и category_uid, то прокидывает category_uid
    """

    request_params = {
        'slug': 'slug',
        'category': input_id,
        'category_uid': input_uid,
    }

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        if output_category:
            assert request.query['category_id'] == output_category
        else:
            assert 'category_id' not in request.query

        return NOMENCLATURE_RESPONSE

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request_params,
    )

    assert _mock_eats_nomenclature.has_calls
    assert response.status_code == 200


@pytest.mark.config(
    EATS_PRODUCTS_NOMENCLATURE_REQUEST_SETTINGS=(
        {'menu_goods_category_products_version': 'v2'}
    ),
)
@pytest.mark.parametrize(
    ('input_id', 'input_uid', 'output_category'),
    [
        pytest.param(1, '1', '1'),
        pytest.param(1, None, '1'),
        pytest.param(None, '1', '1'),
        pytest.param(2, '1', '1'),
    ],
)
async def test_menu_goods_category_id_filtered(
        taxi_eats_products, mockserver, input_id, input_uid, output_category,
):
    """
    Проверяем, что правильный id категории прокидывается в номенклатуру.
    В ручку place/category_products/filtered.
    Если заданы оба category и category_uid, то прокидывает category_uid
    """

    request_params = {
        'slug': 'slug',
        'category': input_id,
        'category_uid': input_uid,
    }

    @mockserver.json_handler(
        utils.Handlers.NOMENCLATURE_CATEGORY_PRODUCTS_FILTERED,
    )
    def _mock_eats_nomenclature_filtered(request):
        assert request.query['category_id'] == output_category
        return FILTERED_RESPONSE

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=request_params,
    )

    assert _mock_eats_nomenclature_filtered.has_calls
    assert response.status_code == 200
