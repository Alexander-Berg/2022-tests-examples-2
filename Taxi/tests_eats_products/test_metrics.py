import copy

from tests_eats_products import utils


PRODUCTS_BASE_REQUEST = {'shippingType': 'pickup', 'slug': 'slug'}


async def test_all_mappings_exist(
        taxi_eats_products,
        mockserver,
        load_json,
        taxi_eats_products_monitor,
        add_default_product_mapping,
):
    # Тест проверяет, что метрики mapping_errors не увеличиваются,
    # если есть маппинг для всех товаров.
    add_default_product_mapping()
    metrics_json = await taxi_eats_products_monitor.get_metric(
        'mapping_errors',
    )

    old_products_metric = metrics_json['products_mapping_errors']

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 2

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature-all-mappings-exist.json')

    await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    metrics_json = await taxi_eats_products_monitor.get_metric(
        'mapping_errors',
    )

    assert metrics_json['products_mapping_errors'] - old_products_metric == 0


async def test_no_mapping(
        taxi_eats_products, mockserver, load_json, taxi_eats_products_monitor,
):
    # Тест проверяет, что метрика products_mapping_errors
    # увеличивается на число товаров, для которых нет маппинга.
    metrics_json = await taxi_eats_products_monitor.get_metric(
        'mapping_errors',
    )

    old_products_metric = metrics_json['products_mapping_errors']

    products_request = copy.deepcopy(PRODUCTS_BASE_REQUEST)
    products_request['category'] = 2

    @mockserver.json_handler(utils.Handlers.NOMENCLATURE)
    def _mock_eats_nomenclature(request):
        return load_json('nomenclature-no-mapping.json')

    await taxi_eats_products.post(
        utils.Handlers.MENU_GOODS, json=products_request,
    )
    metrics_json = await taxi_eats_products_monitor.get_metric(
        'mapping_errors',
    )

    assert metrics_json['products_mapping_errors'] - old_products_metric == 3
