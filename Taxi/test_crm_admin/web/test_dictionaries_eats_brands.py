# pylint: disable=unused-variable,unused-argument

import itertools

from aiohttp import web
import pytest

from crm_admin.api import v1_dictionaries_eats_brands_get


@pytest.mark.parametrize(
    'business_types', [None, ['restaurant'], ['restaurant', 'shop']],
)
async def test_eats_brands(web_app_client, mock_eats_brands, business_types):
    all_brands = {
        i
        + 1: {
            'id': i + 1,
            'name': 'kf' + chr(ord('c') + i),
            'business_type': 'restaurant' if i % 3 != 1 else 'shop',
        }
        for i in range(10)
    }

    @mock_eats_brands('/brands/v1/search')
    async def search(request):
        items = [
            {'id': item['id'], 'name': item['name']}
            for item in all_brands.values()
        ]
        pagination = {
            **request.json['pagination'],
            'items': len(items),
            'page_count': 1,
            'total_items': len(items),
        }
        return web.json_response(
            {'items': items, 'pagination': pagination}, status=200,
        )

    @mock_eats_brands('/brands/v1/find-by-ids')
    async def find_by_ids(request):
        return web.json_response(
            {
                'brands': [
                    all_brands[brand_id] for brand_id in request.json['ids']
                ],
            },
            status=200,
        )

    params = params = {'name': 'kfc'}
    if business_types:
        params['business_types'] = ','.join(business_types)
    response = await web_app_client.get(
        '/v1/dictionaries/eats_brands', params=params,
    )
    assert response.status == 200

    items = await response.json()

    expected = all_brands.values()
    if business_types:
        expected = filter(
            lambda item: item['business_type'] in business_types, expected,
        )
    expected = itertools.islice(
        expected, v1_dictionaries_eats_brands_get.NUM_SUGGESTIONS,
    )
    expected = map(
        lambda item: {'label': item['name'], 'value': item['id']}, expected,
    )

    assert list(expected) == items
