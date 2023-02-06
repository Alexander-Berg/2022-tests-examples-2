import pytest


@pytest.mark.pgsql(
    'fleet_rent',
    queries=[
        """
    INSERT INTO rent.records
    (record_id, idempotency_token,
     owner_park_id, owner_serial_id, asset_type, asset_params,
     driver_id,
     begins_at_tz, ends_at_tz,
     charging_type,
     charging_starts_at_tz,
     creator_uid, created_at_tz,
     accepted_at_tz, acceptance_reason,
     terminated_at_tz, termination_reason,
     transfer_order_number)
    VALUES ('record_id1', 'idempotency_token1',
     'park_id', 1, 'other', '{"subtype": "misc"}',
     'driver_id',
     '2020-01-01+00', '2020-01-31+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00', 'Accepted by driver',
     NULL, NULL,
     'park_id_1'),
     ('record_id2', 'idempotency_token2',
     'park_id', 2, 'other', '{"subtype": "misc"}',
     'driver_id',
     '2020-01-01+00', '2020-01-02+00',
     'free',
     '2020-01-02+00',
     'creator_uid', '2020-01-01+00',
     '2020-01-01+00', 'Accepted by driver',
     '2020-01-02+00', 'Terminated by driver',
     'park_id_2')
        """,
    ],
)
@pytest.mark.now('2020-01-04T00:00:00')
async def test_get(web_app_client, mock_load_park_info, patch):
    @patch(
        'fleet_rent.services.confing3.Configs3Service.get_int_ext_rent_limits',
    )
    async def _get_int_ext_limits(park_info):
        return None, 2

    response = await web_app_client.get(
        '/v1/park/rents/used-limits', params={'park_id': 'park_id'},
    )
    assert response.status == 200
    data1 = await response.json()
    assert data1 == {
        'internal': {'used': 1},
        'external': {'used': 0, 'limit': 2},
    }
