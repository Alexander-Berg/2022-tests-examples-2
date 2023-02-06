from grocery_mocks import (  # pylint: disable=E0401
    grocery_menu as mock_grocery_menu,
)
import pytest

from . import combo_products_common as common_combo
from . import common
from . import common_search
from . import const
from . import experiments

COMBO_ID = common_combo.COMBO_ID

PRODUCT_GROUP1 = common_combo.PRODUCT_GROUP1
PRODUCT_GROUP2 = common_combo.PRODUCT_GROUP2
PRODUCT_GROUP3 = common_combo.PRODUCT_GROUP3

NOT_FOUND_METAPRODUCT_ID = 'product-not-found-in-depot'
NOT_FOUND_METAPRODUCT = mock_grocery_menu.ComboProduct(
    'not_found_combo',
    [NOT_FOUND_METAPRODUCT_ID],
    [PRODUCT_GROUP1, PRODUCT_GROUP2],
    'combo_revision_2',
)


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
@pytest.mark.parametrize('minimal_stock', ['0', '5'])
async def test_search_single_selection_combo(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        grocery_search,
        now,
        minimal_stock,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision_1',
        ),
    )
    grocery_menu.add_combo_product(NOT_FOUND_METAPRODUCT)

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            ('meta-product-1', '0'),
            (NOT_FOUND_METAPRODUCT_ID, '0'),
            ('product-1', minimal_stock),
            ('product-2', minimal_stock),
            ('product-3', minimal_stock),
        ],
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)
    grocery_search.add_combo(metaproduct_id=NOT_FOUND_METAPRODUCT_ID)

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()

    if minimal_stock == '0':
        assert response_json['products'] == []
        assert 'combos_products' not in response_json
    else:
        assert response_json['combos_products']

        expected = {'product-1', 'product-2', 'product-3'}
        response_product_ids = {
            product['id'] for product in response_json['combos_products']
        }
        assert expected == set(response_product_ids)

        assert [COMBO_ID] == [
            product['id']
            for product in response_json['products']
            if product['type'] == 'good'
        ]
        assert {True} == {
            product['available']
            for product in response_json['products']
            if product['type'] == 'good'
        }


def _check_response_correctnes(response, minimal_stock):
    assert response.status_code == 200
    response_json = response.json()

    assert 'combos_products' not in response_json
    if minimal_stock == '0':
        assert response_json['products'] == []
    else:
        assert [COMBO_ID] == [
            product['id']
            for product in response_json['products']
            if product['type'] == 'good'
        ]
        assert {True} == {
            product['available']
            for product in response_json['products']
            if product['type'] == 'good'
        }


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
@pytest.mark.parametrize('minimal_stock', ['0', '5'])
async def test_search_non_unique_selection_combo(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        grocery_search,
        now,
        minimal_stock,
):
    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'non_unique_selection_combo',
            [COMBO_ID],
            [product_group],
            'combo_revision_1',
        ),
    )
    grocery_menu.add_combo_product(NOT_FOUND_METAPRODUCT)
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[('product-1', '10'), ('product-2', '50')],
        stocks=[
            ('meta-product-1', '0'),
            (NOT_FOUND_METAPRODUCT_ID, '0'),
            ('product-1', minimal_stock),
            ('product-2', minimal_stock),
        ],
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)
    grocery_search.add_combo(metaproduct_id=NOT_FOUND_METAPRODUCT_ID)

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    _check_response_correctnes(response, minimal_stock)


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
@pytest.mark.parametrize('minimal_stock', ['0', '5'])
async def test_search_single_selection_in_group_combo(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        grocery_search,
        now,
        minimal_stock,
):
    product_group_3 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-1', 'product-3'],
    )
    product_group_4 = mock_grocery_menu.ProductGroup(
        True, 1, ['product-2', 'product-4'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_in_group_combo',
            [COMBO_ID],
            [product_group_3, product_group_4],
            'combo_revision_1',
        ),
    )
    grocery_menu.add_combo_product(NOT_FOUND_METAPRODUCT)

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
            ('product-4', '70'),
        ],
        stocks=[
            ('meta-product-1', '0'),
            (NOT_FOUND_METAPRODUCT_ID, '0'),
            ('product-1', minimal_stock),
            ('product-2', minimal_stock),
            ('product-3', minimal_stock),
            ('product-4', minimal_stock),
        ],
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)
    grocery_search.add_combo(metaproduct_id=NOT_FOUND_METAPRODUCT_ID)

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    _check_response_correctnes(response, minimal_stock)


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
async def test_combos_products_not_duplicates(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        grocery_search,
        now,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision_1',
        ),
    )
    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'duplicated_combo',
            ['meta-product-2'],
            [product_group],
            'combo_revision_2',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            ('meta-product-1', '0'),
            ('meta-product-2', '0'),
            ('product-1', '5'),
            ('product-2', '5'),
            ('product-3', '5'),
        ],
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)
    grocery_search.add_combo(metaproduct_id='meta-product-2')

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['combos_products']

    response_product_ids = [
        product['id'] for product in response_json['combos_products']
    ]
    assert len(response_product_ids) == len(set(response_product_ids))


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
async def test_search_different_combos(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        grocery_search,
        now,
):
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision_1',
        ),
    )

    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2', 'product-3'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'non_unique_selection_combo',
            ['meta-product-2'],
            [product_group],
            'combo_revision_2',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            ('meta-product-1', '0'),
            ('meta-product-2', '0'),
            ('product-1', '5'),
            ('product-2', '5'),
            ('product-3', '5'),
        ],
        combos_ids=[COMBO_ID, 'meta-product-2'],
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)
    grocery_search.add_combo(metaproduct_id='meta-product-2')

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert response_json['combos_products']

    expected = {'product-1', 'product-2', 'product-3'}
    assert expected == {
        product['id'] for product in response_json['combos_products']
    }

    assert {COMBO_ID, 'meta-product-2'} == {
        product['id']
        for product in response_json['products']
        if product['type'] == 'good'
    }


