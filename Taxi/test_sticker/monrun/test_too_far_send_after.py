import pytest

from sticker.monrun import too_far_send_after


@pytest.mark.parametrize(
    'check_config,expected',
    [
        (None, '1; WARN: send_after is 10 minutes more than now'),
        ({'warn': 15, 'crit': 20}, '0; OK'),
        (
            {'warn': 5, 'crit': 15},
            '1; WARN: send_after is 5 minutes more than now',
        ),
        (
            {'warn': 5, 'crit': 10},
            '2; CRIT: send_after is 10 minutes more than now',
        ),
    ],
)
@pytest.mark.now('2019-12-04T07:00:00+0000')
async def test_too_far_send_after(
        monkeypatch, cron_context, check_config, expected,
):
    if check_config:
        monkeypatch.setitem(
            cron_context.config.STICKER_MONRUN_SETTINGS,
            'too_far_send_after',
            check_config,
        )
    result = await too_far_send_after.run_check(cron_context, None)
    assert result == expected
