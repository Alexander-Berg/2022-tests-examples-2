import operator

import pytest


@pytest.mark.parametrize(
    'expected_set_fields_calls',
    [
        pytest.param(
            1,
            marks=pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True),
        ),
        pytest.param(1, marks=pytest.mark.experiments3(filename='exp3.json')),
        pytest.param(0),
    ],
)
async def test_current_prices_calculator_happy_path(
        stq_runner, mockserver, load_json, expected_set_fields_calls,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-1.json')
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert request.json == {
            'call_processing': False,
            'order_id': 'order-id-1',
            'update': {
                'set': {
                    'order.current_prices.kind': 'taximeter',
                    'order.current_prices.user_ride_display_price': 112.0,
                    'order.current_prices.user_total_display_price': 112.0,
                    'order.current_prices.user_total_price': 112.0,
                    'order.current_prices.cashback_price': 12.0,
                    'order.current_prices.possible_cashback': 10.0,
                    'order.current_prices.cost_breakdown': [],
                    'order.current_prices.cashback_by_sponsor.fintech': 5.0,
                    'order.current_prices.discount_cashback': 5.0,
                },
            },
            'user_id': '40d4167a527340caac75e55040bfd49e',
            'version': 'DAAAAAAABgAMAAQABgAAAFiAoThvAQAA',
        }
        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-1'], kwargs={}, expect_fail=False,
    )

    assert _mock_set_order_fields.times_called == expected_set_fields_calls


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
async def test_current_prices_calculator_move_to_cash(
        stq_runner, mockserver, load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-2.json')
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert request.json == {
            'call_processing': False,
            'order_id': 'order-id-2',
            'update': {
                'set': {
                    'order.current_prices.kind': 'taximeter',
                    'order.current_prices.user_ride_display_price': 100.0,
                    'order.current_prices.user_total_display_price': 100.0,
                    'order.current_prices.user_total_price': 100.0,
                    'order.current_prices.cashback_price': 0.0,
                    'order.current_prices.cost_breakdown': [],
                },
                'unset': {'order.current_prices.discount_cashback': None},
            },
            'user_id': '40d4167a527340caac75e55040bfd49e',
            'version': 'DAAAAAAABgAMAAQABgAAAFiAoThvAQAA',
        }
        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-2'], kwargs={}, expect_fail=False,
    )


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=False)
async def test_current_prices_calculator_do_not_commit(
        stq_runner, mockserver, load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-3.json')
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert False

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-3'], kwargs={}, expect_fail=False,
    )


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_SPLIT_REQUEST=True)
async def test_current_prices_calculator_split_payment(
        stq_runner, mockserver, load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        req = request.json
        assert 'order.current_prices.cost_breakdown' in req['update']['set']
        cost_breakdown = req['update']['set'][
            'order.current_prices.cost_breakdown'
        ]
        key = operator.itemgetter('type')
        assert sorted(cost_breakdown, key=key) == sorted(
            [
                {'amount': 100.0, 'type': 'card'},
                {'amount': 12.0, 'type': 'personal_wallet'},
            ],
            key=key,
        )
        update = request.json['update']['set']
        update.pop('order.current_prices.cost_breakdown')
        assert update == {
            'order.current_prices.user_total_price': 112.0,
            'order.current_prices.user_total_display_price': 112.0,
            'order.current_prices.user_ride_display_price': 112.0,
            'order.current_prices.kind': 'taximeter',
            'order.current_prices.cashback_price': 12.0,
            # (112 - 12) * 0.1
            'order.current_prices.cashback_by_sponsor.fintech': 10.0,
            'order.current_prices.discount_cashback': 10.0,
        }
        return {}

    @mockserver.json_handler('/plus-wallet/v1/internal/payment/split')
    def _mock_plus_wallet_split(request):
        assert request.json == {
            'order_id': 'order-id-4',
            'currency': 'RUB',
            'fixed_price': False,
            'payment': {
                'complements': [
                    {
                        'payment_method_id': 'w/123',
                        'type': 'personal_wallet',
                        'withdraw_amount': '33',
                    },
                ],
                'type': 'card',
            },
            'status': 'driving',
            'sum_to_pay': {'ride': '112'},
            'taxi_status': 'waiting',
            'yandex_uid': '4004838623',
            'zone': 'moscow',
        }
        return load_json('plus_wallet_split_response-4.json')

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={}, expect_fail=False,
    )


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_SPLIT_REQUEST=True)
async def test_current_prices_calculator_raises_on_split_fail(
        stq_runner, mockserver, load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        return resp

    @mockserver.json_handler('/plus-wallet/v1/internal/payment/split')
    def mock_plus_wallet_split(request):
        return mockserver.make_response(status=500)

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={}, expect_fail=True,
    )

    assert mock_plus_wallet_split.times_called == 1


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_SPLIT_REQUEST=True)
async def test_current_prices_calculator_no_split_call(
        stq_runner, mockserver, load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        resp['fields']['payment_tech']['type'] = 'cash'
        return resp

    @mockserver.json_handler('/plus-wallet/v1/internal/payment/split')
    def mock_plus_wallet_split(request):
        assert False

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={}, expect_fail=False,
    )

    assert mock_plus_wallet_split.times_called == 0


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_SPLIT_REQUEST=True)
async def test_current_prices_calculator_no_split_without_complements(
        stq_runner, mockserver, load_json,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        resp['fields']['payment_tech']['complements'] = []
        return resp

    @mockserver.json_handler('/plus-wallet/v1/internal/payment/split')
    def mock_plus_wallet_split(request):
        assert False

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={}, expect_fail=False,
    )

    assert mock_plus_wallet_split.times_called == 0


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DECREASE_USER_PRICE_BY_PLUS=True)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_SPLIT_REQUEST=True)
async def test_decrease_cost_by_plus(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        return load_json('order_core_response_order-id-4.json')

    @mockserver.json_handler('/plus-wallet/v1/internal/payment/split')
    def _mock_plus_wallet_split(request):
        return load_json('plus_wallet_split_response-4.json')

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        update = request.json['update']['set']
        assert 'order.current_prices.cost_breakdown' in update
        assert 'order.current_prices.user_total_display_price' in update
        assert 'order.current_prices.user_ride_display_price' in update

        user_total_display_price = update[
            'order.current_prices.user_total_display_price'
        ]
        user_ride_display_price = update[
            'order.current_prices.user_ride_display_price'
        ]
        assert user_total_display_price == 100
        assert user_ride_display_price == 100

        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={}, expect_fail=False,
    )

    assert _mock_set_order_fields.times_called == 1


