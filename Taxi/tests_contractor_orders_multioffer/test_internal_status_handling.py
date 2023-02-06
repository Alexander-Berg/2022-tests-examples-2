import pytest

from tests_contractor_orders_multioffer import pg_helpers as pgh

MULTIOFFER_ID = '72bcbde8-eaed-460f-8f88-eeb4e056c316'
MULTIOFFER_AUCTION_ID = '72bcbde8-eaed-460f-8f88-eeb4e056c317'
MULTIOFFER_AUCTION_WITHOUT_BID_ID = '72bcbde8-eaed-460f-8f88-eeb4e056c318'
BID_ID = '0be9a612-83f8-4f52-b585-16085c20299d'


@pytest.mark.pgsql('contractor_orders_multioffer')
async def test_internal_seen_404(taxi_contractor_orders_multioffer):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'multioffer_id': MULTIOFFER_ID,
        'reason': 'received',
        'timestamp': 123,
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/seen', json=params,
    )
    assert response.status_code == 404


@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_internal_status_handling.sql'],
)
async def test_internal_seen_200(taxi_contractor_orders_multioffer, pgsql):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'multioffer_id': MULTIOFFER_ID,
        'reason': 'received',
        'timestamp': 123,
        'lat': 13.5,
        'lon': 14.5,
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/multioffer/seen', json=params,
    )
    assert response.status_code == 200

    driver_data = pgh.select_multioffer_driver(
        pgsql, MULTIOFFER_ID, 'driver_profile_id', 'park_id',
    )
    assert driver_data['seen_data'] == {
        'reason': 'received',
        'timestamp': 123,
        'lat': 13.5,
        'lon': 14.5,
    }


@pytest.mark.config(
    CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS={
        'enable': True,
        'freeze_duration': 60,
    },
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_internal_status_handling.sql'],
)
async def test_internal_reject_200(
        taxi_contractor_orders_multioffer, pgsql, stq,
):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'request': {
            'accept_date': '2019-01-11T22:49:56+0300',
            'request_date': '2019-01-11T22:49:56+0300',
            'multioffer_id': MULTIOFFER_ID,
        },
        'comment': 'manual',
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/orders-offer/offer/decline', json=params,
    )
    assert response.status_code == 200

    driver_data = pgh.select_multioffer_driver(
        pgsql, MULTIOFFER_ID, 'driver_profile_id', 'park_id',
    )
    assert driver_data['offer_status'] == 'declined'
    assert driver_data['reason'] == 'manual'
    assert stq.contractor_orders_multioffer_defreeze.times_called == 1


@pytest.mark.config(
    CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS={
        'enable': True,
        'freeze_duration': 60,
    },
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_internal_status_handling.sql'],
)
@pytest.mark.parametrize(
    'multioffer_id, bid_id',
    [
        (MULTIOFFER_AUCTION_ID, BID_ID),
        (MULTIOFFER_AUCTION_WITHOUT_BID_ID, None),
    ],
)
async def test_internal_reject_auction_200(
        taxi_contractor_orders_multioffer, pgsql, stq, multioffer_id, bid_id,
):
    params = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'request': {
            'accept_date': '2019-01-11T22:49:56+0300',
            'request_date': '2019-01-11T22:49:56+0300',
            'multioffer_id': multioffer_id,
        },
        'comment': 'manual',
    }
    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/orders-offer/offer/decline', json=params,
    )
    assert response.status_code == 200

    driver_data = pgh.select_multioffer_driver(
        pgsql, multioffer_id, 'driver_profile_id', 'park_id',
    )
    assert driver_data['offer_status'] == 'declined'
    assert driver_data['reason'] == 'manual'

    if bid_id is not None:
        bid_data = pgh.select_multioffer_bid(pgsql, multioffer_id, bid_id)
        assert bid_data['status'] == 'cancelled'
        assert bid_data['reason'] == 'manual'

    assert stq.contractor_orders_multioffer_defreeze.times_called == 1
