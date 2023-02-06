from tests_fleet_parks import utils


async def test_ok(taxi_fleet_parks):
    headers = {'X-Ya-Service-Ticket': utils.SERVICE_TICKET}

    response = await taxi_fleet_parks.post(
        'v1/cities/retrieve_by_name',
        json={'consumer': 'test', 'name_in_set': ['city1']},
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'cities_by_name': [
            {
                'cities': [
                    {
                        'data': {
                            'country_id': 'cid1234',
                            'lat': 10.0,
                            'lon': 20.0,
                            'name': 'city1',
                            'tz': 3,
                            'uuid': 'CITY1',
                            'zoom': 10,
                            'geoarea': 'geoarea1',
                        },
                        'id': '123456789012345678901234',
                        'revision': '0_1234567_1',
                    },
                ],
                'name': 'city1',
            },
        ],
    }