@pytest.mark.parametrize(
    'should_fail',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CURRENT_PRICES_CALCULATOR_FAIL_WITHOUT_PRICING_DATA=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                CURRENT_PRICES_CALCULATOR_FAIL_WITHOUT_PRICING_DATA=False,
            ),
        ),
    ],
)
async def test_fail_on_missing_pricing_data(
        stq_runner, mockserver, load_json, should_fail,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        del resp['fields']['order']['pricing_data']
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert False

    await stq_runner.current_prices_calculator.call(
        task_id='task_id',
        args=['order-id-4'],
        kwargs={},
        expect_fail=should_fail,
    )


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_RESCHEDULE_ENABLED=True)
async def test_current_prices_race(stq_runner, mockserver, load_json, stq):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        del resp['fields']['order']['taxi_status']
        return resp

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={},
    )

    assert stq.current_prices_calculator.times_called == 1


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
@pytest.mark.parametrize(
    'status,taxi_status',
    [('cancelled', None), ('finished', 'cancelled'), ('finished', 'failed')],
)
async def test_current_prices_on_cancel(
        stq_runner, mockserver, load_json, stq, status, taxi_status,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        resp['fields']['order']['cost'] = 666
        resp['fields']['order']['status'] = status
        if taxi_status:
            resp['fields']['order']['taxi_status'] = taxi_status
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        update = request.json['update']['set']
        assert update == {
            'order.current_prices.user_total_price': 666.0,
            'order.current_prices.user_total_display_price': 666.0,
            'order.current_prices.user_ride_display_price': 666.0,
            'order.current_prices.kind': 'final_cost',
            'order.current_prices.cost_breakdown': [],
            'order.current_prices.cashback_price': 0.0,
            'order.current_prices.cashback_by_sponsor.fintech': 0.0,
            'order.current_prices.discount_cashback': 0.0,
        }

        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={},
    )


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
async def test_current_prices_on_finish_with_coupon(
        stq_runner, mockserver, load_json, stq,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        resp['fields']['order']['coupon'] = {'valid': True, 'value': 50}
        resp['fields']['order']['status'] = 'finished'
        resp['fields']['order']['taxi_status'] = 'complete'
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        update = request.json['update']['set']
        assert update == {
            'order.current_prices.user_total_price': 166.0,
            'order.current_prices.user_total_display_price': 166.0,
            'order.current_prices.user_ride_display_price': 166.0,
            'order.current_prices.kind': 'final_cost',
            'order.current_prices.cost_breakdown': [],
            'order.current_prices.cashback_price': 17.0,
            # 10% from user total price and round up is disabled
            'order.current_prices.cashback_by_sponsor.fintech': 16.0,
            'order.current_prices.discount_cashback': 16.0,
        }

        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={},
    )


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
async def test_order_core_race_condition(
        stq_runner, mockserver, load_json, stq,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-4.json')
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        return mockserver.make_response(
            json={'code': '123', 'message': 'error_msg'}, status=409,
        )

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={},
    )

    assert stq.current_prices_calculator.times_called == 1


