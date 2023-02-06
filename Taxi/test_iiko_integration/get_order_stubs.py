import copy

from test_iiko_integration import stubs


CONFIG_RESTAURANT_INFO = copy.deepcopy(stubs.CONFIG_RESTAURANT_INFO)
CONFIG_RESTAURANT_INFO['restaurant01'].update(
    {'geopoint': {'lon': 55.734625, 'lat': 37.642932}},
)


CONFIG_RESTAURANT_GROUP_INFO = copy.deepcopy(
    stubs.CONFIG_RESTAURANT_GROUP_INFO,
)

CONFIG_RESTAURANT_GROUP_INFO['restaurant_group_01'].update(
    {'name_tanker_key': 'restaurants.restaurant_01_key'},
)

ORDER_ITEMS = [
    dict(
        item_id=1,
        product_id='01',
        name='Hamburger',
        quantity='3',
        price_per_unit='50',
        price_for_customer='150',
        vat_percent='20',
        vat_amount='25',
        discount_amount='0',
        discount_percent='0',
        price_without_discount='150',
    ),
    dict(
        item_id=2,
        product_id='02',
        name='Cola',
        quantity='0.1',
        price_per_unit='250',
        price_for_customer='20.0',
        vat_percent='0',
        vat_amount='0',
        discount_amount='5.0',
        discount_percent='20',
        price_without_discount='25.0',
    ),
    dict(
        item_id=3,
        product_id='03',
        name='French_fries',
        quantity='0',
        price_per_unit='100',
        price_for_customer='0',
        vat_percent='0',
        vat_amount='0',
        discount_amount='0',
        discount_percent='0',
        price_without_discount='0',
    ),
]

ORDER_OK_RESPONSE = dict(
    amount='170',
    currency='RUB',
    order_id='01',
    restaurant_order_id='iiko_1',
    money_amount='120',
    complement_amount='50',
    items=[
        dict(
            item_id=1,
            product_id='01',
            name='Hamburger',
            quantity='3',
            price_per_unit='50',
            price_for_customer='150',
            vat_percent='20',
            vat_amount='25',
            discount_amount='0',
            discount_percent='0',
            price_without_discount='150',
            money_amount='100',
            complement_amount='50',
        ),
        dict(
            item_id=2,
            product_id='02',
            name='Cola',
            quantity='0.1',
            price_per_unit='250',
            price_for_customer='20.0',
            vat_percent='0',
            vat_amount='0',
            discount_amount='5.0',
            discount_percent='20',
            price_without_discount='25.0',
            money_amount='20.0',
        ),
        dict(
            item_id=3,
            product_id='03',
            name='French_fries',
            quantity='0',
            price_per_unit='100',
            price_for_customer='0',
            vat_percent='0',
            vat_amount='0',
            discount_amount='0',
            discount_percent='0',
            price_without_discount='0',
            money_amount='0',
            complement_amount='0',
        ),
    ],
    restaurant_info=dict(
        geopoint={'lon': 55.734625, 'lat': 37.642932},
        country_code='RU',
        region_id=1,
        eda_client_id=1,
        name='Ресторан 01',
        address='address_ru',
    ),
    amount_without_discount='175',
    cashback=dict(rate='30', value='51'),
    discount='5',
    status=dict(
        restaurant_status='PAYMENT_CONFIRMED',
        invoice_status='CLEARED',
        updated_at='2020-04-04T17:00:00+00:00',
    ),
    invoice_id='invoice_01',
)

ORDER_OK_RESPONSE_FOR_USER = {
    **ORDER_OK_RESPONSE,
    'items': [
        dict(
            item_id=1,
            product_id='01',
            name='Hamburger',
            quantity='3',
            price_per_unit='50.00',
            price_for_customer='150.00',
            vat_percent='20',
            vat_amount='25.00',
            discount_amount='0.00',
            discount_percent='0.00',
            price_without_discount='150.00',
            money_amount='100.00',
            complement_amount='50.00',
        ),
        dict(
            item_id=2,
            product_id='02',
            name='Cola',
            quantity='0.1',
            price_per_unit='250.00',
            price_for_customer='20.00',
            vat_percent='0',
            vat_amount='0.00',
            discount_amount='5.00',
            discount_percent='20.00',
            price_without_discount='25.00',
            money_amount='20.00',
        ),
        dict(
            item_id=3,
            product_id='03',
            name='French_fries',
            quantity='0',
            price_per_unit='100.00',
            price_for_customer='0.00',
            vat_percent='0',
            vat_amount='0.00',
            discount_amount='0.00',
            discount_percent='0.00',
            price_without_discount='0.00',
            money_amount='0.00',
            complement_amount='0.00',
        ),
    ],
    'amount_without_discount': '175.00',
    'cashback': dict(rate='30.00', value='51'),
    'discount': '5.00',
    'amount': '170.00',
    'money_amount': '120.00',
    'complement_amount': '50.00',
}

