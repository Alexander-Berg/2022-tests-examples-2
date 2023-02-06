async def test_routing_launched(taxi_cargo_sdd, pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id, created_ts,
            routing_task_id
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T11:30:00+00:00'::TIMESTAMPTZ,
            'task_id_1'
        ),
        (
            'seg2', 1, 'corp_id',
            'routing_launched', 1, 'moscow',
            '2021-10-30T13:30:00+00:00'::TIMESTAMPTZ,
            'task_id_1'
        )
        """,
    )

    response = await taxi_cargo_sdd.post(
        '/admin/v1/segment/status',
        json={'segment_id': 'seg1'},
        headers={'Accept-Language': 'ru'},
    )
    assert response.json()['status'] == 'routing_launched'
    assert response.json()['status_description'] == 'ru routing launched'
    assert response.json()['routing_task_id'] == 'task_id_1'
    assert 'delivery_interval' not in response.json()
    assert 'dropped_location_reason' not in response.json()
    assert response.status_code == 200


async def test_waybill_building_awaited(taxi_cargo_sdd, pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id,
            delivery_interval_from, delivery_interval_to
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'waybill_building_awaited', 1, 'moscow',
            '2021-10-30T12:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T15:30:00+00:00'::TIMESTAMPTZ
        )
        """,
    )

    response = await taxi_cargo_sdd.post(
        '/admin/v1/segment/status',
        json={'segment_id': 'seg1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'waybill_building_awaited'
    assert response.json()['status_description'] == 'ru waybill awaited'
    assert 'routing_task_id' not in response.json()
    assert 'dropped_location_reason' not in response.json()
    assert response.json()['delivery_interval'] == {
        'from': '2021-10-30T12:30:00+00:00',
        'to': '2021-10-30T15:30:00+00:00',
    }


async def test_dropped_locations(taxi_cargo_sdd, pgsql):
    cursor = pgsql['cargo_sdd'].cursor()
    cursor.execute(
        """
        INSERT INTO cargo_sdd.segments(
            segment_id, revision, corp_client_id,
            status, waybill_building_version, zone_id,
            delivery_interval_from, delivery_interval_to,
            routing_task_id, dropped_location_reason
        )
        VALUES (
            'seg1', 1, 'corp_id',
            'dropped', 1, 'moscow',
            '2021-10-30T12:30:00+00:00'::TIMESTAMPTZ,
            '2021-10-30T15:30:00+00:00'::TIMESTAMPTZ,
            'task_id', 'reason'
        )
        """,
    )

    response = await taxi_cargo_sdd.post(
        '/admin/v1/segment/status',
        json={'segment_id': 'seg1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'dropped'
    assert response.json()['status_description'] == 'ru dropped'
    assert response.json()['routing_task_id'] == 'task_id'
    assert response.json()['dropped_location_reason'] == 'reason'
    assert response.json()['delivery_interval'] == {
        'from': '2021-10-30T12:30:00+00:00',
        'to': '2021-10-30T15:30:00+00:00',
    }


async def test_unknown_segment(taxi_cargo_sdd):
    response = await taxi_cargo_sdd.post(
        '/admin/v1/segment/status',
        json={'segment_id': 'seg1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 404
    assert response.json() == {'code': 'not_found', 'message': 'ru unknown'}
