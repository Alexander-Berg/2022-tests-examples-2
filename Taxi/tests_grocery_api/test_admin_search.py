import pytest

from . import common
from . import const

# Проверяет, что поисковая выдача возвращается с ценами и скидками.
@pytest.mark.config(GROCERY_API_SEARCH_ADMIN_FLOW={'search_flow': 'internal'})
async def test_returns_search_results(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    location = const.LOCATION

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
            {
                'in_stock': '10',
                'product_id': 'product-2',
                'quantity_limit': '0',
            },
        ],
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
    )
    grocery_search.add_product(product_id='product-1')
    grocery_search.add_product(product_id='product-2')
    grocery_search.add_product(product_id='product-not-in-depot')
    grocery_p13n.add_modifier(product_id='product-1', value='0.7')
    grocery_p13n.add_modifier(product_id='product-2', value='0.15')

    response = await taxi_grocery_api.post(
        '/admin/grocery-api/v1/search',
        headers={'Accept-Language': 'ru'},
        json={
            'text': 'query-text-for-product-1',
            'depot_id': legacy_depot_id,
            'user_location': location,
            'user_offer_id': 'test-offer',
            'user_auth_context_specific_params': {},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 1
    response_product = response_json['products'][0]
    assert response_product['id'] == 'product-1'
    assert response_product['title'] == 'product-1-title'
    assert response_product['discount_pricing'] == {
        'price': '1',
        'price_template': '1 $SIGN$$CURRENCY$',
    }


# Проверяет, что пробрасывается пользовательский контекст авторизации для
# скидок.
@pytest.mark.config(GROCERY_API_SEARCH_ADMIN_FLOW={'search_flow': 'internal'})
async def test_keeps_user_auth_context(
        taxi_grocery_api,
        overlord_catalog,
        grocery_search,
        load_json,
        mockserver,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    location = const.LOCATION
    yandex_uid = '34b881ab54764918b27cc79eb93bbd9b'
    app_info = (
        'app_brand=yataxi,app_ver3=0,device_make=xiaomi,'
        'app_name=mobileweb_android,app_build=release,'
        'device_model=redmi 6,app_ver2=9,app_ver1=4,platform_ver1=9'
    )
    locale = 'ru'
    personal_phone_id = 'd3cc36a326ab40099747f33712cd6c0a'
    eats_user_id = '177010956'
    appmetrica_device_id = '13b505c1eabece24bda8dd9003c3638e'
    phone_id = '60312429f6e5259a728c8495'
    geo_id = '3'
    session = 'taxi:34b881ab54764918b27cc79eb93bbd9b'
    bound_sessions = 'taxi:zce2e3135aaa4b2f9c710edaee8656d1'

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
    )
    grocery_search.add_product(product_id='product-1')

    @mockserver.json_handler(
        '/grocery-p13n/internal/v1/p13n/v1/discount-modifiers',
    )
    def _discount_modifiers(request):
        assert request.headers.get('X-Request-Application') == app_info
        assert request.headers.get('X-Request-Language') == locale
        assert request.headers.get('X-YaTaxi-User') == (
            f'personal_phone_id={personal_phone_id},'
            f'eats_user_id={eats_user_id}'
        )
        assert (
            request.headers.get('X-AppMetrica-DeviceId')
            == appmetrica_device_id
        )
        assert request.headers.get('X-YaTaxi-PhoneId') == phone_id
        assert request.headers.get('X-Yandex-UID') == yandex_uid
        assert request.headers.get('X-YaTaxi-GeoID') == geo_id
        assert request.headers.get('X-YaTaxi-Session') == session
        assert request.headers.get('X-YaTaxi-Bound-Sessions') == bound_sessions
        assert request.headers.get('X-YaTaxi-Pass-Flags') == 'ya-plus'
        return {'modifiers': []}

    response = await taxi_grocery_api.post(
        '/admin/grocery-api/v1/search',
        headers={'Accept-Language': 'ru'},
        json={
            'text': 'query-text-for-product-1',
            'depot_id': legacy_depot_id,
            'user_location': location,
            'user_offer_id': 'test-offer',
            'user_auth_context_specific_params': {
                'app_info': app_info,
                'personal_phone_id': personal_phone_id,
                'locale': locale,
                'eats_user_id': eats_user_id,
                'appmetrica_device_id': appmetrica_device_id,
                'phone_id': phone_id,
                'yandex_uid': yandex_uid,
                'geo_id': geo_id,
                'session': session,
                'bound_sessions': bound_sessions,
                'has_ya_plus': True,
            },
        },
    )
    assert response.status_code == 200
    assert _discount_modifiers.times_called > 0


WMS_ITEMS = {'product-1_title': {'ru': 'Йогурт', 'en': 'Yogurt'}}

# Проверяет, что выдача локализуется.
@pytest.mark.config(GROCERY_API_SEARCH_ADMIN_FLOW={'search_flow': 'internal'})
@pytest.mark.parametrize('locale', ['ru', 'en'])
@pytest.mark.translations(wms_items=WMS_ITEMS)
async def test_localizes_search_results(
        taxi_grocery_api,
        overlord_catalog,
        grocery_p13n,
        grocery_search,
        load_json,
        locale,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    location = const.LOCATION

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
    )
    grocery_search.add_product(product_id='product-1')

    response = await taxi_grocery_api.post(
        '/admin/grocery-api/v1/search',
        headers={'Accept-Language': locale},
        json={
            'text': 'query-text-for-product-1',
            'depot_id': legacy_depot_id,
            'user_location': location,
            'user_offer_id': 'test-offer',
            'user_auth_context_specific_params': {},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 1
    response_product = response_json['products'][0]
    assert response_product['id'] == 'product-1'
    assert response_product['title'] == WMS_ITEMS['product-1_title'][locale]


# Проверяет, что в поисковой выдаче возвращается НДС.
@pytest.mark.config(GROCERY_API_SEARCH_ADMIN_FLOW={'search_flow': 'internal'})
async def test_returns_vat(
        taxi_grocery_api, overlord_catalog, grocery_search, load_json,
):
    depot_id = const.DEPOT_ID
    legacy_depot_id = const.LEGACY_DEPOT_ID
    location = const.LOCATION
    vat = '5.0'

    common.prepare_overlord_catalog_json(
        load_json,
        overlord_catalog,
        location,
        products_data=[
            {
                'description': 'product-1-description',
                'image_url_template': 'product-1-image-url-template',
                'long_title': 'product-1-long-title',
                'product_id': 'product-1',
                'title': 'product-1-title',
                'vat': vat,
            },
        ],
        product_stocks=[
            {
                'in_stock': '10',
                'product_id': 'product-1',
                'quantity_limit': '5',
            },
        ],
        depot_id=depot_id,
        legacy_depot_id=legacy_depot_id,
    )
    grocery_search.add_product(product_id='product-1')

    response = await taxi_grocery_api.post(
        '/admin/grocery-api/v1/search',
        headers={'Accept-Language': 'ru'},
        json={
            'text': 'query-text-for-product-1',
            'depot_id': legacy_depot_id,
            'user_location': location,
            'user_offer_id': 'test-offer',
            'user_auth_context_specific_params': {},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json['products']) == 1
    response_product = response_json['products'][0]
    assert response_product['id'] == 'product-1'
    assert response_product['vat'] == vat
