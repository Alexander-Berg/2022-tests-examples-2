import datetime
import json

from aiohttp import web
import pytest

from atlas_etl.generated.cron import run_cron


NOW = datetime.datetime(2021, 4, 27, 16, 30, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.scooter_orders': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_scooter_orders(
        clickhouse_client_mock, load_json, patch, mock_replication, db,
):
    read_queue_response = load_json('scooter_orders_read_queue.json')
    confirm_id = '0624b6c28af0412582c24345792de98f'
    rule_name = 'scooter_analytics_compiled_rides'
    targets = ['scooter_analytics_compiled_rides_atlas_ext']
    read_count = 0

    @mock_replication(f'/v1/queue/retrieve_partitions/{rule_name}')
    async def _retrieve_partitions_handler(
            request,
    ):  # pylint: disable=unused-variable
        return web.json_response(data={'queue_partitions': None}, status=200)

    @mock_replication(f'/v1/queue/read/{rule_name}')
    async def _queue_read_handler(request):  # pylint: disable=unused-variable
        nonlocal read_count
        if read_count:
            return web.json_response(
                data={
                    'confirm_id': '123',
                    'items': [],
                    'count': 0,
                    'last_upload_ts': '',
                    'output_format': 'json',
                    'try_next_read_after': 60,
                },
            )
        read_count += 1
        assert request.json == {'targets': targets, 'limit': 10000}

        return web.json_response(
            data={
                'confirm_id': confirm_id,
                'items': [
                    {
                        'data': json.dumps(read_queue_response),
                        'id': '1',
                        'upload_ts': (
                            NOW - datetime.timedelta(minutes=2)
                        ).isoformat(),
                    },
                ],
                'count': 1,
                'last_upload_ts': (
                    NOW - datetime.timedelta(minutes=1)
                ).isoformat(),
                'output_format': 'json',
                'try_next_read_after': None,
            },
            status=200,
        )

    @mock_replication(f'/v1/queue/confirm/{rule_name}')
    async def _confirm_read_response(
            request,
    ):  # pylint: disable=unused-variable
        assert request.json == {'targets': targets, 'confirm_id': confirm_id}

        return web.json_response(data={'confirm_id': 'ololo'}, status=200)

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        data = kwargs.get('params')
        expected_ch_insert = load_json('scooter_orders_ch_insert.json')
        assert data == expected_ch_insert
        return len(data)

    await run_cron.main(['atlas_etl.crontasks.scooter_orders', '-t', '0'])

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.scooter_orders'},
    )

    assert str(etl_info['last_upload_date']) == '2021-04-27 16:27:19'
