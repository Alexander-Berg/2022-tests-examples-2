import pytest

from cashback.stq import cashback_rates_processing


async def test_rates_processing_not_cashback(stq3_context, order_archive_mock):
    order_proc = {
        '_id': 'order_id',
        'commit_state': 'done',
        'extra_data': {'cashback': {'is_cashback': False}},
        'order': {
            'performer': {'tariff': {'class': 'econom'}, 'paid_supply': False},
        },
    }
    order_archive_mock.set_order_proc(order_proc)

    await cashback_rates_processing.task(stq3_context, 'order_id')


@pytest.mark.parametrize(
    'commit_state', ['init', 'pending', 'reserved', 'rollback'],
)
async def test_rates_processing_order_proc_not_committed(
        commit_state, stq3_context, order_archive_mock, mock_cashback, stq,
):
    @mock_cashback('/internal/rates/order')
    def _mock_coeff_register(request):
        assert False

    order_proc = {
        '_id': 'order_id',
        'commit_state': commit_state,
        'order': {
            'discount': {
                'cashbacks': [
                    {
                        'value': 0.1,
                        'class': 'econom',
                        'max_absolute_value': 300,
                    },
                ],
            },
        },
    }
    order_archive_mock.set_order_proc(order_proc)

    await cashback_rates_processing.task(stq3_context, 'order_id')

    assert _mock_coeff_register.times_called == 0
    assert stq.cashback_rates_processing.times_called == 1


@pytest.mark.config(
    CASHBACK_SPONSPOR_STATIC_PAYLOAD={
        'fintech': {'issuer': 'master'},
        'new_marketing': {'ticket': 'TAXIBACKEND-1'},
    },
)
@pytest.mark.config(CASHBACK_DISABLED_MARKETING_CASHBACKS=['new_marketing'])
@pytest.mark.parametrize(
    'pricing_user_meta, expected_rates, '
    'expected_possible_rates, expected_marketing_rates',
    [
        pytest.param(
            {'cashback_rate': 0.1},
            [{'class': 'econom', 'value': 0.1}],
            None,
            {},
            id='meta-without-max-value',
        ),
        pytest.param(
            {
                'cashback_rate': 0.1,
                'cashback_max_value': 1000,
                'possible_cashback_rate': 0.1,
            },
            [{'class': 'econom', 'max_absolute_value': 1000, 'value': 0.1}],
            {'enabled': True, 'value': 0.1},
            {},
            id='meta-with-max-value',
        ),
        pytest.param(
            {
                'cashback_rate': 0.1,
                'cashback_max_value': 1000,
                'possible_cashback_rate': 0.1,
                'marketing_cashback:fix': 100,
                'marketing_cashback:fintech:rate': 0.05,
                'marketing_cashback:fintech:fix': 50,
                'marketing_cashback:fintech:max_value': 60,
                'marketing_cashback:new_marketing:rate': 0.05,
                'marketing_cashback:new_marketing:fix': 50,
                'marketing_cashback:new_marketing:max_value': 60,
            },
            [{'class': 'econom', 'max_absolute_value': 1000, 'value': 0.1}],
            {'enabled': True, 'value': 0.1},
            {
                'fintech': {
                    'value': 0.05,
                    'max_absolute_value': 60,
                    'static_payload': {'issuer': 'master'},
                    'enabled': True,
                },
                'new_marketing': {
                    'value': 0.05,
                    'max_absolute_value': 60,
                    'static_payload': {'ticket': 'TAXIBACKEND-1'},
                    'enabled': False,
                },
            },
            id='marketing-cashbacks',
        ),
        pytest.param(
            {}, [{'class': 'econom', 'value': 0}], None, {}, id='no-meta',
        ),
    ],
)
async def test_rates_processing_new_pricing(
        stq3_context,
        order_archive_mock,
        mock_cashback,
        pricing_user_meta,
        expected_rates,
        expected_possible_rates,
        expected_marketing_rates,
):
    @mock_cashback('/internal/rates/order')
    def _mock_coeff_register(request):
        assert request.json['cashback']['by_classes'] == expected_rates

        if expected_possible_rates is not None:
            assert request.json['possible_cashback'] == expected_possible_rates
        else:
            assert request.json.get('possible_cashback', None) is None

        assert request.json['marketing_cashback'] == expected_marketing_rates

    order_proc = {
        '_id': 'order_id',
        'commit_state': 'done',
        'extra_data': {'cashback': {'is_cashback': True}},
        'order': {
            'performer': {'tariff': {'class': 'econom'}, 'paid_supply': False},
            'pricing_data': {'user': {'meta': pricing_user_meta}},
            'using_new_pricing': True,
        },
    }
    order_archive_mock.set_order_proc(order_proc)

    await cashback_rates_processing.task(stq3_context, 'order_id')


@pytest.mark.parametrize(
    'paid_supply, paid_supply_price, expected_rates',
    [
        pytest.param(
            False,
            None,
            [{'class': 'econom', 'value': 0.1, 'max_absolute_value': 200}],
            id='without-paid-supply',
        ),
        pytest.param(
            None,
            None,
            [{'class': 'econom', 'value': 0.1, 'max_absolute_value': 200}],
            id='without-paid-supply',
        ),
        pytest.param(
            True,
            50,
            [{'class': 'econom', 'max_absolute_value': 250, 'value': 0.1}],
            id='with-paid_supply',
        ),
        pytest.param(
            True,
            None,
            [{'class': 'econom', 'value': 0.1, 'max_absolute_value': 200}],
            id='without-paid-supply',
        ),
    ],
)
async def test_rates_processing_paid_supply(
        stq3_context,
        order_archive_mock,
        mock_cashback,
        paid_supply,
        paid_supply_price,
        expected_rates,
):
    @mock_cashback('/internal/rates/order')
    def _mock_coeff_register(request):
        assert request.json['cashback']['by_classes'] == expected_rates

    order_proc = {
        '_id': 'order_id',
        'commit_state': 'done',
        'extra_data': {'cashback': {'is_cashback': True}},
        'order': {
            'performer': {
                'tariff': {'class': 'econom'},
                'paid_supply': paid_supply,
            },
            'pricing_data': {
                'user': {
                    'meta': {'cashback_rate': 0.1, 'cashback_max_value': 200},
                    'additional_prices': {
                        'paid_supply': {
                            'meta': {
                                'cashback_rate': 0.1,
                                'cashback_max_value': 250,
                            },
                        },
                    },
                },
            },
            'using_new_pricing': True,
            'fixed_price': {'paid_supply_price': paid_supply_price},
        },
    }
    order_archive_mock.set_order_proc(order_proc)

    await cashback_rates_processing.task(stq3_context, 'order_id')
