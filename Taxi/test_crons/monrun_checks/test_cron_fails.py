import pytest

from crons.crontasks import generate_monrun_checks
from crons.generated.cron import run_monrun


@pytest.mark.parametrize(
    'dev_team,expected_result',
    [
        (
            'team_1',
            '2; Following tasks are in status CRIT: task_2 (triggered by time)'
            '. Following tasks are in status WARN: task_1. '
            'Services: https://tariff-editor-unstable.taxi.tst.yandex-team.ru'
            '/dev/cron?service=service_2, '
            'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/dev/cron'
            '?service=service_1',
        ),
        (
            'team_2',
            f'1; Following tasks are in status WARN: task_3. '
            'Services: https://tariff-editor-unstable.taxi.tst.yandex-team.ru'
            '/dev/cron?service=service_3',
        ),
        ('team_3', '0; OK'),
    ],
)
async def test_cron_fails(dev_team, expected_result):
    base_args = [
        arg.format(team_name='platform')
        for arg in generate_monrun_checks.MONRUN_COMMAND_BASE_ARGS
    ]
    res = await run_monrun.main(base_args + ['--dev-team', dev_team])
    assert res == expected_result
