import pytest


@pytest.mark.parametrize(
    'zone_type, expected_answer',
    [
        ('fan_zone', 'zones_list_fan_zone.json'),
        ('airport', 'zones_list_airport.json'),
    ],
)
async def test_zones_list(
        taxi_special_zones, mongodb, zone_type, expected_answer, load_json,
):
    response = await taxi_special_zones.get('zones/types?id=fan_zone')
    assert response.status_code == 200

    response = await taxi_special_zones.post(
        'zones/list',
        {'limit': 10, 'skip': 0, 'type': zone_type, 'show_deleted': False},
    )
    assert response.status_code == 200
    zones = response.json()['zones']
    assert sorted(zones, key=lambda x: x['id']) == load_json(expected_answer)


@pytest.mark.parametrize(
    'show_deleted, zones_expected', [(True, ['data4']), (False, [])],
)
async def test_zones_list_show_deleted(
        taxi_special_zones, mongodb, show_deleted, zones_expected,
):
    response = await taxi_special_zones.post(
        'zones/list',
        {
            'limit': 10,
            'skip': 0,
            'type': 'deleted',
            'show_deleted': show_deleted,
        },
    )
    assert response.status_code == 200
    zones = sorted(map(lambda x: x['id'], response.json()['zones']))
    assert zones == zones_expected


@pytest.mark.parametrize(
    'limit, skip, expected_num_zones',
    [(2, 0, 2), (1, 0, 1), (2, 1, 1), (2, 2, 0)],
)
async def test_zones_list_partial(
        taxi_special_zones,
        mongodb,
        load_json,
        limit,
        skip,
        expected_num_zones,
):
    response = await taxi_special_zones.post(
        'zones/list',
        {
            'limit': limit,
            'skip': skip,
            'type': 'fan_zone',
            'show_deleted': False,
        },
    )
    assert response.status_code == 200
    assert len(response.json()['zones']) == expected_num_zones


async def test_zones_list_bad_request(taxi_special_zones, mongodb):
    response = await taxi_special_zones.post('zones/list', {})
    assert response.status_code == 400
