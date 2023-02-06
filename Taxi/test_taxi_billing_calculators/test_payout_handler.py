import copy
import functools
import logging
import sys

import pytest

from taxi.billing.util import dates

from taxi_billing_calculators import config
from taxi_billing_calculators.calculators import handling_exceptions
from taxi_billing_calculators.calculators.payout import actions
from taxi_billing_calculators.calculators.payout import models as payout_models
from taxi_billing_calculators.calculators.payout import payout_handler
from taxi_billing_calculators.docs import doc_creator
from . import payout_test_clients

logging.basicConfig(stream=sys.stdout)


@pytest.mark.parametrize(
    'test_data_path',
    [
        pytest.param(
            'payout_create_journal.json',
            marks=pytest.mark.now('2019-09-15T00:00:00'),
        ),
        pytest.param(
            'payout_create_journal_filtering_old_event_at.json',
            marks=pytest.mark.now('2020-01-01T00:00:00'),
        ),
        pytest.param(
            'reversal_payout_create_journal.json',
            marks=pytest.mark.now('2019-09-15T00:00:00'),
        ),
        pytest.param(
            'due_payout_create_journal.json',
            marks=pytest.mark.now('2019-09-15T00:00:00'),
        ),
    ],
)
# pylint: disable=invalid-name
async def test_create_docs(test_data_path, load_json):
    test_data = load_json(test_data_path)
    payout_data = test_data['payout']
    payout = payout_models.Payout.from_json(payout_data)

    cfg = config.Config()
    cfg.BILLING_OLD_JOURNAL_LIMIT_DAYS = 10
    context = payout_models.PayoutHandlerContext(
        config=cfg,
        stq_agent=payout_test_clients.StqAgentClientMock(),
        billing_accounts_client=payout_test_clients.BillingAccountsClient(
            existing_accounts=test_data.get('existing_accounts'),
        ),
        billing_docs_client=payout_test_clients.BillingDocsClient(),
        billing_reports_client=payout_test_clients.BillingReportsClient(),
        billing_tlog_client=payout_test_clients.BillingTLogApiClient(),
        billing_limits_client=payout_test_clients.BillingLimitsApiClient,
        processing_client=payout_test_clients.ProcessingApiClient(),
        log_extra=None,
    )

    journal_doc_parameters = test_data['journal_doc_parameters']

    # pylint: disable=protected-access
    doc_creator_doc = payout_handler._make_doc_for_doc_creator(
        cfg=context.config,
        payout=payout,
        doc_kind=journal_doc_parameters['kind'],
        external_event_ref=journal_doc_parameters['external_event_ref'],
        log_extra=None,
    )

    await doc_creator.create_docs(
        billing_docs_client=context.billing_docs_client,
        billing_accounts_client=context.billing_accounts_client,
        doc_creator_docs=[doc_creator_doc],
        log_extra=context.log_extra,
    )

    assert (
        context.billing_accounts_client.created_entities
        == test_data['expected_entities']
    )
    created_docs = context.billing_docs_client.created_docs
    extended_docs = []
    for doc in created_docs:
        extended_doc = copy.deepcopy(doc)
        for entry in extended_doc['journal_entries']:
            full_account_desc = (
                context.billing_accounts_client.created_accounts[
                    entry['account_id'] - 1
                ]
            )
            full_account_desc.pop('expired', None)
            entry.update({'account': full_account_desc})
            entry.pop('account_id')
        extended_docs.append(extended_doc)
    assert extended_docs == test_data['expected_docs_with_accounts']


@pytest.mark.now('2020-06-01T05:00:00+00:00')
@pytest.mark.parametrize(
    'test_data_path',
    [
        'payout_create_reversal_payout.json',
        'payout_create_reversal_not_all_entries_fetched.json',
        'payout_create_reversal_none_entry_id.json',
    ],
)
# pylint: disable=invalid-name
async def test_create_reversal_payout(test_data_path, load_json):
    test_data = load_json(test_data_path)
    payout_data = test_data['payout']
    payout = payout_models.Payout.from_json(payout_data)

    context = payout_models.PayoutHandlerContext(
        config=config.Config(),
        stq_agent=payout_test_clients.StqAgentClientMock(),
        billing_accounts_client=payout_test_clients.BillingAccountsClient(),
        billing_docs_client=payout_test_clients.BillingDocsClient(),
        billing_reports_client=payout_test_clients.BillingReportsClient(
            existing_docs=test_data['existing_docs'],
        ),
        billing_tlog_client=payout_test_clients.BillingTLogApiClient(),
        billing_limits_client=payout_test_clients.BillingLimitsApiClient,
        processing_client=payout_test_clients.ProcessingApiClient(),
        log_extra=None,
    )

    try:
        # pylint: disable=protected-access
        reversal_payout = await payout_handler._create_reversal_payout(
            payout=payout, context=context,
        )
        expected_reversal_payout = payout_models.Payout.from_json(
            test_data['expected_reversal_payout'],
        )
        assert reversal_payout == expected_reversal_payout
    except handling_exceptions.PostponeHandling:
        assert test_data['expected_is_postponed']


@pytest.mark.now('2019-09-13T09:00:00.000000+00:00')
@pytest.mark.parametrize('test_data_path', ['push_entries.json'])
# pylint: disable=invalid-name
async def test_push_entries(
        test_data_path, load_json, taxi_billing_calculators_stq_taximeter_ctx,
):
    test_data = load_json(test_data_path)
    context = payout_models.PayoutHandlerContext(
        config=config.Config(),
        stq_agent=payout_test_clients.StqAgentClientMock(),
        billing_accounts_client=payout_test_clients.BillingAccountsClient(
            existing_accounts=test_data['existing_accounts'],
        ),
        billing_docs_client=payout_test_clients.BillingDocsClient(),
        billing_reports_client=payout_test_clients.BillingReportsClient(
            existing_docs=test_data['existing_docs'],
        ),
        billing_tlog_client=payout_test_clients.BillingTLogApiClient(),
        billing_limits_client=payout_test_clients.BillingLimitsApiClient,
        processing_client=payout_test_clients.ProcessingApiClient(),
        log_extra=None,
    )

    payout_data = test_data['payout']
    payout = payout_models.Payout.from_json(payout_data)
    payout.post_processing_actions = [
        actions.send_to_tlog,
        functools.partial(
            actions.send_to_taximeter,
            additional_data={'order_cost': '1000.0', 'order_currency': 'RUB'},
            db_id='<db_id>',
            driver_uuid='<driver_uuid>',
            kind='subvention',
        ),
        functools.partial(
            actions.create_income_journal,
            income_event_at=dates.parse_datetime(
                '2019-09-09T09:00:00.000000+00:00',
            ),
        ),
    ]

    # pylint: disable=protected-access
    await payout_handler._push_entries(
        payout=payout,
        context=context,
        created_docs=test_data['existing_docs'],
    )

    assert (
        context.billing_docs_client.created_docs == test_data['expected_docs']
    )
    assert (
        context.billing_tlog_client.entries
        == test_data['expected_tlog_entries']
    )