@pytest.mark.parametrize(
    'payment_type,'
    'current_cost,'
    'pricing_user_total,'
    'cashback_fixed_price,'
    'cashback_rate,'
    'unite_total_price_enabled,'
    'expected_kind,'
    'expected_total,'
    'expected_plus_cashback,'
    'expected_discount_cashback,'
    'expected_discount_cashback_sponsor,'
    'possible_cashback_rate,'
    'possible_cashback_fixed_price,'
    'expected_possible_cashback',
    [
        pytest.param(
            'card',
            None,
            900,
            100,
            0.05,
            False,
            'fixed',
            1000.0,
            100.0,
            45.0,
            'mastercard',
            0.1,
            100,
            100.0,
            id='both cashbacks, fixed, no unite',
        ),
        pytest.param(
            'card',
            None,
            1000,
            100,
            0.05,
            True,
            'fixed',
            1000.0,
            100.0,
            45.0,
            'otkrytie_mastercard',
            0.1,
            110.0,
            110.0,
            id='both cashbacks, fixed, unite',
        ),
        pytest.param(
            'card',
            900,
            900,
            100,
            0.05,
            False,
            'taximeter',
            1000.0,
            100.0,
            45.0,
            'mastercard_and_promsvyazbank',
            0.1,
            100.0,
            90.0,
            id='both cashbacks, cc, no unite',
        ),
        pytest.param(
            'card',
            1000,
            1000,
            100,
            0.05,
            True,
            'taximeter',
            1000.0,
            100.0,
            45.0,
            'otkrytie_mastercard',
            0.1,
            110.0,
            90.0,
            id='both cashbacks, cc, unite',
        ),
        pytest.param(
            'cash',
            None,
            900,
            100,
            0.05,
            False,
            'fixed',
            1000.0,
            100.0,  # todo: 100 and total 100 is looks wrong, should we fix it?
            0.0,
            'mastercard',
            0.1,
            100.0,
            0.0,
            id='moved to cash, both cashbacks, fixed, no unite',
        ),
        pytest.param(
            'cash',
            None,
            1000,
            100,
            0.05,
            True,
            'fixed',
            1000.0,
            100.0,  # todo: 100 and total 100 is looks wrong, should we fix it?
            0.0,
            'mastercard_and_promsvyazbank',
            0.1,
            110.0,
            0.0,
            id='moved to cash, both cashbacks, fixed, unite',
        ),
        pytest.param(
            'cash',
            900,
            900,
            100,
            0.05,
            False,
            'taximeter',
            900.0,
            0.0,
            0.0,
            'otkrytie_mastercard',
            0.1,
            100.0,
            0.0,
            id='moved to cash, both cashbacks, cc, no unite',
        ),
        pytest.param(
            'cash',
            900,
            1000,
            100,
            0.05,
            True,
            'taximeter',
            900.0,
            0.0,
            0.0,
            'mastercard',
            0.1,
            100.0,
            0.0,
            id='moved to cash, both cashbacks, cc, unite',
        ),
    ],
)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
async def test_current_prices_calculator_unite(
        stq_runner,
        mockserver,
        load_json,
        payment_type,
        current_cost,
        pricing_user_total,
        cashback_fixed_price,
        cashback_rate,
        unite_total_price_enabled,
        expected_kind,
        expected_total,
        expected_plus_cashback,
        expected_discount_cashback,
        expected_discount_cashback_sponsor,
        possible_cashback_rate,
        possible_cashback_fixed_price,
        expected_possible_cashback,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-1_template.json')
        resp['fields']['payment_tech']['type'] = payment_type
        resp['fields']['order_info']['cc'] = current_cost
        resp['fields']['order']['pricing_data']['user']['price'][
            'total'
        ] = pricing_user_total
        resp['fields']['order']['pricing_data']['user']['meta'][
            'cashback_rate'
        ] = cashback_rate
        resp['fields']['order']['pricing_data']['user']['meta'][
            'possible_cashback_rate'
        ] = possible_cashback_rate
        resp['fields']['order']['pricing_data']['user']['meta'][
            'possible_cashback_fixed_price'
        ] = possible_cashback_fixed_price
        resp['fields']['order']['pricing_data']['user']['meta'][
            f'cashback_sponsor:{expected_discount_cashback_sponsor}'
        ] = 1
        if cashback_fixed_price:
            resp['fields']['order']['pricing_data']['user']['meta'][
                'cashback_fixed_price'
            ] = cashback_fixed_price
            resp['fields']['order']['pricing_data']['user']['meta'][
                'cashback_tariff_multiplier'
            ] = 0.9
        if unite_total_price_enabled:
            resp['fields']['order']['pricing_data']['user']['meta'][
                'unite_total_price_enabled'
            ] = 1
            resp['fields']['order']['pricing_data']['user']['meta'][
                'plus_cashback_rate'
            ] = 0.1
            resp['fields']['order']['pricing_data']['user']['meta'][
                'user_ride_price'
            ] = 900
            resp['fields']['order']['pricing_data']['user']['meta'][
                'cashback_calc_coeff'
            ] = 0
            resp['fields']['order']['pricing_data']['user']['meta'][
                'cashback_tariff_multiplier'
            ] = None
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert request.json == {
            'call_processing': False,
            'order_id': 'order-id-1',
            'update': {
                'set': {
                    'order.current_prices.kind': expected_kind,
                    'order.current_prices.user_ride_display_price': (
                        expected_total
                    ),
                    'order.current_prices.user_total_display_price': (
                        expected_total
                    ),
                    'order.current_prices.user_total_price': expected_total,
                    'order.current_prices.cashback_price': (
                        expected_plus_cashback
                    ),
                    'order.current_prices.discount_cashback': (
                        expected_discount_cashback
                    ),
                    'order.current_prices.possible_cashback': (
                        expected_possible_cashback
                    ),
                    'order.current_prices.cost_breakdown': [],
                    f'order.current_prices.cashback_by_sponsor.'
                    f'{expected_discount_cashback_sponsor}': (
                        expected_discount_cashback
                    ),
                },
            },
            'user_id': '40d4167a527340caac75e55040bfd49e',
            'version': 'DAAAAAAABgAMAAQABgAAAFiAoThvAQAA',
        }
        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-1'], kwargs={}, expect_fail=False,
    )

    assert _mock_set_order_fields.times_called == 1


