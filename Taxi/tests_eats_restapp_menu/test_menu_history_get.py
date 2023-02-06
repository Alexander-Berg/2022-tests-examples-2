import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'MS4xNjA5NDU5MjAwMDAwLlh0dWlHWUUzeE96cER1WDN0dndkeFE'
MENU_REVISION_MEASURES = 'MS4xNjA5NDU5MjAwMDAwLjk0U19laTA0Zmp3MDMwekNwTGRGWmc'
MENU_REVISION_NEW_STORAGE = (
    'MS4xNjA5NDU5MjAwMDAwLkxpSjNKbkd2b1lrd2hXWTBYeEdkNFE'
)


async def test_menu_history_get_no_access(
        taxi_eats_restapp_menu, mock_place_access_400,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/history',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert mock_place_access_400.times_called == 1


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
async def test_menu_history_get_400(
        taxi_eats_restapp_menu, mock_place_access_200,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/history',
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'

    assert mock_place_access_200.times_called == 0


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
async def test_menu_history_get_basic(
        taxi_eats_restapp_menu, mock_place_access_200,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/history',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cursor': '3',
        'history': [
            {
                'revision': 'Mi45',
                'status_type': 'success',
                'status': 'applied',
                'created_at': '2021-04-04T04:04:04+00:00',
                'applied_at': '2021-04-04T04:04:04+00:00',
                'changes': {
                    'categories': [
                        {
                            'id': '103263',
                            'name': 'Завтрак',
                            'status': 'rejected',
                            'errors': [
                                {'code': '123', 'message': 'CategoryMessage1'},
                            ],
                        },
                        {
                            'id': '103265',
                            'name': 'Закуски',
                            'status': 'rejected',
                        },
                    ],
                    'items': [
                        {
                            'id': '1234583',
                            'name': 'Сухофрукты',
                            'status': 'rejected',
                            'errors': [
                                {'code': '777', 'message': 'ItemMessage2'},
                            ],
                        },
                        {
                            'id': '1234595',
                            'name': 'Сметана 20%',
                            'status': 'rejected',
                        },
                    ],
                },
            },
            {
                'revision': 'Mi4z',
                'status_type': 'success',
                'status': 'applied',
                'created_at': '2021-04-04T04:04:04+00:00',
                'applied_at': '2021-04-04T04:04:04+00:00',
                'changes': {
                    'categories': [
                        {
                            'id': '103263',
                            'name': 'Завтрак',
                            'status': 'approved',
                        },
                        {
                            'id': '103265',
                            'name': 'Закуски',
                            'status': 'approved',
                        },
                    ],
                    'items': [
                        {
                            'id': '1234583',
                            'name': 'Сухофрукты',
                            'status': 'approved',
                        },
                        {
                            'id': '1234595',
                            'name': 'Сметана 20%',
                            'status': 'approved',
                        },
                    ],
                },
            },
        ],
    }


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
async def test_menu_history_get_limit(
        taxi_eats_restapp_menu, mock_place_access_200,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/history',
        params={'place_id': PLACE_ID, 'limit': 1},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'cursor': '9',
        'history': [
            {
                'revision': 'Mi45',
                'status_type': 'success',
                'status': 'applied',
                'created_at': '2021-04-04T04:04:04+00:00',
                'applied_at': '2021-04-04T04:04:04+00:00',
                'changes': {
                    'categories': [
                        {
                            'id': '103263',
                            'name': 'Завтрак',
                            'status': 'rejected',
                            'errors': [
                                {'code': '123', 'message': 'CategoryMessage1'},
                            ],
                        },
                        {
                            'id': '103265',
                            'name': 'Закуски',
                            'status': 'rejected',
                        },
                    ],
                    'items': [
                        {
                            'id': '1234583',
                            'name': 'Сухофрукты',
                            'status': 'rejected',
                            'errors': [
                                {'code': '777', 'message': 'ItemMessage2'},
                            ],
                        },
                        {
                            'id': '1234595',
                            'name': 'Сметана 20%',
                            'status': 'rejected',
                        },
                    ],
                },
            },
        ],
    }

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/history',
        params={'place_id': PLACE_ID, 'cursor': 9, 'limit': 1},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'history': [
            {
                'revision': 'Mi4z',
                'status_type': 'success',
                'status': 'applied',
                'created_at': '2021-04-04T04:04:04+00:00',
                'applied_at': '2021-04-04T04:04:04+00:00',
                'changes': {
                    'categories': [
                        {
                            'id': '103263',
                            'name': 'Завтрак',
                            'status': 'approved',
                        },
                        {
                            'id': '103265',
                            'name': 'Закуски',
                            'status': 'approved',
                        },
                    ],
                    'items': [
                        {
                            'id': '1234583',
                            'name': 'Сухофрукты',
                            'status': 'approved',
                        },
                        {
                            'id': '1234595',
                            'name': 'Сметана 20%',
                            'status': 'approved',
                        },
                    ],
                },
            },
        ],
        'cursor': '3',
    }
