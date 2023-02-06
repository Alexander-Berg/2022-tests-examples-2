import functools
import operator

import pytest

from taxi.billing.util import dates
from testsuite.utils import ordered_object

from taxi_billing_calculators import config
from taxi_billing_calculators import models as calc_models
from taxi_billing_calculators.calculators.payout import actions
from taxi_billing_calculators.calculators.payout import models as payout_models
from taxi_billing_calculators.calculators.payout.converters import (
    b2b_user_payment,
)
from taxi_billing_calculators.calculators.payout.converters import cashback
from taxi_billing_calculators.calculators.payout.converters import (
    invoice_transaction_cleared,
)
from taxi_billing_calculators.calculators.payout.converters import (
    subvention_antifraud,
)
from . import payout_test_clients


@pytest.mark.parametrize(
    'test_data_path,action',
    [
        ('send_to_tlog.json', actions.send_to_tlog),
        ('send_dry_to_tlog.json', actions.send_to_tlog),
        ('send_cashback_to_tlog.json', cashback.send_cashback_to_tlog),
        (
            'send_cashback_to_tlog_with_payload.json',
            cashback.send_cashback_to_tlog,
        ),
        (
            'send_cashback_to_tlog_with_free_form_payload.json',
            cashback.send_cashback_to_tlog,
        ),
        (
            'send_cashback_to_tlog_with_wallet_id.json',
            cashback.send_cashback_to_tlog,
        ),
        (
            'send_cashback_to_tlog_with_transaction_type.json',
            cashback.send_cashback_to_tlog,
        ),
        (
            'send_cashless_payments_to_tlog.json',
            invoice_transaction_cleared.send_cashless_payments_to_tlog,
        ),
        (
            'send_cashless_payments_to_tlog_with_contract_id.json',
            invoice_transaction_cleared.send_cashless_payments_to_tlog,
        ),
        (
            'send_antifraud_check_to_tlog.json',
            subvention_antifraud.send_antifraud_check_to_tlog,
        ),
        (
            'send_antifraud_check_to_tlog_with_contract_id.json',
            subvention_antifraud.send_antifraud_check_to_tlog,
        ),
        (
            'send_b2b_user_payments_to_tlog.json',
            b2b_user_payment.send_b2b_user_payments_to_tlog,
        ),
        (
            'send_empty_b2b_user_payments_to_tlog.json',
            b2b_user_payment.send_b2b_user_payments_to_tlog,
        ),
    ],
)
@pytest.mark.now('2020-04-13T12:00:00.000000+00:00')
async def test_send_to_tlog_action(
        test_data_path, action, load_json, monkeypatch,
):
    test_data = load_json(test_data_path)
    context = _create_context()
    monkeypatch.setattr(
        config.Config,
        'BILLING_CALCULATORS_SEND_ENTRIES_TO_BILLING_FIN_PAYOUTS',
        True,
    )
    await _test_post_processing_action(context, test_data, action)


