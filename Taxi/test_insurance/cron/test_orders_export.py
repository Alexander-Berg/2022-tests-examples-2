import datetime

import pytest

from insurance.generated.cron import run_cron


@pytest.mark.skip(
    'testsuite does not support tests for "run_map" in YT: TAXIDATA-2789',
)
@pytest.mark.now('2020-10-04T10:05:00+03:00')
@pytest.mark.yt(dyn_table_data=['yt_orders.yaml'])
@pytest.mark.config(YT_REPLICA_ORDERS_MONTHLY='//home/taxi/orders_monthly')
async def test_orders_export(yt_apply, yt_client):
    tbl = '//home/taxi/orders_monthly/2020-10'

    yt_client.unmount_table(tbl, sync=True)
    yt_client.mount_table(tbl, sync=True)

    await run_cron.main(['insurance.crontasks.orders_export', '-t', '0'])


@pytest.mark.now('2020-10-17T10:05:00+03:00')
@pytest.mark.config(YT_REPLICA_ORDERS_MONTHLY='//home/taxi/orders_monthly')
async def test_orders_export_with_yt_patch(
        cron_context, patch, mockserver, load_json, mongodb, yt_client,
):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/list')
    def _tariff_zones(http_request):
        if http_request.query.get('cursor'):
            return {'zones': [], 'next_cursor': ''}
        return load_json('response_tariff.json')

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(*args, **kwargs):
        return 'mds_key'

    @patch('insurance.generated.cron.yt_wrapper.plugin.AsyncYTClient.run_map')
    async def _run_map(mapper, source_table, destination_table, spec):
        yt_client.write_table(destination_table, load_json('mock_job.json'))

    date_export = datetime.datetime(2020, 10, 16)

    orders_count = await cron_context.mongo.insured_orders_counts.find(
        {'date': date_export},
    ).to_list(None)
    assert not orders_count

    await run_cron.main(['insurance.crontasks.orders_export', '-t', '0'])

    exports = await cron_context.mongo.insured_orders_export.find(
        {'date': date_export},
    ).to_list(None)

    assert len(exports) == 2
    for export in exports:
        assert export['mds_key'] == 'mds_key'
        assert export['insurer_id'] in ['1', '2']

    orders_count = await cron_context.mongo.insured_orders_counts.find(
        {'date': date_export},
    ).to_list(None)

    assert len(orders_count) == 2
    for count in orders_count:
        assert (count['insurer_id'], count['orders_count']) in [
            ('1', 2),
            ('2', 1),
        ]
