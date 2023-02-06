import pytest


EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS = {
    'adult_image_placeholder_with_resize': {
        'resized_url_pattern': 'adult_image_url_with_resize',
        'url': 'adult_image_url',
    },
}


@pytest.mark.pgsql(
    'eats_retail_order_history', files=['db_orders_and_items.sql'],
)
async def test_orders_for_ordershistory(taxi_eats_retail_order_history):
    response = await taxi_eats_retail_order_history.post(
        '/internal/retail-order-history/v1/orders-for-history',
        json={'order_nrs': ['121-121', '122-122', '123-123', '124-124']},
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'order_nr': '121-121',
                'total_amount': '384',
                'items': [
                    {
                        'origin_id': '214664',
                        'name': 'Салат со шпинатом и сыром сулугуни',
                        'images_url_template': [],
                    },
                    {
                        'origin_id': '214665',
                        'name': 'Греческий салат',
                        'images_url_template': ['image_url_1', 'image_url_2'],
                    },
                ],
            },
            {'order_nr': '122-122', 'total_amount': '284', 'items': []},
            {'order_nr': '123-123', 'total_amount': '234', 'items': []},
            {'order_nr': '124-124', 'total_amount': '0', 'items': []},
        ],
    }


@pytest.mark.pgsql(
    'eats_retail_order_history', files=['db_orders_and_items_adult.sql'],
)
@pytest.mark.parametrize(
    'expected_image_urls',
    [
        # В этом тесте товар 214664 не отмечен флажком adult,
        # а 214665 - отмечен. Проверяется, что при выключенном конфиге
        # EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS изображения обоих
        # товаров отправляются без изменений несмотря на то, что один из
        # них отмечен флагом adult.
        pytest.param(
            [
                '214664_image_url_1',
                '214664_image_url_2',
                '214665_image_url_1',
                '214665_image_url_2',
            ],
        ),
        # В этом тесте товар 214664 не отмечен флажком adult,
        # а 214665 - отмечен. Проверяется, что при включенном конфиге
        # EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS изображения 214664
        # отправляются без изменений, а два изображения товара 214665
        # заменяются на один плейсхолдер который указан в конфиге.
        pytest.param(
            [
                '214664_image_url_1',
                '214664_image_url_2',
                'adult_image_url_with_resize',
            ],
            marks=(
                pytest.mark.config(
                    EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS=(
                        EATS_RETAIL_ORDER_HISTORY_ADULT_SETTINGS
                    ),
                ),
            ),
        ),
    ],
)
async def test_orders_for_ordershistory_adult(
        taxi_eats_retail_order_history, expected_image_urls,
):
    response = await taxi_eats_retail_order_history.post(
        '/internal/retail-order-history/v1/orders-for-history',
        json={'order_nrs': ['121-121', '122-122', '123-123', '124-124']},
    )
    assert response.status_code == 200
    assert len(response.json()['orders']) == 1

    order = response.json()['orders'][0]

    images_urls = []
    for item in order['items']:
        for image_url in item['images_url_template']:
            images_urls.append(image_url)

    assert expected_image_urls == images_urls
