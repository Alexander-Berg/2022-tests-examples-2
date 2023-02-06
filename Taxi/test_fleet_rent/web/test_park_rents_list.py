import pytest


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_list(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/list', params={'park_id': 'park_id'}, json={},
    )
    assert response.status == 200
    data = await response.json()
    rent_records = data['rent_records']
    assert len(rent_records) == 7


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.now('2020-03-01T00:00:00')
async def test_list_filtered(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/list',
        params={'park_id': 'park_id'},
        json={
            'time_range': {
                'from': '2020-01-04T00:00:00+00:00',
                'to': '2020-01-5T00:00:00+00:00',
                'applies_to': 'duration',
            },
            'states': ['new', 'ended'],
        },
    )
    assert response.status == 200
    data = await response.json()
    rent_records = data['rent_records']
    assert rent_records == [
        {
            'acceptance_reason': 'acceptance_reason',
            'accepted_at': '2020-01-01T03:00:00+03:00',
            'begins_at': '2020-01-01T03:00:00+03:00',
            'asset': {'type': 'other', 'subtype': 'misc'},
            'owner_park_id': 'park_id',
            'owner_serial_id': 2,
            'charging': {'type': 'free'},
            'charging_starts_at': '2020-01-01T03:00:00+03:00',
            'created_at': '2020-01-02T03:00:00+03:00',
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id2',
            'ends_at': '2020-01-10T03:00:00+03:00',
            'record_id': 'record_id2',
            'state': 'ended',
        },
        {
            'begins_at': '2020-01-01T03:00:00+03:00',
            'asset': {'type': 'other', 'subtype': 'misc'},
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'charging': {'type': 'free'},
            'charging_starts_at': '2020-01-01T03:00:00+03:00',
            'created_at': '2020-01-01T03:00:00+03:00',
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id1',
            'ends_at': '2020-01-10T03:00:00+03:00',
            'record_id': 'record_id1',
            'state': 'new',
        },
    ]


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.now('2020-03-01T00:00:00')
async def test_total(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/aggregations',
        params={'park_id': 'park_id'},
        json={
            'time_range': {
                'from': '2020-01-04T00:00:00+00:00',
                'to': '2020-01-5T00:00:00+00:00',
                'applies_to': 'duration',
            },
            'states': ['new', 'ended'],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'total_records': 2,
        'total_by_asset': {
            'car': 0,
            'other': {'chair': 0, 'deposit': 0, 'device': 0, 'misc': 2},
        },
    }


@pytest.mark.pgsql('fleet_rent', files=['asset_filter.sql'])
@pytest.mark.now('2020-03-01T00:00:00')
async def test_list_filter_asset_type(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/list',
        params={'park_id': 'park_id'},
        json={'asset': {'type': 'car', 'car_ids': ['car_id1']}},
    )
    assert response.status == 200
    data = await response.json()
    rent_records = data['rent_records']
    assert rent_records == [
        {
            'begins_at': '2020-01-01T03:00:00+03:00',
            'asset': {'type': 'car', 'car_id': 'car_id1'},
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'charging': {'type': 'free'},
            'charging_starts_at': '2020-01-01T03:00:00+03:00',
            'created_at': '2020-01-01T03:00:00+03:00',
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id1',
            'ends_at': '2020-01-10T03:00:00+03:00',
            'record_id': 'record_id1',
            'state': 'new',
        },
    ]


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.now('2020-03-01T00:00:00')
async def test_list_alt_trange(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/list',
        params={'park_id': 'park_id'},
        json={
            'time_range': {
                'from': '2020-01-01T00:00:00+00:00',
                'to': '2020-01-02T00:00:00+00:00',
                'applies_to': 'ends_at',
            },
        },
    )
    assert response.status == 200
    data = await response.json()
    rent_records = data['rent_records']
    assert rent_records == [
        {
            'begins_at': '2020-01-02T03:00:00+03:00',
            'asset': {'type': 'other', 'subtype': 'misc'},
            'owner_park_id': 'park_id',
            'owner_serial_id': 7,
            'charging': {'type': 'free'},
            'charging_starts_at': '2020-01-02T03:00:00+03:00',
            'created_at': '2020-01-01T03:00:00+03:00',
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id7',
            'record_id': 'record_id7',
            'state': 'park_terminated',
            'terminated_at': '2020-01-01T03:00:00+03:00',
            'termination_reason': 'Terminated by park, uid=123',
        },
    ]


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
@pytest.mark.now('2020-03-01T00:00:00')
async def test_list_by_driver(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/list',
        params={'park_id': 'park_id'},
        json={'driver_id': 'driver_id1'},
    )
    assert response.status == 200
    data = await response.json()
    rent_records = data['rent_records']
    assert rent_records == [
        {
            'begins_at': '2020-01-01T03:00:00+03:00',
            'asset': {'subtype': 'misc', 'type': 'other'},
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'charging': {'type': 'free'},
            'charging_starts_at': '2020-01-01T03:00:00+03:00',
            'created_at': '2020-01-01T03:00:00+03:00',
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id1',
            'ends_at': '2020-01-10T03:00:00+03:00',
            'record_id': 'record_id1',
            'state': 'new',
        },
    ]
    response2 = await web_app_client.post(
        '/v1/park/rents/aggregations',
        params={'park_id': 'park_id'},
        json={'driver_id': 'driver_id1'},
    )
    assert response2.status == 200
    data = await response2.json()
    assert data == {
        'total_records': 1,
        'total_by_asset': {
            'car': 0,
            'other': {'chair': 0, 'deposit': 0, 'device': 0, 'misc': 1},
        },
    }


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id, asset_type, asset_params,
 driver_id,
 begins_at_tz, ends_at_tz,
 charging_type, charging_starts_at_tz,
 creator_uid, created_at_tz,
 accepted_at_tz, acceptance_reason,
 rejected_at_tz, rejection_reason,
 terminated_at_tz, termination_reason,
 transfer_order_number)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,'other', '{"subtype": "misc"}',
        'driver_id1',
        '2020-01-01+00', '2020-01-10+00',
        'free', '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        '2020-01-01+00', 'acceptance_reason',
        NULL, NULL,
        '2020-01-02+00', 'Terminated by park, uid=123',
        'park_id_1'),
       ('record_id2', 'idempotency_token2',
        'park_id', 2,'other', '{"subtype": "misc"}',
        'driver_id2',
        '2020-01-01+00', '2020-01-10+00',
        'free', '2020-01-01+00',
        'creator_uid', '2020-01-02+00',
        '2020-01-01+00', 'acceptance_reason',
        NULL, NULL,
        '2020-01-02+00', 'Terminated by driver',
        'park_id_2')
        """,
    ],
)
@pytest.mark.now('2020-03-01T00:00:00')
async def test_list_terminated(web_app_client, mock_load_park_info):
    response = await web_app_client.post(
        '/v1/park/rents/list',
        params={'park_id': 'park_id'},
        json={'states': ['park_terminated']},
    )
    assert response.status == 200
    data = await response.json()
    rent_records = data['rent_records']
    assert rent_records == [
        {
            'acceptance_reason': 'acceptance_reason',
            'accepted_at': '2020-01-01T03:00:00+03:00',
            'asset': {'subtype': 'misc', 'type': 'other'},
            'begins_at': '2020-01-01T03:00:00+03:00',
            'charging': {'type': 'free'},
            'charging_starts_at': '2020-01-01T03:00:00+03:00',
            'created_at': '2020-01-01T03:00:00+03:00',
            'creator_uid': 'creator_uid',
            'driver_id': 'driver_id1',
            'ends_at': '2020-01-10T03:00:00+03:00',
            'owner_park_id': 'park_id',
            'owner_serial_id': 1,
            'record_id': 'record_id1',
            'state': 'park_terminated',
            'terminated_at': '2020-01-02T03:00:00+03:00',
            'termination_reason': 'Terminated by park, uid=123',
        },
    ]
    response2 = await web_app_client.post(
        '/v1/park/rents/aggregations',
        params={'park_id': 'park_id'},
        json={'states': ['park_terminated']},
    )
    assert response2.status == 200
    data2 = await response2.json()
    assert data2 == {
        'total_records': 1,
        'total_by_asset': {
            'car': 0,
            'other': {'chair': 0, 'deposit': 0, 'device': 0, 'misc': 1},
        },
    }


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
INSERT INTO rent.affiliations
(record_id,
 park_id, local_driver_id,
 original_driver_park_id, original_driver_id,
 creator_uid, created_at_tz,
 state)
VALUES ('affiliation_id',
        'park_id', 'driver_id2',
        'original_driver_park_id', 'original_driver_id',
        'creator_uid', '2020-01-01+00',
        'active')
        """,
        """
INSERT INTO rent.records
(record_id, idempotency_token,
 owner_park_id, owner_serial_id,
 asset_type, asset_params,
 driver_id,
 affiliation_id,
 begins_at_tz, ends_at_tz,
 charging_type, charging_starts_at_tz,
 creator_uid, created_at_tz,
 transfer_order_number)
VALUES ('record_id1', 'idempotency_token1',
        'park_id', 1,
        'other', '{"subtype": "misc"}',
        'driver_id1',
        NULL,
        '2020-01-01+00', '2020-01-10+00',
        'free', '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        'park_id_1'),
       ('record_id2', 'idempotency_token2',
        'park_id', 2,
        'other', '{"subtype": "misc"}',
        'driver_id1',
        NULL,
        '2020-01-01+00', '2020-01-10+00',
        'free', '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        'park_id_2'),
       ('record_id3', 'idempotency_token3',
        'park_id', 3,
        'other', '{"subtype": "misc"}',
        'driver_id2',
        'affiliation_id',
        '2020-01-01+00', '2020-01-10+00',
        'free', '2020-01-01+00',
        'creator_uid', '2020-01-01+00',
        'park_id_3')
        """,
    ],
)
@pytest.mark.now('2020-03-01T00:00:00')
@pytest.mark.parametrize(
    'is_external, amount', [[True, 1], [False, 2], [None, 3]],
)
async def test_filter_external(
        web_app_client, mock_load_park_info, is_external, amount,
):
    rent_response = await web_app_client.post(
        '/v1/park/rents/list',
        params={'park_id': 'park_id'},
        json={'is_external': is_external},
    )
    assert rent_response.status == 200
    rent_data = await rent_response.json()

    total_response = await web_app_client.post(
        '/v1/park/rents/aggregations',
        params={'park_id': 'park_id'},
        json={'is_external': is_external},
    )
    assert total_response.status == 200
    total_data = await total_response.json()

    assert (
        len(rent_data['rent_records']) == total_data['total_records'] == amount
    )
