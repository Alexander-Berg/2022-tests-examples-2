import decimal
import typing

import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import models

RECEIPT_1 = models.Receipt(
    order_id=consts.ORDER_ID,
    receipt_id='receipt_id_1',
    receipt_data_type='order',
    items=[],
    total=decimal.Decimal(0),
    receipt_type=models.ReceiptType.payment.name,
    link='https://url.pdf',
    receipt_source=consts.FNS_SOURCE,
    payload=models.receipt_payload(models.Country.Russia),
)
RECEIPT_2 = models.Receipt(
    order_id=consts.ORDER_ID,
    receipt_id='receipt_id_2',
    receipt_data_type='order',
    items=[],
    total=decimal.Decimal(0),
    receipt_type=models.ReceiptType.refund.name,
    link='https://url.pdf',
    receipt_source=consts.EASY_COUNT_SOURCE,
    payload=models.receipt_payload(
        models.Country.Israel, external_id='external_id',
    ),
)


@pytest.fixture(name='grocery_invoices_receipts')
def _grocery_invoices_receipts(taxi_grocery_invoices):
    async def _inner(status_code=200, **kwargs):
        response = await taxi_grocery_invoices.post(
            '/admin/invoices/v1/receipts',
            json={'order_id': consts.ORDER_ID, **kwargs},
        )
        assert response.status_code == status_code
        return response.json()

    return _inner


async def test_basic(grocery_invoices_receipts, grocery_invoices_db):
    receipts = [RECEIPT_1, RECEIPT_2]

    grocery_invoices_db.insert(*receipts)

    response = await grocery_invoices_receipts()

    _check_receipts(response['receipts'], receipts)


async def test_only_cold_storage(
        grocery_invoices_receipts, grocery_cold_storage,
):
    receipts = [RECEIPT_1, RECEIPT_2]

    for receipt in receipts:
        grocery_cold_storage.append_receipt(receipt)

    response = await grocery_invoices_receipts()

    _check_receipts(response['receipts'], receipts)


async def test_with_cold_storage(
        grocery_invoices_receipts, grocery_invoices_db, grocery_cold_storage,
):
    receipts = [RECEIPT_2, RECEIPT_1]

    grocery_invoices_db.insert(*receipts)

    grocery_cold_storage.append_receipt(RECEIPT_1)

    response = await grocery_invoices_receipts()

    _check_receipts(response['receipts'], receipts)


def _check_receipts(response: dict, receipts: typing.List[models.Receipt]):
    def _expected(receipt: models.Receipt):
        return dict(
            url=receipt.link,
            receipt_data_type=receipt.receipt_data_type,
            total=str(receipt.total),
        )

    assert response['payments'] == [
        _expected(it)
        for it in receipts
        if it.receipt_type == models.ReceiptType.payment.name
    ]

    assert response['refunds'] == [
        _expected(it)
        for it in receipts
        if it.receipt_type == models.ReceiptType.refund.name
    ]
