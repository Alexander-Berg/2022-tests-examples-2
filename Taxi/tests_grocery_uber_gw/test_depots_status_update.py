import pytest

from tests_grocery_uber_gw import consts
from tests_grocery_uber_gw import models

DEPOTS_MAPPING = {'enabled': True, 'limit': 50}

DEPOTS_STATUS_UPDATE = {'enabled': True, 'period_seconds': 60}


@pytest.mark.config(GROCERY_UBER_GW_DEPOTS_MAPPING_SETTINGS=DEPOTS_MAPPING)
@pytest.mark.config(
    GROCERY_UBER_GW_DEPOTS_STATUS_UPDATE_SETTINGS=DEPOTS_STATUS_UPDATE,
)
@pytest.mark.suspend_periodic_tasks('depots-status-update-periodic')
async def test_basic(
        taxi_grocery_uber_gw,
        grocery_uber_gw_db,
        mock_uber_api,
        grocery_depots,
):
    """ Checking that the task correctly synchronizes the store statuses """

    expected_get_request_count = len(consts.DEFAULT_STORES)
    expected_set_request_count = 0
    depot_statuses = ['disabled', 'active', 'closed', 'coming_soon']
    for i, store in enumerate(consts.DEFAULT_STORES.values()):
        grocery_depots.add_depot(
            depot_test_id=i,
            status=depot_statuses[i % len(depot_statuses)],
            depot_id=store.merchant_store_id,
            legacy_depot_id=store.merchant_store_id,
        )
        if depot_statuses[i % len(depot_statuses)] != 'active':
            expected_set_request_count += 1

    await taxi_grocery_uber_gw.invalidate_caches()

    grocery_uber_gw_db.flush_distlocks()

    await taxi_grocery_uber_gw.run_periodic_task(
        'depots-status-update-periodic',
    )

    assert (
        mock_uber_api.restaurant_status_times_called
        == expected_get_request_count + expected_set_request_count
    )


@pytest.mark.config(GROCERY_UBER_GW_DEPOTS_MAPPING_SETTINGS=DEPOTS_MAPPING)
@pytest.mark.config(
    GROCERY_UBER_GW_DEPOTS_STATUS_UPDATE_SETTINGS=DEPOTS_STATUS_UPDATE,
)
@pytest.mark.parametrize(
    'active_clause_id, expected_request_count',
    [(None, 4), (0, 5), (1, 5), (2, 6), (3, 6), (4, 5)],
)
@pytest.mark.suspend_periodic_tasks('depots-status-update-periodic')
async def test_grocery_uber_gw_uber_store_status_override(
        taxi_grocery_uber_gw,
        grocery_uber_gw_db,
        mock_uber_api,
        grocery_depots,
        experiments3,
        load_json,
        active_clause_id,
        expected_request_count,
):
    """ Checking config overriding Uber Store statuses """

    stores = [
        models.Store(
            store_id='00000000-0000-0000-0000-000000000001',
            status='ONLINE',
            merchant_store_id='deli_id_1',
        ),
        models.Store(
            store_id='00000000-0000-0000-0000-000000000002',
            status='ONLINE',
            merchant_store_id='deli_id_2',
        ),
        models.Store(
            store_id='00000000-0000-0000-0000-000000000003',
            status='OFFLINE',
            merchant_store_id='deli_id_3',
        ),
    ]
    mock_uber_api_payload = {'stores': {}}
    for store in stores:
        mock_uber_api_payload['stores'][store.store_id] = store
    mock_uber_api.set_payload(mock_uber_api_payload)

    depot_statuses = ['active', 'disabled', 'disabled']
    for i, store in enumerate(stores):
        grocery_depots.add_depot(
            depot_test_id=i,
            status=depot_statuses[i],
            depot_id=store.merchant_store_id,
            legacy_depot_id=store.merchant_store_id,
        )

    if active_clause_id is not None:
        exp3_json = load_json(
            'grocery_uber_gw_uber_store_status_override.json',
        )
        exp3_json['configs'][0]['clauses'][active_clause_id]['enabled'] = True
        experiments3.add_experiments_json(exp3_json)

    await taxi_grocery_uber_gw.invalidate_caches()
    grocery_uber_gw_db.flush_distlocks()
    await taxi_grocery_uber_gw.run_periodic_task(
        'depots-status-update-periodic',
    )

    assert (
        mock_uber_api.restaurant_status_times_called == expected_request_count
    )
