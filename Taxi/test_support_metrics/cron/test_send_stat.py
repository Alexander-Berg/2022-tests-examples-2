# pylint: disable=redefined-outer-name, unused-variable
from aiohttp import web
import pytest

from support_metrics.generated.cron import run_cron


STAT_1 = {
    'action': 'create',
    'count': 25,
    'fielddate': '2019-07-02T15:00:01',
    'in_addition': '1',
    'line': 'first',
    'login': 'superuser',
    'new_line': 'null',
}
STAT_2 = {
    'action': 'forward',
    'count': 22,
    'fielddate': '2019-07-02T15:00:02',
    'in_addition': '0',
    'line': 'first',
    'login': 'support_1',
    'new_line': 'second',
}
STAT_3 = {
    'action': 'close',
    'count': 32,
    'fielddate': '2019-07-02T15:00:03',
    'in_addition': '0',
    'line': 'first',
    'login': 'support_2',
    'new_line': 'null',
}


@pytest.mark.parametrize(
    'expected_result', [({'data': [STAT_1, STAT_2, STAT_3]})],
)
async def test_send_stat(cron_context, mock_upload_stat, expected_result):
    @mock_upload_stat('/_api/report/data', prefix=True)
    def handler(request):
        assert request.headers['Authorization'] == 'OAuth ROBOT_STAT'
        assert list(request.json.keys()) == ['data']
        print(expected_result, type(expected_result))
        data = sorted(request.json['data'], key=lambda d: d['fielddate'])
        assert data == expected_result['data']
        return web.json_response({})

    await run_cron.main(
        ['support_metrics.crontasks.send_stat_to_stat', '-t', '0'],
    )
    db = cron_context.postgresql.support_metrics[0]
    result = await db.primary_fetch(
        'SELECT * FROM events.aggregated_stat ORDER BY id ASC',
    )
    for record in result:
        assert record['sent']


@pytest.mark.parametrize(
    'expected_result',
    [([{'data': [STAT_1]}, {'data': [STAT_2]}, {'data': [STAT_3]}])],
)
@pytest.mark.config(SUPPORT_METRICS_STAT_BULK_SIZE=1)
async def test_send_parts(cron_context, mock_upload_stat, expected_result):
    calls = 0

    @mock_upload_stat('/_api/report/data', prefix=True)
    def handler(request):
        nonlocal calls
        assert request.headers['Authorization'] == 'OAuth ROBOT_STAT'
        assert list(request.json.keys()) == ['data']
        data = sorted(request.json['data'], key=lambda d: d['fielddate'])
        assert data == expected_result[calls]['data']
        calls += 1
        return web.json_response({})

    await run_cron.main(
        ['support_metrics.crontasks.send_stat_to_stat', '-t', '0'],
    )
    db = cron_context.postgresql.support_metrics[0]
    result = await db.primary_fetch(
        'SELECT * FROM events.aggregated_stat ORDER BY id ASC',
    )
    for record in result:
        assert record['sent']
