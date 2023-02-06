import pytest


HEADERS = {'X-Yandex-UID': '1'}


def check_response(resp, num_shuttles):
    assert 'vehicles' in resp
    assert len(resp['vehicles']) == num_shuttles
    num_booked = 0
    for vehicle in resp['vehicles']:
        vehicle_required_keys = [
            'id',
            'name',
            'path',
            'route_id',
            'state',
            'type',
        ]
        assert len(vehicle_required_keys) == len(vehicle.keys())
        for key in vehicle.keys():
            assert key in vehicle_required_keys
            if key == 'state' and vehicle[key] == 'booked':
                num_booked += 1
            vehicle_required_keys.remove(key)
        assert not vehicle_required_keys

        for path_item in vehicle['path']:
            path_item_required_keys = ['azimuth', 'position', 'time']
            assert len(path_item_required_keys) == len(path_item.keys())
            for key in path_item.keys():
                assert key in path_item_required_keys
                path_item_required_keys.remove(key)
            assert not path_item_required_keys
    assert num_booked == num_shuttles


@pytest.mark.parametrize('route_available', [False, True])
async def test_simple(
        taxi_masstransit, load_json, experiments3, route_available,
):
    experiments3.add_experiments_json(
        load_json(
            'add_shuttle_exp.json'
            if route_available
            else 'add_shuttle_exp_restricted.json',
        ),
    )

    response = await taxi_masstransit.post(
        '/4.0/masstransit/v1/vehicles',
        {'bbox': [37.0, 55.0, 38.0, 56.0], 'shuttle_ids': ['shuttle_2']},
        headers=HEADERS,
    )

    assert response.status_code == 200
    response_data = response.json()
    expected_ids = ['shuttle_2'] if route_available else []
    check_response(response_data, len(expected_ids))
    vehicle_ids = [v['id'] for v in response_data['vehicles']]
    for i in vehicle_ids:
        assert i in expected_ids
        expected_ids.remove(i)
    assert not expected_ids
