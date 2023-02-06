# pylint: disable=redefined-outer-name,unused-variable,global-statement
import pytest

from selfemployed.scripts import fetch_unbound_sync
from selfemployed.scripts import run_script
from . import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, park_id, driver_id, status, created_at, modified_at)
        VALUES
            ('smz1', 'unbound_1', 'p1', 'd1', 'confirmed', NOW(), NOW()),
            ('smz2', 'unbound_2', 'p2', 'd2', 'confirmed', NOW(), NOW()),
            ('smz3', 'unbound_3', 'p3', 'd3', 'confirmed', NOW(), NOW()),
            ('smz4', 'unbound_4', 'p4', 'd4', 'bad_permissions', NOW(), NOW()),
            ('smz5', 'unbound_5', 'p5', 'd5', 'bad_permissions', NOW(), NOW());
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_fetch_unbound_sync(se_cron_context, loop, patch, monkeypatch):
    monkeypatch.setattr(fetch_unbound_sync, 'POSTGRES_STEP', 3)

    repeats = {'unbound': 0}

    @patch('selfemployed.fns.client.Client.get_newly_unbound')
    async def get_newly_unbound(*args, **kwargs):
        pass

    @patch('selfemployed.fns.client.Client.get_newly_unbound_response')
    async def get_newly_unbound_response(*args, **kwargs):
        if repeats['unbound'] < 5:
            repeats['unbound'] += 1
            return (
                [{'inn': 'unbound_%d' % repeats['unbound'], 'timestamp': '1'}],
                True,
            )
        return [], False

    @patch('selfemployed.clients.taximeter.TaximeterClient.update_bindings')
    async def update_bindings(*args, **kwargs):
        pass

    await run_script.main(
        ['selfemployed.scripts.fetch_unbound_sync', '-t', '0'],
    )
