from aiohttp import web
import pytest

from qc_invites.generated.cron import run_cron


@pytest.mark.config(
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=False,
    ),
)
async def test_invite_entities_basic(mockserver, pgsql):
    @mockserver.json_handler('/quality-control/api/v1/pass/data')
    def _qc_pass_data_handler(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_handler(request):
        return {'parks': []}

    @mockserver.handler('/communications/driver/notification/bulk-push')
    def _push_handler(request):
        return web.json_response(status=200, content_type='text/plain')

    await run_cron.main(['qc_invites.crontasks.invite_entities', '-t', '0'])
    cursor = pgsql['qc_invites'].cursor()
    cursor.execute('SELECT invited FROM invites.entities')
    invite_ids = [row[0] for row in cursor]
    for invited in invite_ids:
        assert invited


@pytest.mark.config(
    QC_COMMS_CHECK_PUSH_SETTINGS=dict(
        lag='5s', expiration='1h', use_client_notify=True,
    ),
)
async def test_invite_entities_basic_client_notify(mockserver, pgsql):
    @mockserver.json_handler('/quality-control/api/v1/pass/data')
    def _qc_pass_data_handler(request):
        return {}

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_handler(request):
        return {'parks': []}

    @mockserver.handler('/client-notify/v2/bulk-push')
    def _push_cn_handler(request):
        return web.json_response(data={'notifications': []})

    await run_cron.main(['qc_invites.crontasks.invite_entities', '-t', '0'])
    cursor = pgsql['qc_invites'].cursor()
    cursor.execute('SELECT invited FROM invites.entities')
    invite_ids = [row[0] for row in cursor]
    for invited in invite_ids:
        assert invited
