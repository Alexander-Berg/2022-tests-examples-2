import pytest

from tests_contractor_orders_multioffer import pg_helpers as pgh

SINGLE_DRIVER_OFFER = '72bcbde8-eaed-460f-8f88-eeb4e056c316'


def _get_dap_headers(driver_id):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': 'park_id',
        'X-YaTaxi-Driver-Profile-Id': driver_id,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
    }


@pytest.mark.parametrize('enable_fast_auction', [True, False])
@pytest.mark.parametrize(
    'multioffer_id, order_id, driver_id, code, status',
    [
        (SINGLE_DRIVER_OFFER, '123', 'driver_profile_id_1', 200, 'win'),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            '123',
            'driver_profile_id_1',
            200,
            'win_if_fast',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            '123',
            'driver_profile_id_2',
            200,
            'accepted',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c319',
            '123',
            'driver_profile_id_3',
            404,
            'declined',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c666',
            '123',
            'driver_profile_id_1',
            404,
            None,
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c317',
            '456',
            'driver_profile_id_1',
            200,
            'win',
        ),
        (
            '72bcbde8-eaed-460f-8f88-eeb4e056c318',
            '124',
            'driver_profile_id_1',
            406,
            'sent',
        ),
    ],
)
@pytest.mark.pgsql(
    'contractor_orders_multioffer',
    files=['multioffer_driver_orders_offer_offer_accept.sql'],
)
async def test_orders_offer_accept(
        taxi_contractor_orders_multioffer,
        taxi_config,
        stq_runner,
        stq,
        pgsql,
        multioffer_id,
        order_id,
        driver_id,
        code,
        status,
        lookup,
        enable_fast_auction,
        mockserver,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDERS_MULTIOFFER_FAST_AUCTION_SETTINGS': (
                enable_fast_auction
            ),
        },
    )
    params = {
        'accept_date': '2019-01-11T19:49:56+0000',
        'request_date': '2019-01-11T19:49:56+0000',
        'multioffer_id': multioffer_id,
    }
    callback_url = mockserver.url(
        f'lookup/event?order_id={order_id}&version=1&lookup_mode=multioffer',
    )
    pgh.update_callback_url(
        pgsql,
        multioffer_id,
        {'url': callback_url, 'timeout_ms': 100, 'attempts': 1},
    )
    response = await taxi_contractor_orders_multioffer.post(
        '/driver/v1/orders-offer/offer/accept',
        json=params,
        headers=_get_dap_headers(driver_id),
    )

    if status == 'win_if_fast':
        status = 'win' if enable_fast_auction else 'accepted'
    assert response.status_code == code

    if status == 'win':
        complete = stq.contractor_orders_multioffer_complete.next_call()
        assert complete['id'] == multioffer_id + '-complete'
        await stq_runner.contractor_orders_multioffer_complete.call(
            task_id=multioffer_id + '-complete', args=[multioffer_id],
        )

    lookup_called = int(status == 'win')
    assert lookup.event_called_winner == lookup_called

    pg_fields = pgh.select_multioffer_driver(
        pgsql, multioffer_id, driver_id, 'park_id',
    )

    if status in ('win', 'accepted'):
        assert pg_fields == {
            'answer': True,
            'offer_status': status,
            'answer_received_at': params['request_date'],
            'candidate_json': {},
            'enriched_json': {},
        }

    elif status == 'declined':
        assert pg_fields == {
            'answer': False,
            'offer_status': status,
            'candidate_json': {},
            'enriched_json': {},
        }
    elif status == 'sent':
        assert pg_fields == {
            'offer_status': status,
            'candidate_json': {},
            'enriched_json': {},
        }
    else:
        assert pg_fields == {}
