import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
INVALID_REVISION = '123'
VALID_REVISION = 'Mi4x'
NEW_REVISION = 'Mi4y'


@pytest.mark.experiments3(filename='transitional_settings.json')
async def test_ns_menu_update_patch_no_access(
        taxi_eats_restapp_menu, mock_write_access_403, load_json,
):
    response = await taxi_eats_restapp_menu.patch(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/update',
        params={'place_id': PLACE_ID, 'revision': INVALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': load_json('add_data.json')},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to place is denied',
    }

    assert mock_write_access_403.times_called == 1


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.now('2021-01-01T12:00:00Z')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
async def test_ns_menu_update_patch_basic(
        taxi_eats_restapp_menu,
        mock_write_access_200,
        load_json,
        stq,
        testpoint,
        pg_get_items,
        pg_get_categories,
        pg_get_menus,
):
    @testpoint('DuplicateAdd')
    def duplicate_add(arg):
        pass

    response = await taxi_eats_restapp_menu.patch(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/update',
        params={'place_id': PLACE_ID, 'revision': VALID_REVISION},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
        json={'menu': load_json('add_data.json')},
    )

    assert response.status_code == 200
    assert response.json() == {
        'revision': NEW_REVISION,
        'status': 'processing',
        'status_type': 'intermediate',
    }

    assert duplicate_add.times_called == 0
    assert mock_write_access_200.times_called == 1
    assert stq.eats_restapp_menu_update_menu.times_called == 1

    assert pg_get_items() == [
        [
            'GvtfijKmw-7D3rq2P4HwOw',
            'E-OCogy5OchwoFkQBBwUNQ',
            'KuZBq6IrxmkJ7SayDAKukQ',
            '1p5HU_vkq9xx0inmbj0e9A',
            '11FxOYiYfpMxmANj4kGJzg',
            '11FxOYiYfpMxmANj4kGJzg',
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
                'adult': True,
                'ordinary': False,
                'choosable': False,
                'shipping_types': ['delivery', 'pickup'],
            },
            [],
            [],
        ],
        [
            'GvtfijKmw-7D3rq2P4HwOw',
            'lznyVopZR8WDV1-qLK8aWA',
            'Nz2Shnjo4NIWI81ok9uJ7Q',
            '2cuzQTSki68K-J2lUjgmLw',
            '11FxOYiYfpMxmANj4kGJzg',
            '11FxOYiYfpMxmANj4kGJzg',
            '1234595',
            {
                'description': '',
                'weight': {'value': '50', 'unit': 'г'},
                'name': 'Сметана 20% (меняем имя и цену)',
            },
            {
                'category_origin_ids': ['103263'],
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
                'adult': False,
                'ordinary': True,
                'choosable': True,
                'shipping_types': ['delivery', 'pickup'],
                'origin_id': '1234595',
                'price': '200',
            },
            [],
            [],
        ],
        [
            'TqjC5e1bquH7XSjQ25GSRg',
            '2UQ6wQn8GWTNCqWu7due6g',
            '7lTf-KMko8ztWQRe5Uvq5g',
            'wYQ4mli-PCdUK5abj6d_1A',
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
                'adult': False,
                'ordinary': True,
                'choosable': True,
                'shipping_types': ['delivery', 'pickup'],
            },
            [],
            [],
        ],
        [
            'TqjC5e1bquH7XSjQ25GSRg',
            'E-OCogy5OchwoFkQBBwUNQ',
            'KuZBq6IrxmkJ7SayDAKukQ',
            '1p5HU_vkq9xx0inmbj0e9A',
            '11FxOYiYfpMxmANj4kGJzg',
            '11FxOYiYfpMxmANj4kGJzg',
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
                'adult': True,
                'ordinary': False,
                'choosable': False,
                'shipping_types': ['delivery', 'pickup'],
            },
            [],
            [],
        ],
    ]

    assert pg_get_categories() == [
        [
            'IE-pRfuH3-XH8V4TaOhCbg',
            'fHe9_eFwwSU_4a57S4R0GQ',
            {
                'sort': 160,
                'available': True,
                'legacy_id': 567,
                'origin_id': '103265',
                'name': 'Закуски (меняем имя)',
            },
            '103265',
        ],
        [
            'IE-pRfuH3-XH8V4TaOhCbg',
            'hpbibTB0x9w4TbvgC5yW7g',
            {
                'origin_id': '103263',
                'name': 'Завтрак',
                'sort': 130,
                'available': True,
                'legacy_id': 123,
            },
            '103263',
        ],
        [
            'Jly24hdsOplLFU1pwvXZRA',
            '7OprL8pisQH9nuaEavPqaA',
            {
                'origin_id': '103265',
                'name': 'Закуски',
                'sort': 160,
                'available': True,
                'legacy_id': 567,
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
                'legacy_id': 123,
            },
            '103263',
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
                109151,
                None,
                'Jly24hdsOplLFU1pwvXZRA',
                'TqjC5e1bquH7XSjQ25GSRg',
                'user_generated',
                'applied',
                None,
            ),
            (
                2,
                1,
                109151,
                777,
                'IE-pRfuH3-XH8V4TaOhCbg',
                'GvtfijKmw-7D3rq2P4HwOw',
                'user_generated',
                'processing',
                None,
            ),
        )
    )
