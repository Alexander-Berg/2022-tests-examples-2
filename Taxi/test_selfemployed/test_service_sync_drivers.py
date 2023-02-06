import pytest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO se.nalogru_phone_bindings
            (phone_pd_id, inn_pd_id, status, bind_request_id)
        VALUES ('PHONE_PD_ID', 'INN_PD_ID', 'COMPLETED', NULL);
        INSERT INTO se.finished_profiles
            (park_id, contractor_profile_id, phone_pd_id, inn_pd_id)
        VALUES ('p1', 'd1', 'PHONE_PD_ID', 'INN_PD_ID');
        """,
    ],
)
async def test_service_sync_drivers(se_client, se_web_context):
    await se_client.post(
        '/selfemployed/service/v1/sync/driver',
        json={
            'original_park_id': 'p1',
            'original_driver_id': 'd1',
            'mapped_park_id': 'p2',
            'mapped_driver_id': 'd2',
        },
    )
    profile_record = await se_web_context.pg.main_master.fetchrow(
        'SELECT phone_pd_id FROM se.finished_profiles\n'
        'WHERE (park_id, contractor_profile_id) = ($1, $2)',
        'p2',
        'd2',
    )
    assert profile_record['phone_pd_id'] == 'PHONE_PD_ID'
