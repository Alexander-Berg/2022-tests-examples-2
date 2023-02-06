import datetime

import pytest

from atlas_etl.generated.cron import run_cron

NOW = datetime.datetime(2021, 3, 10, 6, 17, 12, 135)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.chatterbox_stats': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_chatterbox_stats(
        clickhouse_client_mock,
        mock_support_metrics,
        load_json,
        fix_ch_insert_data,
        patch,
):
    chatterbox_data = load_json('chatterbox_data.json')

    @mock_support_metrics('/v1/chatterbox/raw_stats/list')
    async def handle(request):  # pylint: disable=unused-variable
        created_ts = request.query['created_ts']
        return chatterbox_data.get(created_ts, [])

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        data = kwargs.get('params')
        data = fix_ch_insert_data(data)
        expected_ch_insert = load_json('expected_ch_insert.json')
        assert data == expected_ch_insert
        return len(data)

    await run_cron.main(['atlas_etl.crontasks.chatterbox_stats', '-t', '0'])
