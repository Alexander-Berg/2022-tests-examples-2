import pytest


@pytest.mark.config(
    ROUTER_SELECT=[
        {'routers': ['yamaps', 'tigraph']},
        {
            'ids': ['moscow'],
            'routers': ['linear-fallback', 'yamaps', 'tigraph'],
        },
    ],
)
@pytest.mark.now('2021-11-17T12:23:00+00:00')
async def test_route_info(taxi_candidates, driver_positions, mockserver):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55.1, 35.1]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55.1, 35.1]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55.1, 35.1]},
        ],
    )

    @mockserver.json_handler('fleet-orders-guarantee/v1/guaranteed/list')
    def _mock(request):
        return {
            'orders': [
                {
                    'id': 'order_id1',
                    'contractor_udid': '56f968f07c0aa65c44998e4b',
                    'created_at': '2021-11-17T12:23:00+00:00',
                    'booked_at': '2021-11-17T12:27:00+00:00',
                    'location_from': [55.1, 35.1],
                    'locations_to': [[13.424845, 52.512714]],
                    'lookup_triggered': True,
                },
                {
                    'id': 'order_id2',
                    'contractor_udid': '56f968f07c0aa65c44998e4e',
                    'created_at': '2021-11-17T12:23:00.892+00:00',
                    'booked_at': '2021-11-17T13:33:00+00:00',
                    'location_from': [55.1, 35.1],
                    'locations_to': [[13.424845, 52.512714]],
                    'lookup_triggered': False,
                },
                {
                    'id': 'order_id3',
                    'contractor_udid': '56f968f07c0aa65c44998e4f',
                    'created_at': '2021-11-17T12:23:00.892+00:00',
                    'booked_at': '2021-11-17T13:57:00+00:00',
                    'location_from': [55.1, 35.1],
                    'locations_to': [[13.424845, 52.512714]],
                    'lookup_triggered': False,
                },
            ],
        }

    request_body = {
        'geoindex': 'kdtree',
        'limit': 100,
        'filters': ['product/booked_contractor'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'max_route_time': 3600,
        'max_route_distance': 100000,
        'order': {
            'calc': {'time': 240.0},
            'request': {
                'source': {'geopoint': [55.2, 35]},
                'destinations': [{'geopoint': [55, 35]}],
            },
        },
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid3'