ORDER_2_OK_RESPONSE = dict(
    amount='200',
    currency='RUB',
    order_id='02',
    restaurant_order_id='iiko_2',
    items=[],
    restaurant_info=dict(
        geopoint={'lon': 55.734625, 'lat': 37.642932},
        country_code='RU',
        region_id=1,
        eda_client_id=1,
        name='Ресторан 01',
        address='address_ru',
    ),
    amount_without_discount='220',
    cashback=dict(rate='50', value='100'),
    discount='20',
    status=dict(
        restaurant_status='PENDING',
        invoice_status='INIT',
        updated_at='2020-04-04T17:00:00+00:00',
    ),
)

ORDER_3_OK_RESPONSE = dict(
    amount='200',
    money_amount='200',
    currency='RUB',
    order_id='03',
    restaurant_order_id='iiko_3',
    items=[],
    restaurant_info=dict(
        geopoint={'lon': 55.734625, 'lat': 37.642932},
        country_code='RU',
        region_id=1,
        eda_client_id=1,
        name='Ресторан 01',
        address='address_ru',
    ),
    amount_without_discount='220',
    cashback=dict(rate='50', value='100'),
    discount='20',
    status=dict(
        restaurant_status='PAYMENT_CONFIRMED',
        invoice_status='CLEARED',
        updated_at='2020-04-04T17:00:00+00:00',
    ),
    yandex_uid='4041153212',
)

ORDER_NOT_FOUND_RESPONSE = dict(
    code='order_not_found', message='No order with such id in db',
)

ORDER_BY_INVOICE_ID_NOT_FOUND_RESPONSE = dict(
    code='order_not_found', message='No order with such invoice_id in db',
)

