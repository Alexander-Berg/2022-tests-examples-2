import pytest

PARTNER_ID = '777'
PLACE_ID = '109151'
MENU_REVISION = 'Mi41'


@pytest.mark.experiments3(filename='transitional_settings.json')
async def test_ns_menu_active_get_no_access(
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


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
@pytest.mark.parametrize(
    (
        'moderation_available',
        'called_core_old',
        'called_core_new',
        'base_file',
        'revision_file',
        'menu_revision',
    ),
    [
        pytest.param(
            False,
            1,
            0,
            'base_data.json',
            'revision_data.json',
            MENU_REVISION,
            id='no moderation',
        ),
        pytest.param(
            True,
            0,
            1,
            'base_data.json',
            'revision_data.json',
            MENU_REVISION,
            marks=[
                pytest.mark.experiments3(
                    filename='moderation_flow_settings.json',
                ),
            ],
            id='with moderation',
        ),
        pytest.param(
            False,
            1,
            0,
            'base_data_measures.json',
            'revision_data_measures.json',
            MENU_REVISION,
            id='with measures',
        ),
        pytest.param(
            False,
            1,
            0,
            'base_data_measures.json',
            'revision_data_measures.json',
            MENU_REVISION,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_SQL_BATCHING={
                        'read_batch_size': 1,
                        'write_batch_size': 1,
                    },
                ),
            ],
            id='with measures (1 batch)',
        ),
    ],
)
async def test_ns_menu_active_get_basic(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pg_get_revisions,
        pg_get_categories,
        pg_get_items,
        pg_get_menus,
        moderation_available,
        called_core_old,
        called_core_new,
        base_file,
        revision_file,
        menu_revision,
):
    @mockserver.json_handler(
        f'/eats-core-restapp/v1/places/{PLACE_ID}/place-menu',
    )
    def mock_place_menu(request):
        return load_json(base_file)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu_new(request):
        return load_json(base_file)

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    resp_json = response.json()
    resp_json['menu']['categories'] = sorted(
        resp_json['menu']['categories'], key=lambda x: x['id'],
    )
    resp_json['menu']['items'] = sorted(
        resp_json['menu']['items'], key=lambda x: x['id'],
    )
    assert resp_json == {
        'revision': menu_revision,
        'menu': load_json(revision_file),
        'new_moderation_available': moderation_available,
    }

    assert mock_place_access_200.times_called == 1
    assert mock_place_menu.times_called == called_core_old
    assert mock_place_menu_new.times_called == called_core_new

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert len(pg_get_revisions()) == 4

    assert mock_place_access_200.times_called == 2
    assert mock_place_menu.times_called == 2 * called_core_old
    assert mock_place_menu_new.times_called == 2 * called_core_new

    if revision_file != 'revision_data_measures.json':
        assert pg_get_items() == [
            [
                'NAL1Nv-jZ5lxZMLK5B7mJQ',
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
            [
                'NAL1Nv-jZ5lxZMLK5B7mJQ',
                'rgPjuy-SmxcZNsUqmdcpGg',
                'KuZBq6IrxmkJ7SayDAKukQ',
                '3Jl_oNdYTkPlLzELXMZ9mw',
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
                },
                [],
                [],
            ],
            [
                'cth27DbS0H_aZNL8gq_MGA',
                '1OGZuMFJeUD8yFaSJXdg_w',
                '3DYMsodJhgctIqBPqPB2sg',
                'J5KM3ksN3atJuLawCpHzZQ',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '1234595',
                {
                    'name': 'Сметана 20%',
                    'description': '',
                    'measure': 50.0,
                    'measureUnit': 'г',
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
            [
                'cth27DbS0H_aZNL8gq_MGA',
                '38jcShGOQU43tEy-2okKLg',
                'bKrzofHPCzLC3jbJJ6vSHg',
                'bZh1-urGAsvDbG-yHfVQKw',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '1234583',
                {
                    'name': 'Сухофрукты',
                    'description': '',
                    'measure': 35.0,
                    'measureUnit': 'г',
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
                [],
                [],
            ],
        ]

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
                    5,
                    None,
                    109151,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'NAL1Nv-jZ5lxZMLK5B7mJQ',
                    'external',
                    'not_applicable',
                    None,
                ),
                (
                    1,
                    None,
                    109152,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    2,
                    None,
                    109153,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    3,
                    None,
                    109154,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    4,
                    None,
                    109155,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
            )
        )
    else:
        assert pg_get_items() == [
            [
                'ANywB-cFX-LaqqfbJQfRoQ',
                'JLsrQwHk2SCVGwRXYup3Ow',
                'TqUAFQVo0qpDy9FVfi9kfQ',
                'a6EM7B5TBevOqkqRPH0j9Q',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '987',
                {
                    'name': 'Сметана 20%',
                    'description': '',
                    'weight': {'value': '123.23', 'unit': 'л'},
                },
                {
                    'origin_id': '987',
                    'category_origin_ids': ['103263'],
                    'price': '1000',
                    'vat': '0',
                    'sort': 100,
                    'legacy_id': 37660169,
                    'available': True,
                    'pictures': [],
                },
                [],
                [],
            ],
            [
                'ANywB-cFX-LaqqfbJQfRoQ',
                'd7lyvIw3okYRBAz2CqHL0g',
                '3oUozgqeDA8tkCr_7gKq6Q',
                '3Jl_oNdYTkPlLzELXMZ9mw',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '1234583',
                {
                    'name': 'Сухофрукты',
                    'description': '',
                    'weight': {'unit': 'г', 'value': '1.0'},
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
                [],
                [],
            ],
            [
                'ANywB-cFX-LaqqfbJQfRoQ',
                'eolsgeLBOzP-r6ymV1D42Q',
                'dzZjUE86cou3ccl8iChQdA',
                'MpdXkZIwB5YMgbTl52zqwQ',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '988',
                {
                    'name': 'Сметана 15%',
                    'description': '',
                    'weight': {'value': '500', 'unit': 'мл'},
                },
                {
                    'origin_id': '988',
                    'category_origin_ids': ['103263'],
                    'price': '1200',
                    'vat': '0',
                    'sort': 100,
                    'legacy_id': 37660170,
                    'available': True,
                    'pictures': [],
                },
                [],
                [],
            ],
            [
                'ANywB-cFX-LaqqfbJQfRoQ',
                's3NnLNdanHR-KLD5dYmBgw',
                'iPWrdxYKQQ0oV3RdPFq3yA',
                'tcWj7YQMc7a4xLUxj0hgUw',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '1234595',
                {
                    'name': 'Сметана 20%',
                    'description': '',
                    'weight': {'unit': 'г', 'value': '1.0'},
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
            [
                'cth27DbS0H_aZNL8gq_MGA',
                '1OGZuMFJeUD8yFaSJXdg_w',
                '3DYMsodJhgctIqBPqPB2sg',
                'J5KM3ksN3atJuLawCpHzZQ',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '1234595',
                {
                    'name': 'Сметана 20%',
                    'description': '',
                    'measure': 50.0,
                    'measureUnit': 'г',
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
            [
                'cth27DbS0H_aZNL8gq_MGA',
                '38jcShGOQU43tEy-2okKLg',
                'bKrzofHPCzLC3jbJJ6vSHg',
                'bZh1-urGAsvDbG-yHfVQKw',
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                '1234583',
                {
                    'name': 'Сухофрукты',
                    'description': '',
                    'measure': 35.0,
                    'measureUnit': 'г',
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
                [],
                [],
            ],
        ]

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
                    5,
                    None,
                    109151,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'ANywB-cFX-LaqqfbJQfRoQ',
                    'external',
                    'not_applicable',
                    None,
                ),
                (
                    1,
                    None,
                    109152,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    2,
                    None,
                    109153,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    3,
                    None,
                    109154,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    4,
                    None,
                    109155,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
            )
        )


@pytest.mark.experiments3(filename='transitional_settings.json')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_restapp_menu_erms_integration',
    consumers=['eats-restapp-menu/transitional_settings'],
    clauses=[],
    default_value={'update_enabled': False, 'get_enabled': True},
    is_config=True,
)
@pytest.mark.config(
    EATS_RESTAPP_MENU_PICTURE_SETTINGS={
        'url_prefix': 'https://testing.eda.tst.yandex.net/images',
        'image_postfix': '.jpg',
        'thumbnail_postfix': '-80x80.jpg',
        'image_processing_enabled': False,
    },
)
@pytest.mark.parametrize(
    (
        'moderation_available',
        'called_erms',
        'base_file',
        'revision_file',
        'menu_revision',
    ),
    [
        pytest.param(
            False,
            1,
            'base_data_erms.json',
            'revision_data.json',
            MENU_REVISION,
            id='no moderation',
        ),
        pytest.param(
            True,
            1,
            'base_data_erms.json',
            'revision_data.json',
            MENU_REVISION,
            marks=[
                pytest.mark.experiments3(
                    filename='moderation_flow_settings.json',
                ),
            ],
            id='with moderation',
        ),
        pytest.param(
            False,
            1,
            'base_data_measures_erms.json',
            'revision_data_measures.json',
            MENU_REVISION,
            id='with measures',
        ),
        pytest.param(
            False,
            1,
            'base_data_measures_erms.json',
            'revision_data_measures.json',
            MENU_REVISION,
            marks=[
                pytest.mark.config(
                    EATS_RESTAPP_MENU_SQL_BATCHING={
                        'read_batch_size': 1,
                        'write_batch_size': 1,
                    },
                ),
            ],
            id='with measures (1 batch)',
        ),
    ],
)
async def test_ns_menu_active_get_erms(
        taxi_eats_restapp_menu,
        mock_place_access_200,
        mockserver,
        load_json,
        pg_get_revisions,
        pg_get_categories,
        pg_get_items,
        pg_get_menus,
        moderation_available,
        called_erms,
        base_file,
        revision_file,
        menu_revision,
):
    @mockserver.json_handler('/eats-rest-menu-storage/internal/v1/menu')
    def mock_place_menu(request):
        return load_json(base_file)

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert response.status_code == 200
    resp_json = response.json()
    resp_json['menu']['categories'] = sorted(
        resp_json['menu']['categories'], key=lambda x: x['id'],
    )
    resp_json['menu']['items'] = sorted(
        resp_json['menu']['items'], key=lambda x: x['id'],
    )
    assert resp_json == {
        'revision': menu_revision,
        'menu': load_json(revision_file),
        'new_moderation_available': moderation_available,
    }

    assert mock_place_access_200.times_called == 1
    assert mock_place_menu.times_called == called_erms

    response = await taxi_eats_restapp_menu.get(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/active',
        params={'place_id': PLACE_ID},
        headers={'X-YaEda-PartnerId': PARTNER_ID},
    )

    assert len(pg_get_revisions()) == 4

    assert mock_place_access_200.times_called == 2
    assert mock_place_menu.times_called == 2 * called_erms

    if revision_file != 'revision_data_measures.json':
        expected = load_json('expected_erms.json')
        assert pg_get_items() == expected['items']
        assert pg_get_categories() == expected['categories']

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
                    5,
                    None,
                    109151,
                    None,
                    'ktb44zVUnYnueQw2f0wcag',
                    'CdxV9Tl35erBZFmoSF1W3Q',
                    'external',
                    'not_applicable',
                    None,
                ),
                (
                    1,
                    None,
                    109152,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    2,
                    None,
                    109153,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    3,
                    None,
                    109154,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    4,
                    None,
                    109155,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
            )
        )
    else:
        expected = load_json('expected_measures_erms.json')
        assert pg_get_items() == expected['items']
        assert pg_get_categories() == expected['categories']

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
                    5,
                    None,
                    109151,
                    None,
                    'ktb44zVUnYnueQw2f0wcag',
                    'qKlF2RX-xMKvEtvUgKk6eA',
                    'external',
                    'not_applicable',
                    None,
                ),
                (
                    1,
                    None,
                    109152,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    2,
                    None,
                    109153,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    3,
                    None,
                    109154,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
                (
                    4,
                    None,
                    109155,
                    None,
                    'Jly24hdsOplLFU1pwvXZRA',
                    'cth27DbS0H_aZNL8gq_MGA',
                    'user_generated',
                    'applied',
                    None,
                ),
            )
        )
