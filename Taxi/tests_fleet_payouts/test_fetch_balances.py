import datetime as dt

import pytest

from tests_fleet_payouts.utils import pg


@pytest.fixture(name='mock_parks_replica')
def mock_parks_replica_(mockserver, load_json):
    parks_replica = load_json('parks_replica.json')

    @mockserver.json_handler(
        '/parks-replica/v1/parks/by_billing_client_id/retrieve_bulk',
    )
    def handler(request):
        bcids = request.json['billing_client_ids']
        at_date = (
            dt.datetime.fromisoformat(request.json['at']).date().isoformat()
        )
        if at_date in parks_replica.keys():
            parks_replica_at = parks_replica[at_date]
        else:
            parks_replica_at = []
        return {
            'parks': [
                x for x in parks_replica_at if x['billing_client_id'] in bcids
            ],
        }

    return handler


@pytest.mark.now('2020-01-01')
@pytest.mark.yt(static_table_data=['yt_balances.yaml'])
async def test_fetch_balances(
        taxi_fleet_payouts, mock_parks_replica, pgsql, yt_apply,
):
    await taxi_fleet_payouts.run_task('periodic-balance-fetch')

    balances = pg.dump_balances(pgsql)
    assert len(balances) == 2

    timers = pg.dump_payment_timers(pgsql)
    assert timers == {
        '1': {'clid': '1', 'expires_at': None},
        '2': {'clid': '2', 'expires_at': None},
    }
