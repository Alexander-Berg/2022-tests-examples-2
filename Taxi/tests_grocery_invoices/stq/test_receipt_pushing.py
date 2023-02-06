import decimal

from tests_grocery_invoices import consts
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models

RECEIPT_DATA_1 = {
    'order_id': consts.ORDER_ID,
    'payload': {
        'receipt_id': 'receipt_id_1',
        'receipt_data_type': 'order',
        'items': [],
        'total': '0.0000',
        'receipt_type': 'payment',
        'link': 'link',
        'receipt_source': consts.FNS_SOURCE,
        'payload': {'country': models.Country.Russia.name},
        'created': consts.NOW,
    },
}
RECEIPT_DATA_2 = {
    'order_id': consts.ORDER_ID,
    'payload': {
        'receipt_id': 'receipt_id_2',
        'receipt_data_type': 'order',
        'items': models.items_to_json(
            [helpers.make_receipt_item('item_1', '10', '1')],
        ),
        'total': '10.0000',
        'receipt_type': 'refund',
        'link': consts.EASY_COUNT_LINK,
        'receipt_source': consts.EASY_COUNT_SOURCE,
        'payload': {
            'country': models.Country.Israel.name,
            'external_id': 'external_id',
            'receipt_uuid': 'receipt_uuid',
        },
        'created': None,
    },
}


async def test_basic(
        run_grocery_invoices_receipt_pushing, grocery_invoices_db,
):
    receipts = [RECEIPT_DATA_1, RECEIPT_DATA_2]

    await run_grocery_invoices_receipt_pushing(receipts)

    pg_receipts = grocery_invoices_db.load_receipts(consts.ORDER_ID)
    assert pg_receipts == [_expected_receipt(it) for it in receipts]


def _expected_receipt(receipt_data: dict) -> models.Receipt:
    payload = receipt_data['payload']

    return models.Receipt(
        order_id=receipt_data['order_id'],
        receipt_id=payload['receipt_id'],
        receipt_data_type=payload['receipt_data_type'],
        items=payload['items'],
        total=decimal.Decimal(payload['total']),
        receipt_type=payload['receipt_type'],
        link=payload['link'],
        receipt_source=payload['receipt_source'],
        payload=payload['payload'],
    )
