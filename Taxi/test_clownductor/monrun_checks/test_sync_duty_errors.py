import pytest

from clownductor.generated.cron import run_monrun

STATISTICS_METRIC = 'crontask.clownductor.sync_duty_admin.error'
LINK = 'See more /dev/cron/clownductor-crontasks-sync_duty_admins'


@pytest.mark.parametrize(
    ['value', 'expected'],
    [
        (0, f'0; Found 0 errors. {LINK}'),
        (1, f'1; WARN: Found 1 errors. {LINK}'),
        (2, f'2; CRIT: Found 2 errors. {LINK}'),
    ],
)
@pytest.mark.now('2019-10-19T12:08:12')
async def test_sync_duty_admins(mockserver, value, expected):
    @mockserver.json_handler('/statistics/v1/metrics/list')
    def _handler(request):
        assert request.method == 'POST'
        assert request.json == {
            'metric_names': [STATISTICS_METRIC],
            'service': 'clownductor_cron',
            'interval': 300,
            'timestamp': '2019-10-19T15:08:12+03:00',
        }
        return {'metrics': [{'name': STATISTICS_METRIC, 'value': value}]}

    msg = await run_monrun.run(['clownductor.monrun_checks.sync_duty_errors'])
    assert _handler.times_called == 1
    assert msg == expected