MARKET_EATS_AND_LAVKA_ID = common_search.MARKET_EATS_AND_LAVKA_ID


@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.SEARCH_FLOW_MARKET
async def test_search_market_combo(
        taxi_grocery_api,
        overlord_catalog,
        mbi_api,
        grocery_depots,
        grocery_menu,
        grocery_products,
        market_report_proxy,
):
    location = [0, 0]

    metaproduct_id = common_combo.COMBO_ID

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [metaproduct_id],
            [
                common_combo.PRODUCT_GROUP1,
                common_combo.PRODUCT_GROUP2,
                common_combo.PRODUCT_GROUP3,
            ],
            'combo_revision_1',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            (metaproduct_id, '1'),
            ('product-1', '5'),
            ('product-2', '5'),
            ('product-3', '5'),
        ],
    )

    overlord_catalog.add_location(
        location=location,
        depot_id=const.DEPOT_ID,
        legacy_depot_id=MARKET_EATS_AND_LAVKA_ID,
    )

    mbi_api.add_depot(
        common_search.MARKET_SERVICE_ID,
        common_search.MARKET_EATS_AND_LAVKA_ID,
        common_search.MARKET_FEED_ID,
        common_search.MARKET_PARTNER_ID,
        common_search.MARKET_BUSINESS_ID,
    )
    grocery_depots.add_depot(
        depot_id=const.DEPOT_ID,
        depot_test_id=int(MARKET_EATS_AND_LAVKA_ID),
        location=location,
        country_iso3=common_search.MARKET_COUNTRY_ISO3,
        region_id=common_search.MARKET_REGION_ID,
    )

    market_report_proxy.add_product(product_id='product-1')
    market_report_proxy.add_product(product_id=metaproduct_id)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'query-text', 'position': {'location': location}},
        headers={'X-Request-Language': common_search.MARKET_LOCALE},
    )
    assert response.status_code == 200

    response_json = response.json()

    expected = {'product-1', 'product-2', 'product-3'}
    assert expected == {
        product['id'] for product in response_json['combos_products']
    }

    assert {metaproduct_id, 'product-1'} == {
        product['id']
        for product in response_json['products']
        if product['type'] == 'good'
    }


@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.SEARCH_FLOW_SAAS
@pytest.mark.parametrize(
    'quantity,expected_products_ids,expected_combos_products',
    [
        pytest.param('0', ['product-1'], None),
        pytest.param(
            '5',
            ['product-1', 'meta-product-1'],
            {'product-1', 'product-2', 'product-3'},
        ),
    ],
)
async def test_search_saas_combos(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        offers,
        now,
        saas_search_proxy,
        quantity,
        expected_products_ids,
        expected_combos_products,
):
    location = common.DEFAULT_LOCATION
    product_id = 'product-1'
    metaproduct_id = 'meta-product-1'

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [common_combo.COMBO_ID],
            [
                common_combo.PRODUCT_GROUP1,
                common_combo.PRODUCT_GROUP2,
                common_combo.PRODUCT_GROUP3,
            ],
            'combo_revision_1',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            (metaproduct_id, '0'),
            ('product-1', '5'),
            ('product-2', quantity),
            ('product-3', '5'),
        ],
    )

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=location,
    )

    saas_search_proxy.add_product(product_id=product_id)
    saas_search_proxy.add_metaproduct(metaproduct_id=metaproduct_id)

    request_json = {
        'text': 'query-text',
        'position': {'location': location},
        'offer_id': 'test-offer',
    }

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search', json=request_json,
    )

    assert response.status_code == 200
    response_json = response.json()

    assert expected_products_ids == [
        product['id'] for product in response_json['products']
    ]

    if expected_combos_products is not None:
        assert expected_combos_products == {
            product['id'] for product in response_json['combos_products']
        }
    else:
        assert 'combos_products' not in response_json

    assert saas_search_proxy.saas_search_times_called() == 2


