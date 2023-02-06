# pylint: disable=redefined-outer-name,unused-variable,global-statement
import pytest

from selfemployed.generated.cron import run_cron
from . import conftest


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO cron_runs
        VALUES ('send_bound_to_xservice', NOW() - INTERVAL '1 minute')
        """,
        """
        INSERT INTO profiles (id, inn, status, park_id, driver_id,
                              created_at, modified_at)
        VALUES
            ('smz1', 'inn1', 'confirmed', 'p1', 'd1', NOW(), NOW()),
            ('smz2', 'inn2', 'rejected', 'p2', 'd2', NOW(), NOW()),
            ('smz3', 'inn3', 'bad_permissions', 'p3', 'd3', NOW(), NOW()),
            ('smz4', 'inn4', 'confirmed', 'p4', 'd4', NOW(), NOW()),

            ('smz5', 'inn5', 'confirmed', 'p5', 'd5',
                NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes'),
            ('smz6', 'inn6', 'rejected', 'p6', 'd6',
                NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes'),
            ('smz7', 'inn7', 'bad_permissions', 'p7', 'd7',
                NOW() - INTERVAL '15 minutes', NOW() - INTERVAL '15 minutes')
        """,
    ],
)
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_send_bound_to_xservice(se_cron_context, patch, taxi_config):
    fns_self_employment_settings = taxi_config.get(
        'TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS',
    )
    fns_self_employment_settings['enable_unbounded_sync_job'] = True

    bound_recv = []
    unbound_recv = []

    @patch('selfemployed.clients.taximeter.TaximeterClient.update_bindings')
    async def send_bound_to_xservice(bound, unbound, **kwargs):
        bound_recv.extend(bound)
        unbound_recv.extend(unbound)
        return

    await run_cron.main(
        ['selfemployed.crontasks.send_bound_to_xservice', '-t', '0'],
    )

    assert bound_recv == ['p1', 'p4']
    assert unbound_recv == ['p2', 'p3']
