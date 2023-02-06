import uuid

import pytest

EATS_CATALOG_STORAGE_RETRIEVE_PLACES_URL = (
    '/eats-catalog-storage/internal'
    '/eats-catalog-storage/v1/search/places/list'
)


@pytest.mark.config(
    EATS_RETAIL_MAGNIT_PARSER_LOYALTY_BRAND_INFO={
        'slug_name': {
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
@pytest.mark.parametrize(
    'request_data, code, file_name, has_calls',
    [
        (
            {
                'eater_id': uuid.uuid4().hex,
                'order_nr': uuid.uuid4().hex,
                'place_id': '123456',
            },
            200,
            'catalog_storage.json',
            True,
        ),
        (
            {
                'eater_id': uuid.uuid4().hex,
                'order_nr': uuid.uuid4().hex,
                'place_id': '1234567',
            },
            200,
            'wrong_catalog_storage.json',
            False,
        ),
    ],
)
async def test_order_loyalty(
        mockserver,
        load_json,
        web_app_client,
        web_context,
        request_data,
        code,
        stq,
        file_name,
        has_calls,
):
    @mockserver.json_handler(EATS_CATALOG_STORAGE_RETRIEVE_PLACES_URL)
    def _mock_eats_catalog_storage(request):
        return mockserver.make_response(status=code, json=load_json(file_name))

    response = await web_app_client.post(
        '/v1/order_loyalty', json=request_data,
    )

    assert response.status == code
    assert stq.eats_retail_magnit_parser_loyalty.has_calls == has_calls
