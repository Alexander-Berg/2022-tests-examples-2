# pylint: disable=redefined-outer-name, too-many-locals
import pytest

from taxi.clients import mds

from taxi_corp import cron_run


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.config(CORP_REPORTS_TTL=86400)
@pytest.mark.now('2020-02-02T03:00:00.000')
async def test_cleanup(db, patch):
    module = 'taxi_corp.stuff.cleanup_old_reports'

    @patch('taxi.clients.mds.MDSClient.remove')
    async def _remove(file_key):
        assert file_key == 'report0000_mds_key'

    assert await db.corp_reports.count() == 2
    await cron_run.main([module, '-t', '0'])
    assert await db.corp_reports.find({}, projection=['_id']).to_list(
        None,
    ) == [{'_id': 'report0002'}]
    assert _remove.calls


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.config(CORP_REPORTS_TTL=86400)
@pytest.mark.now('2020-02-02T03:00:00.000')
@pytest.mark.parametrize(
    ['status_code', 'expected_count'],
    [
        pytest.param(404, 1, id='http 404 not found'),
        pytest.param(500, 2, id='http 500'),
    ],
)
async def test_http_errors(db, patch, status_code, expected_count):
    module = 'taxi_corp.stuff.cleanup_old_reports'

    @patch('taxi.clients.mds.MDSClient.remove')
    async def _remove(file_key):
        raise mds.MDSHTTPError(status_code)

    assert await db.corp_reports.count() == 2

    try:
        await cron_run.main([module, '-t', '0'])
    except mds.MDSHTTPError:
        pass

    assert (
        await db.corp_reports.count({}, projection=['_id']) == expected_count
    )
    assert _remove.calls
