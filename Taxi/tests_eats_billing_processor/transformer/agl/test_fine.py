import pytest
import yaml

from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - amount#fine:
                client_id: '5678'
                amount#xget: /event/amount
                timestamp#xget: /event/transaction_date
                order_finished_at#xget: /event/order_finished_at
                fine_params:
                    fine: '10'
                    fix_fine: '10'
                    min_fine: '0'
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_fine(testpoint, transformer_fixtures):
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    billing_payment = {
        'amount': '1000',
        'transaction_date': '2021-04-05T09:25:00+00:00',
        'order_finished_at': '2021-04-05T09:24:00+00:00',
    }

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=billing_payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {
        'amount': {'calculated_amount': '110', 'actual_amount': '110'},
    }


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - amount#fine:
                client_id: '5678'
                amount#xget: /event/amount
                timestamp#xget: /event/transaction_date
                order_finished_at#xget: /event/order_finished_at
                fine_params:
                    application_period: 48
                    fine: '10'
                    fix_fine: '10'
                    min_fine: '0'
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_fine_application_period(testpoint, transformer_fixtures):
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    billing_payment = {
        'amount': '1000',
        'transaction_date': '2021-04-05T00:00:00+03:00',
        'order_finished_at': '2021-04-01T09:24:00+00:00',
    }

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=billing_payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {
        'amount': {'calculated_amount': '0', 'actual_amount': '0'},
    }
