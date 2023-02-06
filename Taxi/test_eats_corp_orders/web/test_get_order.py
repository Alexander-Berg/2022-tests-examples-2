import pytest


@pytest.mark.pgsql(
    'eats_corp_orders', files=['terminal_tokens.sql', 'orders.sql'],
)
async def test_get_order(web_app_client, mock_eats_catalog_storage, load_json):
    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/search/places/list',
    )
    async def _search_place(request):
        place_id = int(request.json['place_ids'][0])
        res = load_json('eats-catalog-storage.json')
        res['places'][0]['place_id'] = place_id
        return res

    response = await web_app_client.get(
        '/v1/order', params={'order_id': 'order_id'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'order_id': 'order_id',
        'status': 'new',
        'items': [
            {'price': '60', 'quantity': '1', 'title': 'Шоколад Bounty 55г'},
        ],
        'place_id': '146',
        'place_name': 'place_name',
        'place_address': {'city': 'city', 'short': 'short'},
        'created_at': '2020-02-02T03:00:00+03:00',
    }
