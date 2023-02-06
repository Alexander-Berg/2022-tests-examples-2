import pytest

from insurance.generated.cron import run_cron


@pytest.mark.now('2020-10-30T10:05:00+03:00')
@pytest.mark.parametrize(
    'exports_removed',
    [
        pytest.param(
            2,
            marks=pytest.mark.config(MAX_DAYS_EXPORT_STORING=10),
            id='simple',
        ),
        pytest.param(
            0,
            marks=pytest.mark.config(MAX_DAYS_EXPORT_STORING=100),
            id='nothing to remove',
        ),
        pytest.param(
            6,
            marks=pytest.mark.config(MAX_DAYS_EXPORT_STORING=1),
            id='remove all',
        ),
    ],
)
async def test_export_cleanup(cron_context, patch, exports_removed):
    @patch('taxi.clients.mds.MDSClient.exists')
    async def _exists(*args, **kwargs):
        return True

    @patch('taxi.clients.mds.MDSClient.remove')
    async def _remove(mds_key, **kwargs):
        assert mds_key

    exports_count_before = (
        await cron_context.mongo.insured_orders_export.count()
    )

    await run_cron.main(['insurance.crontasks.export_cleanup', '-t', '0'])

    exports_count_after = (
        await cron_context.mongo.insured_orders_export.count()
    )

    assert exports_count_before - exports_count_after == exports_removed
