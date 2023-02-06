import pytest

from tests_eats_products import experiments
from tests_eats_products import utils


PRODUCT_PUBLIC_ID = 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001'
BASE_REQUEST = {
    'place_slug': utils.PLACE_SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}
BRAND_REQUEST = {
    'brand_slug': utils.BRAND_SLUG,
    'product_public_id': PRODUCT_PUBLIC_ID,
}
INFORMERS_BLOCK = 'informers'


@experiments.communications(product_card_informers_enabled=True)
@experiments.DETAILED_DATA_DESCRIPTIONS_ENABLED
@pytest.mark.parametrize(
    'name_and_about_product_widgets_enabled',
    [
        pytest.param(True, marks=experiments.product_card_widgets(True)),
        pytest.param(False, marks=experiments.product_card_widgets(False)),
    ],
)
async def test_menu_product_informers(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        add_default_product_mapping,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        name_and_about_product_widgets_enabled,
):
    """
    Если в конфиге включено получение информеров в карточке товара,
    то ответе будут информеры после галлереи из eats-communications
    """
    sql_add_brand()
    sql_add_place()
    add_default_product_mapping()

    informers = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert request.json['types'] == ['informers']
        assert request.json['screen'] == 'product_card'
        assert request.json['place_id'] == str(utils.PLACE_ID)
        assert request.json['brand_id'] == str(utils.BRAND_ID)
        return {'payload': {'stories': [], 'informers': informers}}

    mock_nomenclature_dynamic_info_context.add_product(PRODUCT_PUBLIC_ID)
    mock_nomenclature_static_info_context.add_product(
        PRODUCT_PUBLIC_ID, description_general='some description',
    )

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST,
    )
    assert response.status_code == 200
    assert mock_eats_communications.times_called == 1

    detailed_data = response.json()['detailed_data']

    if name_and_about_product_widgets_enabled:
        expected_order = [
            'gallery',
            'product_name',
            'product_details',
            INFORMERS_BLOCK,
        ]
        informers_data = detailed_data[3]
    else:
        expected_order = ['gallery', INFORMERS_BLOCK, 'header', 'description']
        informers_data = detailed_data[1]

    assert [data['type'] for data in detailed_data] == expected_order
    assert informers_data['payload'] == {'informers': informers}


@pytest.mark.parametrize(
    'status_code', [400, 429, 500, 'timeout', 'network_error', 'bad_format'],
)
@experiments.communications(product_card_informers_enabled=True)
async def test_menu_product_informers_bad_response(
        taxi_eats_products,
        mockserver,
        sql_add_brand,
        sql_add_place,
        add_default_product_mapping,
        status_code,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
):
    """
    Если в конфиге включено получение информеров в карточке товара,
    но eats-communications вернуло какой-то плохой ответ, то ручка вернет 200
    без коммуникаций
    """
    sql_add_brand()
    sql_add_place()
    add_default_product_mapping()

    mock_nomenclature_dynamic_info_context.add_product(PRODUCT_PUBLIC_ID)
    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_screen_communications(request):
        if status_code == 'timeout':
            raise mockserver.TimeoutError()
        if status_code == 'network_error':
            raise mockserver.NetworkError()
        elif status_code == 'bad_format':
            return {'payload': {'bad_format': 'bad_format'}}
        return mockserver.make_response(status=status_code)

    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=BASE_REQUEST,
    )
    assert response.status_code == 200
    assert mock_screen_communications.times_called == 1
    assert INFORMERS_BLOCK not in {
        data['type'] for data in response.json()['detailed_data']
    }


@pytest.mark.config(
    EATS_PRODUCTS_PRODUCT_HANDLER_SETTINGS={
        'use_fallback_to_generalized_info_product_not_found': True,
    },
)
@experiments.communications(product_card_informers_enabled=True)
@pytest.mark.parametrize('product_request', [BASE_REQUEST, BRAND_REQUEST])
async def test_menu_product_informers_fallback_generalized_info(
        taxi_eats_products,
        mock_nomenclature_dynamic_info_context,
        mock_nomenclature_static_info_context,
        mockserver,
        sql_add_brand,
        sql_add_place,
        add_default_product_mapping,
        mock_generalized_info_context,
        product_request,
):
    """
    Если в конфиге включено получение информеров в карточке товара, и данные
    о товаре получаются из обобщенной ручки, то информеры будут в ответе
    """
    sql_add_brand()
    sql_add_place()
    add_default_product_mapping()

    informers = [
        utils.make_text_image_informer('1'),
        utils.make_background_informer('2'),
    ]

    @mockserver.json_handler(utils.Handlers.SCREEN_COMMUNICATIONS)
    def mock_eats_communications(request):
        assert request.json['types'] == ['informers']
        assert request.json['screen'] == 'product_card'
        assert request.json['place_id'] == str(utils.PLACE_ID)
        assert request.json['brand_id'] == str(utils.BRAND_ID)
        return {'payload': {'stories': [], 'informers': informers}}

    mock_nomenclature_static_info_context.add_product(PRODUCT_PUBLIC_ID)
    mock_generalized_info_context.set_generalized_info(
        PRODUCT_PUBLIC_ID, 'item_1', '100.0', ['1'],
    )
    response = await taxi_eats_products.post(
        utils.Handlers.MENU_PRODUCT, json=product_request,
    )

    assert response.status_code == 200
    assert mock_generalized_info_context.handler.times_called == 1
    assert mock_eats_communications.times_called == 1
    detailed_data = response.json()['detailed_data']
    assert [data['type'] for data in detailed_data] == [
        'gallery',
        INFORMERS_BLOCK,
        'header',
        'description',
    ]
    informers_data = detailed_data[1]
    assert informers_data['payload'] == {'informers': informers}
