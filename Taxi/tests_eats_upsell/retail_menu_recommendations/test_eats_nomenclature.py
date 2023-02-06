import eats_adverts_goods  # pylint: disable=import-error
import pytest

from tests_eats_upsell import eats_catalog_storage
from tests_eats_upsell import eats_products
from tests_eats_upsell import experiments
from . import types


@experiments.promo_settings(positions=[0, 1])
@experiments.create_promotion('testsuite')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion='testsuite',
            products=[
                eats_adverts_goods.types.Product(product_id='6', core_id=6),
                eats_adverts_goods.types.Product(product_id='7', core_id=7),
            ],
        ),
    ],
)
@pytest.mark.experiments3(
    name='eats_upsell_products_aviability',
    consumers=['eats-upsell/retail/v1/menu/recommendations'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.parametrize(
    'products_ids, umlaas_items_ids, info, expected',
    [
        pytest.param(
            ['6', '7', '8', '9'],
            ['8', '9'],
            {
                'products': [
                    {
                        'id': '6',
                        'parent_category_ids': [],
                        'is_available': True,
                        'price': 1.99,
                    },
                    {
                        'id': '7',
                        'parent_category_ids': [],
                        'is_available': False,
                        'price': 1.99,
                    },
                    {
                        'id': '8',
                        'parent_category_ids': [],
                        'is_available': True,
                        'price': 1.99,
                        'in_stock': 1,
                    },
                    {
                        'id': '9',
                        'parent_category_ids': [],
                        'is_available': False,
                        'price': 3.99,
                        'in_stock': 0,
                    },
                ],
            },
            ['6', '8'],
            id='umlaas response',
        ),
    ],
)
async def test_upsell_products_aviability_ok(
        mockserver,
        retail_recommendations,
        umlaas_eats_retail_suggest,
        eats_catalog_storage_service,
        products_menu_items,
        umlaas_items_ids,
        products_ids,
        info,
        expected,
):
    """
    Проверяет корректную работу запроса в eats-nomenclature,
    если все сервисы работают
    """

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def products_info(request):
        data = request.json
        assert len(data['product_ids']) == len(products_ids)
        for product_id in data['product_ids']:
            assert data['product_ids'].count(product_id) == products_ids.count(
                product_id,
            )
        return info

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id, place=eats_catalog_storage.Place(slug=place_slug),
    )
    eats_catalog_storage_service.add_place(place)

    umlaas_eats_retail_suggest.set_status_code(200)
    umlaas_eats_retail_suggest.set_recommendations(umlaas_items_ids)

    products_items_ids = [1, 2, 3, 4, 5]
    for id_product in products_items_ids:
        products_menu_items.add_item(
            eats_products.RetailItem(core_item_id=id_product),
        )

    item = types.RequestItem(public_id='42')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )

    assert response.status_code == 200

    assert products_info.times_called == 1

    response_data = response.json()
    assert len(response_data['recommendations']) == len(expected)

    for item in response_data['recommendations']:
        assert item['public_id'] in expected


@experiments.promo_settings(positions=[0, 1])
@pytest.mark.experiments3(
    name='eats_upsell_products_aviability',
    consumers=['eats-upsell/retail/v1/menu/recommendations'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@experiments.create_promotion('testsuite')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion='testsuite',
            products=[
                eats_adverts_goods.types.Product(product_id='6', core_id=6),
                eats_adverts_goods.types.Product(product_id='7', core_id=7),
            ],
        ),
    ],
)
async def test_nomenclature_not_responding(
        mockserver,
        retail_recommendations,
        eats_catalog_storage_service,
        umlaas_eats_retail_suggest,
):
    """
    Проверяет, что если eats-nomenclature ответил с ошибкой,
    в ответе eats-upsell будут все товары
    """

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def products_info(request):
        return mockserver.make_response('no items info', status=500)

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id, place=eats_catalog_storage.Place(slug=place_slug),
    )
    eats_catalog_storage_service.add_place(place)

    umlaas_eats_retail_suggest.set_status_code(200)
    umlaas_eats_retail_suggest.set_recommendations(['1', '2', '3'])

    item = types.RequestItem(public_id='42')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )

    assert response.status_code == 200

    assert products_info.times_called == 1

    expected = ['1', '2', '3', '6', '7']

    response_data = response.json()
    assert len(response_data['recommendations']) == len(expected)

    for item in response_data['recommendations']:
        assert item['public_id'] in expected