@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
async def test_current_prices_paid_supply_on_creation(
        stq_runner, mockserver, load_json, stq,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_with_paid_supply.json')
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        update = request.json['update']['set']
        assert update == {
            'order.current_prices.user_total_price': 250.0,
            'order.current_prices.user_total_display_price': 250.0,
            'order.current_prices.user_ride_display_price': 250.0,
            'order.current_prices.kind': 'prediction',
            'order.current_prices.cost_breakdown': [],
        }

        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={},
    )

    assert _mock_set_order_fields.times_called == 1


@pytest.mark.parametrize('paid_supply', [True, False])
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
async def test_current_prices_paid_supply_on_assigned(
        stq_runner, mockserver, load_json, stq, paid_supply,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_with_paid_supply.json')
        resp['fields']['order']['performer']['paid_supply'] = paid_supply
        resp['fields']['order']['status'] = 'assigned'
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        update = request.json['update']['set']
        if paid_supply:
            assert update == {
                'order.current_prices.user_total_price': 250.0,
                'order.current_prices.user_total_display_price': 250.0,
                'order.current_prices.user_ride_display_price': 250.0,
                'order.current_prices.kind': 'prediction',
                'order.current_prices.cost_breakdown': [],
            }
        else:
            assert update == {
                'order.current_prices.user_total_price': 199.0,
                'order.current_prices.user_total_display_price': 199.0,
                'order.current_prices.user_ride_display_price': 199.0,
                'order.current_prices.kind': 'prediction',
                'order.current_prices.cost_breakdown': [],
            }
        return {}

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-4'], kwargs={},
    )

    assert _mock_set_order_fields.times_called == 1


