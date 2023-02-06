import pytest

from . import utils


@pytest.mark.parametrize(
    'request_file, expected_response_file',
    [
        ('takeout_request.json', 'takeout_response.json'),
        ('takeout_request_nodata.json', 'takeout_response_nodata.json'),
    ],
)
async def test_takeout(
        taxi_routehistory,
        load_json,
        request_file,
        expected_response_file,
        pgsql,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))
    request = load_json(request_file)
    response = await taxi_routehistory.post('v1/takeout', request)
    assert response.status_code == 200
    assert response.json() == load_json(expected_response_file)


@pytest.mark.parametrize(
    'fill, request_file, expected_status',
    [
        (True, 'takeout_status_request_1.json', 'ready_to_delete'),
        (True, 'takeout_status_request_2.json', 'empty'),
        (False, 'takeout_status_request_1.json', 'empty'),
        (False, 'takeout_status_request_2.json', 'empty'),
    ],
)
async def test_takeout_status(
        taxi_routehistory,
        load_json,
        request_file,
        expected_status,
        pgsql,
        fill,
):
    if fill:
        utils.fill_db(
            pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'),
        )
    request = load_json(request_file)
    response = await taxi_routehistory.post('v1/takeout/status/', request)
    assert response.status_code == 200
    assert response.json() == {'data_state': expected_status}


@pytest.mark.parametrize(
    'request_file, expected_orders',
    [
        (
            'takeout_delete_request_1.json',
            ['99999999-0000-0000-0000-000000000001'],
        ),
    ],
)
async def test_takeout_delete(
        taxi_routehistory, load_json, request_file, expected_orders, pgsql,
):
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    utils.fill_db(cursor_ph, load_json('db_ph.json'))

    request = load_json(request_file)
    response = await taxi_routehistory.post('v1/takeout/delete/', request)
    assert response.status_code == 200

    records = utils.read_phone_history_db(cursor, cursor_ph).phone_history
    order_ids = list(map(lambda x: x['order_id'], records))
    assert order_ids == expected_orders


@pytest.mark.parametrize(
    'fill, request_file, expected_status',
    [
        (True, 'takeout_search_status_request_1.json', 'ready_to_delete'),
        (True, 'takeout_search_status_request_2.json', 'empty'),
        (True, 'takeout_search_status_request_3.json', 'ready_to_delete'),
        (False, 'takeout_search_status_request_1.json', 'empty'),
        (False, 'takeout_search_status_request_2.json', 'empty'),
    ],
)
async def test_takeout_search_status(
        taxi_routehistory,
        load_json,
        request_file,
        expected_status,
        pgsql,
        fill,
):
    if fill:
        utils.fill_db(
            pgsql['routehistory'].cursor(), load_json('db_search.json'),
        )
    request = load_json(request_file)
    response = await taxi_routehistory.post(
        'v1/takeout/search-status/', request,
    )
    assert response.status_code == 200
    assert response.json() == {'data_state': expected_status}


@pytest.mark.parametrize(
    'request_file, expected',
    [
        (
            'takeout_search_delete_request_1.json',
            [(111, 2020), (222, 2021), (222, 2022)],
        ),
        ('takeout_search_delete_request_2.json', [(222, 2021), (222, 2022)]),
        ('takeout_search_delete_request_3.json', [(111, 2020)]),
        ('takeout_search_delete_request_4.json', []),
    ],
)
async def test_takeout_search_delete(
        taxi_routehistory, load_json, request_file, expected, pgsql,
):
    cursor = pgsql['routehistory'].cursor()
    utils.fill_db(cursor, load_json('db_search.json'))

    request = load_json(request_file)
    response = await taxi_routehistory.post(
        'v1/takeout/search-delete/', request,
    )
    assert response.status_code == 200
    cursor.execute(
        'SELECT yandex_uid, created '
        'FROM routehistory.search_history '
        'ORDER BY yandex_uid, created',
    )
    search_ids = utils.convert_pg_result(cursor.fetchall())
    search_ids = list(map(lambda x: (x[0], x[1].year), search_ids))
    assert search_ids == expected
