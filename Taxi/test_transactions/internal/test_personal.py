from typing import Optional

import pytest

from transactions.internal import personal
from transactions.models import payment
from transactions.models import wrappers


@pytest.mark.parametrize(
    'invoice_data, expected_phone',
    [
        (
            {
                'invoice_request': {'personal_phone_id': 'abc'},
                'invoice_payment_tech': {},
            },
            '112',
        ),
        ({'invoice_request': {}, 'invoice_payment_tech': {}}, None),
    ],
)
async def test_unmangle_user_phone(
        stq3_context, mockserver, invoice_data, expected_phone,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    # pylint: disable=unused-variable
    def mock_phones_retrieve(request):
        resp_body = {'value': '112', 'id': 'phone_id'}
        return mockserver.make_response(status=200, json=resp_body)

    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    actual_phone = await personal.unmangle_user_phone(stq3_context, invoice)
    assert actual_phone == expected_phone


@pytest.mark.parametrize(
    'invoice_data, expected_email',
    [
        (
            {
                'invoice_request': {'personal_email_id': 'email_id'},
                'invoice_payment_tech': {},
            },
            'x@example.com',
        ),
        ({'invoice_request': {}, 'invoice_payment_tech': {}}, None),
    ],
)
async def test_unmangle_user_email(
        stq3_context, mockserver, invoice_data, expected_email,
):
    @mockserver.json_handler('/personal/v1/emails/retrieve')
    # pylint: disable=unused-variable
    def mock_emails_retrieve(request):
        resp_body = {'value': 'x@example.com', 'id': 'email_id'}
        return mockserver.make_response(status=200, json=resp_body)

    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    actual_email = await personal.unmangle_user_email(stq3_context, invoice)
    assert actual_email == expected_email


def fri(tin_id: Optional[str]) -> payment.FiscalReceiptInfo:
    return payment.FiscalReceiptInfo(tin_id, '', '', None)


def ufi(
        info: payment.FiscalReceiptInfo, tin: Optional[str],
) -> personal.UnmangledFiscalInfo:
    return personal.UnmangledFiscalInfo(info, tin)


@pytest.mark.parametrize(
    'input_items, expected_items',
    [
        ([], []),
        (
            [fri('known-1'), fri('unknown-1')],
            [ufi(fri('known-1'), 'tin-1'), ufi(fri('unknown-1'), None)],
        ),
        ([fri(None)], [ufi(fri(None), None)]),
    ],
)
async def test_unmangle_fiscal_receipt_infos(
        stq3_context, mockserver, input_items, expected_items,
):
    @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
    # pylint: disable=unused-variable
    def mock_tins_bulk_retrieve(request):
        assert request.json['items']
        return mockserver.make_response(
            status=200, json={'items': [{'id': 'known-1', 'value': 'tin-1'}]},
        )

    actual_items = await personal.unmangle_fiscal_receipt_infos(
        stq3_context, input_items,
    )
    assert actual_items == expected_items
