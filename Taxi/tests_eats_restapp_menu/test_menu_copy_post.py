import copy

import pytest

PARTNER_ID = '777'
PLACE_ID = '109152'
REVISION = 'Mi4y'
REVISION_NOT_FOUND = 'Mi4xMDgw'
TARGET_PLACE_ID = '109151'
CORE_PLACES_INFO = [
    {
        'id': int(PLACE_ID),
        'name': 'name3',
        'available': False,
        'currency': {'code': 'code3', 'sign': 'sign3', 'decimal_places': 3},
        'country_code': 'country_code3',
        'address': {
            'country': 'country3',
            'city': 'city3',
            'street': 'street3',
            'building': 'building3',
            'full': 'country3 city3 street3 building3',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'type': 'native',
        'slug': 'slug3',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'brand2', 'business_type': 'some_type'},
    },
    {
        'id': int(TARGET_PLACE_ID),
        'name': 'name3',
        'available': False,
        'currency': {'code': 'code3', 'sign': 'sign3', 'decimal_places': 3},
        'country_code': 'country_code3',
        'address': {
            'country': 'country3',
            'city': 'city3',
            'street': 'street3',
            'building': 'building3',
            'full': 'country3 city3 street3 building3',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'type': 'native',
        'slug': 'slug3',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'brand2', 'business_type': 'some_type'},
    },
]
MODERATION_RESPONSE = {
    'items': [
        {
            'task_id': '456',
            'status': 'process',
            'queue': 'restapp_moderation_menu',
            'payload': '{"id":"qwertyuiop","photo_url":"http://url"}',
            'reasons': [],
            'moderator_context': 'Ivanov',
            'context': '{"place_id":1234567}',
        },
        {
            'task_id': '123',
            'status': 'process',
            'queue': 'restapp_moderation_item',
            'payload': (
                '{"id":"1234595","value":'
                '"{\\"name\\":\\"name\\",\\"'
                'description\\":\\"new_descr\\"}"}'
            ),
            'reasons': [],
            'moderator_context': 'Petrov',
            'context': '{"place_id":1234567}',
        },
        {
            'task_id': '246',
            'status': 'process',
            'queue': 'restapp_moderation_item',
            'payload': (
                '{"id":"qwerty","value":"'
                '{\\"name\\":\\"name\\",\\'
                '"description\\":\\"new_de'
                'scr\\"}","modified_value"'
                ':"{\\"description\\":\\"new_descr\\"}"}'
            ),
            'reasons': [],
            'moderator_context': 'Petrov',
            'context': '{"place_id":1234567}',
        },
    ],
}

EMPTY_MENU_RESPONSE = {
    'is_success': True,
    'payload': {'menu': {'categories': [], 'items': []}},
}


async def test_menu_copy_post_no_access(taxi_eats_restapp_menu):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy',
        params={
            'target_place_id': TARGET_PLACE_ID,
            'source_place_id': PLACE_ID,
            'source_revision': REVISION,
        },
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': '1,2,3',
        },
        json={},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to target place is denied',
    }


async def test_menu_copy_post_no_access_source(taxi_eats_restapp_menu):
    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy',
        params={
            'target_place_id': TARGET_PLACE_ID,
            'source_place_id': PLACE_ID,
            'source_revision': REVISION,
        },
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': f'1,2,3,{TARGET_PLACE_ID}',
        },
        json={},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'Access to source place is denied',
    }


async def test_menu_copy_post_not_found(taxi_eats_restapp_menu, mockserver):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def mock_places_info(request):
        return {'payload': CORE_PLACES_INFO}

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy',
        params={
            'target_place_id': TARGET_PLACE_ID,
            'source_place_id': PLACE_ID,
            'source_revision': REVISION_NOT_FOUND,
        },
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': f'1,2,3,{PLACE_ID},{TARGET_PLACE_ID}',
        },
        json={},
    )

    assert mock_places_info.times_called == 1
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Menu with id 1080 not found',
    }


async def test_menu_copy_post_invalid_brand(
        taxi_eats_restapp_menu, mockserver,
):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def mock_places_info(request):
        changed = copy.deepcopy(CORE_PLACES_INFO)
        changed[1]['brand']['slug'] = 'CHANGED_brand'
        return {'payload': changed}

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy',
        params={
            'target_place_id': TARGET_PLACE_ID,
            'source_place_id': PLACE_ID,
            'source_revision': REVISION,
        },
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': f'1,2,3,{PLACE_ID},{TARGET_PLACE_ID}',
        },
        json={},
    )

    assert mock_places_info.times_called == 1
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Invalid target and source brands',
    }


@pytest.mark.experiments3(filename='moderation_flow_settings.json')
async def test_menu_copy_post_basic(
        taxi_eats_restapp_menu, mockserver, pg_get_menus,
):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def mock_places_info(request):
        return {'payload': CORE_PLACES_INFO}

    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def mock_place_menu(request):
        return EMPTY_MENU_RESPONSE

    @mockserver.json_handler('eats-moderation/moderation/v1/tasks/list')
    def mock_moderation(request):
        return MODERATION_RESPONSE

    response = await taxi_eats_restapp_menu.post(
        '/4.0/restapp-front/eats-restapp-menu/v1/menu/copy',
        params={
            'target_place_id': TARGET_PLACE_ID,
            'source_place_id': PLACE_ID,
            'source_revision': REVISION,
        },
        headers={
            'X-YaEda-PartnerId': PARTNER_ID,
            'X-YaEda-Partner-Places': f'1,2,3,{PLACE_ID},{TARGET_PLACE_ID}',
        },
        json={},
    )

    assert mock_places_info.times_called == 1
    assert mock_place_menu.times_called == 1
    assert mock_moderation.times_called == 1
    assert response.status_code == 200
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
                'cth27DbS0H_aZNL8gq_MGA',
                'user_generated',
                'applied',
                None,
            ),
            (
                11,
                None,
                109151,
                None,
                '11FxOYiYfpMxmANj4kGJzg',
                '11FxOYiYfpMxmANj4kGJzg',
                'external',
                'not_applicable',
                None,
            ),
            (
                12,
                11,
                109151,
                777,
                'Jly24hdsOplLFU1pwvXZRA',
                'G_BhZYF_kfrWcRKoOTIzHQ',
                'user_generated',
                'processing',
                None,
            ),
            (
                2,
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
                3,
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
                4,
                None,
                109154,
                None,
                'Jly24hdsOplLFU1pwvXZRA',
                'cth27DbS0H_aZNL8gq_MGA',
                'user_generated',
                'applied',
                None,
            ),
        )
    )
