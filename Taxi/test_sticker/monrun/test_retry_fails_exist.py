import pytest

from sticker.monrun import retry_fails_exist


@pytest.mark.pgsql('sticker', files=('warn.sql',))
async def test_retry_fails_exist_warn(cron_context):
    check_result = await retry_fails_exist.run_check(cron_context, None)

    assert check_result == (
        '1; WARN: there are mail requests in queue scheduled for at least '
        'a second retry'
    )


@pytest.mark.pgsql('sticker', files=('ok.sql',))
async def test_retry_fails_exist_ok(cron_context):
    check_result = await retry_fails_exist.run_check(cron_context, None)

    assert check_result == (
        '0; OK: all mail requests scheduled for retry are waiting for '
        'the first attempt'
    )