@experiments.promo_settings(positions=[0, 1])
@experiments.create_promotion('testsuite')
@pytest.mark.eats_adverts_goods_cache(
    product_tables=[
        eats_adverts_goods.types.ProductsTable(
            promotion='testsuite',
            products=[
                eats_adverts_goods.types.Product(product_id='6', core_id=6),
                eats_adverts_goods.types.Product(product_id='7', core_id=7),
            ],
        ),
    ],
)
@pytest.mark.experiments3(
    name='eats_upsell_products_aviability',
    consumers=['eats-upsell/retail/v1/menu/recommendations'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
async def test_upsell_products_aviability_duplicating(
        mockserver,
        retail_recommendations,
        umlaas_eats_retail_suggest,
        eats_catalog_storage_service,
        products_menu_items,
):
    """
    Проверяет, что в eats-nomenclature не приходят дубликаты товаров
    """

    products_ids = ['6', '7']

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def products_info(request):
        data = request.json
        assert len(data['product_ids']) == len(products_ids)
        for product_id in data['product_ids']:
            assert data['product_ids'].count(product_id) == products_ids.count(
                product_id,
            )

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id, place=eats_catalog_storage.Place(slug=place_slug),
    )
    eats_catalog_storage_service.add_place(place)

    umlaas_eats_retail_suggest.set_status_code(200)
    umlaas_eats_retail_suggest.set_recommendations(['6', '7'])

    item = types.RequestItem(public_id='42')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )

    assert response.status_code == 200
    assert products_info.times_called == 1


@pytest.mark.config(
    EATS_UPSELL_NOMENCLATURE_REQUEST_SETTINGS={
        'max_requests': 3,
        'max_items_per_request': 2,
    },
)
@pytest.mark.experiments3(
    name='eats_upsell_products_aviability',
    consumers=['eats-upsell/retail/v1/menu/recommendations'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
async def test_upsell_products_aviability_concurrency(
        mockserver,
        retail_recommendations,
        umlaas_eats_retail_suggest,
        eats_catalog_storage_service,
        testpoint,
):
    """
    Проверяет параллельные запросы на корректность
    """

    products_ids = ['1', '2', '3', '4', '5', '6']
    nomenclature_response = {
        'products': [
            {
                'id': '1',
                'parent_category_ids': [],
                'is_available': True,
                'price': 44.99,
            },
            {
                'id': '2',
                'parent_category_ids': [],
                'is_available': False,
                'price': 44.99,
            },
            {
                'id': '3',
                'parent_category_ids': [],
                'is_available': True,
                'price': 44.99,
            },
            {
                'id': '4',
                'parent_category_ids': [],
                'is_available': False,
                'price': 44.99,
                'in_stock': 0,
            },
            {
                'id': '5',
                'parent_category_ids': [],
                'is_available': True,
                'price': 44.99,
                'in_stock': 0,
            },
        ],
    }

    @testpoint('field_place_id')
    async def check_place_id_type(arg):
        assert arg == '1'

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def products_info(request):
        return nomenclature_response

    place_id: int = 1
    place_slug: str = f'place_{place_id}'
    place = eats_catalog_storage.StoragePlace(
        place_id=place_id, place=eats_catalog_storage.Place(slug=place_slug),
    )
    eats_catalog_storage_service.add_place(place)

    umlaas_eats_retail_suggest.set_status_code(200)
    umlaas_eats_retail_suggest.set_recommendations(products_ids)

    item = types.RequestItem(public_id='42')
    response = await retail_recommendations.send_request(
        item=item, place_slug=place_slug,
    )

    assert response.status_code == 200
    assert products_info.times_called == 3

    expected = ['1', '3', '5']

    response_data = response.json()
    assert len(response_data['recommendations']) == len(expected)

    for item in response_data['recommendations']:
        assert item['public_id'] in expected

    assert check_place_id_type.times_called == 3
