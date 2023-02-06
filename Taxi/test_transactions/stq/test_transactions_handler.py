# pylint: disable=protected-access

import datetime as dt

import pytest

from transactions.internal import transactions_handler
from transactions.internal.payment_gateways import agent
from transactions.models import const
from transactions.models import wrappers


@pytest.mark.parametrize(
    'invoice_id, expected_eta',
    [
        ('no-hold-success', None),
        ('one-ready-to-clear', 0),
        ('ready-to-clear-by-clear-eta', 0),
        ('not-ready-to-clear-by-clear-eta', dt.datetime(2020, 2, 2, 6, 0, 1)),
        ('ready-to-clear-by-automatic', 0),
        ('ready-to-clear-by-automatic-personal-wallet', 0),
        ('not-ready-to-clear-by-automatic', dt.datetime(2020, 2, 2, 6, 0, 1)),
    ],
)
@pytest.mark.filldb(orders='for_test_prepare_to_clear')
@pytest.mark.now('2020-02-02T06:00:00')
async def test_prepare_to_clear(invoice_id, expected_eta, stq3_context):
    invoice = await _fetch_invoice(invoice_id, stq3_context)
    _, eta = await transactions_handler._prepare_to_clear(
        invoice, stq3_context, log_extra=None,
    )
    assert eta == expected_eta


@pytest.mark.parametrize(
    'invoice_id, expected',
    [
        ('no-active-operation', False),
        ('active-update-operation', True),
        ('active-update-compensations-operation', False),
    ],
)
@pytest.mark.filldb(orders='for_test_can_start_new_hold')
async def test_can_start_new_hold(invoice_id, expected, stq3_context):
    invoice = await _fetch_invoice(invoice_id, stq3_context)
    assert (
        transactions_handler._can_start_new_hold_or_refund(invoice) is expected
    )


async def _fetch_invoice(invoice_id, stq3_context):
    doc = await stq3_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    return wrappers._InvoiceV2(doc, fields=stq3_context.transactions.fields)


def test_unknown_stage():
    stage = transactions_handler.UnknownStage()

    assert stage.get_name() is None
    assert stage.get_full_stage_names(agent.AgentGateway()) == []


@pytest.mark.parametrize(
    'billing_service, payment_type, name, expected_full_stage_names',
    [
        pytest.param(
            'uber',
            const.PaymentType.CARD,
            'hold',
            [
                'agent:hold:billing_service=uber:payment_type=card',
                'agent:hold:billing_service=uber',
                'agent:hold',
            ],
            id='it should include stage for payment type if it is present',
        ),
        pytest.param(
            'uber',
            None,
            'hold',
            ['agent:hold:billing_service=uber', 'agent:hold'],
            id='it should exclude stage for payment type if it is absent',
        ),
    ],
)
def test_transaction_stage(
        billing_service, payment_type, name, expected_full_stage_names,
):
    gateway = agent.AgentGateway()
    stage = transactions_handler.TransactionStage(
        billing_service=billing_service, payment_type=payment_type, name=name,
    )

    assert stage.get_name() == name
    assert stage.get_full_stage_names(gateway) == expected_full_stage_names


@pytest.mark.parametrize(
    'invoice_data',
    [
        pytest.param(
            {'billing_tech': {'transactions': []}, 'invoice_payment_tech': {}},
            id='it should return UnknownStage when there is no transactions',
        ),
        pytest.param(
            {
                'billing_tech': {'transactions': [{'status': 'weird'}]},
                'invoice_payment_tech': {},
            },
            id='it should return UnknownStage if transactions.status is weird',
        ),
    ],
)
def test_get_unknown_stage(stq3_context, invoice_data):
    invoice = wrappers.make_invoice(
        invoice_data, stq3_context.transactions.fields,
    )
    stage = transactions_handler.get_stage(invoice)
    assert isinstance(stage, transactions_handler.UnknownStage)


@pytest.mark.parametrize(
    'invoice_data, expected_full_stage_names',
    [
        pytest.param(
            {
                'billing_tech': {
                    'transactions': [
                        {
                            'status': 'hold_pending',
                            'payment_method_type': 'sbp',
                        },
                    ],
                },
                'invoice_payment_tech': {},
                'invoice_request': {'billing_service': 'uber'},
            },
            [
                'agent:hold:billing_service=uber:payment_type=sbp',
                'agent:hold:billing_service=uber',
                'agent:hold',
            ],
            id='it should include stage for payment type if it is present',
        ),
        pytest.param(
            {
                'billing_tech': {'transactions': [{'status': 'hold_pending'}]},
                'invoice_payment_tech': {},
                'invoice_request': {'billing_service': 'uber'},
            },
            ['agent:hold:billing_service=uber', 'agent:hold'],
            id='it should exclude stage for payment type if it is absent',
        ),
    ],
)
def test_get_transaction_stage(
        stq3_context, invoice_data, expected_full_stage_names,
):
    gateway = agent.AgentGateway()
    invoice = wrappers.make_invoice(
        invoice_data, stq3_context.transactions.fields,
    )
    stage = transactions_handler.get_stage(invoice)
    assert stage.get_full_stage_names(gateway) == expected_full_stage_names
