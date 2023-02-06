import datetime

import pytest

from sticker.monrun import too_many_failed


REAL_FAILED_NUM = 3


@pytest.mark.parametrize(
    'check_config,expected_result',
    [
        (
            {
                'too_many_failed': {'warn': 4, 'crit': 7},
                'too_many_failed_via_sender': {'warn': 10, 'crit': 10},
            },
            '0; OK: not too many failed mail requests in queue',
        ),
        (
            {
                'too_many_failed': {'warn': 2, 'crit': 10},
                'too_many_failed_via_sender': {'warn': 10, 'crit': 10},
            },
            (
                '1; WARN: there are too many failed mail requests: 3 >= 2 '
                '(too_many_failed)'
            ),
        ),
        (
            {
                'too_many_failed': {'warn': 1, 'crit': 3},
                'too_many_failed_via_sender': {'warn': 10, 'crit': 10},
            },
            (
                '2; CRIT: there are too many failed mail requests: 3 >= 3 '
                '(too_many_failed)'
            ),
        ),
        (
            {
                'too_many_failed': {'warn': 1, 'crit': 3},
                'too_many_failed_via_sender': {'warn': 1, 'crit': 1},
            },
            (
                '2; CRIT: there are too many failed mail requests: 1 >= 1 '
                '(too_many_failed_via_sender)'
            ),
        ),
    ],
)
@pytest.mark.now(datetime.datetime(2019, 1, 2, 9, 0, 0).isoformat())
async def test_too_old_in_queue(
        monkeypatch, cron_context, check_config, expected_result,
):
    monkeypatch.setitem(
        cron_context.config.STICKER_MONRUN_SETTINGS,
        'too_many_failed',
        check_config['too_many_failed'],
    )
    monkeypatch.setitem(
        cron_context.config.STICKER_MONRUN_SETTINGS,
        'too_many_failed_via_sender',
        check_config['too_many_failed_via_sender'],
    )

    check_result = await too_many_failed.run_check(cron_context, None)
    assert check_result == expected_result
