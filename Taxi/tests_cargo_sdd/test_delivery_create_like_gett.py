async def test_happy_path(taxi_cargo_sdd, pgsql):
    request_body = {
        'some_field': 'some value',
        'mb_points': [
            {'coordinates': {'lon': 37.1, 'lat': 55.1}},
            {'coordinates': {'lon': 37.5, 'lat': 55.5}},
        ],
    }
    corp_client_id = '99999999829e48cca458b5feb1617777'

    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery/create-raw',
        json=request_body,
        headers={'X-B2B-Client-Id': corp_client_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT request_body, corp_client_id
        FROM cargo_sdd.gett_like_requests
        ORDER BY id
        """,
    )
    assert cursor.fetchall() == [(request_body, corp_client_id)]
    # hashlib.md5(json.dumps(
    # request_body, sort_keys=True).encode('utf-8')).hexdigest()


async def test_double_request(taxi_cargo_sdd, pgsql):
    request_body = {
        'some_field': 'some value',
        'mb_points': [
            {'coordinates': {'lon': 37.1, 'lat': 55.1}},
            {'coordinates': {'lon': 37.5, 'lat': 55.5}},
        ],
    }
    corp_client_id = '99999999829e48cca458b5feb1617777'

    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery/create-raw',
        json=request_body,
        headers={'X-B2B-Client-Id': corp_client_id},
    )
    assert response.status_code == 200
    assert response.json() == {}

    response = await taxi_cargo_sdd.post(
        '/api/integration/v1/same-day/delivery/create-raw',
        json=request_body,
        headers={'X-B2B-Client-Id': corp_client_id},
    )
    assert response.status_code == 409
    assert response.json() == {}

    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        SELECT request_body, corp_client_id
        FROM cargo_sdd.gett_like_requests
        ORDER BY id
        """,
    )
    assert cursor.fetchall() == [(request_body, corp_client_id)]
