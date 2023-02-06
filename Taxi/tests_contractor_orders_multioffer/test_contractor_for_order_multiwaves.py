import copy

import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo
from tests_contractor_orders_multioffer import pg_helpers as pgh

MULTIOFFER_ID = 'ecc6dc92-6d56-48a3-884d-f31390cd9a3c'


@pytest.mark.parametrize('driver_count', [0, 1, 2])
async def test_contractor_for_order_locked_dispatch(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        candidates,
        experiments3,
        pgsql,
        stq,
        driver_count,
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
            max_waves=2,
        ),
    )
    candidates.ids = {
        '4bb5a0018d9641c681c1a854b21ec9ab' if driver_count > 0 else None,
        'e26e1734d70b46edabe993f515eda54e' if driver_count > 1 else None,
    }

    # Act
    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )

    # Assert
    assert response.status_code == 200
    assert response.json()['message'] == 'delayed'

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics.get('total_orders', 0) == 1
    assert metrics.get('moscow', {}).get('total_orders', 0) == 1

    multioffer = pgh.select_recent_multioffer(pgsql)
    assert multioffer
    assert multioffer['status'] == 'in_progress'
    assert multioffer['wave'] == 1

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer['id'])
    assert len(drivers) == driver_count

    if driver_count > 0:
        assert stq.contractor_orders_multioffer_assign.times_called == 1
    else:
        assert stq.contractor_orders_multioffer_assign.times_called == 0

    if driver_count > 0:
        assert drivers[0] == {
            'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'driver_profile_id': '4bb5a0018d9641c681c1a854b21ec9ab',
            'offer_status': 'sent',
            'score': 0.0,
        }

    if driver_count > 1:
        assert drivers[1] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': 'e26e1734d70b46edabe993f515eda54e',
            'offer_status': 'sent',
            'score': 1.0,
        }


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=[
        'multioffer_multiwave_1_in_progress.sql',
        'multioffer_multiwave_complete.sql',
    ],
)
@pytest.mark.parametrize('has_candidates', [True, False])
async def test_contractor_for_order_2_wave(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        experiments3,
        candidates,
        pgsql,
        stq,
        has_candidates,
):
    taxi_config.set_values(cfo.create_version_settings('1.00'))
    experiments3.add_config(
        **cfo.experiment3(
            tag='*', contractor_limit=2, enable_doaa=True, max_waves=2,
        ),
    )

    if has_candidates:
        candidates.ids -= {
            '4bb5a0018d9641c681c1a854b21ec9ab',
            'e26e1734d70b46edabe993f515eda54e',
        }
    else:
        candidates.ids = {}

    # Act

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=cfo.DEFAULT_PARAMS,
    )

    # Assert

    assert response.status_code == 200
    assert response.json()['message'] == 'delayed'

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics.get('total_orders', 0) == 0
    assert metrics.get('moscow', {}).get('total_orders', 0) == 0

    multioffer = pgh.select_recent_multioffer(pgsql)
    assert multioffer
    assert multioffer['status'] == 'in_progress'
    assert multioffer['wave'] == 2

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer['id'])
    assert len(drivers) == (4 if has_candidates else 2)

    assert drivers[0] == {
        'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
        'driver_profile_id': '4bb5a0018d9641c681c1a854b21ec9ab',
        'offer_status': 'declined',
        'score': 0.0,
    }

    assert drivers[1] == {
        'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
        'driver_profile_id': 'e26e1734d70b46edabe993f515eda54e',
        'offer_status': 'declined',
        'score': 1.0,
    }

    if has_candidates:
        assert stq.contractor_orders_multioffer_assign.times_called == 1

        assert drivers[2] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': 'fc7d65d48edd40f9be1ced0f08c98dcd',
            'offer_status': 'sent',
            'score': 2.0,
        }

        assert drivers[3] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': '47ee2a629f624e6fa07ebd0e159da258',
            'offer_status': 'sent',
            'score': 3.0,
        }

    else:
        assert stq.contractor_orders_multioffer_assign.times_called == 0


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=[
        'multioffer_multiwave_1_in_progress.sql',
        'multioffer_multiwave_complete.sql',
        'multioffer_multiwave_2_in_progress.sql',
    ],
)
@pytest.mark.parametrize('driver_away', [True, False])
async def test_contractor_for_order_relauch_auction(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        experiments3,
        candidates,
        pgsql,
        stq,
        driver_away,
):
    if driver_away:
        candidates.ids -= {'e26e1734d70b46edabe993f515eda54e'}

    taxi_config.set_values(cfo.create_version_settings('1.00'))
    experiments3.add_config(
        **cfo.experiment3(
            tag='*', contractor_limit=2, enable_doaa=True, max_waves=2,
        ),
    )

    # Act

    lookup_req = copy.deepcopy(cfo.DEFAULT_PARAMS)
    lookup_req['auction'] = {'iteration': 1}
    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=lookup_req,
    )

    # Assert

    assert response.status_code == 200
    assert response.json()['message'] == 'delayed'

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics.get('total_orders', 0) == 0
    assert metrics.get('moscow', {}).get('total_orders', 0) == 0

    multioffer = pgh.select_recent_multioffer(pgsql)
    assert multioffer
    assert multioffer['status'] == 'in_progress'

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer['id'])
    assert len(drivers) == 4

    if driver_away:
        assert drivers[0] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': 'e26e1734d70b46edabe993f515eda54e',
            'offer_status': 'declined',
            'score': 1.0,
        }

        assert drivers[1] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': '47ee2a629f624e6fa07ebd0e159da258',
            'offer_status': 'sent',
            'score': 3.0,
        }

        assert drivers[2] == {
            'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'driver_profile_id': '4bb5a0018d9641c681c1a854b21ec9ab',
            'offer_status': 'sent',
            'auction': {'auction_type': 'price_increment', 'iteration': 1},
            'score': 4.0,
        }

        assert drivers[3] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': 'fc7d65d48edd40f9be1ced0f08c98dcd',
            'offer_status': 'sent',
            'auction': {'auction_type': 'price_increment', 'iteration': 1},
            'score': 5.0,
        }

    else:
        assert drivers[0] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': 'fc7d65d48edd40f9be1ced0f08c98dcd',
            'offer_status': 'declined',
            'score': 2.0,
        }

        assert drivers[1] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': '47ee2a629f624e6fa07ebd0e159da258',
            'offer_status': 'sent',
            'score': 3.0,
        }

        assert drivers[2] == {
            'park_id': '7f74df331eb04ad78bc2ff25ff88a8f2',
            'driver_profile_id': '4bb5a0018d9641c681c1a854b21ec9ab',
            'offer_status': 'sent',
            'auction': {'auction_type': 'price_increment', 'iteration': 1},
            'score': 4.0,
        }

        assert drivers[3] == {
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_profile_id': 'e26e1734d70b46edabe993f515eda54e',
            'offer_status': 'sent',
            'auction': {'auction_type': 'price_increment', 'iteration': 1},
            'score': 5.0,
        }

    assert stq.contractor_orders_multioffer_assign.times_called == 1

    complete = stq.contractor_orders_multioffer_assign.next_call()
    kwargs = complete['kwargs']
    assert kwargs['multioffer_id'] == MULTIOFFER_ID
    assert kwargs['wave'] == 3
    assert len(kwargs['drivers']) == 2

    if driver_away:
        assert (
            kwargs['drivers'][0]['driver_profile_id']
            == '4bb5a0018d9641c681c1a854b21ec9ab'
        )
        assert (
            kwargs['drivers'][1]['driver_profile_id']
            == 'fc7d65d48edd40f9be1ced0f08c98dcd'
        )
    else:
        assert (
            kwargs['drivers'][0]['driver_profile_id']
            == '4bb5a0018d9641c681c1a854b21ec9ab'
        )
        assert (
            kwargs['drivers'][1]['driver_profile_id']
            == 'e26e1734d70b46edabe993f515eda54e'
        )


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=[
        'multioffer_multiwave_1_in_progress.sql',
        'multioffer_multiwave_complete.sql',
        'multioffer_multiwave_2_in_progress.sql',
    ],
)
async def test_contractor_for_order_relauch_auction_wo_drivers(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        experiments3,
        candidates,
        pgsql,
        stq,
):
    candidates.ids = {}

    taxi_config.set_values(cfo.create_version_settings('1.00'))
    experiments3.add_config(
        **cfo.experiment3(
            tag='*', contractor_limit=2, enable_doaa=True, max_waves=2,
        ),
    )

    # Act

    lookup_req = copy.deepcopy(cfo.DEFAULT_PARAMS)
    lookup_req['auction'] = {'iteration': 1}
    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=lookup_req,
    )

    # Assert

    assert response.status_code == 200
    assert response.json()['message'] == 'delayed'

    multioffer = pgh.select_recent_multioffer(pgsql)
    assert multioffer
    assert multioffer['status'] == 'in_progress'

    drivers = pgh.select_multioffer_drivers(pgsql, multioffer['id'])
    assert len(drivers) == 4

    assert stq.contractor_orders_multioffer_assign.times_called == 0
    assert stq.contractor_orders_multioffer_complete.times_called == 1

    complete = stq.contractor_orders_multioffer_complete.next_call()
    kwargs = complete['kwargs']
    assert kwargs['multioffer_id'] == MULTIOFFER_ID
    assert kwargs['wave'] == 3
