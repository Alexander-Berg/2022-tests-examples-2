# pylint: disable=too-many-lines
import copy

import pytest

from tests_eats_products import eats_upsell_recommendations as upsell
from tests_eats_products import experiments
from tests_eats_products import utils

HEADERS = {
    'X-AppMetrica-DeviceId': 'device_id',
    'x-platform': 'android_app',
    'x-app-version': '12.11.12',
    'X-Eats-User': 'user_id=456',
}

PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'

SLUG = 'slug'
BRAND_SLUG = 'brand1'

BASE_REQUEST_NO_SLUG_PUBLIC = {'product_public_id': PRODUCT_PUBLIC_ID}

BASE_REQUEST_PUBLIC = {
    'place_slug': SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}

BASE_REQUEST_PLACE_BRAND_PUBLIC = {
    'place_slug': SLUG,
    'brand_slug': BRAND_SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}

BASE_REQUEST_BRAND_PUBLIC = {
    'brand_slug': BRAND_SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}


NON_EXISTENT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69bfff'


@utils.PARAMETRIZE_FALLBACK_PRODUCT_HANDLERS
async def test_menu_product_one_of_handlers_doesnt_contain_product(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        mock_generalized_info_context,
        use_fallback_to_generalized_info_not_found,
):
    """
        Eсли в v1/place/products/info
        или v1/products/info нет запрашиваемого товара,
        и в ручке v1/product/generalized-info нет запрашиваемого товара,
        то ручка вернет 404
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(
        'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert resp.status_code == 404
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_generalized_info_context.handler.times_called == (
        1 if use_fallback_to_generalized_info_not_found else 0
    )


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@pytest.mark.parametrize(
    'base_request',
    [
        BASE_REQUEST_PUBLIC,
        BASE_REQUEST_PLACE_BRAND_PUBLIC,
        BASE_REQUEST_BRAND_PUBLIC,
    ],
)
async def test_menu_product_generalized_info_timeout(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_generalized_info_context,
        add_default_product_mapping,
        base_request,
):
    """
        Если v1/product/generalized-info не отвечает
        мы возвращаем 500
    """
    add_default_product_mapping()
    mock_generalized_info_context.set_timeout_error(True)
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=base_request, headers=HEADERS,
    )
    assert resp.status_code == 500


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@pytest.mark.parametrize(
    'base_request',
    [
        BASE_REQUEST_PUBLIC,
        BASE_REQUEST_PLACE_BRAND_PUBLIC,
        BASE_REQUEST_BRAND_PUBLIC,
    ],
)
async def test_menu_product_generalized_info_network_error(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_generalized_info_context,
        add_default_product_mapping,
        base_request,
):
    """
        Тест проверяет, что если v1/product/generalized-info
        возвращает NetworkError
        мы получаем 500
    """
    add_default_product_mapping()
    mock_generalized_info_context.set_network_error(True)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=base_request, headers=HEADERS,
    )
    assert resp.status_code == 500


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@pytest.mark.parametrize('response_code', [400, 404, 429, 500])
@pytest.mark.parametrize(
    'base_request',
    [
        BASE_REQUEST_PUBLIC,
        BASE_REQUEST_PLACE_BRAND_PUBLIC,
        BASE_REQUEST_BRAND_PUBLIC,
    ],
)
async def test_menu_product_generalized_info_bad_responses(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_generalized_info_context,
        add_default_product_mapping,
        response_code,
        base_request,
):
    """
        Проверяет статус коды ошибок от v1/product/generalized-info
    """
    add_default_product_mapping()
    mock_generalized_info_context.set_status(response_code)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=base_request, headers=HEADERS,
    )
    if response_code == 404:
        assert resp.status_code == 404
    else:
        assert resp.status_code == 500
        assert resp.json() == {
            'code': '500',
            'message': 'Internal Server Error',
        }


@utils.PARAMETRIZE_FALLBACK_PRODUCT_HANDLERS
async def test_menu_product_generalized_no_slug(
        taxi_eats_products, use_fallback_to_generalized_info_not_found,
):
    """
        Проверяет код ошибки, если не задан плейс слаг и бренд слаг
    """
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json=BASE_REQUEST_NO_SLUG_PUBLIC,
        headers=HEADERS,
    )
    assert resp.status_code == 400


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@pytest.mark.parametrize(
    'with_recomendations',
    [
        pytest.param(
            True,
            id='with recomendations',
            marks=experiments.UPSELL_RECOMMENDATIONS_ENABLED,
        ),
        pytest.param(
            False,
            id='without recomendations',
            marks=experiments.UPSELL_RECOMMENDATIONS_DISABLED,
        ),
    ],
)
@pytest.mark.parametrize(
    ['has_id_mapping'],
    [
        pytest.param(True, id='core id in mapping'),
        pytest.param(False, id='core id not in mapping'),
    ],
)
@pytest.mark.parametrize('has_currency_in_db', [False, True])
@pytest.mark.parametrize(['with_categories'], ([True], [False]))
@pytest.mark.parametrize(['v1_products_info_has_product'], ([True], [False]))
async def test_menu_product_fallback_generalized_info(
        taxi_eats_products,
        load_json,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        add_default_product_mapping,
        mock_generalized_info_context,
        v1_products_info_has_product,
        with_categories,
        with_recomendations,
        has_id_mapping,
        sql_set_place_currency,
        has_currency_in_db,
):
    """
        Если только в v1/place/products/info
        или в обоих ручках
        нет запрашиваемого товара,
        мы фоллбечнимся на generalized_info
        и на основе неё отдадим товар.
        Также проверяется, что не используется маппинг в сценарии
        фоллбэка и выставляется дефолтный core_id
    """
    if has_id_mapping:
        add_default_product_mapping()

    request = copy.deepcopy(BASE_REQUEST_PUBLIC)
    request['with_categories'] = with_categories
    if v1_products_info_has_product:
        mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)
    mock_nomenclature_get_parent_context.add_category('1', 'category 1', '2')
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'],
    )
    expected_response = load_json('expected_generalized_info.json')

    if has_currency_in_db:
        sql_set_place_currency(code='BYN', sign='руб.')
        expected_response['place']['currency'] = {
            'code': 'BYN',
            'sign': 'руб.',
        }

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    if with_categories:
        expected_response['categories'] = [{'id': '1', 'name': 'category 1'}]

    assert mock_upsell_recommendations.times_called == (
        1 if with_recomendations else 0
    )
    assert resp.status_code == 200
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert (
        mock_nomenclature_static_info_context.handler.times_called == 0
        if with_categories
        else 1
    )
    assert mock_generalized_info_context.handler.times_called == 1
    assert resp.json()['menu_item']['available'] is False
    assert resp.json() == expected_response


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@pytest.mark.parametrize('has_currency_in_db', [False, True])
@experiments.UPSELL_RECOMMENDATIONS_ENABLED
@pytest.mark.parametrize(['with_categories'], ([True], [False]))
async def test_menu_product_generalized_info_by_brand_slug(
        taxi_eats_products,
        load_json,
        mock_nomenclature_get_parent_context,
        add_default_product_mapping,
        mock_generalized_info_context,
        sql_set_place_currency,
        with_categories,
        has_currency_in_db,
):
    """
        Если пришли только с бренд слагом
        отдаём товар на основе generalized_info
        с available True
    """
    add_default_product_mapping()

    request = copy.deepcopy(BASE_REQUEST_BRAND_PUBLIC)
    request['with_categories'] = with_categories
    mock_nomenclature_get_parent_context.add_category('1', 'category 1', '2')
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID,
        name='item_1',
        price='100.0',
        parent_category_ids=['1'],
    )
    expected_response = load_json('expected_slug_generalized_info.json')
    if has_currency_in_db:
        sql_set_place_currency(code='BYN', sign='руб.')
        expected_response['place']['currency'] = {
            'code': 'BYN',
            'sign': 'руб.',
        }

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )

    if with_categories:
        expected_response['categories'] = [{'id': '1', 'name': 'category 1'}]
    assert resp.status_code == 200

    assert mock_nomenclature_get_parent_context.handler.times_called == (
        1 if with_categories else 0
    )
    assert mock_generalized_info_context.handler.times_called == 1
    assert resp.json()['menu_item']['available'] is True
    assert resp.json() == expected_response


@utils.PARAMETRIZE_FALLBACK_PRODUCT_HANDLERS
async def test_menu_product_place_prior(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        use_fallback_to_generalized_info_not_found,
):
    """
        Если пришли с бренд слагом и плейс слагом
        плейс слаг приоритетнее
    """
    add_default_product_mapping()

    mock_nomenclature_dynamic_info_context.add_product(
        PRODUCT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json=BASE_REQUEST_PLACE_BRAND_PUBLIC,
        headers=HEADERS,
    )

    assert resp.status_code == 200
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
async def test_menu_product_generalized_info_by_brand_unknown_slug(
        taxi_eats_products, add_default_product_mapping,
):
    """
        Если пришёл неизвестный бренд слаг, то отдаёт 404
    """
    add_default_product_mapping()

    request = copy.deepcopy(BASE_REQUEST_BRAND_PUBLIC)
    request['brand_slug'] = SLUG

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=request, headers=HEADERS,
    )
    assert resp.status_code == 404


@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@pytest.mark.parametrize(
    'base_request', [BASE_REQUEST_PUBLIC, BASE_REQUEST_BRAND_PUBLIC],
)
async def test_menu_generalized_info_no_discount_applicator(
        taxi_eats_products,
        load_json,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        mock_generalized_info_context,
        eats_order_stats,
        base_request,
):
    """
        Тест проверяет, что при фоллбэке на v1/products/info
        не применяется discount_applicator
    """
    add_default_product_mapping()
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'],
    )
    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=base_request, headers=HEADERS,
    )
    assert resp.status_code == 200
    assert resp.json()['menu_item']['promoPrice'] is None
    assert resp.json()['menu_item']['promoTypes'] == []


@experiments.UPSELL_RECOMMENDATIONS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_DISCOUNTS_ENABLED
@experiments.DISCOUNTS_APPLICATOR_CASHBACK_ENABLED
@experiments.CASHBACK_DISCOUNTS_ENABLED
@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
    EATS_PRODUCTS_SETTINGS=utils.EATS_PRODUCT_DEFAULT_SETTINGS,
)
async def test_menu_generalized_info_discount(
        taxi_eats_products,
        load_json,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        add_default_product_mapping,
        mock_generalized_info_context,
        eats_order_stats,
        mock_nomenclature_get_parent_context,
        mock_upsell_recommendations,
        mock_v2_match_discounts_context,
):
    """
        Тест проверяет, что при фоллбэке на обобщённую ручку
        при наличии рекомендаций для них скидки проставляются,
        а для самого товара они не применяются.
    """
    add_default_product_mapping()

    mock_upsell_recommendations.add_recommendations(
        upsell.DEFAULT_RECOMMENDATIONS,
    )

    mock_nomenclature_dynamic_info_context.add_product(
        upsell.PUBLIC_IDS[0], price=100, is_available=True, old_price=200,
    )
    mock_nomenclature_static_info_context.add_product(upsell.PUBLIC_IDS[0])

    mock_v2_match_discounts_context.add_discount_product(
        upsell.PUBLIC_IDS[0], 'absolute', 11.0,
    )

    mock_v2_match_discounts_context.add_cashback_product(
        PRODUCT_PUBLIC_ID, 'absolute', 4.0,
    )
    mock_v2_match_discounts_context.add_discount_product(
        PRODUCT_PUBLIC_ID, 'absolute', 3.0,
    )
    mock_v2_match_discounts_context.set_use_tags(True)

    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'],
    )

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST_PUBLIC, headers=HEADERS,
    )
    assert resp.status_code == 200

    assert mock_v2_match_discounts_context.handler.times_called == 1
    assert mock_generalized_info_context.handler.times_called == 1

    menu_item = resp.json()['menu_item']
    assert menu_item['promoPrice'] is None

    items = resp.json()['detailed_data'][4]['payload']['recommendations'][0][
        'items'
    ]
    assert len(items) == 1
    assert items[0]['promoPrice'] == 89
    assert items[0]['promoTypes'][0]['type'] == 'price_discount'


@utils.PARAMETRIZE_FALLBACK_PRODUCT_HANDLERS
@pytest.mark.parametrize(
    'product_id',
    (
        ({'product_public_id': NON_EXISTENT_PUBLIC_ID}),
        ({'product_core_id': '1'}),
    ),
)
async def test_menu_product_product_not_found(
        taxi_eats_products,
        product_id,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_generalized_info_context,
        add_default_product_mapping,
        use_fallback_to_generalized_info_not_found,
):
    """
        Тест проверяет, что получаем 404 при отсутствии товара в
       /eats-nomenclature/v1/place/products/info,
       /eats-nomenclature/v1/products/info и
       /eats-retail-seo/v1/product/generalized-info
    """
    add_default_product_mapping()
    mock_nomenclature_dynamic_info_context.add_product(
        product_id, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json={'place_slug': SLUG, **product_id},
        headers=HEADERS,
    )
    assert resp.status_code == 404
    assert mock_nomenclature_dynamic_info_context.handler.times_called == 1
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert mock_generalized_info_context.handler.times_called == (
        1 if use_fallback_to_generalized_info_not_found else 0
    )


@utils.PARAMETRIZE_FALLBACK_PRODUCT_HANDLERS
@pytest.mark.parametrize('with_categories', [True, False])
async def test_menu_product_no_mapping_public_id_to_core_id(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mock_nomenclature_get_parent_context,
        with_categories,
        use_fallback_to_generalized_info_not_found,
):
    """
    Тест проверяет, что при отсутствии маппинга public_id->origin
    возвращается ошибка 404
    """
    mock_nomenclature_dynamic_info_context.add_product(
        NON_EXISTENT_PUBLIC_ID, price=100, is_available=True, old_price=None,
    )
    mock_nomenclature_static_info_context.add_product(NON_EXISTENT_PUBLIC_ID)

    resp = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT,
        json={
            'place_slug': SLUG,
            'product_public_id': NON_EXISTENT_PUBLIC_ID,
            'with_categories': with_categories,
        },
        headers=HEADERS,
    )

    assert mock_nomenclature_dynamic_info_context.handler.times_called == (
        2 if with_categories else 1
    )
    assert mock_nomenclature_static_info_context.handler.times_called == 1
    assert resp.status_code == 404
    assert resp.json() == {
        'code': 'mapping_not_found',
        'message': 'MappingNotFound',
    }
