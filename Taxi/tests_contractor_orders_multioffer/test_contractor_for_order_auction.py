import copy

import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo
from tests_contractor_orders_multioffer import pg_helpers as pgh


async def test_contractor_for_order_auction(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        candidates,
        experiments3,
        pgsql,
        stq,
):
    # Arrange
    taxi_config.set_values(cfo.create_version_settings('1.00'))
    experiments3.add_config(
        **cfo.experiment3(
            tag='*',
            contractor_threshold=0,
            contractor_limit=2,
            enable_doaa=True,
            locked_dispatch='test_multioffer',
            is_auction=True,
            disable_chains=True,
            max_waves=2,
        ),
    )

    # Act
    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    request = copy.deepcopy(cfo.DEFAULT_PARAMS)
    request['auction'] = {'iteration': 0}
    request['driver_bid_info'] = {'min_price': 1000, 'max_price': 3000}
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=request,
    )

    # Assert
    assert response.status_code == 200
    assert response.json()['message'] == 'delayed'

    assert candidates.query['only_free'] is True

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics.get('total_orders', 0) == 1
    assert metrics.get('moscow', {}).get('total_orders', 0) == 1

    multioffer = pgh.select_recent_multioffer(pgsql)
    expect_status = 'in_progress'
    assert multioffer
    assert multioffer['status'] == expect_status
    assert multioffer['wave'] == 1
    assert multioffer['auction'] == {
        'auction_type': 'auction',
        'iteration': 0,
        'min_price': 1000.0,
        'max_price': 3000.0,
    }

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer['id'])
    assert len(drivers) == 2

    assert stq.contractor_orders_multioffer_assign.times_called == 1
    assert drivers[0] == {
        'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
        'driver_profile_id': '4bb5a0018d9641c681c1a854b21ec9ab',
        'offer_status': 'sent',
        'score': 0.0,
    }
    assert drivers[1] == {
        'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
        'driver_profile_id': 'e26e1734d70b46edabe993f515eda54e',
        'offer_status': 'sent',
        'score': 1.0,
    }


@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=[
        'multioffer_bid_create.sql',
        'multioffer_bid_create_bids.sql',
        'multioffer_bid_complete.sql',
    ],
)
async def test_contractor_for_order_auction_winner(
        taxi_config, taxi_contractor_orders_multioffer,
):
    request = copy.deepcopy(cfo.DEFAULT_PARAMS)
    request['order_id'] = '456'
    request['lookup']['version'] = 1
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=request,
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'found'

    candidate = response.json()['candidate']
    assert candidate['uuid'] == 'driver_profile_id_1'
    assert candidate['auction']['accepted_driver_price'] == 1000.0
