import json


URL = '/umlaas-eats/v1/next-card'


async def test_next_card_default(taxi_umlaas_eats, load):

    request_body = load('request.json')
    response = await taxi_umlaas_eats.post(URL, data=request_body)
    assert response.status == 200
    data = json.loads(response.text)

    assert data == {
        'card_id': 'moloko_12_12',
        'card_type': 'menu_item',
        'content': {'id': 12, 'name': 'Молоко', 'place_id': 12},
        'context': {
            'card_type': 'menu_item',
            'category': {'name': 'moloko', 'score': 999},
            'content': {'id': 12, 'name': 'Молоко', 'place_id': 12},
            'score': 999,
        },
    }
