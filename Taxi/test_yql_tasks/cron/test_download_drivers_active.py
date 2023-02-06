import typing

import pytest

from yql_tasks.generated.cron import run_cron

EXPECTED_DATA_FILE = 'expected_data.json'


@pytest.mark.config(
    YQL_TASKS_DRIVERS_ACTIVE_TABLE='home/tests/drivers_actives',
    YQL_TASKS_PDA_DRIVERS_TABLE='home/tests/pda',
)
async def test_chyt_download_drivers_active(patch, load_json, mock_yt_call):
    # arrange
    @patch('client_chyt.components.AsyncChytClient.execute')
    # pylint: disable=W0612
    async def clickhouse_query(query_chyt: str) -> typing.List[dict]:
        return [{'last_ride': '2022-05-05'}]

    expected_data = load_json(EXPECTED_DATA_FILE)
    yt_handler = mock_yt_call([])

    # act
    await run_cron.main(
        ['yql_tasks.crontasks.download_drivers_active', '-t', '0'],
    )

    # assert
    yt_call = yt_handler.calls[0]
    assert clickhouse_query.calls == [expected_data['clickhouse_call']]
    assert list(yt_call['args'][1:]) == expected_data['yt_call_args']
    assert yt_call['kwargs'] == expected_data['yt_call_kwargs']
