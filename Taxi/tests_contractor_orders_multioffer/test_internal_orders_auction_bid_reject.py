import pytest

from tests_contractor_orders_multioffer import pg_helpers as pgh

CURRENT_DT = '2020-03-20T11:22:33.123456Z'


def _unordered(value):
    return sorted(tuple(sorted(x.items())) for x in value)


@pytest.mark.parametrize(
    'multioffer_id, bids, success',
    [
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c317',
            [
                'b5d8c6fa-c891-4306-924f-0db1c217eb28',
                '0be9a612-83f8-4f52-b585-16085c20299d',
            ],
            [True, True],
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_bid_create.sql', 'multioffer_bid_create_bids.sql'],
)
@pytest.mark.config(
    CONTRACTOR_ORDERS_MULTIOFFER_FREEZING_SETTINGS={
        'enable': True,
        'freeze_duration': 60,
    },
)
@pytest.mark.now(CURRENT_DT)
async def test_orders_auction_bid_reject(
        taxi_contractor_orders_multioffer,
        pgsql,
        stq,
        multioffer_id,
        bids,
        success,
):
    params = {
        'multioffer_id': multioffer_id,
        'bids': [{'bid_id': x} for x in bids],
    }

    response = await taxi_contractor_orders_multioffer.post(
        '/internal/v1/orders-auction/bid/reject', json=params,
    )

    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data['bids_statuses']) == len(bids)

    drivers_to_defreeze = []
    for i, (bid_id, bid_success) in enumerate(zip(bids, success)):
        assert response_data['bids_statuses'][i]['bid_id'] == bid_id
        assert response_data['bids_statuses'][i]['success'] == bid_success
        bid = pgh.select_multioffer_bid(pgsql, multioffer_id, bid_id)
        assert bid['status'] == 'rejected'

        driver = pgh.select_multioffer_driver(
            pgsql, multioffer_id, bid['driver_profile_id'], bid['park_id'],
        )
        assert driver['offer_status'] == 'lose'

        candidate_json = driver['candidate_json']
        drivers_to_defreeze.append(
            {
                'car_id': candidate_json.get('car_number', ''),
                'unique_driver_id': candidate_json.get('unique_driver_id', ''),
            },
        )

    assert stq.contractor_orders_multioffer_defreeze.times_called == 1
    kwargs = stq.contractor_orders_multioffer_defreeze.next_call()['kwargs']
    assert kwargs['multioffer_id'] == multioffer_id
    assert _unordered(kwargs['drivers']) == _unordered(drivers_to_defreeze)
