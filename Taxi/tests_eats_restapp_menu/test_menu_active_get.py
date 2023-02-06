import json

import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'MS4xNjA5NDU5MjAwMDAwLlh0dWlHWUUzeE96cER1WDN0dndkeFE'
MENU_REVISION_MEASURES = 'MS4xNjA5NDU5MjAwMDAwLjk0U19laTA0Zmp3MDMwekNwTGRGWmc'
MENU_REVISION_NEW_STORAGE = 'Mi4x'


async def test_menu_active_get_no_access(
        taxi_eats_restapp_menu, mock_place_access_400,
):
    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
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
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_active_get_basic(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pg_get_revisions,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data.json')

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': MENU_REVISION,
        'menu': load_json('revision_data.json'),
        'new_moderation_available': False,
    }

    assert mock_place_access_200.times_called == 1
    assert mock_place_menu.times_called == 1

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    revs = pg_get_revisions()
    assert len(revs) == 5 and all(
        rev['revision'] == MENU_REVISION for rev in revs
    )

    assert mock_place_access_200.times_called == 2
    assert mock_place_menu.times_called == 2


@pytest.mark.experiments3(filename='moderation_flow_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_active_get_new_mod(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pg_get_revisions,
):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data.json')

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': MENU_REVISION,
        'menu': load_json('revision_data.json'),
        'new_moderation_available': True,
    }

    assert mock_place_access_200.times_called == 1
    assert mock_place_menu.times_called == 1

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    revs = pg_get_revisions()
    assert len(revs) == 5 and all(
        rev['revision'] == MENU_REVISION for rev in revs
    )

    assert mock_place_access_200.times_called == 2
    assert mock_place_menu.times_called == 2


@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
async def test_menu_active_get_measures(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pg_get_menu_content,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_measures.json')

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': MENU_REVISION_MEASURES,
        'menu': load_json('revision_data_measures.json'),
        'new_moderation_available': False,
    }

    assert mock_place_access_200.times_called == 1
    assert mock_place_menu.times_called == 1

    datas = pg_get_menu_content()
    assert json.loads(datas[0]['menu_json']) == load_json(
        'revision_data_measures_db.json',
    )


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': True,
    },
)
@pytest.mark.pgsql('eats_restapp_menu', files=('fill_data.sql',))
async def test_menu_active_get_new_storage(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pg_get_revisions,
        pg_get_menus,
        pg_get_categories,
        pg_get_categories_by_parts,
        pg_get_items,
        pg_get_items_by_parts,
        pg_get_revision_transitions,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json('base_data_new_storage.json')

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': MENU_REVISION_NEW_STORAGE,
        'menu': load_json('revision_data_new_storage.json'),
        'new_moderation_available': False,
    }

    assert mock_place_access_200.times_called == 1
    assert mock_place_menu.times_called == 1

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert len(pg_get_revisions()) == 4

    assert mock_place_access_200.times_called == 2
    assert mock_place_menu.times_called == 2

    categories_parts = pg_get_categories_by_parts()
    assert (
        len(categories_parts['categories']) == 2
        and len(categories_parts['to_categories']) == 1
    )
    items_parts = pg_get_items_by_parts()
    assert (
        len(items_parts['items']) == 2
        and len(items_parts['item_data_bases']) == 2
        and len(items_parts['item_data']) == 2
        and len(items_parts['options_bases']) == 2
        and len(items_parts['options']) == 2
        and len(items_parts['to_items']) == 1
    )

    assert pg_get_categories() == [
        [
            'Jly24hdsOplLFU1pwvXZRA',
            '7OprL8pisQH9nuaEavPqaA',
            {
                'origin_id': '103265',
                'name': 'Закуски',
                'sort': 160,
                'available': True,
            },
            '103265',
        ],
        [
            'Jly24hdsOplLFU1pwvXZRA',
            'cGijaeNvGeqgE3KXkgnbyA',
            {
                'origin_id': '103263',
                'name': 'Завтрак',
                'sort': 130,
                'available': True,
            },
            '103263',
        ],
    ]

    assert pg_get_items() == [
        [
            'jXSXHzaN5GneNA69o37Jtw',
            '9vHAOCtwP8wHLYhdmdLJ_Q',
            'KuZBq6IrxmkJ7SayDAKukQ',
            '3Jl_oNdYTkPlLzELXMZ9mw',
            'YQy_RCbaZ7pYrYXkzTZ_Ag',
            '_eyQOaKo8EGwAS67MUq5ew',
            '1234583',
            {
                'name': 'Сухофрукты',
                'description': '',
                'weight': {'value': '35', 'unit': 'г'},
            },
            {
                'origin_id': '1234583',
                'category_origin_ids': ['103263'],
                'price': '100',
                'vat': '0',
                'sort': 100,
                'legacy_id': 37660163,
                'available': True,
                'pictures': [
                    {
                        'avatarnica_identity': (
                            '1370147/36ca994761eb1fd00066ac634c96e0d9'
                        ),
                    },
                ],
            },
            [{'name': 'Основа каши', 'options': [{'name': 'Молоко'}]}],
            [
                {
                    'origin_id': '2716195',
                    'options': [
                        {
                            'origin_id': '26783155',
                            'price': '0',
                            'min_amount': 0,
                            'max_amount': 1,
                            'available': True,
                            'legacy_id': 93947398,
                        },
                    ],
                    'min_selected_options': 1,
                    'max_selected_options': 1,
                    'sort': 100,
                    'legacy_id': 12465033,
                },
            ],
        ],
        [
            'jXSXHzaN5GneNA69o37Jtw',
            'o2zXZdnDv9aukE-qKIFUig',
            '7lTf-KMko8ztWQRe5Uvq5g',
            'tcWj7YQMc7a4xLUxj0hgUw',
            '11FxOYiYfpMxmANj4kGJzg',
            '11FxOYiYfpMxmANj4kGJzg',
            '1234595',
            {
                'name': 'Сметана 20%',
                'description': '',
                'weight': {'value': '50', 'unit': 'г'},
            },
            {
                'origin_id': '1234595',
                'category_origin_ids': ['103263'],
                'price': '100',
                'vat': '0',
                'sort': 100,
                'legacy_id': 37660168,
                'available': True,
                'pictures': [
                    {
                        'avatarnica_identity': (
                            '1368744/9d2253f1d40f86ff4e525e998f49dfca'
                        ),
                    },
                ],
            },
            [],
            [],
        ],
    ]

    assert (
        tuple(
            (
                it['id'],
                it['base_id'],
                it['place_id'],
                it['author_id'],
                it['categories_hash'],
                it['items_hash'],
                it['origin'],
                it['status'],
                it['errors_json'],
            )
            for it in pg_get_menus()
        )
        == (
            (
                1,
                None,
                int(PLACE_ID),
                None,
                'Jly24hdsOplLFU1pwvXZRA',
                'jXSXHzaN5GneNA69o37Jtw',
                'external',
                'not_applicable',
                None,
            ),
        )
    )