@pytest.mark.parametrize(
    'current_cost, wallet_payment, expected_cashback',
    [
        pytest.param(112, 12, 10),
        pytest.param(100, 100, None),
        pytest.param(100, 99, None),
    ],
)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_DO_COMMIT=True)
@pytest.mark.config(CURRENT_PRICES_CALCULATOR_SPLIT_REQUEST=True)
async def test_unite_with_wallet(
        stq_runner,
        mockserver,
        load_json,
        current_cost,
        wallet_payment,
        expected_cashback,
):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _mock_order_fields(request):
        resp = load_json('order_core_response_order-id-1_template.json')
        resp['fields']['order_info']['cc'] = current_cost
        resp['fields']['order']['pricing_data']['user']['meta'][
            'unite_total_price_enabled'
        ] = 1
        resp['fields']['order']['pricing_data']['user']['meta'][
            'plus_cashback_rate'
        ] = 0.1
        resp['fields']['order']['pricing_data']['user']['meta'][
            'user_ride_price'
        ] = current_cost - (expected_cashback or 0)
        resp['fields']['order']['pricing_data']['user']['price'][
            'total'
        ] = current_cost
        resp['fields']['order']['pricing_data']['user']['meta'][
            'cashback_calc_coeff'
        ] = 0
        resp['fields']['order']['pricing_data']['user']['meta'][
            'cashback_tariff_multiplier'
        ] = None
        resp['fields']['payment_tech'] = {
            'payment_method_id': '123',
            'type': 'card',
            'complements': [
                {
                    'payment_method_id': 'w/123',
                    'type': 'personal_wallet',
                    'withdraw_amount': wallet_payment,
                },
            ],
        }
        return resp

    @mockserver.json_handler('/order-core/v1/tc/set-order-fields')
    def _mock_set_order_fields(request):
        assert (
            request.json['update']['set'].get(
                'order.current_prices.cashback_price',
            )
            == expected_cashback
        )
        return {}

    @mockserver.json_handler('/plus-wallet/v1/internal/payment/split')
    def _mock_plus_wallet_split(request):
        card_payment = max(1, current_cost - wallet_payment)
        response = {
            'currency': 'RUB',
            'sum_to_pay': {
                'ride': [
                    {
                        'payment_method_id': '123',
                        'sum': str(card_payment),
                        'type': 'card',
                    },
                    {
                        'payment_method_id': 'w/123',
                        'sum': str(wallet_payment),
                        'type': 'personal_wallet',
                    },
                ],
                'tips': [],
            },
        }
        return response

    await stq_runner.current_prices_calculator.call(
        task_id='task_id', args=['order-id-1'], kwargs={}, expect_fail=False,
    )

    assert _mock_set_order_fields.times_called == 1
