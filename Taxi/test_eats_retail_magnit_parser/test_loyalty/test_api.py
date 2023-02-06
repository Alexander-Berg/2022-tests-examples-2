import pytest

EATS_CATALOG_STORAGE_RETRIEVE_PLACES_URL = (
    '/eats-catalog-storage/internal'
    '/eats-catalog-storage/v1/search/places/list'
)


@pytest.mark.parametrize('validate_status', [True, False])
async def test_create_card(
        loyalty_web_app_client,
        loyalty_method,
        magnit_loyalty_login_mock,
        magnit_loyalty_check_balance_mock,
        validate_status,
):
    magnit_loyalty_login_mock()
    magnit_loyalty_check_balance_mock(valid=validate_status)
    response = await loyalty_web_app_client.post(
        loyalty_method, json={'card_number': '4446578'},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['success'] == validate_status
    if not validate_status:
        assert response_data['reason']


@pytest.mark.config(
    EATS_RETAIL_MAGNIT_PARSER_LOYALTY_BRAND_INFO={
        '__default__': {
            'enable_loyalty': True,
            'loyalty': {
                'text': 'temp_test',
                'description': 'description',
                'icon_loyalty': 'icon_loyalty',
                'link_loyalty': 'link_loyalty',
                'description_title': 'description_title',
                'title': 'title',
                'mask': 'mask',
            },
        },
    },
)
async def test_get_card(
        mockserver,
        loyalty_web_app_client,
        loyalty_card,
        loyalty_method,
        load_json,
):
    @mockserver.json_handler(EATS_CATALOG_STORAGE_RETRIEVE_PLACES_URL)
    def _mock_eats_catalog_storage(request):
        return mockserver.make_response(
            status=200, json=load_json('catalog_storage.json'),
        )

    response = await loyalty_web_app_client.get(
        loyalty_method, params={'place_slug': 'brand_id'},
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data == {
        'card_number': loyalty_card,
        'enable_loyalty': True,
        'loyalty': {
            'text': 'temp_test',
            'description': 'description',
            'icon_loyalty': 'icon_loyalty',
            'link_loyalty': 'link_loyalty',
            'description_title': 'description_title',
            'title': 'title',
            'mask': 'mask',
        },
    }


@pytest.mark.config(
    EATS_RETAIL_MAGNIT_PARSER_LOYALTY_BRAND_INFO={
        '__default__': {'enable_loyalty': False},
    },
)
async def test_get_card_without_user(mockserver, web_app_client, load_json):
    @mockserver.json_handler(EATS_CATALOG_STORAGE_RETRIEVE_PLACES_URL)
    def _mock_eats_catalog_storage(request):
        return mockserver.make_response(
            status=200, json=load_json('catalog_storage.json'),
        )

    response = await web_app_client.get('/v1/loyalty?place_slug=brand_id')

    assert response.status == 200
    response_data = await response.json()
    assert response_data == {'enable_loyalty': False}


async def test_delete_card(
        loyalty_web_app_client, loyalty_card, loyalty_method,
):
    response = await loyalty_web_app_client.delete(
        loyalty_method, json={'card_number': loyalty_card},
    )
    assert response.status == 200
    response = await loyalty_web_app_client.get(
        loyalty_method, params={'place_slug': 'test'},
    )
    assert response.status == 200


async def test_update_card(
        loyalty_web_app_client, loyalty_card, loyalty_method,
):
    new_card_number = '9872225'
    response = await loyalty_web_app_client.post(
        loyalty_method, json={'card_number': new_card_number},
    )
    assert response.status == 200
    response = await loyalty_web_app_client.get(
        loyalty_method, params={'place_slug': 'test'},
    )
    response_data = await response.json()
    assert response_data == {
        'card_number': new_card_number,
        'enable_loyalty': False,
    }
