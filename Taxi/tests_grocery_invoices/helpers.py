# pylint: disable=inconsistent-return-statements

from tests_grocery_invoices import consts
from tests_grocery_invoices import models


def get_item_title(country: models.Country, item_type: models.ItemType):
    if item_type == models.ItemType.delivery:
        if country == models.Country.Russia:
            return consts.DELIVERY_RECEIPT_RU
        if country == models.Country.Israel:
            return consts.DELIVERY_RECEIPT_HE
        if country == models.Country.France:
            return consts.DELIVERY_RECEIPT_FR
        if country in [models.Country.GreatBritain, models.Country.RSA]:
            return consts.DELIVERY_RECEIPT_EN

    if item_type == models.ItemType.tips:
        if country == models.Country.Russia:
            return consts.TIPS_RECEIPT_RU
        if country == models.Country.Israel:
            return consts.TIPS_RECEIPT_HE
        if country == models.Country.France:
            return consts.TIPS_RECEIPT_FR
        if country in [models.Country.GreatBritain, models.Country.RSA]:
            return consts.TIPS_RECEIPT_EN

    if item_type == models.ItemType.service_fee:
        if country == models.Country.Russia:
            return consts.SERVICE_FEE_RECEIPT_RU
        if country == models.Country.Israel:
            return consts.SERVICE_FEE_RECEIPT_HE
        if country == models.Country.France:
            return consts.SERVICE_FEE_RECEIPT_FR
        if country in [models.Country.GreatBritain, models.Country.RSA]:
            return consts.SERVICE_FEE_RECEIPT_EN

    assert False


def get_vat(country: models.Country):
    if country == models.Country.Russia:
        return consts.RUSSIA_VAT
    if country == models.Country.Israel:
        return consts.ISRAEL_VAT
    if country == models.Country.France:
        return consts.FRANCE_VAT
    if country == models.Country.GreatBritain:
        return consts.BRITAIN_VAT
    if country == models.Country.RSA:
        return consts.RSA_VAT

    assert False


def make_polling_task_id(polling_id, receipt_data_type, source):
    return f'{polling_id}/{receipt_data_type}/{source}'


def make_cart_item(
        item_id, price, quantity, vat=None, full_price=None, supplier_tin=None,
):
    if full_price is None:
        full_price = price

    if vat is None:
        vat = consts.RUSSIA_VAT

    sub_items = [
        models.GroceryCartSubItem(
            item_id=item_id + '_0',
            price=str(price),
            full_price=str(full_price),
            quantity=str(quantity),
        ),
    ]

    return models.GroceryCartItemV2(
        item_id=item_id,
        sub_items=sub_items,
        title=item_id,
        vat=vat,
        supplier_tin=supplier_tin,
    )


def cart_item_from_model(item: models.Item):
    return make_cart_item(
        item_id=item.item_id,
        price=item.price,
        full_price=item.full_price,
        quantity=item.quantity,
        vat=item.vat,
    )


def make_receipt_item(
        item_id, price, quantity, item_type='product', vat=None, title=None,
):
    return models.Item(
        item_id=item_id,
        price=str(price),
        quantity=str(quantity),
        vat=vat,
        item_type=item_type,
        title=title,
    )


def make_product_receipt(country):
    return [
        make_receipt_item(
            item_id=product['item_id'] + '_0',
            price=product['price'],
            quantity=product['quantity'],
            vat=get_vat(country),
            title=product['item_id'],
        )
        for product in consts.PRODUCTS
    ]


def make_delivery_receipt(country):
    return [
        make_receipt_item(
            item_id='delivery',
            price=consts.DELIVERY_AMOUNT,
            quantity=1,
            item_type='delivery',
            vat=get_vat(country),
            title=get_item_title(country, models.ItemType.delivery),
        ),
    ]


def make_tips_receipt(country):
    return [
        make_receipt_item(
            item_id='tips',
            price=consts.TIPS_AMOUNT,
            quantity=1,
            item_type='tips',
            vat=get_vat(country),
            title=get_item_title(country, models.ItemType.tips),
        ),
    ]


def make_service_fee_receipt(country):
    return [
        make_receipt_item(
            item_id='service_fee',
            price=consts.SERVICE_FEE_AMOUNT,
            quantity=1,
            item_type='service_fee',
            vat=get_vat(country),
            title=get_item_title(country, models.ItemType.service_fee),
        ),
    ]


def make_cart_items(country):
    return [
        make_cart_item(**product, vat=get_vat(country))
        for product in consts.PRODUCTS
    ]


def create_receipt_pg_task(
        task_id, task_type, receipt_type, status, items, created=consts.NOW_DT,
):
    args = {
        'items': [
            {
                'item_id': item.item_id,
                'price': item.price,
                'quantity': item.quantity,
                'item_type': item.item_type,
            }
            for item in items
        ],
        'country': models.Country.Russia.name,
        'order_id': consts.ORDER_ID,
        'terminal_id': consts.TERMINAL_ID,
        'operation_id': consts.OPERATION_ID,
        'receipt_type': receipt_type,
        'payment_method': consts.DEFAULT_PAYMENT_METHOD,
        'payment_finished': consts.PAYMENT_FINISHED,
        'receipt_data_type': consts.DELIVERY_RECEIPT_DATA_TYPE,
        'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
    }

    task = models.Task(
        task_id=task_id,
        task_type=task_type,
        order_id=consts.ORDER_ID,
        status=status,
        args=args,
        result_payload=None,
        params={
            'source': consts.EATS_CORE_SOURCE,
            'country_iso3': models.Country.France.country_iso3,
            'exec_tries': 1,
        },
        created=created,
    )

    return task
