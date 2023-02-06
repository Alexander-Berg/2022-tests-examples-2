import json

import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Item:ClientGeoSharing:TrackIds:999:888',
        {
            'order0': json.dumps({'track_id': 'user0'}),
            'order1': json.dumps({'track_id': 'user1'}),
            'order2': json.dumps({'track_id': 'user2'}),
            'order3': json.dumps({'track_id': 'user3'}),
        },
    ],
)
async def test_client_locations(taxi_contractor_orders_polling, mockserver):
    @mockserver.json_handler('/geosharing/geosharing/v1/getpos')
    def _geosharing(request):
        user_id = request.json['user_id']
        if user_id in ['user0', 'user1']:
            return {
                'result': 'ok',
                'user_position': {
                    'position': [37.5, 55.7],
                    'accuracy': 15,
                    'retrieved_at': '2020-10-10T21:00:01Z',
                },
            }
        if user_id == 'user2':
            return mockserver.make_response(status=500, json={})
        return {'result': 'error'}

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['client_locations'] == [
        {
            'location': {
                'accuracy': 15.0,
                'lat': 55.7,
                'lon': 37.5,
                'timestamp': '2020-10-10T21:00:01.000000Z',
            },
            'order_id': 'order0',
        },
        {
            'location': {
                'accuracy': 15.0,
                'lat': 55.7,
                'lon': 37.5,
                'timestamp': '2020-10-10T21:00:01.000000Z',
            },
            'order_id': 'order1',
        },
    ]