@pytest.mark.parametrize(
    'test_data_path,action',
    [
        (
            'send_to_tlog_grocery_revenues.json',
            functools.partial(
                actions.send_to_tlog_grocery_eats_topics,
                topic='grocery_revenues',
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-13T12:00:00.000000+00:00')
async def test_send_to_tlog_grocery_revenues_action(
        test_data_path, action, load_json, monkeypatch,
):
    test_data = load_json(test_data_path)
    context = _create_context()
    monkeypatch.setattr(
        config.Config,
        'BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT',
        {'gross_sales_b2c': {'payment': 1, 'refund': -1}},
    )
    await _test_post_processing_action(context, test_data, action)


@pytest.mark.parametrize(
    'test_data_path,action',
    [
        (
            'send_to_tlog_eats_revenues.json',
            functools.partial(
                actions.send_to_tlog_grocery_eats_topics,
                topic='eats_revenues',
            ),
        ),
        (
            'send_to_tlog_eats_expenses.json',
            functools.partial(
                actions.send_to_tlog_grocery_eats_topics,
                topic='eats_expenses',
            ),
        ),
        (
            'send_to_tlog_eats_agent.json',
            functools.partial(
                actions.send_to_tlog_eats_agent, topic='eats_agent',
            ),
        ),
        (
            'send_to_tlog_eats_payments.json',
            functools.partial(
                actions.send_to_tlog_grocery_eats_topics,
                topic='eats_payments',
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-13T12:00:00.000000+00:00')
async def test_send_to_tlog_eats_revenues_action(
        test_data_path, action, load_json, monkeypatch,
):
    test_data = load_json(test_data_path)
    context = _create_context()
    monkeypatch.setattr(
        config.Config,
        'BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT',
        {
            'eats_delivery_fee': {'payment': 1, 'refund': -1},
            'eats_marketing_promocode_picker': {'payment': 1, 'refund': -1},
            'eats_badge_corporate': {'payment': 1, 'refund': -1},
            'eats_client_service_fee': {'payment': 1, 'refund': -1},
        },
    )
    await _test_post_processing_action(context, test_data, action)


@pytest.mark.parametrize(
    'test_data_path',
    [
        'send_to_taximeter.json',
        'send_to_taximeter_hiring.json',
        'send_to_taximeter_hiring_with_car.json',
        'send_to_taximeter_software_subscription_wo_total.json',
        'send_to_taximeter_software_subscription_with_total.json',
        'send_dry_to_taximeter.json',
        'send_to_taximeter_additional_data.json',
        'send_to_taximeter_zero_commission.json',
        'send_to_taximeter_no_alias_id.json',
        'send_to_taximeter_filter_park_commission.json',
    ],
)
async def test_send_to_taximeter_action(
        test_data_path, load_json, taxi_billing_calculators_stq_taximeter_ctx,
):
    context = _create_context()
    test_data = load_json(test_data_path)
    await _test_post_processing_action(
        context,
        test_data,
        functools.partial(
            actions.send_to_taximeter, **test_data['action_keywords'],
        ),
    )


@pytest.mark.now('2019-09-13T09:00:00.000000+00:00')
@pytest.mark.parametrize(
    'test_data_path, limit_days',
    [
        ('create_income_journal.json', 365),
        ('create_income_journal_hiring.json', 365),
        ('create_income_journal_hiring_with_car.json', 365),
        ('create_income_journal_software_subscription_wo_total.json', 365),
        ('create_income_journal_software_subscription_with_total.json', 365),
        ('create_income_journal_driver_referral.json', 365),
        ('create_income_journal_old_event_at.json', 1),
    ],
)
async def test_create_income_journal_action(
        test_data_path, limit_days, load_json, monkeypatch,
):
    context = _create_context()
    test_data = load_json(test_data_path)

    monkeypatch.setattr(
        config.Config, 'BILLING_OLD_JOURNAL_LIMIT_DAYS', limit_days,
    )

    await _test_post_processing_action(
        context,
        test_data,
        functools.partial(
            actions.create_income_journal,
            income_event_at=dates.parse_datetime(
                '2019-09-09T09:00:00.000000+00:00',
            ),
        ),
    )


@pytest.mark.parametrize(
    'test_case_json', ('send_to_limits_stq_via_billing_functions.json',),
)
async def test_send_to_limits(test_case_json, load_json):
    context = _create_context()

    test_data = load_json(test_case_json)
    await _test_post_processing_action(
        context, test_data, actions.send_to_limits,
    )
    calls = context.stq_agent.calls
    ordered_object.assert_eq(
        calls, test_data['expected_limits_stq_calls'], 'task_id',
    )


@pytest.mark.parametrize(
    'test_case_json',
    ('send_balance_update.json', 'send_balance_update_no_events.json'),
)
async def test_send_balance_update(test_case_json, load_json):
    context = _create_context()

    test_data = load_json(test_case_json)
    await _test_post_processing_action(
        context, test_data, actions.send_balance_update,
    )
    calls = context.stq_agent.calls
    ordered_object.assert_eq(
        calls, test_data['expected_balance_update_stq_calls'], 'task_id',
    )


@pytest.mark.parametrize(
    'test_case_json',
    (
        'send_income_entries.json',
        'send_income_entries_cash.json',
        'send_income_entries_no_events.json',
        'send_income_entries_rounding_error.json',
    ),
)
async def test_send_income_entries(test_case_json, load_json):
    context = _create_context()

    test_data = load_json(test_case_json)
    await _test_post_processing_action(
        context, test_data, actions.send_income_entries,
    )
    assert (
        context.processing_client.processing_requests
        == test_data['expected_processing_requests']
    )


async def _test_post_processing_action(context, test_data, action):
    if 'configs' in test_data:
        for cfg, value in test_data['configs'].items():
            setattr(context.config, cfg, value)

    input_entries = [
        calc_models.JournalEntry.from_json(entry)
        for entry in test_data['all_entries']
    ]

    payout_data = test_data['payout']
    payout = payout_models.Payout.from_json(payout_data)

    await action(payout=payout, context=context, all_entries=input_entries)

    assert (
        context.billing_accounts_client.created_accounts
        == test_data['expected_accounts']
    )

    assert (
        context.billing_accounts_client.created_entities
        == test_data['expected_entities']
    )

    assert (
        context.billing_docs_client.created_docs == test_data['expected_docs']
    )
    assert (
        context.billing_tlog_client.entries
        == test_data['expected_tlog_entries']
    )
    assert sorted(
        context.billing_limits_client.entries,
        key=operator.itemgetter('limit_ref'),
    ) == test_data.get('expected_limits_entries', [])
    assert sorted(context.billing_limits_client.tokens) == test_data.get(
        'expected_limits_headers', [],
    )


def _create_context():
    return payout_models.PayoutHandlerContext(
        config=config.Config(),
        stq_agent=payout_test_clients.StqAgentClientMock(),
        billing_accounts_client=payout_test_clients.BillingAccountsClient(),
        billing_docs_client=payout_test_clients.BillingDocsClient(),
        billing_reports_client=payout_test_clients.BillingReportsClient(),
        billing_tlog_client=payout_test_clients.BillingTLogApiClient(),
        billing_limits_client=payout_test_clients.BillingLimitsApiClient(),
        processing_client=payout_test_clients.ProcessingApiClient(),
        log_extra=None,
    )
