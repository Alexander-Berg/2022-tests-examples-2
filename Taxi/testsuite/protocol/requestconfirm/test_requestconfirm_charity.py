import json

import pytest

from protocol.ordercommit import order_commit_common


PLAIN_ORDER_ID = 'plain_order'
PLAIN_ALIAS_ID = 'plain_alias_id'

DECOUPLING_ORDER_ID = 'decoupling_order'
DECOUPLING_ALIAS_ID = 'decoupling_alias_id'


@pytest.fixture
def mock_persey_payments(mockserver):
    def _do_mock(exp_req, resp, is_error=False, ticket=None):
        @mockserver.json_handler(
            '/persey_payments/internal/v1/charity/ride_donation/estimate',
            prefix=True,
        )
        def _handler(request):
            if ticket is not None:
                assert request.headers['X-Ya-Service-Ticket'] == ticket

            assert request.query_string.decode() == exp_req

            if is_error:
                return mockserver.make_response(
                    {'code': 'error', 'message': 'error'}, 500,
                )

            return resp

        return _handler

    return _do_mock


@pytest.mark.parametrize(
    [
        'is_cashback',
        'payment_type',
        'coupon',
        'exp_total_price',
        'exp_total_display_price',
        'exp_ride_display_price',
        'exp_charity_price',
        'exp_cashback_price',
        'exp_persey_payments_req',
        'persey_payments_error',
        'persey_payments_resp',
        'persey_payments_times_called',
    ],
    [
        pytest.param(
            True,
            'card',
            {},
            1321,
            1326,
            1321,
            5,
            321,
            (
                f'order_id={PLAIN_ORDER_ID}&'
                'payment_tech_type=card&'
                'ride_cost=1321.000000'
            ),
            False,
            {'amount_info': {'amount': '5', 'currency_code': 'RUB'}},
            1,
            marks=pytest.mark.experiments3(
                filename='complete_screen_exp.json',
            ),
            id='cashback + charity',
        ),
        pytest.param(
            True,
            'card',
            {'valid': True, 'was_used': True, 'value': 3},
            1318,
            1323,
            1318,
            5,
            321,
            (
                f'order_id={PLAIN_ORDER_ID}&'
                'payment_tech_type=card&'
                'ride_cost=1318.000000'
            ),
            False,
            {'amount_info': {'amount': '5', 'currency_code': 'RUB'}},
            1,
            marks=pytest.mark.experiments3(
                filename='complete_screen_exp.json',
            ),
            id='cashback + charity + coupon',
        ),
        pytest.param(
            False,
            'card',
            {},
            1000,
            1005,
            1000,
            5,
            None,
            (
                f'order_id={PLAIN_ORDER_ID}&'
                'payment_tech_type=card&'
                'ride_cost=1000.000000'
            ),
            False,
            {'amount_info': {'amount': '5', 'currency_code': 'RUB'}},
            1,
            marks=pytest.mark.experiments3(
                filename='complete_screen_exp.json',
            ),
            id='wo cashback',
        ),
        pytest.param(
            True,
            'card',
            {},
            1321,
            1321,
            1321,
            None,
            321,
            None,
            False,
            None,
            0,
            id='no exp -> no charity',
        ),
        pytest.param(
            False,
            'cash',
            {},
            1000,
            1000,
            1000,
            None,
            None,
            (
                f'order_id={PLAIN_ORDER_ID}&'
                'payment_tech_type=cash&'
                'ride_cost=1000.000000'
            ),
            False,
            {},
            1,
            marks=pytest.mark.experiments3(
                filename='complete_screen_exp.json',
            ),
            id='no charity, no cashback',
        ),
        pytest.param(
            True,
            'card',
            {},
            1321,
            1321,
            1321,
            None,
            321,
            (
                f'order_id={PLAIN_ORDER_ID}&'
                'payment_tech_type=card&'
                'ride_cost=1321.000000'
            ),
            True,
            None,
            2,
            marks=pytest.mark.experiments3(
                filename='complete_screen_exp.json',
            ),
            id='persey_payments fail',
        ),
    ],
)
@pytest.mark.config(
    HTTP_CLIENTS={
        '__default__': {'retries': 3, 'timeout': 2000},
        'persey_payments': {'retries': 2, 'timeout': 2000},
    },
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'persey-payments'}],
    TVM_SERVICES={'protocol': 23, 'persey-payments': 123},
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_charity(
        taxi_protocol,
        tvm2_client,
        load_json,
        db,
        mock_persey_payments,
        is_cashback,
        payment_type,
        coupon,
        exp_total_price,
        exp_total_display_price,
        exp_ride_display_price,
        exp_charity_price,
        exp_cashback_price,
        exp_persey_payments_req,
        persey_payments_error,
        persey_payments_resp,
        persey_payments_times_called,
):
    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'123': {'ticket': ticket}}))

    db.order_proc.update(
        {'_id': PLAIN_ORDER_ID},
        {
            '$set': {
                'extra_data.cashback.is_cashback': is_cashback,
                'extra_data.cashback.is_plus_cashback': is_cashback,
                'order.request.payment.type': payment_type,
                'payment_tech.type': payment_type,
                'order.coupon': coupon,
            },
        },
    )

    pp_mock = mock_persey_payments(
        exp_persey_payments_req,
        persey_payments_resp,
        persey_payments_error,
        ticket,
    )

    response = taxi_protocol.post(
        (
            '1.x/requestconfirm?clid=999012&'
            'apikey=d19a9b3b59424881b57adf5b0f367a2c'
        ),
        load_json('plain_request.json'),
    )
    assert response.status_code == 200

    proc = db.order_proc.find_one(PLAIN_ORDER_ID)

    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert pp_mock.times_called == persey_payments_times_called

    order_commit_common.check_current_prices(
        proc,
        'final_cost',
        exp_total_price,
        exp_total_display_price,
        exp_ride_display_price,
        exp_cashback_price,
        exp_charity_price,
    )


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(filename='complete_screen_exp.json')
def test_requestconfirm_charity_decoupling(
        taxi_protocol, db, load_json, mock_persey_payments,
):
    pp_mock = mock_persey_payments(
        (
            f'order_id={DECOUPLING_ORDER_ID}&'
            'payment_tech_type=corp&'
            'ride_cost=674.000000'
        ),
        {'amount_info': {'amount': '6', 'currency_code': 'RUB'}},
    )

    response = taxi_protocol.post(
        (
            '1.x/requestconfirm?clid=999012&'
            'apikey=d19a9b3b59424881b57adf5b0f367a2c'
        ),
        load_json('decoupling_request.json'),
    )
    assert response.status_code == 200

    proc = db.order_proc.find_one(DECOUPLING_ORDER_ID)

    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert pp_mock.times_called == 1

    order_commit_common.check_current_prices(
        proc, 'final_cost', 674, 680, 674, None, 6,
    )
