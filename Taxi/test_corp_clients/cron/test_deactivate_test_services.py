# pylint:disable=redefined-outer-name

import pytest

from corp_clients.generated.cron import run_cron


@pytest.fixture
def cargo_claims_mock(mockserver):
    data = {
        'cargo_no_limits': {'total': 100, 'completed': 50},
        'cargo_ride_limit_reached': {'total': 10, 'completed': 5},
    }

    @mockserver.json_handler('cargo-claims/v2/claims/corp-stats')
    async def _corp_stats(request):
        return data.get(
            request.query['corp_client_id'], {'total': 0, 'completed': 0},
        )


@pytest.mark.usefixtures('simple_secdist')
async def test_deactivate(db, cargo_claims_mock):

    module = 'corp_clients.crontasks.deactivate_test_services'
    await run_cron.main([module, '-t', '0'])

    clients = await db.corp_clients.find(
        {},
        projection={
            '_id': False,
            'yandex_login': True,
            'services.taxi.is_active': True,
            'services.cargo.is_active': True,
        },
    ).to_list(None)

    clients_with_services = {
        client['yandex_login']: (
            client['services'].get('taxi', {}).get('is_active'),
            client['services'].get('cargo', {}).get('is_active'),
        )
        for client in clients
    }

    assert clients_with_services == {
        'no_services': (None, None),
        'no_taxi': (None, None),
        'active_non_test': (True, None),
        'disabled_non_test': (False, None),
        'no_limits': (True, None),
        'expired_date': (False, None),
        'future_date': (True, None),
        'ride_limit_reached': (False, None),
        'cargo_no_limits': (None, True),
        'cargo_expired_date': (None, False),
        'cargo_ride_limit_reached': (None, False),
    }
