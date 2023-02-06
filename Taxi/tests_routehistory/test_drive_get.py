import pytest


async def test_drive_get_simple(
        taxi_routehistory, routehistory_internal, load_json, pgsql,
):
    # Fill DB
    await routehistory_internal.call('WriteDrive', load_json('orders.json'))

    response = await taxi_routehistory.post(
        'routehistory/drive-get', {}, headers={'X-Yandex-UID': '123456'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
    # Wipe the db and ensure that we get an empty response
    cursor = pgsql['routehistory'].cursor()
    cursor.execute('DELETE FROM routehistory.drive_history')
    response = await taxi_routehistory.post(
        'routehistory/drive-get', {}, headers={'X-Yandex-UID': '123456'},
    )
    assert response.status_code == 200
    assert response.json() == {'results': []}


@pytest.mark.parametrize(
    'body, expected_limit',
    [
        ({'max_results': 1}, 'limit_one'),
        (
            {'max_results': 20, 'min_created': '2020-04-01T20:00:00+0000'},
            'limit_many',
        ),
        ({'min_created': '2020-04-01T20:00:00+0000'}, 'limit_many'),
    ],
)
async def test_drive_get_limits(
        taxi_routehistory,
        routehistory_internal,
        load_json,
        body,
        expected_limit,
):
    await routehistory_internal.call('WriteDrive', load_json('orders.json'))

    response = await taxi_routehistory.post(
        'routehistory/drive-get', body, headers={'X-Yandex-UID': '20000'},
    )
    assert response.status_code == 200
    assert (
        response.json()
        == load_json('expected_response_limits.json')[expected_limit]
    )


async def test_drive_get_no_limits(
        taxi_routehistory, routehistory_internal, load_json,
):
    await routehistory_internal.call('WriteDrive', load_json('orders.json'))

    response = await taxi_routehistory.post(
        'routehistory/drive-get', {}, headers={'X-Yandex-UID': '20000'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_no_limits.json')


@pytest.mark.config(
    ROUTEHISTORY_CACHES={
        'caches': {
            '__default__': {
                'bucket_count': 1000,
                'part_count': 10,
                'shift_period_ms': 100000,
            },
        },
    },
)
async def test_drive_get_cache(
        taxi_routehistory, routehistory_internal, load_json, pgsql,
):
    # Fill DB
    await routehistory_internal.call('WriteDrive', load_json('orders.json'))

    response = await taxi_routehistory.post(
        'routehistory/drive-get', {}, headers={'X-Yandex-UID': '123456'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')
    # Wipe the db and ensure that we get an empty response
    cursor = pgsql['routehistory'].cursor()
    cursor.execute('DELETE FROM routehistory.drive_history')
    response = await taxi_routehistory.post(
        'routehistory/drive-get', {}, headers={'X-Yandex-UID': '123456'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response.json')


@pytest.mark.parametrize(
    'body, exist',
    [({}, True), ({'origin': 'go'}, True), ({'origin': 'drive'}, False)],
)
async def test_drive_get_origin(
        taxi_routehistory, routehistory_internal, load_json, body, exist,
):
    await routehistory_internal.call('WriteDrive', load_json('orders.json'))

    response = await taxi_routehistory.post(
        'routehistory/drive-has-orders',
        body,
        headers={'X-Yandex-UID': '20000'},
    )
    assert response.status_code == 200
    assert response.json()['has_orders'] == exist
