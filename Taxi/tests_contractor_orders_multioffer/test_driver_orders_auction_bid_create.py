import pytest

from tests_contractor_orders_multioffer import pg_helpers as pgh

CURRENT_DT = '2020-03-20T11:22:33.123456Z'


def _get_dap_headers(park_id, driver_profile_id):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
    }


@pytest.mark.parametrize('price', [500, 1000, 2000, 2500])
@pytest.mark.parametrize('iteration', [0, 1, 2])
@pytest.mark.parametrize(
    'multioffer_id, park_id, driver_profile_id, status_code, prices, '
    'iterations, error_code, message',
    [
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c316',
            'park_id',
            'driver_profile_id_1',
            404,
            None,
            None,
            'auction_not_found',
            'Auction not found',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            'park_id',
            'driver_profile_id_xx',
            404,
            None,
            None,
            'driver_not_found',
            'Driver not found',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            'park_id',
            'driver_profile_id_3',
            404,
            None,
            None,
            'driver_not_found',
            'Driver not found',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            'park_id',
            'driver_profile_id_1',
            406,
            (500,),
            (1,),
            'invalid_price',
            'Invalid price',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            'park_id',
            'driver_profile_id_1',
            406,
            None,
            (0,),
            'invalid_iteration',
            'Invalid iteration',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            'park_id',
            'driver_profile_id_1',
            200,
            (1000, 2000, 2500),
            (1,),
            None,
            None,
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c317',
            'park_id',
            'driver_profile_id_1',
            200,
            (1000,),
            (1,),
            None,
            None,
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c317',
            'park_id',
            'driver_profile_id_1',
            406,
            (2000, 2500),
            (1,),
            'invalid_number_of_driver_bids',
            'Invalid number of driver bids',
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_bid_create.sql', 'multioffer_bid_create_bids.sql'],
)
@pytest.mark.now(CURRENT_DT)
async def test_orders_auction_bid_create(
        taxi_contractor_orders_multioffer,
        pgsql,
        taxi_config,
        multioffer_id,
        park_id,
        driver_profile_id,
        status_code,
        price,
        iteration,
        prices,
        iterations,
        error_code,
        message,
):

    taxi_config.set_values(
        {
            'CONTRACTOR_ORDERS_MULTIOFFER_INVALID_STATES': {
                'state': ['unknown'],
                'state_by_order': ['unknown'],
                'state_for_pricing': ['unknown'],
                'state_for_bid_creating': ['win', 'lose', 'declined'],
            },
        },
    )
    if prices is not None and price not in prices:
        return

    if iterations is not None and iteration not in iterations:
        return

    params = {
        'multioffer_id': multioffer_id,
        'iteration': iteration,
        'price': price,
    }

    response = await taxi_contractor_orders_multioffer.post(
        '/driver/v1/orders-auction/bid/create',
        json=params,
        headers=_get_dap_headers(park_id, driver_profile_id),
    )

    assert response.status_code == status_code
    response_data = response.json()

    if response.status_code != 200:
        assert response_data['code'] == error_code
        assert response_data['message'] == message
    else:
        bid = pgh.select_multioffer_driver_bid(
            pgsql, multioffer_id, park_id, driver_profile_id, 'created',
        )

        assert response_data['multioffer_id'] == multioffer_id
        assert response_data['bid_id'] == bid['id']
