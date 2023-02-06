import pytest


from transactions.internal import archivation
from transactions.models import fields
from transactions.models import wrappers


@pytest.mark.parametrize(
    'test_case_path',
    [
        pytest.param(
            'pending_operations.json',
            id='it should return True when operations are pending',
        ),
        pytest.param(
            'pending_cashback_operations.json',
            id='it should return True when cashback operations are pending',
        ),
        pytest.param(
            'pending_compensation_operations.json',
            id=(
                'it should return True when compensation operations '
                'are pending'
            ),
        ),
        pytest.param(
            'pending_transactions.json',
            id='it should return True when transactions are pending',
        ),
        pytest.param(
            'finished.json',
            id='it should return False when nothing is pending',
        ),
    ],
)
def test_is_pending(load_json, test_case_path):
    test_case = load_json(test_case_path)
    invoice = wrappers.make_invoice(test_case['invoice'], fields.Fields())
    expected = test_case['expected']

    assert archivation.is_pending(invoice) is expected


@pytest.mark.parametrize(
    'test_case_path',
    [
        pytest.param(
            'paid.json', id='it should return True when invoice is paid',
        ),
        pytest.param(
            'unpaid.json', id='it should return False when invoice is unpaid',
        ),
    ],
)
def test_is_paid(load_json, test_case_path):
    test_case = load_json(test_case_path)
    invoice = wrappers.make_invoice(test_case['invoice'], fields.Fields())
    expected = test_case['expected']

    assert archivation.is_paid(invoice, fields.Fields()) is expected


@pytest.mark.parametrize(
    'test_case_path',
    [
        pytest.param(
            'handled.json', id='it should return True when invoice is handled',
        ),
        pytest.param(
            'not_handled.json',
            id='it should return False when invoice is not handled',
        ),
    ],
)
def test_is_handled(load_json, test_case_path):
    test_case = load_json(test_case_path)
    invoice = wrappers.make_invoice(test_case['invoice'], fields.Fields())
    expected = test_case['expected']

    assert archivation.is_handled(invoice, fields.Fields()) is expected


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(False, id='it should return False by default'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                TRANSACTIONS_SAVE_IS_HANDLED={'__default__': 1},
            ),
            id='it should return True when default probability is 1',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                TRANSACTIONS_SAVE_IS_HANDLED={'taxi': 1, '__default__': 0},
            ),
            id='it should return True when scope probability is 1',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TRANSACTIONS_SAVE_IS_HANDLED={'taxi': 0, '__default__': 1},
            ),
            id='it should prefer scope value over default value',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TRANSACTIONS_SAVE_IS_HANDLED={
                    'taxi': 0,
                    'eda': 1,
                    '__default__': 0,
                },
            ),
            id='it should ignore other scopes',
        ),
    ],
)
def test_should_save_is_handled_field(stq3_context, expected):
    assert archivation.should_save_is_handled_field(stq3_context) is expected


@pytest.mark.filldb(eda_invoices='for_test_try_save_is_handled')
@pytest.mark.config(TRANSACTIONS_SAVE_IS_HANDLED={'eda': 1, '__default__': 0})
@pytest.mark.parametrize(
    'invoice_id, expected_is_handled, should_update',
    [
        pytest.param(
            'handled_invoice_is_handled_none_id',
            True,
            True,
            id='it should update invoice if is_handled changes None -> True',
        ),
        pytest.param(
            'handled_invoice_is_handled_none_id',
            None,
            False,
            marks=pytest.mark.config(
                TRANSACTIONS_SAVE_IS_HANDLED={'__default__': 0},
            ),
            id='it should not update invoice if config is disabled',
        ),
        pytest.param(
            'not_handled_invoice_is_handled_none_id',
            None,
            False,
            id='it should not update if if is_handled stays False',
        ),
        pytest.param(
            'handled_invoice_is_handled_false_id',
            True,
            True,
            id='it should update invoice if is_handled changes False -> True',
        ),
        pytest.param(
            'not_handled_invoice_is_handled_true_id',
            False,
            True,
            id='it should update invoice if is_handled changes True -> False',
        ),
        pytest.param(
            'handled_invoice_is_handled_true_id',
            True,
            False,
            id='it should update invoice if is_handled stays True',
        ),
    ],
)
async def test_try_save_is_handled(
        invoice_id, expected_is_handled, should_update, eda_stq3_context,
):
    invoice_before = await _fetch_invoice(invoice_id, eda_stq3_context)
    await archivation.try_save_is_handled(invoice_before, eda_stq3_context)
    invoice_after = await _fetch_invoice(invoice_id, eda_stq3_context)
    assert (
        invoice_after['invoice_request'].get('is_handled')
        is expected_is_handled
    )
    assert bool(invoice_after.get('updated')) == should_update


async def _fetch_invoice(invoice_id, eda_stq3_context):
    data = await eda_stq3_context.transactions.invoices.find_one(invoice_id)
    return wrappers.make_invoice(data, fields.Fields())