ORDER_ADMIN_OK_RESPONSE = {
    'order': {
        **ORDER_OK_RESPONSE,
        **{
            'invoice_id': 'invoice_01',
            # 'status': {
            #     'restaurant_status': 'PENDING',
            #     'invoice_status': 'INIT',
            #     'updated_at': '2020-04-04T17:00:00+00:00',
            # },
        },
    },
    'version': 3,
    'status_history': [
        {
            'restaurant_status': 'PENDING',
            'invoice_status': 'INIT',
            'updated_at': '2020-04-04T17:00:00+00:00',
        },
    ],
    'refund_available_reasons': [
        {'code': 'reason_code_1', 'description': 'reason_description_1'},
        {'code': 'reason_code_2', 'description': 'reason_description_2'},
    ],
    'payment_events': [
        {
            'money_amount': '200',
            'complement_amount': '100',
            'created_at': '2020-04-04T17:00:00+00:00',
            'items': [
                {
                    'discount_amount': '0',
                    'discount_percent': '0',
                    'item_id': 1,
                    'name': 'Hamburger',
                    'price_for_customer': '150',
                    'price_per_unit': '50',
                    'price_without_discount': '150',
                    'product_id': '01',
                    'quantity': '3',
                    'vat_amount': '25',
                    'vat_percent': '20',
                    'money_amount': '100',
                    'complement_amount': '50',
                },
                {
                    'discount_amount': '25',
                    'discount_percent': '20',
                    'item_id': 2,
                    'name': 'Cola',
                    'price_for_customer': '100',
                    'price_per_unit': '250',
                    'price_without_discount': '125',
                    'product_id': '02',
                    'quantity': '0.5',
                    'vat_amount': '0',
                    'vat_percent': '0',
                    'money_amount': '100',
                },
                {
                    'discount_amount': '0',
                    'discount_percent': '0',
                    'item_id': 3,
                    'name': 'French_fries',
                    'price_for_customer': '50',
                    'price_per_unit': '100',
                    'price_without_discount': '50',
                    'product_id': '03',
                    'quantity': '0.5',
                    'vat_amount': '0',
                    'vat_percent': '0',
                    'money_amount': '0',
                    'complement_amount': '50',
                },
            ],
            'status': 'done',
            'trust_id': 'trust_id',
            'type': 'charge',
            'updated_at': '2020-04-04T17:00:00+00:00',
        },
        {
            'money_amount': '0',
            'complement_amount': '50',
            'created_at': '2020-04-04T17:00:00+00:00',
            'items': [
                {
                    'discount_amount': '0',
                    'discount_percent': '0',
                    'item_id': 3,
                    'name': 'French_fries',
                    'price_for_customer': '50',
                    'price_per_unit': '100',
                    'price_without_discount': '50',
                    'product_id': '03',
                    'quantity': '0.5',
                    'vat_amount': '0',
                    'vat_percent': '0',
                    'money_amount': '0',
                    'complement_amount': '50',
                },
            ],
            'status': 'processing',
            'trust_id': 'trust_id',
            'type': 'refund',
            'updated_at': '2020-04-04T17:00:00+00:00',
            'ticket': {'ticket': 'TAXITICKET-1', 'type': 'startrack'},
            'reason': {
                'code': 'reason_code_1',
                'description': 'reason_description_1',
            },
            'operator_login': 'login',
        },
        {
            'money_amount': '80',
            'complement_amount': '0',
            'created_at': '2020-04-04T17:00:00+00:00',
            'items': [
                {
                    'discount_amount': '20.0',
                    'discount_percent': '20',
                    'item_id': 2,
                    'name': 'Cola',
                    'price_for_customer': '80.0',
                    'price_per_unit': '250',
                    'price_without_discount': '100.0',
                    'product_id': '02',
                    'quantity': '0.4',
                    'vat_amount': '0',
                    'vat_percent': '0',
                    'money_amount': '80.0',
                },
            ],
            'status': 'pending',
            'type': 'refund',
            'updated_at': '2020-04-04T17:00:00+00:00',
            'ticket': {'ticket': 'CHATTERBOX-2', 'type': 'chatterbox'},
            'reason': {
                'code': 'unknown_reason_code',
                'description': 'unknown_reason_code',
            },
            'operator_login': 'login',
        },
    ],
    'trust_id': 'trust_id',
    'receipts': [
        {
            'type': 'payment',
            'sum': '300',
            'url': 'https://taxi-iiko-integration.s3.yandex.net/document_1',
        },
        {
            'type': 'refund',
            'sum': '50',
            'url': 'https://taxi-iiko-integration.s3.yandex.net/document_2',
        },
        {
            'type': 'refund',
            'sum': '80',
            'url': 'https://taxi-iiko-integration.s3.yandex.net/document_3',
        },
    ],
    'receipt_email': 'user@yandex.ru',
}

ORDER_2_ADMIN_OK_RESPONSE = {
    'order': ORDER_2_OK_RESPONSE,
    'version': 1,
    'status_history': [],
    'refund_available_reasons': [
        {'code': 'reason_code_1', 'description': 'reason_description_1'},
        {'code': 'reason_code_2', 'description': 'reason_description_2'},
    ],
    'payment_events': [],
    'receipts': [],
}

ORDER_3_ADMIN_OK_RESPONSE = {
    'order': ORDER_3_OK_RESPONSE,
    'version': 1,
    'status_history': [],
    'refund_available_reasons': [
        {'code': 'reason_code_1', 'description': 'reason_description_1'},
        {'code': 'reason_code_2', 'description': 'reason_description_2'},
    ],
    'payment_events': [],
    'receipts': [],
    'card_number': '400000****1234',
}


def user_order_with_complement():
    order_copy = copy.deepcopy(ORDER_OK_RESPONSE_FOR_USER)
    order_copy['complement_amount'] = '50.00'
    return order_copy


def admin_order_with_complement():
    order_copy = copy.deepcopy(ORDER_ADMIN_OK_RESPONSE)
    order_copy['order']['complement_amount'] = '50'
    order_copy['order']['cashback']['value'] = '0'
    return order_copy


def add_complement_to_db(pgsql):
    with pgsql['iiko_integration'].cursor() as cursor:
        cursor.execute(
            f'UPDATE iiko_integration.orders SET'
            f' complement_amount = 50, '
            f'complement_payment_method_id = \'123456789abcdef\', '
            f'complement_payment_method_type = \'personal_wallet\';',
        )
