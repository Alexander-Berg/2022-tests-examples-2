import pytest

from tests_eats_retail_order_history import utils

HANDLER = '/internal/v1/order/info'


async def assert_response(
        taxi_eats_retail_order_history, expected_status, expected_response,
):
    response = await taxi_eats_retail_order_history.get(
        HANDLER, params={'order_nr': utils.ORDER_ID},
    )
    assert response.status_code == expected_status
    if expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.parametrize('order_in_db', [True, False])
async def test_internal_order_info_404(
        taxi_eats_retail_order_history, create_order, order_in_db,
):
    if order_in_db:
        create_order(yandex_uid=None, order_nr=utils.ORDER_ID)
    await assert_response(
        taxi_eats_retail_order_history,
        404,
        {
            'code': 'order_not_found',
            'message': 'Отсутствует информация по заказу',
        },
    )


async def test_internal_order_info_from_db(
        taxi_eats_retail_order_history, create_order,
):
    create_order(
        yandex_uid=None,
        order_nr=utils.ORDER_ID,
        place_id=utils.PLACE_ID,
        place_slug=utils.PLACE_SLUG,
        place_name=utils.PLACE_NAME,
        place_business='shop',
        city=utils.CITY,
        place_address=utils.PLACE_ADDRESS,
        order_created_at='2022-02-01T09:05:01.377784+00:00',
    )
    await assert_response(
        taxi_eats_retail_order_history,
        200,
        {
            'application': 'go',
            'created_at': '2022-02-01T09:05:01.377784+00:00',
            'order_nr': '12345',
            'place': {
                'address': {'city': 'Москва', 'short': 'ул. Абвгд, д. 0'},
                'business': 'shop',
                'id': '222325',
                'is_marketplace': False,
                'name': 'Магнит',
                'slug': 'aaa-bbb',
            },
        },
    )


async def test_internal_order_info_from_db_with_brand(
        taxi_eats_retail_order_history, create_order,
):
    create_order(
        yandex_uid=None,
        order_nr=utils.ORDER_ID,
        place_id=utils.PLACE_ID,
        place_slug=utils.PLACE_SLUG,
        place_name=utils.PLACE_NAME,
        place_business='shop',
        city=utils.CITY,
        place_address=utils.PLACE_ADDRESS,
        brand_id=utils.BRAND_ID,
        brand_slug=utils.BRAND_SLUG,
        brand_name=utils.BRAND_NAME,
        order_created_at='2022-02-01T09:05:01.377784+00:00',
    )
    await assert_response(
        taxi_eats_retail_order_history,
        200,
        {
            'application': 'go',
            'created_at': '2022-02-01T09:05:01.377784+00:00',
            'order_nr': '12345',
            'place': {
                'address': {'city': 'Москва', 'short': 'ул. Абвгд, д. 0'},
                'business': 'shop',
                'id': '222325',
                'is_marketplace': False,
                'name': 'Магнит',
                'slug': 'aaa-bbb',
            },
            'brand': {'id': 1, 'name': 'Магнит', 'slug': 'abc'},
        },
    )
