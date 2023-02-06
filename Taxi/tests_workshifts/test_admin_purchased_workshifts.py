import pytest


@pytest.mark.parametrize(
    'park_id, driver_profile_id, last_revision, limit, expected_code, '
    'expected_response',
    [
        ('dbid1', 'uuid1', None, None, 200, 'expected_response1.json'),
        ('dbid1', 'uuid2', None, None, 200, 'expected_response2.json'),
        ('dbid1', 'uuid1', None, 1, 200, 'expected_response3.json'),
        ('dbid1', 'uuid1', '1579598835_95', 2, 200, 'expected_response4.json'),
        ('dbid1', 'uuid1', '1579598835_', 2, 400, 'expected_response5.json'),
        (
            'dbid1',
            'uuid1',
            '157959883595',
            222,
            400,
            'expected_response6.json',
        ),
    ],
)
async def test_admin_purchased_workshifts(
        taxi_workshifts,
        load_json,
        park_id,
        driver_profile_id,
        last_revision,
        limit,
        expected_code,
        expected_response,
):
    params = {'order': 'desc'}
    if last_revision:
        params['revision'] = last_revision
    if limit:
        params['limit'] = limit

    response = await taxi_workshifts.post(
        '/admin/v1/purchased-workshifts',
        params=params,
        json={'park_id': park_id, 'driver_profile_id': driver_profile_id},
    )

    assert response.status_code == expected_code
    assert response.json() == load_json('response/' + expected_response)


@pytest.mark.parametrize(
    'order, response1, response2, response3',
    [
        (
            'desc',
            'expected_response7.json',
            'expected_response8.json',
            'expected_response9.json',
        ),
        (
            'asc',
            'expected_response10.json',
            'expected_response11.json',
            'expected_response12.json',
        ),
    ],
)
async def test_admin_purchased_workshifts_chain(
        taxi_workshifts, load_json, order, response1, response2, response3,
):
    async def get_purchased_workshifts(last_revision=None):
        params = {'limit': 2, 'order': order}
        if last_revision:
            params['revision'] = last_revision
        response = await taxi_workshifts.post(
            '/admin/v1/purchased-workshifts',
            params=params,
            json={'park_id': 'dbid1', 'driver_profile_id': 'uuid1'},
        )

        assert response.status_code == 200
        return response.json()

    response_json = await get_purchased_workshifts()
    assert response_json == load_json('response/' + response1)

    response_json = await get_purchased_workshifts(response_json['revision'])
    assert response_json == load_json('response/' + response2)

    response_json = await get_purchased_workshifts(response_json['revision'])
    assert response_json == load_json('response/' + response3)
