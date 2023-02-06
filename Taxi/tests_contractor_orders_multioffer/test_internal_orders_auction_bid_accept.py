import pytest

from tests_contractor_orders_multioffer import pg_helpers as pgh

CURRENT_DT = '2020-03-20T11:22:33.123456Z'


@pytest.mark.parametrize(
    'multioffer_id, bid_id, success',
    [
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c317',
            'b5d8c6fa-c891-4306-924f-0db1c217eb28',
            True,
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_bid_create.sql', 'multioffer_bid_create_bids.sql'],
)
@pytest.mark.now(CURRENT_DT)
async def test_orders_auction_bid_accept(
        taxi_contractor_orders_multioffer,
        pgsql,
        stq,
        multioffer_id,
        bid_id,
        success,
):
    params = {'multioffer_id': multioffer_id, 'bid_id': bid_id}

    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/orders-auction/bid/accept', json=params,
    )

    assert response.status_code == 200

    bid = pgh.select_multioffer_bid(pgsql, multioffer_id, bid_id)
    assert bid['status'] == 'accepted'

    driver = pgh.select_multioffer_driver(
        pgsql, multioffer_id, bid['driver_profile_id'], bid['park_id'],
    )
    assert driver['offer_status'] == 'accepted'

    assert stq.contractor_orders_multioffer_complete.times_called == 1
