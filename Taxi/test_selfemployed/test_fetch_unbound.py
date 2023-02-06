# pylint: disable=redefined-outer-name,unused-variable,global-statement
import pytest

from selfemployed.crontasks import fetch_unbound
from selfemployed.db import dbmain
from selfemployed.generated.cron import run_cron
from . import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, park_id, driver_id, status, request_id,
            created_at, modified_at)
        VALUES
            ('smz1', 'unb_1', 'p1', 'd1', 'confirmed', null,
            NOW(), NOW()),
            ('smz2', 'unb_2', 'p2', 'd2', 'rejected', 'unb_2:failed',
            NOW(), NOW()),
            ('smz3', 'unb_3', 'p3', 'd3', 'rejected', 'unb_3:in_progress',
            NOW(), NOW()),
            ('smz4', 'unb_4', 'p4', 'd4', 'bad_permissions', null,
            NOW(), NOW()),
            ('smz5', 'unb_5', 'p5', 'd5', 'bad_permissions', null,
            NOW(), NOW());
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
@pytest.mark.skip()
async def test_fetch_unbound(se_cron_context, patch, monkeypatch):
    monkeypatch.setattr(fetch_unbound, 'POSTGRES_STEP', 2)

    repeats = {'bound': 0, 'unb': 0}  # unbound

    @patch('selfemployed.fns.client.Client.get_response_retry')
    async def get_response_retry(*args, **kwargs):
        pass

    @patch('selfemployed.fns.client.Client.get_newly_unbound')
    async def get_newly_unbound(*args, **kwargs):
        pass

    @patch('selfemployed.fns.client.Client.parse_unbound')
    def parse_unbound(*args, **kwargs):
        if repeats['unb'] < 5:
            repeats['unb'] += 1
            return [{'inn': 'unb_%d' % repeats['unb'], 'timestamp': '1'}], True
        return [], False

    fns = {'req_id': None, 'inn': None}

    @patch('selfemployed.fns.client.Client.check_bind_status')
    async def check_bind_status(*args, **kwargs):
        fns['req_id'] = args[0]

    @patch('selfemployed.fns.client.Client.bind_by_inn')
    async def bind_by_inn(*args, **kwargs):
        fns['inn'] = args[0]

    @patch('selfemployed.fns.client.Client.parse_bind_status')
    def parse_bind_status(*args, **kwargs):
        inn, status = fns['req_id'].split(':')
        return status.upper(), inn

    @patch('selfemployed.fns.client.Client.parse_bind')
    def parse_bind(*args, **kwargs):
        return fns['inn'] + ':new'

    @patch('selfemployed.clients.taximeter.TaximeterClient.update_bindings')
    async def update_bindings(*args, **kwargs):
        pass

    await run_cron.main(['selfemployed.crontasks.fetch_unbound', '-t', '0'])

    for park_id, driver_id, status, request_id in [
            ('p1', 'd1', 'rejected', None),
            ('p2', 'd2', 'rejected', 'unb_2:failed'),
            ('p3', 'd3', 'rejected', 'unb_3:in_progress'),
            ('p4', 'd4', 'rejected', 'unb_4:new'),
            ('p5', 'd5', 'rejected', 'unb_5:new'),
    ]:
        data = await dbmain.get_from_selfemployed(
            se_cron_context.pg, park_id, driver_id,
        )
        assert data['status'] == status
        assert data['request_id'] == request_id
