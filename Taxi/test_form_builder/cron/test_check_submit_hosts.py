import pytest

from form_builder.generated.cron import run_cron
from form_builder.utils import network


@pytest.mark.config(
    FORM_BUILDER_CHECK_SUBMIT_HOSTS_SETTINGS={
        'check_periodic': True,
        'check_timeout': 10,
        'chunk_size': 10,
    },
)
async def test_do_stuff(patch, cron_context):
    @patch('form_builder.utils.network._sync_check')
    def _sync_check(host, port, timeout=None):
        assert port == 80
        assert host == 'test.url.com'
        raise network.BadHost(host)

    await run_cron.main(
        ['form_builder.crontasks.check_submit_hosts', '-t', '0', '-d'],
    )
    rows = await cron_context.pg.primary.fetch(
        'SELECT * FROM form_builder.submit_options ORDER BY id;',
    )
    assert len(rows) == 3
    assert [x['host_check_state'] for x in rows] == ['FAILED', None, None]
    assert (
        rows[0]['host_check_fail_reason']
        == 'Host test.url.com is unreachable, possibly a typo'
    )
