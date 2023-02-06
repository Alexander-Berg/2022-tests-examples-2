async def test_get_depot_state(taxi_grocery_surge, mockserver):
    @mockserver.json_handler(
        '/grocery-dispatch-tracking/internal/'
        'grocery-dispatch-tracking/v1/depot-state',
    )
    def _depot_state(request):
        return {
            'orders': [
                {
                    'order_id': '6e32572a76624cec812c733b1fcb3cff-grocery',
                    'order_status': 'dispatching',
                    'courier_dbid_uuid': 'dbid0_uuid0',
                    'assembly_started': '2021-10-26T15:01:19+00:00',
                    'assembly_finished': '2021-10-26T15:05:19+00:00',
                },
            ],
            'performers': [
                {
                    'courier_dbid_uuid': 'dbid0_uuid777',
                    'performer_status': 'idle',
                },
            ],
        }

    response = await taxi_grocery_surge.post(
        '/internal/v1/surge/depot_state', params={'depot_id': '1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'orders': [
            {
                'order_id': '6e32572a76624cec812c733b1fcb3cff-grocery',
                'performer_id': 'dbid0_uuid0',
                'order_status': 'assembled',
                'dispatch_status': 'dispatching',
                'created': '2020-04-12T08:50:00+00:00',
                'assembly_started': '2021-10-26T15:01:19+00:00',
                'assembly_finished': '2021-10-26T15:05:19+00:00',
                'location': {'lat': 0.0, 'lon': 0.0},
                'cart_id': '0fe426b3-96ba-438e-a73a-d2cd70dbe3d9',
            },
        ],
        'performers': [
            {
                'performer_id': 'dbid0_uuid777',
                'performer_status': 'idle',
                'position': {'lat': 0.0, 'lon': 0.0},
                'transport_type': '',
            },
            {
                'performer_id': 'dbid0_uuid0',
                'performer_status': 'idle',
                'position': {'lat': 0.0, 'lon': 0.0},
                'transport_type': 'taxi',
            },
        ],
    }


async def test_get_depot_state_empty(taxi_grocery_surge, mockserver):
    @mockserver.json_handler(
        '/grocery-dispatch-tracking/internal/'
        'grocery-dispatch-tracking/v1/depot-state',
    )
    def _depot_state(request):
        return {'orders': [], 'performers': []}

    response = await taxi_grocery_surge.post(
        '/internal/v1/surge/depot_state', params={'depot_id': '1'},
    )
    assert response.status_code == 200
    assert response.json() == {'orders': [], 'performers': []}
