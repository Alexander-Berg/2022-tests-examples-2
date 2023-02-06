import pytest

pytest_plugins = ['taxi_testsuite.plugins.mocks.mock_yt']


DB_ID, UUID = (
    '7ad36bc7560449998acbe2c57a75c293',
    '870fbf758122ac002c302cff682d3488',
)


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'global_policy_allowed': False,
        'policy_chunk_size': 100,
        'policy_max_connections': 4,
        'policy_use_results': False,
    },
)
async def test_feeds_bulk(web_app_client, mockserver):
    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': 'Driver',
            'channel': 'WALL',
            'yt_table': 'my_yt_table',
            'yt_test_table': 'my_yt_table_verification',
            'local_control': False,
            'global_control': False,
            'channel_info': {
                'channel_name': 'driver_wall',
                'feed_id': 'id',
                'send_at': '2020-09-11T10:00:00+03:00',
            },
            'extra_data': {},
        }

    response = await web_app_client.post(
        'v1/communication/bulk/new', json={'campaign_id': 2, 'group_id': 99},
    )
    assert response.status == 200
