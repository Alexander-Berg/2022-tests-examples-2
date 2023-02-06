import pytest

from agent import const


TRANSLATE = {
    const.ERROR_ACCESS_DENIED: {'ru': 'Ошибка доступа', 'en': 'Access denied'},
    'shop_permissions_conflict': {
        'ru': 'Более 1 пермишена для магазина',
        'en': 'More then 1 permission for shop',
    },
    'purchase_not_found': {
        'ru': 'Покупка отсутствует',
        'en': 'Purchase is missing',
    },
    const.PURCHASE_INIT_STATUS_KEY: {
        'ru': 'Покупка инициализирована',
        'en': 'Purchase initialized',
    },
}

GOOD_HEADERS: dict = {
    'X-Yandex-Login': 'mikh-vasily',
    'Accept-Language': 'ru-ru',
}
BAD_HEADERS: dict = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-en'}
BAD_HEADERS2: dict = {
    'X-Yandex-Login': 'test_user',
    'Accept-Language': 'en-en',
}


DATA = {'purchase_id': '1111'}


@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status, response_content',
    [
        (
            DATA,
            GOOD_HEADERS,
            200,
            {
                'purchase_id': '1111',
                'status_key': const.PURCHASE_INIT_STATUS_KEY,
                'status_locale': 'Покупка инициализирована',
                'type': 'test_type',
            },
        ),
        (
            DATA,
            BAD_HEADERS,
            403,
            {'code': const.ERROR_ACCESS_DENIED, 'message': 'Access denied'},
        ),
        (
            DATA,
            BAD_HEADERS2,
            403,
            {
                'code': 'shop_permissions_conflict',
                'message': 'More then 1 permission for shop',
            },
        ),
        (
            {'purchase_id': '3333'},
            GOOD_HEADERS,
            404,
            {'code': 'purchase_not_found', 'message': 'Покупка отсутствует'},
        ),
        (
            {'purchase_id': '2222'},
            GOOD_HEADERS,
            404,
            {'code': 'purchase_not_found', 'message': 'Покупка отсутствует'},
        ),
    ],
)
async def test_purchase_status(
        web_context,
        web_app_client,
        input_data,
        headers,
        status,
        response_content,
):
    purchase_id = input_data['purchase_id']
    response_get = await web_app_client.get(
        f'/shop/goods/purchase-status/{purchase_id}', headers=headers,
    )
    assert response_get.status == status
    assert await response_get.json() == response_content
