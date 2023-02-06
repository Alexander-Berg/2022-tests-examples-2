import datetime

import pytest

from sticker.monrun import too_long_in_status


@pytest.mark.parametrize(
    'check_config,expected_fail_statuses',
    [
        (
            [
                {'status': 'PENDING', 'warn': 58, 'crit': 80},
                {'status': 'PROCESSING', 'warn': 118, 'crit': 140},
            ],
            {'PENDING': ('warn', 1), 'PROCESSING': ('warn', 1)},
        ),
        (
            [
                {'status': 'PENDING', 'warn': 1, 'crit': 58},
                {'status': 'PROCESSING', 'warn': 140, 'crit': 150},
            ],
            {'PENDING': ('crit', 1)},
        ),
        (
            [
                {'status': 'PENDING', 'warn': 1, 'crit': 58, 'crit_count': 2},
                {'status': 'PROCESSING', 'warn': 140, 'crit': 150},
            ],
            {'PENDING': ('warn', 2)},
        ),
        (
            [
                {
                    'status': 'PENDING',
                    'warn': 1,
                    'crit': 58,
                    'crit_count': 2,
                    'warn_count': 3,
                },
                {'status': 'PROCESSING', 'warn': 140, 'crit': 150},
            ],
            {},
        ),
        (
            [
                {'status': 'PENDING', 'warn': 60, 'crit': 70},
                {'status': 'PROCESSING', 'warn': 40, 'crit': 80},
            ],
            {'PROCESSING': ('crit', 1)},
        ),
        (
            [
                {'status': 'PENDING', 'warn': 60, 'crit': 120},
                {'status': 'PROCESSING', 'warn': 120, 'crit': 150},
            ],
            {},
        ),
    ],
)
@pytest.mark.now(datetime.datetime(2019, 1, 2, 9, 0, 0).isoformat())
async def test_too_long_in_status(
        monkeypatch, cron_context, check_config, expected_fail_statuses,
):
    monkeypatch.setitem(
        cron_context.config.STICKER_MONRUN_SETTINGS,
        'too_long_in_status',
        check_config,
    )

    check_result = await too_long_in_status.run_check(cron_context, None)

    if not expected_fail_statuses:
        assert check_result == (
            '0; OK: no mail requests stay in non-terminal status for too long'
        )
        return

    fail_level_str = '1; WARN'
    if any(
            status == 'crit'
            for status, count in expected_fail_statuses.values()
    ):
        fail_level_str = '2; CRIT'

    expected_result = (
        f'{fail_level_str}: mail requests in non-terminal status for too long'
    )

    for config_section in check_config:
        status = config_section['status']

        if status not in expected_fail_statuses:
            continue

        fail_time_threshold = config_section[expected_fail_statuses[status][0]]
        expected_fail_count = expected_fail_statuses[status][1]

        expected_result += (
            f', at least {expected_fail_count} requests are more than '
            f'{fail_time_threshold} minutes in {status}'
        )

    assert check_result == expected_result
