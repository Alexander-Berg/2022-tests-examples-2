import copy

import asynctest
import pytest

from transactions.internal.payment_gateways.compensation import trust
from transactions.models import compensation
from transactions.models import notify
from transactions.models import wrappers


@pytest.mark.now('2020-09-07T00:00:00')
@pytest.mark.parametrize(
    'testcase_json, ', ['start_new_compensation_rounded_amount.json'],
)
async def test_start_new_compensation(
        patch,
        stq3_context,
        load_py_json,
        patch_commit_payments,
        mock_get_service_order,
        mock_trust_create_basket,
        *,
        testcase_json,
):
    testcase = load_py_json(testcase_json)
    payment_request = compensation.Payment.from_dict(
        data=testcase,
        round_amount=stq3_context.transactions.trust_details.round_amount,
    )
    gateway = trust.TrustGateway(['card'], stq3_context)
    local_invoice_data = copy.deepcopy(testcase['invoice_data'])
    invoice = wrappers.make_invoice(
        local_invoice_data, fields=stq3_context.transactions.fields,
    )
    mock_get_service_order('<alias_id>', status='success', status_code='')
    mock_trust_create_basket(purchase_token='compensation-purchase-token')
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    invoice, _ = await gateway.start_new_compensation(
        invoice=invoice,
        operation_id=testcase['operation_id'],
        payment_request=payment_request,
        context=stq3_context,
        tlog_notifier=tlog_notifier,
        log_extra=None,
    )
    assert not tlog_notifier.method_calls
    actual_compensations = invoice['billing_tech']['compensations']
    assert actual_compensations == testcase['expected_compensations']


@pytest.fixture(name='patch_commit_payments')
def _patch_commit_payments(patch):
    @patch('transactions.models.invoice_operations.commit_payments')
    # pylint: disable=unused-variable
    async def commit_payments(invoice, update, *args):
        invoice = copy.deepcopy(invoice.data)
        update_set = update.get('$set')
        update_push = update.get('$push')
        if update_set:
            for key, value in update_set.items():
                path = key.split('.')
                _extract_from_dictionary(invoice, *path[:-1])[path[-1]] = value
        if update_push:
            for key, value in update_push.items():
                path = key.split('.')
                _extract_from_dictionary(invoice, *path[:-1])[path[-1]].append(
                    value,
                )
        return invoice


def _extract_from_dictionary(dictionary: dict, *keys_or_indexes):
    value = dictionary
    for key_or_index in keys_or_indexes:
        if isinstance(value, list):
            key_or_index = int(key_or_index)
        value = value[key_or_index]
    return value