@experiments.MODES_ROOT_LAYOUT_ENABLED
@pytest.mark.parametrize('is_combos_enabled', [False, True])
@experiments.SEARCH_FLOW_INTERNAL
async def test_search_enable_combos(
        taxi_grocery_api,
        experiments3,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        grocery_search,
        is_combos_enabled,
):
    experiments3.add_config(
        name='grocery_api_search_enable_combos',
        consumers=['grocery-api/search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': is_combos_enabled},
            },
        ],
    )

    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'single_selection_combo',
            [COMBO_ID],
            [PRODUCT_GROUP1, PRODUCT_GROUP2, PRODUCT_GROUP3],
            'combo_revision_1',
        ),
    )

    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[
            ('product-1', '10'),
            ('product-2', '50'),
            ('product-3', '100'),
        ],
        stocks=[
            (COMBO_ID, '0'),
            ('product-1', '5'),
            ('product-2', '5'),
            ('product-3', '5'),
        ],
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': 'test-offer',
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    response_json = response.json()

    assert is_combos_enabled == ('combos_products' in response_json)
    assert is_combos_enabled == (len(response_json['products']) != 0)


@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.COMBOS_IN_SEARCH_ENABLED
@experiments.create_search_flow_experiment('internal')
@pytest.mark.config(
    GROCERY_API_STICKERS_INFO={
        'selection-combo-sticker': {
            'sticker_color': 'yellow',
            'text_color': 'white',
        },
    },
)
@pytest.mark.translations(
    virtual_catalog={
        'selection-combo-sticker': {'ru': 'selection combo sticker'},
    },
)
async def test_combo_sticker(
        taxi_grocery_api,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        grocery_p13n,
        offers,
        grocery_search,
        now,
):
    product_group = mock_grocery_menu.ProductGroup(
        False, 2, ['product-1', 'product-2'],
    )
    grocery_menu.add_combo_product(
        mock_grocery_menu.ComboProduct(
            'non_unique_selection_combo',
            [COMBO_ID],
            [product_group],
            'combo_revision_1',
        ),
    )
    common_combo.prepare_combo_test_context(
        overlord_catalog,
        grocery_products,
        product_prices=[('product-1', '10'), ('product-2', '50')],
        stocks=[
            ('meta-product-1', '0'),
            ('product-1', '5'),
            ('product-2', '5'),
        ],
    )

    grocery_p13n.add_bundle_v2_modifier(
        value=10, bundle_id='non_unique_selection_combo',
    )

    grocery_search.add_combo(metaproduct_id=COMBO_ID)

    offer_id = 'test-offer'
    offers.add_offer_elementwise(
        offer_id=offer_id,
        offer_time=now,
        depot_id=common.DEFAULT_DEPOT_ID,
        location=common.DEFAULT_LOCATION,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={
            'text': 'product-1',
            'position': {'location': common.DEFAULT_LOCATION},
            'offer_id': offer_id,
        },
        headers={'X-Request-Language': 'ru'},
    )
    assert response.status_code == 200
    stickers = response.json()['products'][0]['stickers']
    assert len(stickers) == 1
    assert stickers[0] == {
        'sticker_color': 'yellow',
        'text': 'selection combo sticker',
        'text_color': 'white',
    }


@experiments.COMBOS_IN_SEARCH_ENABLED
@pytest.mark.parametrize('search_flow', ['internal', 'saas', 'market'])
async def test_combo_search_report(
        taxi_grocery_api,
        add_test_offer,
        overlord_catalog,
        grocery_menu,
        grocery_products,
        prepare_default_combo,
        add_default_depot,
        market_report_proxy,
        saas_search_proxy,
        grocery_search,
        search_flow,
):
    saas_search_proxy.add_metaproduct(metaproduct_id=COMBO_ID)
    grocery_search.add_combo(metaproduct_id=COMBO_ID)
    market_report_proxy.add_product(product_id=COMBO_ID)

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search-report',
        json={
            'text': 'test-query',
            'external_depot_id': const.LEGACY_DEPOT_ID,
            'search_flow': search_flow,
        },
    )

    assert response.status_code == 200
    products = response.json()['products']
    assert len(products) == 1
    assert products[0]['id'] == COMBO_ID
    assert products[0]['title'] == 'product-title'

    assert (
        search_flow != 'internal'
        or grocery_search.internal_search_v2_times_called() == 1
    )
    assert (
        search_flow != 'saas'
        or saas_search_proxy.saas_search_times_called() == 2
    )
    assert search_flow != 'market' or market_report_proxy.times_called == 1
